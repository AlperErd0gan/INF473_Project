import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, "agent_decisions.log")


def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


class CaseLogger:
    """Accumulates a full agent discussion transcript for one analysis case, then appends to log file."""

    def __init__(self, student_name: str | None, student_number: str | None):
        self._lines: list[str] = []
        self._ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        label = student_name or "Bilinmeyen Öğrenci"
        number = f" ({student_number})" if student_number else ""
        self._header = f"CASE: {label}{number}"

    def _line(self, text: str = ""):
        self._lines.append(text)

    def open_case(self, gpa: float, total_courses: int, passed_ects: int):
        self._line("=" * 80)
        self._line(f"{self._header}")
        self._line(f"Timestamp : {self._ts}")
        self._line("=" * 80)
        self._line()
        self._line("[ADIM 1] Transkript ayrıştırıldı.")
        self._line(f"  GNO      : {gpa:.2f}")
        self._line(f"  Ders say.: {total_courses}")
        self._line(f"  AKTS (G) : {passed_ects}")
        self._line()

    def open_deliberation(self):
        self._line("[ADIM 2] Alt-ajan değerlendirmesi:")
        self._line()

    def log_verdict(self, agent: str, verdict: str, statement: str, issues: list[str]):
        icon = "✓" if verdict == "pass" else "✗"
        self._line(f"  [{agent}] → {verdict.upper()} {icon}")
        self._line(f"  \"{statement}\"")
        if issues:
            for issue in issues:
                self._line(f"    ! {issue}")
        self._line()

    def open_cross_examination(self):
        self._line("[ADIM 3] Çapraz inceleme (ajanlar arası):")
        self._line()

    def log_cross_comment(self, agent: str, comment: str):
        self._line(f"  [{agent}]: {comment}")
        self._line()

    def log_master_deliberation(self, verdicts: dict, all_issues: list[str]):
        self._line("[ADIM 4] MasterAgent değerlendirmesi:")
        pass_count = sum(1 for v in verdicts.values() if v == "pass")
        fail_count = len(verdicts) - pass_count
        self._line(f"  Oy dağılımı: {pass_count} PASS / {fail_count} FAIL")
        for agent, verdict in verdicts.items():
            icon = "✓" if verdict == "pass" else "✗"
            self._line(f"    {icon} {agent}: {verdict.upper()}")
        self._line()
        if all_issues:
            self._line(f"  Engelleyici koşullar ({len(all_issues)} adet):")
            for i, issue in enumerate(all_issues, 1):
                self._line(f"    {i}. {issue}")
        else:
            self._line("  Engelleyici koşul yok. Tüm kriterler sağlandı.")
        self._line()

    def log_final_decision(self, is_graduated: bool, all_issues: list[str]):
        self._line("-" * 80)
        if is_graduated:
            self._line("[KARAR] ✓ MEZUN OLABİLİR")
        else:
            self._line("[KARAR] ✗ MEZUN OLAMAZ")
            for i, issue in enumerate(all_issues, 1):
                self._line(f"  {i}. {issue}")
        self._line("=" * 80)
        self._line()
        self._line()

    def flush(self):
        _ensure_log_dir()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(self._lines) + "\n")
