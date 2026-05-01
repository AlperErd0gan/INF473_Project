import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { getHistory, deleteAnalysis } from "../api";
import { useLang } from "../contexts/LangContext";

export default function History() {
  const { t } = useLang();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [sortDir, setSortDir] = useState("desc");
  const navigate = useNavigate();

  useEffect(() => {
    getHistory()
      .then((data) => { setRecords(data); setLoading(false); })
      .catch((err) => { setError(err.message); setLoading(false); });
  }, []);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm(t.history_delete_confirm)) return;
    try {
      await deleteAnalysis(id);
      setRecords((prev) => prev.filter((r) => r.analysis_id !== id));
    } catch (err) {
      alert(t.history_delete_error + err.message);
    }
  };

  const filtered = useMemo(() => {
    let out = records;
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      out = out.filter(
        (r) =>
          r.student_name?.toLowerCase().includes(q) ||
          r.student_number?.toLowerCase().includes(q)
      );
    }
    if (filter === "graduated") out = out.filter((r) => r.is_graduated);
    if (filter === "missing") out = out.filter((r) => !r.is_graduated);
    if (sortDir === "asc") out = [...out].reverse();
    return out;
  }, [records, search, filter, sortDir]);

  function formatDate(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleDateString("tr-TR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  const gradCount = records.filter((r) => r.is_graduated).length;
  const failCount = records.length - gradCount;

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "20px 0" }}>
        <div style={styles.spinner} />
        <span style={{ color: "var(--text-secondary)", fontSize: 14 }}>{t.history_loading}</span>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>{t.history_title}</h1>
          <p style={styles.subtitle}>{t.history_subtitle(records.length, gradCount, failCount)}</p>
        </div>
        <button onClick={() => navigate("/")} style={styles.newBtn}>
          {t.history_btn_new}
        </button>
      </div>

      {error && (
        <div style={styles.errorBox}>
          <span>⚠</span> <strong>Hata:</strong> {error}
        </div>
      )}

      {records.length > 0 && (
        <div style={styles.toolbar}>
          <input
            type="text"
            placeholder={t.history_search_placeholder}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={styles.searchInput}
          />
          <div style={styles.filters}>
            {[
              { key: "all",       label: t.history_filter_all(records.length) },
              { key: "graduated", label: t.history_filter_grad(gradCount) },
              { key: "missing",   label: t.history_filter_fail(failCount) },
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setFilter(key)}
                style={{ ...styles.filterBtn, ...(filter === key ? styles.filterBtnActive : {}) }}
              >
                {label}
              </button>
            ))}
            <button
              onClick={() => setSortDir((d) => (d === "desc" ? "asc" : "desc"))}
              style={styles.sortBtn}
              title="Sort by date"
            >
              {sortDir === "desc" ? t.history_sort_new : t.history_sort_old}
            </button>
          </div>
        </div>
      )}

      {records.length === 0 ? (
        <div style={styles.empty}>
          <div style={styles.emptyIcon}>📋</div>
          <div style={{ fontSize: 15, color: "var(--text-secondary)" }}>
            {t.history_empty_title}
          </div>
          <button onClick={() => navigate("/")} style={styles.newBtn}>
            {t.history_empty_btn}
          </button>
        </div>
      ) : filtered.length === 0 ? (
        <div style={styles.empty}>
          <div style={styles.emptyIcon}>🔍</div>
          <div style={{ fontSize: 15, color: "var(--text-secondary)" }}>
            {t.history_no_results}
          </div>
        </div>
      ) : (
        <div style={styles.tableWrapper}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>{t.history_col_student}</th>
                <th style={styles.th}>{t.history_col_no}</th>
                <th style={{ ...styles.th, textAlign: "center" }}>{t.history_col_gpa}</th>
                <th style={{ ...styles.th, textAlign: "center" }}>{t.history_col_ects}</th>
                <th style={{ ...styles.th, textAlign: "center" }}>{t.history_col_status}</th>
                <th style={{ ...styles.th, textAlign: "right" }}>{t.history_col_date}</th>
                <th style={{ ...styles.th, textAlign: "center", width: 56 }}></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((rec) => (
                <tr
                  key={rec.analysis_id}
                  style={styles.row}
                  onClick={() => navigate(`/result/${rec.analysis_id}`)}
                >
                  <td style={styles.td}>
                    <div style={styles.nameCell}>
                      <div
                        style={{
                          ...styles.avatarDot,
                          backgroundColor: rec.is_graduated
                            ? "var(--success)"
                            : "var(--error)",
                        }}
                      />
                      {rec.student_name || (
                        <span style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
                          {t.history_unknown}
                        </span>
                      )}
                    </div>
                  </td>
                  <td style={styles.td}>
                    <span className="mono" style={styles.studentNo}>
                      {rec.student_number || "—"}
                    </span>
                  </td>
                  <td style={{ ...styles.td, textAlign: "center" }}>
                    <span
                      className="mono"
                      style={{ color: rec.gpa >= 2.0 ? "var(--success)" : "var(--error)" }}
                    >
                      {rec.gpa?.toFixed(2) ?? "—"}
                    </span>
                  </td>
                  <td style={{ ...styles.td, textAlign: "center" }}>
                    <span
                      className="mono"
                      style={{
                        color:
                          rec.transcript_total_ects >= (rec.required_ects ?? 240)
                            ? "var(--success)"
                            : "var(--error)",
                      }}
                    >
                      {rec.transcript_total_ects ?? "—"}
                    </span>
                  </td>
                  <td style={{ ...styles.td, textAlign: "center" }}>
                    <span
                      style={{
                        ...styles.badge,
                        ...(rec.is_graduated ? styles.badgeGreen : styles.badgeRed),
                      }}
                    >
                      {rec.is_graduated ? t.history_badge_grad : t.history_badge_fail}
                    </span>
                  </td>
                  <td style={{ ...styles.td, textAlign: "right" }}>
                    <span className="mono" style={styles.date}>
                      {formatDate(rec.analyzed_at)}
                    </span>
                  </td>
                  <td style={{ ...styles.td, textAlign: "center" }}>
                    <button
                      onClick={(e) => handleDelete(e, rec.analysis_id)}
                      style={styles.deleteBtn}
                      title={t.history_delete_title}
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={styles.tableFooter}>
            {t.history_footer(filtered.length, records.length)}
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  header: {
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between",
    marginBottom: 28,
    flexWrap: "wrap",
    gap: 16,
  },
  title: {
    fontSize: 34,
    marginBottom: 6,
    lineHeight: 1.2,
  },
  subtitle: {
    color: "var(--text-secondary)",
    fontSize: 14,
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
  errorBox: {
    backgroundColor: "var(--error-bg)",
    border: "1px solid var(--error-border)",
    borderRadius: 8,
    padding: "14px 18px",
    color: "var(--error)",
    marginBottom: 20,
    fontSize: 14,
    display: "flex",
    gap: 8,
    alignItems: "center",
  },
  toolbar: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    marginBottom: 16,
    flexWrap: "wrap",
  },
  searchInput: {
    flex: "1 1 200px",
    minWidth: 180,
    backgroundColor: "var(--card)",
    border: "1px solid var(--border)",
    borderRadius: 7,
    color: "var(--text-primary)",
    fontFamily: "'Inter', sans-serif",
    fontSize: 14,
    padding: "8px 14px",
    outline: "none",
    transition: "border-color 0.15s",
  },
  filters: {
    display: "flex",
    gap: 6,
    flexWrap: "wrap",
  },
  filterBtn: {
    backgroundColor: "var(--card)",
    border: "1px solid var(--border)",
    borderRadius: 6,
    color: "var(--text-secondary)",
    fontSize: 13,
    fontWeight: 500,
    padding: "7px 14px",
    cursor: "pointer",
    transition: "all 0.15s",
  },
  filterBtnActive: {
    backgroundColor: "var(--gold-subtle)",
    borderColor: "var(--gold-muted)",
    color: "var(--gold)",
  },
  sortBtn: {
    backgroundColor: "var(--overlay)",
    border: "1px solid var(--border)",
    borderRadius: 6,
    color: "var(--text-secondary)",
    fontSize: 12,
    fontWeight: 500,
    padding: "7px 12px",
    cursor: "pointer",
    fontFamily: "monospace",
  },
  empty: {
    textAlign: "center",
    padding: "64px 24px",
    color: "var(--text-secondary)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 14,
  },
  emptyIcon: {
    fontSize: 36,
    opacity: 0.6,
  },
  newBtn: {
    backgroundColor: "var(--gold)",
    color: "#0b1120",
    border: "none",
    borderRadius: 7,
    padding: "10px 22px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    whiteSpace: "nowrap",
    transition: "opacity 0.15s",
  },
  tableWrapper: {
    backgroundColor: "var(--card)",
    border: "1px solid var(--border)",
    borderRadius: 10,
    overflow: "hidden",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
  },
  th: {
    padding: "11px 16px",
    fontSize: 11,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "0.1em",
    color: "var(--text-secondary)",
    backgroundColor: "var(--overlay)",
    borderBottom: "1px solid var(--border)",
    textAlign: "left",
  },
  row: {
    borderBottom: "1px solid var(--border)",
    cursor: "pointer",
    transition: "background-color 0.1s",
  },
  td: {
    padding: "13px 16px",
    fontSize: 14,
    color: "var(--text-primary)",
  },
  nameCell: {
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  avatarDot: {
    width: 6,
    height: 6,
    borderRadius: "50%",
    flexShrink: 0,
  },
  studentNo: {
    fontSize: 12,
    color: "var(--text-secondary)",
  },
  badge: {
    display: "inline-block",
    padding: "3px 10px",
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 600,
    letterSpacing: "0.06em",
    textTransform: "uppercase",
    border: "1px solid",
  },
  badgeGreen: {
    backgroundColor: "var(--success-bg)",
    color: "var(--success)",
    borderColor: "var(--success-border)",
  },
  badgeRed: {
    backgroundColor: "var(--error-bg)",
    color: "var(--error)",
    borderColor: "var(--error-border)",
  },
  date: {
    fontSize: 12,
    color: "var(--text-muted)",
  },
  deleteBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    fontSize: 13,
    padding: "4px 8px",
    borderRadius: 4,
    color: "var(--text-muted)",
    transition: "color 0.15s",
  },
  tableFooter: {
    padding: "10px 16px",
    fontSize: 12,
    color: "var(--text-muted)",
    borderTop: "1px solid var(--border)",
    backgroundColor: "var(--overlay)",
  },
};
