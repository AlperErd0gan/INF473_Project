import os
import json
from typing import Optional
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from gsu_requirements import GSU_BIL_REQUIREMENTS

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"
FAILED_GRADES = {"FF", "DZ", "F"}

PARSE_SYSTEM_PROMPT = """You are a university transcript parsing expert. Extract ALL courses from a GSU (Galatasaray University) transcript, including failed ones.

The transcript format is tab-separated with semester headers and course rows:

  2021 - 2022 Güz Yarıyılı
  Kodu    Ders Adı    Notu    Kredi    AKTS    Türü
  INF112-B    Programlamaya Giriş    BA    5.0    6    Z
  ...
  AKADEMİK NOT ORTALAMASI    ANO    KREDİ TOPLAMI    AKTS TOPLAMI
  Yarıyıl    2.10    23.5    30.0
  Genel    2.10    23.5    30.0

Column mapping:
- Kodu → code (course code, may include section suffix like -A, -B, -C — keep as-is)
- Ders Adı → name
- Notu → grade (AA, BA, BB, CB, CC, DC, DD, F, W, DZ, FF, etc.)
- AKTS → ects (integer)

GPA extraction:
- The cumulative GPA is on the LAST "Genel" row in the transcript, second column (e.g. "Genel    2.49    ..." → gpa = 2.49)

Skip these rows entirely (do NOT extract as courses):
- "AKADEMİK NOT ORTALAMASI ..." header rows
- "Yarıyıl ..." summary rows
- "Genel ..." summary rows
- Semester header rows (e.g. "2021 - 2022 Güz Yarıyılı")
- Column header rows ("Kodu    Ders Adı ...")

Return ONLY valid JSON matching this exact schema:
{
  "student_name": string or null,
  "student_number": string or null,
  "gpa": number,
  "courses": [
    {"code": string, "name": string, "grade": string, "ects": integer}
  ]
}

Rules:
- Include ALL courses even failed ones (F, FF, DZ, W)
- Course codes must be uppercase
- ects must be an integer (use the AKTS column, not Kredi)
- Return raw JSON only, no markdown, no explanation"""

REPORT_SYSTEM_PROMPT = """You are a graduation advisor for the Computer Engineering department at GSU (Galatasaray University).

Write a concise 2-3 sentence graduation status report in Turkish using formal language.
Base your report strictly on the provided analysis data — do not add or infer anything beyond what is given.

Compare courses strictly by course code. Do not infer missing courses from names. A course is only missing if its exact code does not appear in the passed courses list.

Return ONLY valid JSON: {"report": "Turkish report text here"}"""


class CourseEntry(BaseModel):
    code: str
    name: str
    grade: str
    ects: int


class ParsedTranscript(BaseModel):
    student_name: Optional[str]
    student_number: Optional[str]
    gpa: float
    courses: list[CourseEntry]


class AgentVerdict(BaseModel):
    agent: str
    verdict: str  # "pass" | "fail"
    issues: list[str]
    details: dict


def _normalize_code(code: str) -> str:
    """Strip section suffix (e.g. INF112-B → INF112) and normalize whitespace/case."""
    normalized = code.strip().replace(" ", "").upper()
    # Remove trailing -[A-Z] or -[A-Z][0-9] section indicators
    import re
    normalized = re.sub(r"-[A-Z][0-9]?$", "", normalized)
    return normalized


def _chat(system: str, user: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    return response.choices[0].message.content


class TranscriptParserAgent:
    """Parses raw transcript text into structured data using LLM."""

    def parse(self, transcript_text: str) -> ParsedTranscript:
        raw = _chat(PARSE_SYSTEM_PROMPT, transcript_text)
        return ParsedTranscript.model_validate_json(raw)


class CourseVerifierAgent:
    """Checks mandatory course completion against GSU curriculum."""

    def evaluate(self, parsed: ParsedTranscript) -> AgentVerdict:
        passed = [c for c in parsed.courses if c.grade.strip().upper() not in FAILED_GRADES]
        completed_codes = {_normalize_code(c.code) for c in passed}
        mandatory = GSU_BIL_REQUIREMENTS["mandatory_courses"]

        completed_mandatory = [
            f"{c['code']} - {c['name']}"
            for c in mandatory
            if _normalize_code(c["code"]) in completed_codes
        ]
        missing_mandatory = [
            f"{c['code']} - {c['name']}"
            for c in mandatory
            if _normalize_code(c["code"]) not in completed_codes
        ]

        issues = []
        if missing_mandatory:
            codes = ", ".join(c.split(" - ")[0] for c in missing_mandatory)
            issues.append(f"{len(missing_mandatory)} zorunlu ders eksik: {codes}")

        return AgentVerdict(
            agent="CourseVerifier",
            verdict="pass" if not missing_mandatory else "fail",
            issues=issues,
            details={
                "completed_mandatory": completed_mandatory,
                "missing_mandatory": missing_mandatory,
                "completed_codes": sorted(completed_codes),
            },
        )


class ECTSVerifierAgent:
    """Checks total ECTS credits meet graduation threshold."""

    def evaluate(self, parsed: ParsedTranscript) -> AgentVerdict:
        passed = [c for c in parsed.courses if c.grade.strip().upper() not in FAILED_GRADES]
        transcript_total_ects = sum(c.ects for c in passed)
        required_ects = GSU_BIL_REQUIREMENTS["min_ects"]
        print(f"[ECTSVerifierAgent] Parsed ECTS sum: {transcript_total_ects}")

        ects_ok = transcript_total_ects >= required_ects
        issues = []
        if not ects_ok:
            issues.append(f"AKTS yetersiz: {transcript_total_ects} / minimum {required_ects}")

        return AgentVerdict(
            agent="ECTSVerifier",
            verdict="pass" if ects_ok else "fail",
            issues=issues,
            details={
                "transcript_total_ects": transcript_total_ects,
                "required_ects": required_ects,
            },
        )


class RequirementsAgent:
    """Checks GPA and elective group requirements."""

    def evaluate(self, parsed: ParsedTranscript) -> AgentVerdict:
        passed = [c for c in parsed.courses if c.grade.strip().upper() not in FAILED_GRADES]
        completed_codes = {_normalize_code(c.code) for c in passed}

        gpa_ok = parsed.gpa >= GSU_BIL_REQUIREMENTS["min_gpa"]
        issues = []

        if not gpa_ok:
            issues.append(f"GNO yetersiz: {parsed.gpa:.2f} / minimum 2.00")

        elective_issues = []
        for group in GSU_BIL_REQUIREMENTS["elective_groups"]:
            group_codes = {_normalize_code(o["code"]) for o in group["options"]}
            taken_count = len(completed_codes & group_codes)
            required = group["required_count"]
            if taken_count < required:
                needed = required - taken_count
                sem = group["semester"]
                desc = group.get("description", "INF seçmeli")
                elective_issues.append(
                    f"Dönem {sem} {desc}: {needed} ders eksik (mevcut {taken_count}/{required})"
                )

        issues.extend(elective_issues)

        return AgentVerdict(
            agent="RequirementsChecker",
            verdict="pass" if not issues else "fail",
            issues=issues,
            details={
                "gpa": parsed.gpa,
                "gpa_ok": gpa_ok,
                "elective_issues": elective_issues,
            },
        )


class MasterAgent:
    """
    Orchestrates CourseVerifierAgent, ECTSVerifierAgent, and RequirementsAgent.
    Collects verdicts, determines graduation eligibility, and generates final report.
    """

    def __init__(self):
        self.parser = TranscriptParserAgent()
        self.course_agent = CourseVerifierAgent()
        self.ects_agent = ECTSVerifierAgent()
        self.requirements_agent = RequirementsAgent()

    def run(self, transcript_text: str) -> dict:
        parsed = self.parser.parse(transcript_text)

        course_verdict = self.course_agent.evaluate(parsed)
        ects_verdict = self.ects_agent.evaluate(parsed)
        req_verdict = self.requirements_agent.evaluate(parsed)

        all_issues = course_verdict.issues + ects_verdict.issues + req_verdict.issues
        is_graduated = all(
            v.verdict == "pass" for v in [course_verdict, ects_verdict, req_verdict]
        )

        report = self._generate_report(parsed, ects_verdict, all_issues, is_graduated, course_verdict)

        return {
            "student_name": parsed.student_name,
            "student_number": parsed.student_number,
            "gpa": parsed.gpa,
            "transcript_total_ects": ects_verdict.details["transcript_total_ects"],
            "required_ects": ects_verdict.details["required_ects"],
            "is_graduated": is_graduated,
            "completed_courses": [c.model_dump() for c in parsed.courses],
            "completed_mandatory_courses": course_verdict.details["completed_mandatory"],
            "missing_courses": course_verdict.details["missing_mandatory"],
            "missing_conditions": all_issues,
            "agent_verdicts": {
                "course_verifier": course_verdict.model_dump(),
                "ects_verifier": ects_verdict.model_dump(),
                "requirements_checker": req_verdict.model_dump(),
            },
            "report_text": report,
        }

    def _generate_report(
        self,
        parsed: ParsedTranscript,
        ects_verdict: AgentVerdict,
        all_issues: list[str],
        is_graduated: bool,
        course_verdict: AgentVerdict,
    ) -> str:
        summary = {
            "student_name": parsed.student_name,
            "gpa": parsed.gpa,
            "transcript_total_ects": ects_verdict.details["transcript_total_ects"],
            "required_ects": ects_verdict.details["required_ects"],
            "is_graduated": is_graduated,
            "missing_conditions": all_issues,
            "missing_mandatory_count": len(course_verdict.details["missing_mandatory"]),
            "missing_mandatory_courses": course_verdict.details["missing_mandatory"],
            "completed_codes": course_verdict.details["completed_codes"],
        }
        raw = _chat(REPORT_SYSTEM_PROMPT, json.dumps(summary, ensure_ascii=False, indent=2))
        return json.loads(raw).get("report", "")


def run_analysis_pipeline(transcript_text: str) -> dict:
    return MasterAgent().run(transcript_text)
