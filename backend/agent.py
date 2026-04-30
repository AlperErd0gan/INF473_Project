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
FAILED_GRADES = {"FF", "DZ"}

PARSE_SYSTEM_PROMPT = """You are a university transcript parsing expert. Extract ALL courses from the transcript, including failed ones.

Extract the ECTS value exactly as written after the course grade. Every line follows the format: CODE Name - GRADE - X AKTS. Extract X as the ects value.

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
- Include ALL courses even failed ones (FF, DZ, W)
- Course codes must be uppercase
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


def parse_transcript(transcript_text: str) -> ParsedTranscript:
    raw = _chat(PARSE_SYSTEM_PROMPT, transcript_text)
    return ParsedTranscript.model_validate_json(raw)


def _compute_analysis(parsed: ParsedTranscript) -> dict:
    passed = [c for c in parsed.courses if c.grade.strip().upper() not in FAILED_GRADES]
    completed_codes = {c.code.strip().replace(" ", "").upper() for c in passed}
    transcript_total_ects = sum(c.ects for c in passed)
    print(f"[DEBUG] Parsed ECTS sum: {transcript_total_ects}")

    mandatory = GSU_BIL_REQUIREMENTS["mandatory_courses"]
    completed_mandatory = [
        f"{c['code']} - {c['name']}" for c in mandatory if c["code"].strip().replace(" ", "").upper() in completed_codes
    ]
    missing_mandatory = [
        f"{c['code']} - {c['name']}" for c in mandatory if c["code"].strip().replace(" ", "").upper() not in completed_codes
    ]

    gpa_ok = parsed.gpa >= GSU_BIL_REQUIREMENTS["min_gpa"]
    ects_ok = transcript_total_ects >= GSU_BIL_REQUIREMENTS["min_ects"]

    elective_issues = []
    for group in GSU_BIL_REQUIREMENTS["elective_groups"]:
        group_codes = {o["code"].strip().replace(" ", "").upper() for o in group["options"]}
        taken_count = len(completed_codes & group_codes)
        required = group["required_count"]
        if taken_count < required:
            needed = required - taken_count
            sem = group["semester"]
            desc = group.get("description", "INF seçmeli")
            elective_issues.append(
                f"Dönem {sem} {desc}: {needed} ders eksik (mevcut {taken_count}/{required})"
            )

    missing_conditions = []
    if not gpa_ok:
        missing_conditions.append(f"GNO yetersiz: {parsed.gpa:.2f} / minimum 2.00")
    if not ects_ok:
        missing_conditions.append(f"AKTS yetersiz: {transcript_total_ects} / minimum {GSU_BIL_REQUIREMENTS['min_ects']}")
    if missing_mandatory:
        codes = ", ".join(c.split(" - ")[0] for c in missing_mandatory)
        missing_conditions.append(f"{len(missing_mandatory)} zorunlu ders eksik: {codes}")
    missing_conditions.extend(elective_issues)

    return {
        "transcript_total_ects": transcript_total_ects,
        "required_ects": GSU_BIL_REQUIREMENTS["min_ects"],
        "completed_mandatory": completed_mandatory,
        "missing_mandatory": missing_mandatory,
        "gpa_ok": gpa_ok,
        "ects_ok": ects_ok,
        "is_graduated": len(missing_conditions) == 0,
        "missing_conditions": missing_conditions,
    }


def _generate_report(parsed: ParsedTranscript, analysis: dict) -> str:
    summary = {
        "student_name": parsed.student_name,
        "gpa": parsed.gpa,
        "transcript_total_ects": analysis["transcript_total_ects"],
        "required_ects": analysis["required_ects"],
        "is_graduated": analysis["is_graduated"],
        "missing_conditions": analysis["missing_conditions"],
        "missing_mandatory_count": len(analysis["missing_mandatory"]),
        "missing_mandatory_courses": analysis["missing_mandatory"],
        "completed_codes": list({c.code.strip().replace(" ", "").upper() for c in parsed.courses if c.grade.strip().upper() not in FAILED_GRADES})
    }
    raw = _chat(REPORT_SYSTEM_PROMPT, json.dumps(summary, ensure_ascii=False, indent=2))
    return json.loads(raw).get("report", "")


def run_analysis_pipeline(transcript_text: str) -> dict:
    parsed = parse_transcript(transcript_text)
    analysis = _compute_analysis(parsed)
    report = _generate_report(parsed, analysis)
    return {
        "student_name": parsed.student_name,
        "student_number": parsed.student_number,
        "gpa": parsed.gpa,
        "transcript_total_ects": analysis["transcript_total_ects"],
        "required_ects": analysis["required_ects"],
        "is_graduated": analysis["is_graduated"],
        "completed_courses": [c.model_dump() for c in parsed.courses],
        "completed_mandatory_courses": analysis["completed_mandatory"],
        "missing_courses": analysis["missing_mandatory"],
        "missing_conditions": analysis["missing_conditions"],
        "report_text": report,
    }
