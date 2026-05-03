import sys

with open("backend/agent.py", "r") as f:
    content = f.read()

# Replace CourseVerifierAgent.evaluate
content = content.replace('def evaluate(self, parsed: ParsedTranscript) -> AgentVerdict:', 'def evaluate(self, parsed: ParsedTranscript, lang: str = "tr") -> AgentVerdict:')

content = content.replace("""        issues = []
        if missing_mandatory:
            codes = ", ".join(c.split(" - ")[0] for c in missing_mandatory)
            issues.append(f"{len(missing_mandatory)} zorunlu ders eksik: {codes}")

        total = len(mandatory)
        done = len(completed_mandatory)
        if not missing_mandatory:
            statement = f"Tüm {total} zorunlu ders tamamlandı. Eksik ders yok."
        else:
            statement = (
                f"{done}/{total} zorunlu ders tamamlandı. "
                f"{len(missing_mandatory)} ders eksik: "
                + ", ".join(c.split(" - ")[0] for c in missing_mandatory)
            )""", """        issues = []
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
                statement = f"{done}/{total} zorunlu ders tamamlandı. {len(missing_mandatory)} ders eksik: " + ", ".join(c.split(" - ")[0] for c in missing_mandatory)""")


# Replace ECTSVerifierAgent.evaluate
content = content.replace('def evaluate(self, parsed: ParsedTranscript) -> AgentVerdict:', 'def evaluate(self, parsed: ParsedTranscript, lang: str = "tr") -> AgentVerdict:')

content = content.replace("""        issues = []
        if not ects_ok:
            issues.append(f"AKTS yetersiz: {transcript_total_ects} / minimum {required_ects}")

        if ects_ok:
            surplus = transcript_total_ects - required_ects
            statement = f"Toplam AKTS {transcript_total_ects} / {required_ects}. Eşik sağlandı (+{surplus} fazla)."
        else:
            deficit = required_ects - transcript_total_ects
            statement = f"Toplam AKTS {transcript_total_ects} / {required_ects}. {deficit} AKTS açığı var." """, """        issues = []
        if not ects_ok:
            issues.append(f"Insufficient ECTS: {transcript_total_ects} / minimum {required_ects}" if lang == "en" else f"AKTS yetersiz: {transcript_total_ects} / minimum {required_ects}")

        if ects_ok:
            surplus = transcript_total_ects - required_ects
            statement = f"Total ECTS {transcript_total_ects} / {required_ects}. Threshold met (+{surplus} extra)." if lang == "en" else f"Toplam AKTS {transcript_total_ects} / {required_ects}. Eşik sağlandı (+{surplus} fazla)."
        else:
            deficit = required_ects - transcript_total_ects
            statement = f"Total ECTS {transcript_total_ects} / {required_ects}. {deficit} ECTS deficit." if lang == "en" else f"Toplam AKTS {transcript_total_ects} / {required_ects}. {deficit} AKTS açığı var." """)


# Replace RequirementsAgent.evaluate
content = content.replace('def evaluate(self, parsed: ParsedTranscript) -> AgentVerdict:', 'def evaluate(self, parsed: ParsedTranscript, lang: str = "tr") -> AgentVerdict:')

content = content.replace("""        issues = []

        if not gpa_ok:
            issues.append(f"GNO yetersiz: {parsed.gpa:.2f} / minimum 2.00")""", """        issues = []

        if not gpa_ok:
            issues.append(f"Insufficient GPA: {parsed.gpa:.2f} / minimum 2.00" if lang == "en" else f"GNO yetersiz: {parsed.gpa:.2f} / minimum 2.00")""")

content = content.replace("""        if not language_ok:
            issues.append(
                f"Dil koşulu sağlanmadı: yabancı dil AKTS {language_ects}/12 ve B2+ düzeyi tespit edilemedi"
            )""", """        if not language_ok:
            issues.append(
                f"Language condition not met: foreign language ECTS {language_ects}/12 and B2+ level not detected" if lang == "en" else f"Dil koşulu sağlanmadı: yabancı dil AKTS {language_ects}/12 ve B2+ düzeyi tespit edilemedi"
            )""")

content = content.replace("""                elective_issues.append(
                    f"Dönem {sem} {desc}: {needed} ders eksik (mevcut {taken_count}/{required})"
                )""", """                elective_issues.append(
                    f"Semester {sem} {desc}: missing {needed} course(s) (current {taken_count}/{required})" if lang == "en" else f"Dönem {sem} {desc}: {needed} ders eksik (mevcut {taken_count}/{required})"
                )""")

content = content.replace("""            if "ING144" in failed_codes and "INF321" not in completed_codes:
                elective_issues.append("ING144 başarısızlığı için INF321 Teknik Resim dersi tamamlanmalı.")""", """            if "ING144" in failed_codes and "INF321" not in completed_codes:
                elective_issues.append("Must complete INF321 Technical Drawing due to ING144 failure." if lang == "en" else "ING144 başarısızlığı için INF321 Teknik Resim dersi tamamlanmalı.")""")

content = content.replace("""                elective_issues.append(
                    f"Geçiş kuralları nedeniyle ilave INF seçmeli: {missing} ders eksik "
                    f"(mevcut {total_inf_taken}/{total_inf_required + extra_inf_required})."
                )""", """                elective_issues.append(
                    f"Additional INF elective required due to transition rules: missing {missing} course(s) "
                    f"(current {total_inf_taken}/{total_inf_required + extra_inf_required})." if lang == "en" else f"Geçiş kuralları nedeniyle ilave INF seçmeli: {missing} ders eksik (mevcut {total_inf_taken}/{total_inf_required + extra_inf_required})."
                )""")

content = content.replace("""                elective_issues.append(
                    f"Geçiş kuralları nedeniyle ilave sosyal seçmeli: {missing} ders eksik "
                    f"(mevcut {social_taken}/{social_required + extra_social_required})."
                )""", """                elective_issues.append(
                    f"Additional social elective required due to transition rules: missing {missing} course(s) "
                    f"(current {social_taken}/{social_required + extra_social_required})." if lang == "en" else f"Geçiş kuralları nedeniyle ilave sosyal seçmeli: {missing} ders eksik (mevcut {social_taken}/{social_required + extra_social_required})."
                )""")

content = content.replace("""        parts = []
        if gpa_ok:
            parts.append(f"GNO {parsed.gpa:.2f} ≥ 2.00 (geçer)")
        else:
            parts.append(f"GNO {parsed.gpa:.2f} < 2.00 (yetersiz)")
        if elective_issues:
            parts.append(f"{len(elective_issues)} seçmeli grup eksik")
        else:
            parts.append("tüm seçmeli gruplar tamamlandı")
        statement = "; ".join(parts) + ".\"""", """        parts = []
        if gpa_ok:
            parts.append(f"GPA {parsed.gpa:.2f} ≥ 2.00 (pass)" if lang == "en" else f"GNO {parsed.gpa:.2f} ≥ 2.00 (geçer)")
        else:
            parts.append(f"GPA {parsed.gpa:.2f} < 2.00 (fail)" if lang == "en" else f"GNO {parsed.gpa:.2f} < 2.00 (yetersiz)")
        if elective_issues:
            parts.append(f"{len(elective_issues)} elective group(s) missing" if lang == "en" else f"{len(elective_issues)} seçmeli grup eksik")
        else:
            parts.append("all elective groups completed" if lang == "en" else "tüm seçmeli gruplar tamamlandı")
        statement = "; ".join(parts) + ".\"""")

# Replace MasterAgent.run and _generate_report
content = content.replace('def run(self, transcript_text: str) -> dict:', 'def run(self, transcript_text: str, lang: str = "tr") -> dict:')
content = content.replace('course_verdict = self.course_agent.evaluate(parsed)', 'course_verdict = self.course_agent.evaluate(parsed, lang)')
content = content.replace('ects_verdict = self.ects_agent.evaluate(parsed)', 'ects_verdict = self.ects_agent.evaluate(parsed, lang)')
content = content.replace('req_verdict = self.requirements_agent.evaluate(parsed)', 'req_verdict = self.requirements_agent.evaluate(parsed, lang)')
content = content.replace('report = self._generate_report(parsed, ects_verdict, all_issues, is_graduated, course_verdict)', 'report = self._generate_report(parsed, ects_verdict, all_issues, is_graduated, course_verdict, lang)')


content = content.replace("""    def _generate_report(
        self,
        parsed: ParsedTranscript,
        ects_verdict: AgentVerdict,
        all_issues: list[str],
        is_graduated: bool,
        course_verdict: AgentVerdict,
    ) -> str:""", """    def _generate_report(
        self,
        parsed: ParsedTranscript,
        ects_verdict: AgentVerdict,
        all_issues: list[str],
        is_graduated: bool,
        course_verdict: AgentVerdict,
        lang: str = "tr"
    ) -> str:""")

content = content.replace("""        raw = _chat(REPORT_SYSTEM_PROMPT, json.dumps(summary, ensure_ascii=False, indent=2))
        return json.loads(raw).get("report", "")""", """        lang_instruction = "Write a concise 2-3 sentence graduation status report in English using formal language." if lang == "en" else "Write a concise 2-3 sentence graduation status report in Turkish using formal language."
        prompt = f'''You are a graduation advisor for the Computer Engineering department at GSU (Galatasaray University).

{lang_instruction}
Base your report strictly on the provided analysis data — do not add or infer anything beyond what is given.

Compare courses strictly by course code. Do not infer missing courses from names. A course is only missing if its exact code does not appear in the passed courses list.

Return ONLY valid JSON: {{"report": "report text here"}}'''
        raw = _chat(prompt, json.dumps(summary, ensure_ascii=False, indent=2))
        return json.loads(raw).get("report", "")""")

content = content.replace('def run_analysis_pipeline(transcript_text: str) -> dict:', 'def run_analysis_pipeline(transcript_text: str, lang: str = "tr") -> dict:')
content = content.replace('return MasterAgent().run(transcript_text)', 'return MasterAgent().run(transcript_text, lang)')

with open("backend/agent.py", "w") as f:
    f.write(content)
