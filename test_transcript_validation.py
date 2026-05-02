import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from transcript_validation import validate_single_transcript  # noqa: E402


def test_single_transcript_is_accepted():
    text = """
Ad Soyad: Ayşe Kaya
Öğrenci No: 2021401023
2021 - 2022 Güz Yarıyılı
Kodu\tDers Adı\tNotu\tKredi\tAKTS\tTürü
INF112\tProgramlamaya Giriş\tAA\t5.0\t4\tZ
"""
    assert validate_single_transcript(text) is None


def test_multiple_transcripts_are_rejected_by_student_number():
    text = """
Ad Soyad: Ayşe Kaya
Öğrenci No: 2021401023

Ad Soyad: Zeynep Arslan
Öğrenci No: 2020401007
"""
    assert validate_single_transcript(text) is not None


def test_multiple_transcripts_are_rejected_by_example_headers():
    sample_path = os.path.join(os.path.dirname(__file__), "analysis-input-example.txt")
    with open(sample_path, encoding="utf-8") as f:
        text = f.read()
    assert validate_single_transcript(text) is not None


def test_single_student_line_format_is_accepted():
    text = """
ÖĞRENCİ: Zeynep Arslan | 2020401007
GPA: 3.42
INF112 Programlamaya Giriş - AA - 4 AKTS
    """
    assert validate_single_transcript(text) is None


def test_multiple_transcripts_without_identity_are_rejected_by_cumulative_reset():
    text = """
2021 - 2022 Güz Yarıyılı
AKADEMİK NOT ORTALAMASI\tANO\tKREDİ TOPLAMI\tAKTS TOPLAMI
Genel\t2.70\t20.0\t30.0
2021 - 2022 Bahar Yarıyılı
AKADEMİK NOT ORTALAMASI\tANO\tKREDİ TOPLAMI\tAKTS TOPLAMI
Genel\t2.80\t42.0\t62.0

2020 - 2021 Güz Yarıyılı
AKADEMİK NOT ORTALAMASI\tANO\tKREDİ TOPLAMI\tAKTS TOPLAMI
Genel\t3.10\t18.0\t27.0
"""
    assert validate_single_transcript(text) is not None


def test_single_transcript_without_identity_and_monotonic_cumulative_is_accepted():
    text = """
2021 - 2022 Güz Yarıyılı
AKADEMİK NOT ORTALAMASI\tANO\tKREDİ TOPLAMI\tAKTS TOPLAMI
Genel\t2.70\t20.0\t30.0
2021 - 2022 Bahar Yarıyılı
AKADEMİK NOT ORTALAMASI\tANO\tKREDİ TOPLAMI\tAKTS TOPLAMI
Genel\t2.80\t42.0\t62.0
2022 - 2023 Güz Yarıyılı
AKADEMİK NOT ORTALAMASI\tANO\tKREDİ TOPLAMI\tAKTS TOPLAMI
Genel\t2.85\t64.0\t91.0
"""
    assert validate_single_transcript(text) is None
