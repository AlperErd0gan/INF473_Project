import os
import re
import json
from typing import Optional
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from gsu_requirements import GSU_BIL_REQUIREMENTS
from logger import CaseLogger

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
# Primary model with fallbacks for rate limits or other failures
MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]

FAILED_GRADES = {"FF", "DZ", "F", "IA", "NP", "W", "WF"}

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

REPORT_SYSTEM_PROMPT = """You are the MasterReportAgent for the Computer Engineering department at GSU (Galatasaray University).

Write a concise 2-3 sentence graduation status report in the target language from the user payload.
Base your report strictly on the provided analysis data; do not add or infer anything beyond what is given.

Use advisor-quality academic prose. Do not expose internal machine values, field names, enums, or raw booleans in the report text.
Forbidden report wording includes: true, false, pass, fail, is_graduated, eligible_to_graduate, not_eligible_to_graduate, JSON, boolean.

Interpret the master decision semantically:
- If requirements are satisfied, state that the student meets the graduation requirements.
- If requirements are not satisfied, state that the student does not currently meet the graduation requirements and summarize the main blockers.

Compare courses strictly by course code. Do not infer missing courses from names. A course is only missing if its exact code does not appear in the passed courses list.

Return ONLY valid JSON: {"report": "report text here"}"""


REPORT_REVIEW_SYSTEM_PROMPT = """You are the ReportCriticAgent for a university graduation advisor.

Review the draft report against the analysis data and rewrite it if needed.
Preserve the factual decision and all key blockers. Keep it concise, formal, and in the requested target language.

The final report must not contain internal machine values, field names, enums, or raw booleans.
Forbidden report wording includes: true, false, pass, fail, is_graduated, eligible_to_graduate, not_eligible_to_graduate, JSON, boolean.

Return ONLY valid JSON: {"report": "final polished report text here"}"""


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
    statement: str
    issues: list[str]
    details: dict


def _normalize_code(code: str) -> str:
    """Strip section suffix (e.g. INF112-B → INF112) and normalize whitespace/case."""
    normalized = code.strip().replace(" ", "").upper()
    normalized = re.sub(r"-[A-Z][0-9]?$", "", normalized)
    return normalized


def _accepted_codes_for_requirement(code: str) -> set[str]:
    """
    Return all normalized course codes that satisfy a requirement code,
    including official curriculum equivalencies.
    """
    normalized = _normalize_code(code)
    accepted = {normalized}
    equivalencies = GSU_BIL_REQUIREMENTS.get("course_equivalencies", {})
    for eq in equivalencies.get(normalized, []):
        accepted.add(_normalize_code(eq))
    return accepted


def _is_legacy_curriculum(completed_codes: set[str]) -> bool:
    """
    Heuristic for older CE curriculum variants (e.g. ayid=32),
    where some semester elective counts differ from the current plan.
    """
    legacy_markers = {
        "ING127",  # old plan semester 1 chemistry
        "INF316",  # old plan mandatory (later mapped to INF345)
        "CNT350",  # old plan mandatory (later mapped to CNT250)
        "INF470",  # old plan mandatory course
        "INF211",  # old plan mandatory course
        "INF223",  # old plan OOP code family
        "INF299",  # old plan internship code
        "INF204",  # old plan electromagnetics course
        "ING204",  # old plan high math II
        "ING203",  # old plan high math I
    }
    return bool(completed_codes & legacy_markers)


def _legacy_extra_elective_codes(group: dict) -> set[str]:
    """
    Extra elective codes that are only valid for legacy curricula.
    Keep these separate so current curricula are not under-enforced.
    """
    sem = group.get("semester")
    desc = group.get("description", "INF seçmeli")
    if sem == 6 and desc == "INF seçmeli":
        # In 2022-2025 plans, INF345 could be used as an INF elective pool course.
        return {"INF345"}
    return set()


def _failed_codes(parsed: ParsedTranscript) -> set[str]:
    return {
        _normalize_code(c.code)
        for c in parsed.courses
        if c.grade.strip().upper() in FAILED_GRADES
    }


def _is_language_course(code: str) -> bool:
    normalized = _normalize_code(code)
    return normalized.startswith("FLF") or normalized.startswith("FLE")


def _is_b2_or_higher(name: str) -> bool:
    upper = name.upper()
    return bool(re.search(r"\b(B2(?:\.\d+)?|C1(?:\.\d+)?|C2(?:\.\d+)?)\b", upper))


def _extract_last_cumulative_gpa(transcript_text: str) -> Optional[float]:
    """
    Extract GPA from the last "Genel" summary row deterministically.
    Expected row shape: Genel <gpa> <credit_total> <ects_total>
    """
    matches = list(
        re.finditer(
            r"^\s*Genel\s+([0-9]+(?:[.,][0-9]+)?)\s+[0-9]+(?:[.,][0-9]+)?\s+[0-9]+(?:[.,][0-9]+)?\s*$",
            transcript_text,
            flags=re.MULTILINE,
        )
    )
    if not matches:
        return None

    raw_gpa = matches[-1].group(1).replace(",", ".")
    try:
        return float(raw_gpa)
    except ValueError:
        return None


def _chat(system: str, user: str, tools: list = None, messages: list = None) -> object:
    """Wrapper for Groq API calls with multi-model fallback and optional tool calling."""
    last_exception = None
    
    if messages is None:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        
    for model_name in MODELS:
        try:
            kwargs = {
                "model": model_name,
                "messages": messages,
                "temperature": 0.0,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            else:
                kwargs["response_format"] = {"type": "json_object"}
                
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message
        except Exception as e:
            last_exception = e
            # Only print warning if there are more models to try
            if model_name != MODELS[-1]:
                print(f"Warning: Model {model_name} failed ({e}). Attempting fallback...")
            continue
            
    # If all models fail, raise the last encountered error
    if last_exception:
        raise last_exception
    raise Exception("All configured Groq models failed to respond.")



class TranscriptParserAgent:
    """Parses raw transcript text into structured data using LLM."""

    def parse(self, transcript_text: str) -> ParsedTranscript:
        raw = _chat(PARSE_SYSTEM_PROMPT, transcript_text).content
        parsed = ParsedTranscript.model_validate_json(raw)

        # Deterministic override: GPA must come from the last "Genel" row.
        deterministic_gpa = _extract_last_cumulative_gpa(transcript_text)
        if deterministic_gpa is not None:
            parsed = parsed.model_copy(update={"gpa": deterministic_gpa})

        return parsed


class CourseVerifierAgent:
    """Checks mandatory course completion against GSU curriculum."""

    def evaluate(self, parsed: ParsedTranscript, lang: str = "tr") -> AgentVerdict:
        passed = [c for c in parsed.courses if c.grade.strip().upper() not in FAILED_GRADES]
        completed_codes = {_normalize_code(c.code) for c in passed}
        mandatory = GSU_BIL_REQUIREMENTS["mandatory_courses"]

        completed_mandatory = [
            f"{c['code']} - {c['name']}"
            for c in mandatory
            if completed_codes & _accepted_codes_for_requirement(c["code"])
        ]
        missing_mandatory = [
            f"{c['code']} - {c['name']}"
            for c in mandatory
            if not (completed_codes & _accepted_codes_for_requirement(c["code"]))
        ]

        issues = []
        if missing_mandatory:
            codes = ", ".join(c.split(" - ")[0] for c in missing_mandatory)
            if lang == "en":
                issues.append(f"Missing {len(missing_mandatory)} mandatory courses: {codes}")
            else:
                issues.append(f"{len(missing_mandatory)} zorunlu ders eksik: {codes}")

        total = len(mandatory)
        done = len(completed_mandatory)
        if not missing_mandatory:
            statement = f"All {total} mandatory courses completed. No missing courses." if lang == "en" else f"Tüm {total} zorunlu ders tamamlandı. Eksik ders yok."
        else:
            if lang == "en":
                statement = f"{done}/{total} mandatory courses completed. {len(missing_mandatory)} missing: " + ", ".join(c.split(" - ")[0] for c in missing_mandatory)
            else:
                statement = f"{done}/{total} zorunlu ders tamamlandı. {len(missing_mandatory)} ders eksik: " + ", ".join(c.split(" - ")[0] for c in missing_mandatory)

        return AgentVerdict(
            agent="CourseVerifier",
            verdict="pass" if not missing_mandatory else "fail",
            statement=statement,
            issues=issues,
            details={
                "completed_mandatory": completed_mandatory,
                "missing_mandatory": missing_mandatory,
                "completed_codes": sorted(completed_codes),
            },
        )

    def cross_examine(self, ects_verdict: "AgentVerdict", lang: str = "tr") -> str:
        """Comment on ECTS result from a course perspective."""
        failed_ects = ects_verdict.details["required_ects"] - ects_verdict.details["transcript_total_ects"]
        if lang == "en":
            if ects_verdict.verdict == "fail":
                return (
                    f"ECTS deficit ({failed_ects} ECTS) may be caused by failed courses. "
                    f"Completing missing mandatory courses may close this gap."
                )
            return "ECTS status is sufficient, no additional issues from a course perspective."
        else:
            if ects_verdict.verdict == "fail":
                return (
                    f"AKTS açığı ({failed_ects} AKTS) kısmen başarısız derslerden kaynaklanıyor olabilir. "
                    f"Eksik zorunlu dersler tamamlanırsa AKTS açığı da kapanabilir."
                )
            return "AKTS durumu yeterli, ders tamamlama açısından ek sorun yok."


class ECTSVerifierAgent:
    """Checks total ECTS credits meet graduation threshold."""

    def evaluate(self, parsed: ParsedTranscript, lang: str = "tr") -> AgentVerdict:
        passed = [c for c in parsed.courses if c.grade.strip().upper() not in FAILED_GRADES]
        transcript_total_ects = sum(c.ects for c in passed)
        required_ects = GSU_BIL_REQUIREMENTS["min_ects"]
        print(f"[ECTSVerifierAgent] Parsed ECTS sum: {transcript_total_ects}")

        ects_ok = transcript_total_ects >= required_ects
        issues = []
        if not ects_ok:
            if lang == "en":
                issues.append(f"Insufficient ECTS: {transcript_total_ects} / minimum {required_ects}")
            else:
                issues.append(f"AKTS yetersiz: {transcript_total_ects} / minimum {required_ects}")

        if ects_ok:
            surplus = transcript_total_ects - required_ects
            if lang == "en":
                statement = f"Total ECTS {transcript_total_ects} / {required_ects}. Threshold met (+{surplus} surplus)."
            else:
                statement = f"Toplam AKTS {transcript_total_ects} / {required_ects}. Eşik sağlandı (+{surplus} fazla)."
        else:
            deficit = required_ects - transcript_total_ects
            if lang == "en":
                statement = f"Total ECTS {transcript_total_ects} / {required_ects}. {deficit} ECTS deficit."
            else:
                statement = f"Toplam AKTS {transcript_total_ects} / {required_ects}. {deficit} AKTS açığı var."

        return AgentVerdict(
            agent="ECTSVerifier",
            verdict="pass" if ects_ok else "fail",
            statement=statement,
            issues=issues,
            details={
                "transcript_total_ects": transcript_total_ects,
                "required_ects": required_ects,
            },
        )

    def cross_examine(self, course_verdict: "AgentVerdict", lang: str = "tr") -> str:
        """Comment on course situation from an ECTS perspective."""
        missing = course_verdict.details["missing_mandatory"]
        if lang == "en":
            if missing:
                missing_ects = sum(
                    c["ects"]
                    for c in GSU_BIL_REQUIREMENTS["mandatory_courses"]
                    if f"{c['code']} - {c['name']}" in missing
                )
                return (
                    f"Missing {len(missing)} mandatory courses account for approximately {missing_ects} ECTS. "
                    f"Completing these will improve the ECTS balance."
                )
            return "Mandatory course status does not negatively impact the ECTS calculation."
        else:
            if missing:
                missing_ects = sum(
                    c["ects"]
                    for c in GSU_BIL_REQUIREMENTS["mandatory_courses"]
                    if f"{c['code']} - {c['name']}" in missing
                )
                return (
                    f"Eksik {len(missing)} zorunlu dersin toplam AKTS değeri yaklaşık {missing_ects}. "
                    f"Bu dersler tamamlanırsa AKTS dengesi de iyileşebilir."
                )
            return "Zorunlu ders durumu AKTS hesabını olumsuz etkilemiyor."


class RequirementsAgent:
    """Checks GPA and elective group requirements."""

    def evaluate(self, parsed: ParsedTranscript, lang: str = "tr") -> AgentVerdict:
        passed = [c for c in parsed.courses if c.grade.strip().upper() not in FAILED_GRADES]
        completed_codes = {_normalize_code(c.code) for c in passed}
        failed_codes = _failed_codes(parsed)
        legacy_curriculum = _is_legacy_curriculum(completed_codes)

        gpa_ok = parsed.gpa >= GSU_BIL_REQUIREMENTS["min_gpa"]
        issues = []

        if not gpa_ok:
            issues.append(f"Insufficient GPA: {parsed.gpa:.2f} / minimum 2.00" if lang == "en" else f"GNO yetersiz: {parsed.gpa:.2f} / minimum 2.00")

        language_courses = [c for c in passed if _is_language_course(c.code)]
        language_ects = sum(c.ects for c in language_courses)
        english_b2_or_higher = any(_is_b2_or_higher(c.name) for c in language_courses)
        language_ok = language_ects >= 12 or english_b2_or_higher
        if not language_ok:
            issues.append(
                f"Language condition not met: foreign language ECTS {language_ects}/12 and B2+ level not detected" if lang == "en" else f"Dil koşulu sağlanmadı: yabancı dil AKTS {language_ects}/12 ve B2+ düzeyi tespit edilemedi"
            )

        elective_issues = []
        group_pool_codes = {}
        group_required = {}
        for group in GSU_BIL_REQUIREMENTS["elective_groups"]:
            group_codes = set()
            for option in group["options"]:
                group_codes.update(_accepted_codes_for_requirement(option["code"]))
            if legacy_curriculum:
                for code in _legacy_extra_elective_codes(group):
                    group_codes.add(_normalize_code(code))
            taken_count = len(completed_codes & group_codes)
            required = group["required_count"]
            # Legacy plan (e.g., ayid=32) requires 1 INF elective in semester 6.
            if legacy_curriculum and group["semester"] == 6 and group.get("description", "INF seçmeli") == "INF seçmeli":
                required = 1
            key = (group["semester"], group.get("description", "INF seçmeli"))
            group_pool_codes[key] = group_codes
            group_required[key] = required
            if taken_count < required:
                needed = required - taken_count
                sem = group["semester"]
                desc = group.get("description", "INF seçmeli")
                elective_issues.append(
                    f"Semester {sem} {desc}: missing {needed} course(s) (current {taken_count}/{required})" if lang == "en" else f"Dönem {sem} {desc}: {needed} ders eksik (mevcut {taken_count}/{required})"
                )

        if legacy_curriculum:
            # Transition notes from curriculum: some failed legacy courses require extra
            # electives on top of baseline elective obligations.
            extra_inf_required = 0
            extra_social_required = 0

            if "INF112" in failed_codes:
                extra_social_required += 1
            for code in ("INF115", "INF236", "INF446", "INF470"):
                if code in failed_codes:
                    extra_inf_required += 1
            if "INF204" in failed_codes:
                extra_inf_required += 1

            # ING144 failed -> INF321 technical drawing replacement requirement.
            if "ING144" in failed_codes and "INF321" not in completed_codes:
                elective_issues.append("Must complete INF321 Technical Drawing due to ING144 failure." if lang == "en" else "ING144 başarısızlığı için INF321 Teknik Resim dersi tamamlanmalı.")

            inf_group_keys = [
                (5, "INF seçmeli"),
                (6, "INF seçmeli"),
                (7, "INF seçmeli"),
                (8, "INF seçmeli"),
            ]
            total_inf_taken = len(
                completed_codes
                & set().union(*(group_pool_codes.get(k, set()) for k in inf_group_keys))
            )
            total_inf_required = sum(group_required.get(k, 0) for k in inf_group_keys)
            if total_inf_taken < total_inf_required + extra_inf_required:
                missing = (total_inf_required + extra_inf_required) - total_inf_taken
                elective_issues.append(
                    f"Additional INF elective required due to transition rules: missing {missing} course(s) "
                    f"(current {total_inf_taken}/{total_inf_required + extra_inf_required})." if lang == "en" else f"Geçiş kuralları nedeniyle ilave INF seçmeli: {missing} ders eksik (mevcut {total_inf_taken}/{total_inf_required + extra_inf_required})."
                )

            social_key = (8, "CNT or CC elective")
            social_taken = len(completed_codes & group_pool_codes.get(social_key, set()))
            social_required = group_required.get(social_key, 0)
            if social_taken < social_required + extra_social_required:
                missing = (social_required + extra_social_required) - social_taken
                elective_issues.append(
                    f"Additional social elective required due to transition rules: missing {missing} course(s) "
                    f"(current {social_taken}/{social_required + extra_social_required})." if lang == "en" else f"Geçiş kuralları nedeniyle ilave sosyal seçmeli: {missing} ders eksik (mevcut {social_taken}/{social_required + extra_social_required})."
                )

        issues.extend(elective_issues)

        parts = []
        if gpa_ok:
            parts.append(f"GPA {parsed.gpa:.2f} ≥ 2.00 (pass)" if lang == "en" else f"GNO {parsed.gpa:.2f} ≥ 2.00 (geçer)")
        else:
            parts.append(f"GPA {parsed.gpa:.2f} < 2.00 (fail)" if lang == "en" else f"GNO {parsed.gpa:.2f} < 2.00 (yetersiz)")
        if elective_issues:
            parts.append(f"{len(elective_issues)} elective group(s) missing" if lang == "en" else f"{len(elective_issues)} seçmeli grup eksik")
        else:
            parts.append("all elective groups completed" if lang == "en" else "tüm seçmeli gruplar tamamlandı")
        statement = "; ".join(parts) + "."

        return AgentVerdict(
            agent="RequirementsChecker",
            verdict="pass" if not issues else "fail",
            statement=statement,
            issues=issues,
            details={
                "gpa": parsed.gpa,
                "gpa_ok": gpa_ok,
                "language_ects": language_ects,
                "english_b2_or_higher": english_b2_or_higher,
                "language_ok": language_ok,
                "elective_issues": elective_issues,
            },
        )

    def cross_examine(self, course_verdict: "AgentVerdict", ects_verdict: "AgentVerdict", lang: str = "tr") -> str:
        """Comment on overall picture from a requirements perspective."""
        comments = []
        if lang == "en":
            if course_verdict.verdict == "fail":
                comments.append("Missing mandatory courses may have negatively impacted the GPA.")
            if ects_verdict.verdict == "fail":
                comments.append("ECTS deficit may be linked to missing elective courses.")
            if not comments:
                return "GPA and elective course requirements do not conflict with other findings."
        else:
            if course_verdict.verdict == "fail":
                comments.append("Eksik zorunlu dersler not ortalamasını olumsuz etkilemiş olabilir.")
            if ects_verdict.verdict == "fail":
                comments.append("AKTS açığı seçmeli ders eksikliğiyle bağlantılı olabilir.")
            if not comments:
                return "GNO ve seçmeli ders koşulları diğer bulgularla çelişmiyor."
        return " ".join(comments)


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

    def _check_student_history_tool(self, student_number: str = None, student_name: str = None) -> str:
        """Database tool for the existing MasterAgent."""
        if not student_number and not student_name:
            return json.dumps({"status": "error", "message": "No student information provided."})
        try:
            from database import SessionLocal
            from models import Student, AnalysisResult, Transcript
            from sqlalchemy import or_
            db = SessionLocal()
            
            query = db.query(AnalysisResult).join(Transcript).join(Student)
            
            conditions = []
            if student_number:
                conditions.append(Student.student_number == student_number)
            if student_name:
                conditions.append(Student.name == student_name)
                
            past_analysis = query.filter(or_(*conditions)).order_by(AnalysisResult.analyzed_at.desc()).first()
            
            if past_analysis:
                return json.dumps({
                    "status": "history_found",
                    "previous_gpa": past_analysis.gpa,
                    "was_graduated": past_analysis.is_graduated,
                })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
        finally:
            if 'db' in locals():
                db.close()
        return json.dumps({"status": "no_history"})

    def run(self, transcript_text: str, lang: str = "tr") -> dict:
        # Step 1: Parse
        parsed = self.parser.parse(transcript_text)

        logger = CaseLogger(parsed.student_name, parsed.student_number)

        passed_courses = [c for c in parsed.courses if c.grade.strip().upper() not in FAILED_GRADES]
        passed_ects = sum(c.ects for c in passed_courses)
        logger.open_case(parsed.gpa, len(parsed.courses), passed_ects)

        # Step 2: Independent evaluation
        logger.open_deliberation()
        course_verdict = self.course_agent.evaluate(parsed, lang)
        ects_verdict = self.ects_agent.evaluate(parsed, lang)
        req_verdict = self.requirements_agent.evaluate(parsed, lang)

        logger.log_verdict(
            course_verdict.agent, course_verdict.verdict,
            course_verdict.statement, course_verdict.issues,
        )
        logger.log_verdict(
            ects_verdict.agent, ects_verdict.verdict,
            ects_verdict.statement, ects_verdict.issues,
        )
        logger.log_verdict(
            req_verdict.agent, req_verdict.verdict,
            req_verdict.statement, req_verdict.issues,
        )

        # Step 3: Cross-examination — agents comment on each other's findings
        logger.open_cross_examination()
        logger.log_cross_comment(
            "CourseVerifier",
            self.course_agent.cross_examine(ects_verdict, lang),
        )
        logger.log_cross_comment(
            "ECTSVerifier",
            self.ects_agent.cross_examine(course_verdict, lang),
        )
        logger.log_cross_comment(
            "RequirementsChecker",
            self.requirements_agent.cross_examine(course_verdict, ects_verdict, lang),
        )

        # Step 4: Master deliberation + final decision
        all_issues = course_verdict.issues + ects_verdict.issues + req_verdict.issues
        is_graduated = all(
            v.verdict == "pass" for v in [course_verdict, ects_verdict, req_verdict]
        )

        verdict_map = {
            course_verdict.agent: course_verdict.verdict,
            ects_verdict.agent: ects_verdict.verdict,
            req_verdict.agent: req_verdict.verdict,
        }
        logger.log_master_deliberation(verdict_map, all_issues)
        logger.log_final_decision(is_graduated, all_issues)
        logger.flush()

        report, tool_logs = self._generate_report(
            parsed,
            course_verdict,
            ects_verdict,
            req_verdict,
            all_issues,
            is_graduated,
            lang,
        )

        master_verdict = AgentVerdict(
            agent="MasterAgent",
            verdict="pass" if is_graduated else "fail",
            statement=report,
            issues=[],
            details={
                "is_graduated": is_graduated,
                "tool_logs": tool_logs
            }
        )

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
                "master_agent": master_verdict.model_dump(),
            },
            "report_text": report,
        }

    def _generate_report(
        self,
        parsed: ParsedTranscript,
        course_verdict: AgentVerdict,
        ects_verdict: AgentVerdict,
        req_verdict: AgentVerdict,
        all_issues: list[str],
        is_graduated: bool,
        lang: str = "tr"
    ) -> tuple[str, list]:
        summary = {
            "target_language": "English" if lang == "en" else "Turkish",
            "student": {
                "name": parsed.student_name,
                "number": parsed.student_number,
            },
            "academic_metrics": {
                "gpa": parsed.gpa,
                "transcript_total_ects": ects_verdict.details["transcript_total_ects"],
                "required_ects": ects_verdict.details["required_ects"],
            },
            "master_decision": {
                "internal_status": "eligible_to_graduate" if is_graduated else "not_eligible_to_graduate",
                "use": "Use this as decision evidence only; do not quote the internal_status value.",
            },
            "verifier_assessments": [
                {
                    "agent": course_verdict.agent,
                    "internal_result": course_verdict.verdict,
                    "statement": course_verdict.statement,
                    "issues": course_verdict.issues,
                },
                {
                    "agent": ects_verdict.agent,
                    "internal_result": ects_verdict.verdict,
                    "statement": ects_verdict.statement,
                    "issues": ects_verdict.issues,
                },
                {
                    "agent": req_verdict.agent,
                    "internal_result": req_verdict.verdict,
                    "statement": req_verdict.statement,
                    "issues": req_verdict.issues,
                },
            ],
            "missing_conditions": all_issues,
            "missing_mandatory_count": len(course_verdict.details["missing_mandatory"]),
            "missing_mandatory_courses": course_verdict.details["missing_mandatory"],
            "completed_codes": course_verdict.details["completed_codes"],
        }
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "check_student_history",
                    "description": "Queries the SQLite database to check the student's historical GPA and graduation status by student number or name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "student_number": {"type": "string"},
                            "student_name": {"type": "string"}
                        }
                    },
                },
            }
        ]

        system_prompt = REPORT_SYSTEM_PROMPT + "\n\nYou have access to a tool to check the student's history in the database. Use it if a student number is provided. Incorporate any historical progress into your final report JSON."
        user_prompt = json.dumps(summary, ensure_ascii=False, indent=2)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        # 1. Ask MasterReportAgent to generate report OR call tool
        message = _chat(system_prompt, user_prompt, tools=tools, messages=messages)
        
        tool_logs = []
        
        if message.tool_calls:
            print(f"\n[MasterAgent] 🛠️  CALLING DB TOOL: {[t.function.name for t in message.tool_calls]}")
            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [{"id": t.id, "type": "function", "function": {"name": t.function.name, "arguments": t.function.arguments}} for t in message.tool_calls]
            })
            
            for tool_call in message.tool_calls:
                if tool_call.function.name == "check_student_history":
                    args = json.loads(tool_call.function.arguments)
                    result = self._check_student_history_tool(
                        student_number=args.get("student_number"),
                        student_name=args.get("student_name")
                    )
                    
                    # Create a comment for the frontend
                    parsed_result = json.loads(result)
                    if parsed_result.get("status") == "history_found":
                        prev_gpa = parsed_result.get("previous_gpa")
                        curr_gpa = summary.get("academic_metrics", {}).get("gpa")
                        was_graduated = parsed_result.get("was_graduated")
                        
                        gpa_diff_text = ""
                        if prev_gpa is not None and curr_gpa is not None:
                            diff = curr_gpa - prev_gpa
                            if diff > 0.001:
                                gpa_diff_text = f"an increase of {diff:.2f}" if lang == "en" else f"{diff:.2f} puanlık bir artış"
                            elif diff < -0.001:
                                gpa_diff_text = f"a decrease of {abs(diff):.2f}" if lang == "en" else f"{abs(diff):.2f} puanlık bir düşüş"
                            else:
                                gpa_diff_text = "no change" if lang == "en" else "değişim yok"
                                
                        grad_text = ""
                        if was_graduated is False and is_graduated is True:
                            grad_text = " The student has now fulfilled graduation requirements." if lang == "en" else " Öğrenci artık mezuniyet şartlarını sağlıyor."
                        elif was_graduated is True and is_graduated is False:
                            grad_text = " The student lost their graduation status." if lang == "en" else " Öğrenci mezuniyet durumunu kaybetmiş."
                        elif was_graduated is False and is_graduated is False:
                            grad_text = " The student still has missing requirements." if lang == "en" else " Öğrencinin hala eksik şartları var."
                        elif was_graduated is True and is_graduated is True:
                            grad_text = " The student remains eligible for graduation." if lang == "en" else " Öğrenci mezuniyet hakkını koruyor."

                        if lang == "en":
                            prev_gpa_str = f"{prev_gpa:.2f}" if prev_gpa is not None else "unknown"
                            curr_gpa_str = f"{curr_gpa:.2f}" if curr_gpa is not None else "unknown"
                            comment = f"I compared the new transcript with the past record. The GPA went from {prev_gpa_str} to {curr_gpa_str} ({gpa_diff_text}).{grad_text}"
                        else:
                            prev_gpa_str = f"{prev_gpa:.2f}" if prev_gpa is not None else "bilinmeyen"
                            curr_gpa_str = f"{curr_gpa:.2f}" if curr_gpa is not None else "bilinmeyen"
                            comment = f"Yeni transkripti eski kayıtla karşılaştırdım. Not ortalaması {prev_gpa_str}'den {curr_gpa_str}'ye değişmiş ({gpa_diff_text}).{grad_text}"
                    else:
                        comment = f"I checked the database but found no prior records for this student." if lang == "en" else f"Veritabanını kontrol ettim ancak bu öğrenci için geçmiş bir kayıt bulamadım."
                        
                    tool_logs.append({
                        "tool": "check_student_history",
                        "action": "Database Query",
                        "comment": comment
                    })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result
                    })
            
            # 2. Get final JSON report without tools so it forces JSON output
            message = _chat(system_prompt, user_prompt, tools=None, messages=messages)

        try:
            content = message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            draft_report = json.loads(content).get("report", "").strip()
        except Exception as e:
            print(f"Failed to parse JSON draft: {e}")
            draft_report = message.content
            
        if not draft_report:
            return "", tool_logs
        return self._review_report(draft_report, summary), tool_logs

    def _review_report(self, draft_report: str, summary: dict) -> str:
        review_payload = {
            "target_language": summary["target_language"],
            "draft_report": draft_report,
            "analysis_data": summary,
        }
        try:
            raw = _chat(REPORT_REVIEW_SYSTEM_PROMPT, json.dumps(review_payload, ensure_ascii=False, indent=2)).content
            reviewed_report = json.loads(raw).get("report", "").strip()
            return reviewed_report or draft_report
        except Exception as e:
            print(f"Warning: ReportCriticAgent failed ({e}). Using draft report.")
            return draft_report


def run_analysis_pipeline(transcript_text: str, lang: str = "tr") -> dict:
    return MasterAgent().run(transcript_text, lang)
