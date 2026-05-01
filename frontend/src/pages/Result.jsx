import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getAnalysis, deleteAnalysis } from "../api";
import { useLang } from "../contexts/LangContext";

export default function Result() {
  const { t } = useLang();
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [agentsOpen, setAgentsOpen] = useState(true);

  useEffect(() => {
    getAnalysis(id)
      .then(setData)
      .catch((err) => setError(err.message));
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm(t.result_delete_confirm)) return;
    try {
      await deleteAnalysis(id);
      navigate("/history");
    } catch (err) {
      alert(t.result_delete_error + err.message);
    }
  };

  if (error) {
    return (
      <div style={styles.errorBox}>
        <span>⚠</span>
        <div>
          <strong>Error:</strong> {error}
          <br />
          <button onClick={() => navigate("/")} style={{ ...styles.actionBtn, marginTop: 12 }}>
            {t.result_error_back}
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={styles.loadingWrap}>
        <div style={styles.spinner} />
        <span style={{ color: "var(--text-secondary)", fontSize: 14 }}>{t.result_loading}</span>
      </div>
    );
  }

  const graduated = data.is_graduated;
  const verdicts = data.agent_verdicts || {};
  const mandatoryTotal = 43;
  const completedMandatoryCount = data.completed_courses?.length ?? 0;

  return (
    <div className="fade-in">
      {/* ── Banner ── */}
      <div style={{ ...styles.banner, ...(graduated ? styles.bannerSuccess : styles.bannerError) }}>
        <div style={{ ...styles.bannerIcon, ...(graduated ? { color: "var(--success)" } : { color: "var(--error)" }) }}>
          {graduated ? "✓" : "✗"}
        </div>
        <div style={{ flex: 1 }}>
          <div style={styles.bannerTitle}>
            {graduated ? t.result_graduated : t.result_missing}
          </div>
          {data.report_text && (
            <div style={styles.bannerReport}>{data.report_text}</div>
          )}
        </div>
        {(data.student_name || data.student_number) && (
          <div style={styles.studentInfo}>
            {data.student_name && <div style={styles.studentName}>{data.student_name}</div>}
            {data.student_number && <div className="mono" style={styles.studentNumber}>{data.student_number}</div>}
          </div>
        )}
      </div>

      {/* ── Stats ── */}
      <div style={styles.statsRow}>
        <StatCard
          label={t.result_stat_gpa}
          value={data.gpa?.toFixed(2) ?? "—"}
          unit="/ 4.00"
          sub={t.result_stat_gpa_min}
          ok={data.gpa >= 2.0}
        />
        <StatCard
          label={t.result_stat_ects}
          value={data.transcript_total_ects ?? "—"}
          unit={`/ ${data.required_ects ?? 240}`}
          sub={`Min. ${data.required_ects ?? 240}`}
          ok={(data.transcript_total_ects ?? 0) >= (data.required_ects ?? 240)}
        />
        <StatCard
          label={t.result_stat_mandatory}
          value={completedMandatoryCount}
          unit={`/ ${mandatoryTotal}`}
          sub={t.result_stat_mandatory_sub}
          ok={completedMandatoryCount >= mandatoryTotal}
        />
        <StatCard
          label={t.result_stat_conditions}
          value={data.missing_conditions?.length ?? 0}
          unit=""
          sub={graduated ? t.result_stat_conditions_ok : t.result_stat_conditions_fail}
          ok={!(data.missing_conditions?.length)}
        />
      </div>

      {/* ── Missing conditions ── */}
      {data.missing_conditions?.length > 0 && (
        <div style={styles.conditionsCard}>
          <div style={styles.sectionHeader}>
            <span style={{ color: "var(--error)" }}>⚠</span>
            <h3 style={styles.sectionTitle}>{t.result_missing_conditions}</h3>
          </div>
          <ul style={styles.conditionList}>
            {data.missing_conditions.map((cond, i) => (
              <li key={i} style={styles.conditionItem}>
                <span style={styles.conditionBullet}>{i + 1}</span>
                {cond}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── Agent verdicts ── */}
      {Object.keys(verdicts).length > 0 && (
        <div style={styles.section}>
          <button style={styles.sectionToggle} onClick={() => setAgentsOpen((v) => !v)}>
            <div style={styles.sectionHeader}>
              <span>🤖</span>
              <h3 style={styles.sectionTitle}>{t.result_agents_title}</h3>
            </div>
            <span style={{ color: "var(--text-muted)", fontSize: 13 }}>
              {agentsOpen ? t.result_agents_hide : t.result_agents_show}
            </span>
          </button>

          {agentsOpen && (
            <div style={styles.agentGrid}>
              {Object.entries(verdicts).map(([key, v]) => (
                <AgentCard key={key} verdict={v} labels={t.agent_labels} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Course lists ── */}
      <div style={styles.listsRow}>
        <div style={styles.listCard}>
          <div style={styles.sectionHeader}>
            <span style={{ color: "var(--success)", fontSize: 15 }}>✓</span>
            <h3 style={styles.sectionTitle}>{t.result_completed_courses}</h3>
            <span className="mono" style={styles.countBadge}>
              {data.completed_courses?.length ?? 0}
            </span>
          </div>
          {data.completed_courses?.length > 0 ? (
            <ul style={styles.courseList}>
              {data.completed_courses.map((course, i) => (
                <CourseItem key={i} course={course} type="done" />
              ))}
            </ul>
          ) : (
            <div style={styles.emptyState}>{t.result_none_found}</div>
          )}
        </div>

        <div style={styles.listCard}>
          <div style={styles.sectionHeader}>
            <span style={{ color: "var(--error)", fontSize: 15 }}>✗</span>
            <h3 style={styles.sectionTitle}>{t.result_missing_courses}</h3>
            <span className="mono" style={{ ...styles.countBadge, color: data.missing_courses?.length ? "var(--error)" : "var(--success)" }}>
              {data.missing_courses?.length ?? 0}
            </span>
          </div>
          {data.missing_courses?.length > 0 ? (
            <ul style={styles.courseList}>
              {data.missing_courses.map((course, i) => (
                <CourseItem key={i} course={course} type="missing" />
              ))}
            </ul>
          ) : (
            <div style={{ ...styles.emptyState, color: "var(--success)" }}>
              {t.result_all_complete}
            </div>
          )}
        </div>
      </div>

      {/* ── Actions ── */}
      <div style={styles.actions}>
        <button onClick={() => navigate("/")} style={styles.primaryBtn}>
          {t.result_btn_new}
        </button>
        <button onClick={() => navigate("/history")} style={styles.secondaryBtn}>
          {t.result_btn_history}
        </button>
        <button onClick={handleDelete} style={styles.dangerBtn}>
          {t.result_btn_delete}
        </button>
      </div>
    </div>
  );
}

function StatCard({ label, value, unit, sub, ok }) {
  const isGood = ok;
  return (
    <div style={{ ...styles.statCard, borderColor: isGood ? "var(--success-border)" : "var(--error-border)" }}>
      <div style={{ ...styles.statValue, color: isGood ? "var(--success)" : "var(--error)" }} className="mono">
        {value}
      </div>
      <div style={styles.statUnit}>{unit}</div>
      <div style={styles.statLabel}>{label}</div>
      <div style={{ ...styles.statSub, color: isGood ? "var(--success)" : "var(--text-muted)" }}>{sub}</div>
    </div>
  );
}

function AgentCard({ verdict, labels }) {
  const pass = verdict.verdict === "pass";
  const agentLabels = labels || {
    CourseVerifier:      "Course Verifier",
    ECTSVerifier:        "ECTS Verifier",
    RequirementsChecker: "Requirements Checker",
  };
  const agentIcons = {
    CourseVerifier:      "📚",
    ECTSVerifier:        "🎯",
    RequirementsChecker: "📋",
  };

  return (
    <div style={{
      ...styles.agentCard,
      borderColor: pass ? "var(--success-border)" : "var(--error-border)",
      backgroundColor: pass ? "var(--success-bg)" : "var(--error-bg)",
    }}>
      <div style={styles.agentHeader}>
        <span style={styles.agentIcon}>{agentIcons[verdict.agent] || "🤖"}</span>
        <div style={{ flex: 1 }}>
          <div style={styles.agentName}>{agentLabels[verdict.agent] || verdict.agent}</div>
          <div className="mono" style={{ fontSize: 10, color: "var(--text-muted)" }}>{verdict.agent}</div>
        </div>
        <span style={{
          ...styles.verdictBadge,
          backgroundColor: pass ? "var(--success-bg)" : "var(--error-bg)",
          color: pass ? "var(--success)" : "var(--error)",
          borderColor: pass ? "var(--success-border)" : "var(--error-border)",
        }}>
          {pass ? "PASS ✓" : "FAIL ✗"}
        </span>
      </div>

      {verdict.statement && (
        <div style={styles.agentStatement}>"{verdict.statement}"</div>
      )}

      {verdict.issues?.length > 0 && (
        <ul style={styles.agentIssues}>
          {verdict.issues.map((issue, i) => (
            <li key={i} style={styles.agentIssue}>
              <span style={{ color: "var(--error)" }}>!</span> {issue}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function CourseItem({ course, type }) {
  const parts = course.split(" - ");
  const code = parts[0];
  const name = parts.slice(1).join(" - ");
  return (
    <li style={{ ...styles.courseItem, ...(type === "missing" ? styles.courseItemMissing : {}) }}>
      <span className="mono" style={styles.courseCode}>{code}</span>
      {name && <span style={styles.courseName}>{name}</span>}
    </li>
  );
}

const styles = {
  banner: {
    display: "flex",
    alignItems: "flex-start",
    gap: 18,
    borderRadius: 10,
    padding: "22px 26px",
    marginBottom: 24,
    border: "1px solid",
  },
  bannerSuccess: {
    backgroundColor: "var(--success-bg)",
    borderColor: "var(--success-border)",
  },
  bannerError: {
    backgroundColor: "var(--error-bg)",
    borderColor: "var(--error-border)",
  },
  bannerIcon: {
    fontSize: 26,
    fontWeight: 700,
    lineHeight: 1,
    marginTop: 3,
    flexShrink: 0,
  },
  bannerTitle: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 20,
    fontWeight: 700,
    letterSpacing: "0.02em",
    marginBottom: 6,
    color: "var(--text-primary)",
  },
  bannerReport: {
    fontSize: 14,
    lineHeight: 1.65,
    color: "var(--text-secondary)",
    maxWidth: 640,
  },
  studentInfo: {
    textAlign: "right",
    flexShrink: 0,
  },
  studentName: {
    fontSize: 14,
    fontWeight: 600,
    color: "var(--text-primary)",
  },
  studentNumber: {
    fontSize: 12,
    color: "var(--text-secondary)",
    marginTop: 2,
  },
  statsRow: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 12,
    marginBottom: 20,
  },
  statCard: {
    backgroundColor: "var(--card)",
    borderRadius: 8,
    padding: "18px 20px",
    border: "1px solid",
    textAlign: "center",
  },
  statValue: {
    fontSize: 30,
    fontWeight: 500,
    lineHeight: 1,
    marginBottom: 4,
  },
  statUnit: {
    fontSize: 12,
    color: "var(--text-secondary)",
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 11,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    color: "var(--text-secondary)",
    marginBottom: 4,
  },
  statSub: {
    fontSize: 11,
    fontStyle: "italic",
  },
  conditionsCard: {
    backgroundColor: "var(--error-bg)",
    border: "1px solid var(--error-border)",
    borderRadius: 8,
    padding: "18px 22px",
    marginBottom: 20,
  },
  section: {
    backgroundColor: "var(--card)",
    border: "1px solid var(--border)",
    borderRadius: 8,
    marginBottom: 20,
    overflow: "hidden",
  },
  sectionToggle: {
    width: "100%",
    background: "none",
    border: "none",
    padding: "16px 20px",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    borderBottom: "1px solid var(--border)",
  },
  sectionHeader: {
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  sectionTitle: {
    fontFamily: "'Inter', sans-serif",
    fontSize: 13,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    color: "var(--text-secondary)",
  },
  agentGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: 0,
  },
  agentCard: {
    padding: "18px 20px",
    borderRight: "1px solid var(--border)",
  },
  agentHeader: {
    display: "flex",
    alignItems: "flex-start",
    gap: 10,
    marginBottom: 10,
  },
  agentIcon: {
    fontSize: 18,
    flexShrink: 0,
    marginTop: 2,
  },
  agentName: {
    fontSize: 13,
    fontWeight: 600,
    color: "var(--text-primary)",
    lineHeight: 1.3,
  },
  verdictBadge: {
    display: "inline-block",
    padding: "3px 8px",
    borderRadius: 4,
    fontSize: 10,
    fontWeight: 700,
    letterSpacing: "0.06em",
    border: "1px solid",
    flexShrink: 0,
    fontFamily: "'IBM Plex Mono', monospace",
  },
  agentStatement: {
    fontSize: 12.5,
    color: "var(--text-secondary)",
    lineHeight: 1.55,
    fontStyle: "italic",
    marginBottom: 8,
    paddingLeft: 2,
  },
  agentIssues: {
    listStyle: "none",
    display: "flex",
    flexDirection: "column",
    gap: 4,
    marginTop: 8,
    paddingTop: 8,
    borderTop: "1px solid var(--border)",
  },
  agentIssue: {
    fontSize: 12,
    color: "var(--error)",
    display: "flex",
    gap: 6,
    lineHeight: 1.4,
  },
  listsRow: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 16,
    marginBottom: 20,
  },
  listCard: {
    backgroundColor: "var(--card)",
    border: "1px solid var(--border)",
    borderRadius: 8,
    padding: "18px 22px",
  },
  countBadge: {
    fontSize: 12,
    fontWeight: 600,
    color: "var(--text-muted)",
    marginLeft: "auto",
  },
  courseList: {
    listStyle: "none",
    display: "flex",
    flexDirection: "column",
    gap: 5,
    marginTop: 12,
    maxHeight: 300,
    overflowY: "auto",
  },
  courseItem: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    fontSize: 13,
    color: "var(--text-primary)",
    padding: "3px 0",
  },
  courseItemMissing: {
    color: "var(--error)",
  },
  courseCode: {
    fontSize: 11,
    backgroundColor: "var(--code-bg)",
    padding: "2px 6px",
    borderRadius: 3,
    flexShrink: 0,
    color: "var(--gold)",
  },
  courseName: {
    color: "inherit",
  },
  emptyState: {
    fontSize: 13,
    color: "var(--text-muted)",
    fontStyle: "italic",
    marginTop: 10,
  },
  conditionList: {
    listStyle: "none",
    display: "flex",
    flexDirection: "column",
    gap: 8,
    marginTop: 12,
  },
  conditionItem: {
    fontSize: 14,
    color: "var(--error)",
    display: "flex",
    alignItems: "flex-start",
    gap: 10,
    lineHeight: 1.5,
  },
  conditionBullet: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    width: 20,
    height: 20,
    borderRadius: "50%",
    backgroundColor: "var(--error-bg)",
    border: "1px solid var(--error-border)",
    fontSize: 11,
    fontWeight: 700,
    flexShrink: 0,
    color: "var(--error)",
    fontFamily: "monospace",
    marginTop: 1,
  },
  actions: {
    display: "flex",
    gap: 10,
    marginTop: 8,
    flexWrap: "wrap",
  },
  primaryBtn: {
    backgroundColor: "var(--gold)",
    color: "#0b1120",
    border: "none",
    borderRadius: 7,
    padding: "10px 26px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    transition: "opacity 0.15s",
  },
  secondaryBtn: {
    backgroundColor: "transparent",
    color: "var(--text-secondary)",
    border: "1px solid var(--border)",
    borderRadius: 7,
    padding: "10px 26px",
    fontSize: 14,
    fontWeight: 500,
    cursor: "pointer",
    transition: "border-color 0.15s",
  },
  dangerBtn: {
    backgroundColor: "var(--error-bg)",
    color: "var(--error)",
    border: "1px solid var(--error-border)",
    borderRadius: 7,
    padding: "10px 26px",
    fontSize: 14,
    fontWeight: 500,
    cursor: "pointer",
    marginLeft: "auto",
    transition: "opacity 0.15s",
  },
  actionBtn: {
    backgroundColor: "var(--gold)",
    color: "#0b1120",
    border: "none",
    borderRadius: 6,
    padding: "8px 20px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    display: "inline-block",
  },
  errorBox: {
    backgroundColor: "var(--error-bg)",
    border: "1px solid var(--error-border)",
    borderRadius: 8,
    padding: "20px 24px",
    color: "var(--error)",
    display: "flex",
    gap: 12,
    alignItems: "flex-start",
    fontSize: 14,
  },
  loadingWrap: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    padding: "20px 0",
  },
  spinner: {
    width: 20,
    height: 20,
    border: "2px solid var(--border)",
    borderTopColor: "var(--gold)",
    borderRadius: "50%",
    animation: "spin 0.75s linear infinite",
    flexShrink: 0,
  },
};
