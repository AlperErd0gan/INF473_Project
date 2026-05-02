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


def _parsed(courses, gpa=2.5, add_default_language=True):
    normalized_codes = {c["code"].upper() for c in courses}
    if add_default_language and "FLE203" not in normalized_codes:
        courses = courses + [
            {"code": "FLE203", "name": "İngilizce Cef B2.2", "grade": "BB", "ects": 2},
        ]
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


def test_additional_mandatory_equivalencies_from_curriculum_file():
    parsed = _parsed(
        [
            {"code": "ING104", "name": "Matematik I", "grade": "CC", "ects": 7},
            {"code": "ING105", "name": "Matematik II", "grade": "CC", "ects": 7},
            {"code": "ING114", "name": "Fizik I", "grade": "CC", "ects": 5},
            {"code": "ING115", "name": "Fizik II", "grade": "CC", "ects": 5},
            {"code": "ING125", "name": "Kimya I", "grade": "CC", "ects": 4},
            {"code": "INF470", "name": "Bilgisayar Ağ Laboratuvarı", "grade": "CC", "ects": 3},
            {"code": "INF299", "name": "Staj", "grade": "AA", "ects": 2},
            {"code": "ING203", "name": "Yüksek Matematik I", "grade": "CB", "ects": 5},
            {"code": "ING204", "name": "Yüksek Matematik II", "grade": "CB", "ects": 6},
            {"code": "INF223", "name": "Nesneye Yönelik Programlama", "grade": "BB", "ects": 6},
            {"code": "INF204", "name": "Elektromanyetik Dalgalar", "grade": "CC", "ects": 3},
            {"code": "INF211", "name": "Bilgisayar Müh. için Olasılık/İstatistik", "grade": "CC", "ects": 4},
            {"code": "TUR001", "name": "Türk Dili I", "grade": "BB", "ects": 2},
            {"code": "TUR002", "name": "Türk Dili II", "grade": "BB", "ects": 2},
        ]
    )

    verdict = CourseVerifierAgent().evaluate(parsed)
    missing = set(verdict.details["missing_mandatory"])

    assert "INF402 - Nesnelerin İnternetine Giriş" not in missing
    assert "ING106 - Matematik I" not in missing
    assert "ING107 - Matematik II" not in missing
    assert "ING116 - Fizik I" not in missing
    assert "ING117 - Fizik II" not in missing
    assert "ING111 - Ekonominin Temelleri" not in missing
    assert "INF291 - Staj I" not in missing
    assert "ING251 - Yüksek Matematik I" not in missing
    assert "ING252 - Yüksek Matematik II" not in missing
    assert "INF243 - Nesneye Yönelik Programlama" not in missing
    assert "INF256 - Olasılık" not in missing
    assert "INF257 - İstatistik ve Veri Analizi" not in missing
    assert "FLF101 - Fransızca CEF B2.1 Akademik" not in missing
    assert "FLF201 - Fransızca CEF B2.2 Akademik" not in missing


def test_ia_grade_is_treated_as_failed_for_ects():
    parsed = _parsed(
        [
            {"code": "INF100", "name": "Dummy", "grade": "AA", "ects": 5},
            {"code": "FLE210", "name": "Dummy Lang", "grade": "IA", "ects": 3},
        ],
        add_default_language=False,
    )

    verdict = ECTSVerifierAgent().evaluate(parsed)
    assert verdict.details["transcript_total_ects"] == 5


def test_w_grade_is_treated_as_failed_for_ects():
    parsed = _parsed(
        [
            {"code": "INF100", "name": "Dummy", "grade": "AA", "ects": 5},
            {"code": "INF101", "name": "Dummy 2", "grade": "W", "ects": 4},
        ],
        add_default_language=False,
    )

    verdict = ECTSVerifierAgent().evaluate(parsed)
    assert verdict.details["transcript_total_ects"] == 5


def test_language_requirement_is_checked():
    parsed = _parsed(
        [
            {"code": "FLE203", "name": "İngilizce Cef B2.2", "grade": "FF", "ects": 2},
            {"code": "INF352", "name": "İnsan Bilgisayar Etkileşimine Giriş", "grade": "BB", "ects": 4},
        ]
    )

    verdict = RequirementsAgent().evaluate(parsed)
    assert not verdict.details["language_ok"]
    assert any("Dil koşulu sağlanmadı" in issue for issue in verdict.issues)


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


def test_legacy_semester6_inf345_counts_as_inf_elective():
    parsed = _parsed(
        [
            {"code": "INF316", "name": "Sinyaller ve Sistemler", "grade": "CB", "ects": 4},
            {"code": "INF352", "name": "İnsan Bilgisayar Etkileşimine Giriş", "grade": "BB", "ects": 4},
            {"code": "INF345", "name": "Sayısal İşaret İşleme", "grade": "BB", "ects": 4},
            {"code": "INF430", "name": "Robotik", "grade": "BB", "ects": 4},
            {"code": "INF446", "name": "Bilgisayar Mühendisliğinde Özel Konular", "grade": "AA", "ects": 4},
            {"code": "INF441", "name": "Şifrelemeye Giriş", "grade": "AA", "ects": 4},
            {"code": "MAT383", "name": "Matematiksel Modelleme", "grade": "BB", "ects": 4},
            {"code": "CNT417", "name": "Girişimcilik", "grade": "AA", "ects": 2},
        ]
    )

    verdict = RequirementsAgent().evaluate(parsed)
    assert verdict.details["elective_issues"] == []


def test_legacy_failed_inf112_requires_extra_social_elective():
    parsed = _parsed(
        [
            {"code": "INF316", "name": "Sinyaller ve Sistemler", "grade": "BB", "ects": 4},
            {"code": "INF112", "name": "Programlamaya Giriş", "grade": "FF", "ects": 6},
            {"code": "INF352", "name": "İnsan Bilgisayar Etkileşimine Giriş", "grade": "BB", "ects": 4},
            {"code": "INF365", "name": "Bilgi Teorisi", "grade": "BB", "ects": 4},
            {"code": "INF432", "name": "Bilgisayar Grafikleri", "grade": "BB", "ects": 4},
            {"code": "INF473", "name": "Üretken Yapay Zekaya Giriş", "grade": "BB", "ects": 5},
            {"code": "INF483", "name": "Bilgi Çıkarımı", "grade": "BB", "ects": 4},
            {"code": "IND471", "name": "Yöneylem Araştırması", "grade": "BB", "ects": 4},
            {"code": "CNT414", "name": "Felsefe", "grade": "AA", "ects": 2},
        ]
    )

    verdict = RequirementsAgent().evaluate(parsed)
    assert any("ilave sosyal seçmeli" in issue for issue in verdict.details["elective_issues"])


def test_legacy_failed_inf236_requires_extra_inf_elective():
    parsed = _parsed(
        [
            {"code": "INF316", "name": "Sinyaller ve Sistemler", "grade": "BB", "ects": 4},
            {"code": "INF236", "name": "Programlama Uygulamaları", "grade": "FF", "ects": 2},
            {"code": "INF352", "name": "İnsan Bilgisayar Etkileşimine Giriş", "grade": "BB", "ects": 4},
            {"code": "INF365", "name": "Bilgi Teorisi", "grade": "BB", "ects": 4},
            {"code": "INF432", "name": "Bilgisayar Grafikleri", "grade": "BB", "ects": 4},
            {"code": "INF473", "name": "Üretken Yapay Zekaya Giriş", "grade": "BB", "ects": 5},
            {"code": "INF483", "name": "Bilgi Çıkarımı", "grade": "BB", "ects": 4},
            {"code": "IND471", "name": "Yöneylem Araştırması", "grade": "BB", "ects": 4},
            {"code": "CNT414", "name": "Felsefe", "grade": "AA", "ects": 2},
        ]
    )

    verdict = RequirementsAgent().evaluate(parsed)
    assert any("ilave INF seçmeli" in issue for issue in verdict.details["elective_issues"])


def test_legacy_failed_ing144_requires_inf321():
    parsed = _parsed(
        [
            {"code": "INF316", "name": "Sinyaller ve Sistemler", "grade": "BB", "ects": 4},
            {"code": "ING144", "name": "Teknik Resim", "grade": "FF", "ects": 3},
            {"code": "INF352", "name": "İnsan Bilgisayar Etkileşimine Giriş", "grade": "BB", "ects": 4},
            {"code": "INF365", "name": "Bilgi Teorisi", "grade": "BB", "ects": 4},
            {"code": "INF432", "name": "Bilgisayar Grafikleri", "grade": "BB", "ects": 4},
            {"code": "INF473", "name": "Üretken Yapay Zekaya Giriş", "grade": "BB", "ects": 5},
            {"code": "INF483", "name": "Bilgi Çıkarımı", "grade": "BB", "ects": 4},
            {"code": "IND471", "name": "Yöneylem Araştırması", "grade": "BB", "ects": 4},
            {"code": "CNT414", "name": "Felsefe", "grade": "AA", "ects": 2},
        ]
    )

    verdict = RequirementsAgent().evaluate(parsed)
    assert any("INF321 Teknik Resim" in issue for issue in verdict.details["elective_issues"])
