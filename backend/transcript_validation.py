import re


_MULTI_TRANSCRIPT_ERROR = (
    "Birden fazla transkript tespit edildi. Lütfen tek seferde yalnızca bir öğrencinin "
    "transkriptini yükleyin."
)

_EXAMPLE_HEADER_RE = re.compile(r"(?im)^\s*ÖRNEK\s+\d+\s*:")
_NAME_LINE_RE = re.compile(r"(?im)^\s*Ad\s*Soyad\s*:\s*(.+?)\s*$")
_STUDENT_LINE_RE = re.compile(r"(?im)^\s*ÖĞRENCİ\s*:\s*(.+?)\s*$")
_NUMBER_LINE_RE = re.compile(r"(?im)^\s*Öğrenci\s*No\s*:\s*([^\s]+)\s*$")
_GENERAL_ROW_RE = re.compile(r"(?im)^\s*Genel\s+(.+?)\s*$")


def _normalize_identity_value(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value.strip())
    return cleaned.casefold()


def _extract_name_candidates(text: str) -> set[str]:
    names = {
        _normalize_identity_value(match.group(1))
        for match in _NAME_LINE_RE.finditer(text)
    }
    for match in _STUDENT_LINE_RE.finditer(text):
        value = match.group(1).split("|")[0].strip()
        if value:
            names.add(_normalize_identity_value(value))
    return names


def _extract_number_candidates(text: str) -> set[str]:
    numbers = set()
    for match in _NUMBER_LINE_RE.finditer(text):
        value = match.group(1).strip()
        if value:
            numbers.add(_normalize_identity_value(value))
    for match in _STUDENT_LINE_RE.finditer(text):
        parts = match.group(1).split("|")
        if len(parts) > 1 and parts[1].strip():
            numbers.add(_normalize_identity_value(parts[1]))
    return numbers


def _parse_decimal(value: str) -> float | None:
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def _extract_general_totals(text: str) -> list[float]:
    totals = []
    for match in _GENERAL_ROW_RE.finditer(text):
        row = match.group(1).strip()
        columns = re.split(r"\s+", row)
        if len(columns) < 3:
            continue
        total_ects = _parse_decimal(columns[-1])
        if total_ects is None:
            continue
        totals.append(total_ects)
    return totals


def _has_cumulative_reset(totals: list[float]) -> bool:
    if len(totals) < 2:
        return False
    for previous, current in zip(totals, totals[1:]):
        if current + 1e-6 < previous:
            return True
    return False


def validate_single_transcript(text: str) -> str | None:
    content = text.strip()
    if not content:
        return None

    if len(_EXAMPLE_HEADER_RE.findall(content)) > 1:
        return _MULTI_TRANSCRIPT_ERROR

    names = _extract_name_candidates(content)
    numbers = _extract_number_candidates(content)

    if len(numbers) > 1:
        return _MULTI_TRANSCRIPT_ERROR
    if len(names) > 1:
        return _MULTI_TRANSCRIPT_ERROR

    general_totals = _extract_general_totals(content)
    if _has_cumulative_reset(general_totals):
        return _MULTI_TRANSCRIPT_ERROR

    return None
