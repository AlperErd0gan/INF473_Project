import os
import sys

os.environ.setdefault("GROQ_API_KEY", "test-key")
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from agent import (  # noqa: E402
    CourseEntry,
    ParsedTranscript,
    CourseVerifierAgent,
    ECTSVerifierAgent,
    RequirementsAgent,
)


def _parsed(courses, gpa=2.5):
    return ParsedTranscript(
        student_name="Test Student",
        student_number="123",
        gpa=gpa,
        courses=[CourseEntry(**c) for c in courses],
    )


def test_mandatory_equivalencies_count_as_completed():
    parsed = _parsed(
        [
            {"code": "ING127", "name": "Kimya", "grade": "CC", "ects": 4},
            {"code": "INF316", "name": "Sinyaller ve Sistemler", "grade": "CB", "ects": 4},
            {"code": "CNT350", "name": "Proje Risk ve Değişiklik Yönetimi", "grade": "AA", "ects": 2},
        ]
    )

    verdict = CourseVerifierAgent().evaluate(parsed)
    missing = set(verdict.details["missing_mandatory"])

    assert "ING111 - Ekonominin Temelleri" not in missing
    assert "INF345 - Sayısal Sinyal İşleme" not in missing
    assert "CNT250 - Bilgisayar Mühendisleri için Proje Risk ve Değişiklik Yönetimi" not in missing


def test_ia_grade_is_treated_as_failed_for_ects():
    parsed = _parsed(
        [
            {"code": "INF100", "name": "Dummy", "grade": "AA", "ects": 5},
            {"code": "FLE210", "name": "Dummy Lang", "grade": "IA", "ects": 3},
        ]
    )

    verdict = ECTSVerifierAgent().evaluate(parsed)
    assert verdict.details["transcript_total_ects"] == 5


def test_legacy_elective_code_satisfies_group_requirement():
    parsed = _parsed(
        [
            {"code": "INF352", "name": "İnsan Bilgisayar Etkileşimine Giriş", "grade": "BB", "ects": 4},
            {"code": "INF330", "name": "Robotik", "grade": "BB", "ects": 5},
            {"code": "INF360", "name": "Veri Tabanı Yönetimi ve Güvenliği", "grade": "BB", "ects": 5},
            {"code": "INF432", "name": "Bilgisayar Grafikleri", "grade": "BB", "ects": 5},
            {"code": "INF472", "name": "Bulut Bilişim", "grade": "BB", "ects": 5},
            {"code": "INF473", "name": "Üretken Yapay Zekaya Giriş", "grade": "BB", "ects": 5},
            {"code": "IND471", "name": "Yöneylem Araştırması", "grade": "BB", "ects": 4},
            {"code": "CNT414", "name": "Felsefe", "grade": "AA", "ects": 2},
        ]
    )

    verdict = RequirementsAgent().evaluate(parsed)
    assert verdict.details["elective_issues"] == []


def test_legacy_curriculum_requires_only_one_semester6_inf_elective():
    parsed = _parsed(
        [
            {"code": "INF316", "name": "Sinyaller ve Sistemler", "grade": "CB", "ects": 4},
            {"code": "INF365", "name": "Bilgi Teorisi", "grade": "BA", "ects": 4},
            {"code": "INF432", "name": "Bilgisayar Grafikleri", "grade": "AA", "ects": 4},
            {"code": "INF473", "name": "Üretken Yapay Zekaya Giriş", "grade": "BB", "ects": 5},
            {"code": "INF483", "name": "Bilgi Çıkarımı", "grade": "BB", "ects": 4},
            {"code": "IND471", "name": "Yöneylem Araştırması", "grade": "BB", "ects": 4},
            {"code": "CNT414", "name": "Felsefe", "grade": "AA", "ects": 2},
        ]
    )

    verdict = RequirementsAgent().evaluate(parsed)
    assert not any(issue.startswith("Dönem 6 INF seçmeli") for issue in verdict.details["elective_issues"])
