import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getHistory, deleteAnalysis } from "../api";

export default function History() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    getHistory()
      .then((data) => {
        setRecords(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm("Bu analizi silmek istediğinizden emin misiniz?")) return;
    try {
      await deleteAnalysis(id);
      setRecords(records.filter((r) => r.analysis_id !== id));
    } catch (err) {
      alert("Silme hatası: " + err.message);
    }
  };

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

  if (loading) return <div style={styles.loading}>Yükleniyor...</div>;

  return (
    <div>
      <div style={styles.header}>
        <h1 style={styles.title}>Analiz Geçmişi</h1>
        <p style={styles.subtitle}>Daha önce gerçekleştirilen mezuniyet analizleri</p>
      </div>

      {error && (
        <div style={styles.errorBox}>
          <strong>Hata:</strong> {error}
        </div>
      )}

      {records.length === 0 ? (
        <div style={styles.empty}>
          <div style={styles.emptyIcon}>📋</div>
          <div>Henüz analiz yapılmamış.</div>
          <button onClick={() => navigate("/")} style={styles.newBtn}>
            İlk Analizi Başlat
          </button>
        </div>
      ) : (
        <div style={styles.tableWrapper}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Öğrenci</th>
                <th style={styles.th}>No</th>
                <th style={{ ...styles.th, textAlign: "center" }}>GNO</th>
                <th style={{ ...styles.th, textAlign: "center" }}>ECTS</th>
                <th style={{ ...styles.th, textAlign: "center" }}>Durum</th>
                <th style={{ ...styles.th, textAlign: "right" }}>Tarih</th>
                <th style={{ ...styles.th, textAlign: "center", width: 60 }}>İşlem</th>
              </tr>
            </thead>
            <tbody>
              {records.map((rec) => (
                <tr
                  key={rec.analysis_id}
                  style={styles.row}
                  onClick={() => navigate(`/result/${rec.analysis_id}`)}
                >
                  <td style={styles.td}>
                    {rec.student_name || <span style={styles.muted}>Bilinmiyor</span>}
                  </td>
                  <td style={{ ...styles.td }}>
                    <span className="mono" style={styles.studentNo}>
                      {rec.student_number || "—"}
                    </span>
                  </td>
                  <td style={{ ...styles.td, textAlign: "center" }}>
                    <span className="mono">{rec.gpa?.toFixed(2) ?? "—"}</span>
                  </td>
                  <td style={{ ...styles.td, textAlign: "center" }}>
                    <span className="mono">{rec.total_ects ?? "—"}</span>
                  </td>
                  <td style={{ ...styles.td, textAlign: "center" }}>
                    <span
                      style={{
                        ...styles.badge,
                        ...(rec.is_graduated ? styles.badgeGreen : styles.badgeRed),
                      }}
                    >
                      {rec.is_graduated ? "Mezun" : "Eksik"}
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
                      title="Sil"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const styles = {
  header: {
    marginBottom: 32,
  },
  title: {
    fontSize: 36,
    marginBottom: 10,
  },
  subtitle: {
    color: "var(--text-secondary)",
  },
  loading: {
    color: "var(--text-secondary)",
    fontSize: 14,
  },
  errorBox: {
    backgroundColor: "var(--error-bg)",
    border: "1px solid var(--error)",
    borderRadius: 8,
    padding: "16px 20px",
    color: "#ff6b6b",
    marginBottom: 20,
    fontSize: 14,
  },
  empty: {
    textAlign: "center",
    padding: "60px 24px",
    color: "var(--text-secondary)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 16,
  },
  emptyIcon: {
    fontSize: 40,
  },
  newBtn: {
    backgroundColor: "var(--gold)",
    color: "#0b1120",
    border: "none",
    borderRadius: 6,
    padding: "10px 24px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    marginTop: 8,
  },
  tableWrapper: {
    backgroundColor: "var(--navy-card)",
    border: "1px solid var(--navy-border)",
    borderRadius: 8,
    overflow: "hidden",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
  },
  th: {
    padding: "12px 16px",
    fontSize: 11,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "0.1em",
    color: "var(--text-secondary)",
    backgroundColor: "rgba(255,255,255,0.03)",
    borderBottom: "1px solid var(--navy-border)",
    textAlign: "left",
  },
  row: {
    borderBottom: "1px solid var(--navy-border)",
    cursor: "pointer",
    transition: "background-color 0.1s",
  },
  td: {
    padding: "14px 16px",
    fontSize: 14,
    color: "var(--text-primary)",
  },
  muted: {
    color: "var(--text-secondary)",
    fontStyle: "italic",
  },
  studentNo: {
    fontSize: 12,
    color: "var(--text-secondary)",
  },
  badge: {
    display: "inline-block",
    padding: "3px 10px",
    borderRadius: 3,
    fontSize: 11,
    fontWeight: 600,
    letterSpacing: "0.06em",
    textTransform: "uppercase",
  },
  badgeGreen: {
    backgroundColor: "rgba(46,204,113,0.12)",
    color: "var(--success)",
    border: "1px solid rgba(46,204,113,0.3)",
  },
  badgeRed: {
    backgroundColor: "rgba(231,76,60,0.12)",
    color: "var(--error)",
    border: "1px solid rgba(231,76,60,0.3)",
  },
  date: {
    fontSize: 12,
    color: "var(--text-secondary)",
  },
  deleteBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    fontSize: 16,
    padding: "4px 8px",
    borderRadius: 4,
    transition: "background-color 0.2s",
  },
};
