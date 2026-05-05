import os
import sys

os.environ.setdefault("GROQ_API_KEY", "test-key")
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import agent  # noqa: E402
from agent import AgentVerdict, MasterAgent, ParsedTranscript  # noqa: E402


def test_master_report_is_reviewed_for_machine_like_boolean_language():
    calls = []

    def fake_chat(system, user):
        calls.append((system, user))
        if len(calls) == 1:
            return '{"report": "Mezuniyet durumu false. AKTS yetersiz."}'
        return '{"report": "Öğrenci mezuniyet koşullarını şu anda sağlamamaktadır; toplam AKTS değeri minimum koşulun altındadır."}'

    original_chat = agent._chat
    agent._chat = fake_chat
    try:
        parsed = ParsedTranscript(
            student_name="Test Student",
            student_number="123",
            gpa=2.5,
            courses=[],
        )
        course_verdict = AgentVerdict(
            agent="CourseVerifier",
            verdict="pass",
            statement="Tüm zorunlu dersler tamamlandı.",
            issues=[],
            details={
                "completed_mandatory": [],
                "missing_mandatory": [],
                "completed_codes": [],
            },
        )
        ects_verdict = AgentVerdict(
            agent="ECTSVerifier",
            verdict="fail",
            statement="Toplam AKTS 220 / 240. 20 AKTS açığı var.",
            issues=["AKTS yetersiz: 220 / minimum 240"],
            details={
                "transcript_total_ects": 220,
                "required_ects": 240,
            },
        )
        req_verdict = AgentVerdict(
            agent="RequirementsChecker",
            verdict="pass",
            statement="GNO 2.50 >= 2.00; tüm seçmeli gruplar tamamlandı.",
            issues=[],
            details={},
        )

        report = MasterAgent()._generate_report(
            parsed,
            course_verdict,
            ects_verdict,
            req_verdict,
            ["AKTS yetersiz: 220 / minimum 240"],
            False,
        )

        assert len(calls) == 2
        assert "false" not in report.lower()
        assert "mezuniyet koşullarını şu anda sağlamamaktadır" in report.lower()
    finally:
        agent._chat = original_chat
