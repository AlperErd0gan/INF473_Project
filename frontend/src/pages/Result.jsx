import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getAnalysis, deleteAnalysis } from "../api";

export default function Result() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getAnalysis(id)
      .then(setData)
      .catch((err) => setError(err.message));
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm("Bu analizi silmek istediğinizden emin misiniz?")) return;
    try {
      await deleteAnalysis(id);
      navigate("/history");
    } catch (err) {
      alert("Silme hatası: " + err.message);
    }
  };

  if (error) {
    return (
      <div style={styles.errorBox}>
        <strong>Hata:</strong> {error}
        <button onClick={() => navigate("/")} style={styles.backBtn}>
          Geri Dön
        </button>
      </div>
    );
  }

  if (!data) {
    return <div style={styles.loading}>Yükleniyor...</div>;
  }

  const graduated = data.is_graduated;

  return (
    <div>
      <div
        style={{
          ...styles.banner,
          ...(graduated ? styles.bannerSuccess : styles.bannerError),
        }}
      >
        <div style={styles.bannerIcon}>{graduated ? "✓" : "✗"}</div>
        <div>
          <div style={styles.bannerTitle}>
            {graduated ? "MEZUNİYETE HAK KAZANDI" : "EKSİK KOŞULLAR MEVCUT"}
          </div>
          {data.report_text && (
            <div style={styles.bannerReport}>{data.report_text}</div>
          )}
        </div>
      </div>

      <div style={styles.statsRow}>
        <StatCard label="Genel Not Ortalaması" value={data.gpa?.toFixed(2) ?? "—"} unit="/ 4.00" highlight={data.gpa >= 2.0} />
        <StatCard label="Toplam ECTS" value={data.total_ects ?? "—"} unit="/ 240" highlight={data.total_ects >= 240} />
        <StatCard label="Zorunlu Dersler" value={data.completed_courses?.length ?? 0} unit="/ 29" highlight={(data.completed_courses?.length ?? 0) >= 29} />
      </div>

      <div style={styles.listsRow}>
        <div style={styles.listCard}>
          <h3 style={styles.listTitle}>
            <span style={styles.checkGreen}>✓</span> Tamamlanan Zorunlu Dersler
          </h3>
          {data.completed_courses?.length > 0 ? (
            <ul style={styles.list}>
              {data.completed_courses.map((course, i) => (
                <li key={i} style={styles.listItemDone}>
                  <span className="mono" style={styles.courseCode}>
                    {course.split(" - ")[0] || course}
                  </span>
                  <span style={styles.courseName}>
                    {course.split(" - ").slice(1).join(" - ") || ""}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <div style={styles.emptyList}>Tamamlanan ders bulunamadı</div>
          )}
        </div>

        <div style={styles.listCard}>
          <h3 style={styles.listTitle}>
            <span style={styles.checkRed}>✗</span> Eksik Zorunlu Dersler
          </h3>
          {data.missing_courses?.length > 0 ? (
            <ul style={styles.list}>
              {data.missing_courses.map((course, i) => (
                <li key={i} style={styles.listItemMissing}>
                  <span className="mono" style={styles.courseCode}>
                    {course.split(" - ")[0] || course}
                  </span>
                  <span style={styles.courseName}>
                    {course.split(" - ").slice(1).join(" - ") || ""}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <div style={styles.emptyListGood}>Tüm zorunlu dersler tamamlandı</div>
          )}
        </div>
      </div>

      {data.missing_conditions?.length > 0 && (
        <div style={styles.conditionsCard}>
          <h3 style={styles.listTitle}>Karşılanmayan Koşullar</h3>
          <ul style={styles.list}>
            {data.missing_conditions.map((cond, i) => (
              <li key={i} style={styles.conditionItem}>
                <span style={{ color: "var(--error)" }}>›</span> {cond}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div style={styles.actions}>
        <button onClick={() => navigate("/")} style={styles.backBtn}>
          Yeni Analiz
        </button>
        <button onClick={() => navigate("/history")} style={styles.historyBtn}>
          Geçmişe Git
        </button>
        <button onClick={handleDelete} style={styles.deleteResultBtn}>
          Analizi Sil
        </button>
      </div>
    </div>
  );
}

function StatCard({ label, value, unit, highlight }) {
  return (
    <div style={{ ...styles.statCard, ...(highlight ? styles.statCardGood : styles.statCardBad) }}>
      <div style={styles.statValue} className="mono">{value}</div>
      <div style={styles.statUnit}>{unit}</div>
      <div style={styles.statLabel}>{label}</div>
    </div>
  );
}

const styles = {
  banner: {
    display: "flex",
    alignItems: "flex-start",
    gap: 20,
    borderRadius: 8,
    padding: "24px 28px",
    marginBottom: 32,
    border: "1px solid",
  },
  bannerSuccess: {
    backgroundColor: "var(--success-bg)",
    borderColor: "var(--success)",
    color: "var(--success)",
  },
  bannerError: {
    backgroundColor: "var(--error-bg)",
    borderColor: "var(--error)",
    color: "var(--error)",
  },
  bannerIcon: {
    fontSize: 28,
    fontWeight: 700,
    lineHeight: 1,
    marginTop: 2,
  },
  bannerTitle: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 22,
    fontWeight: 700,
    letterSpacing: "0.02em",
    marginBottom: 6,
  },
  bannerReport: {
    fontSize: 14,
    lineHeight: 1.6,
    color: "var(--text-secondary)",
    maxWidth: 680,
  },
  statsRow: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: 16,
    marginBottom: 28,
  },
  statCard: {
    backgroundColor: "var(--navy-card)",
    borderRadius: 8,
    padding: "20px 24px",
    border: "1px solid",
    textAlign: "center",
  },
  statCardGood: {
    borderColor: "var(--success)",
  },
  statCardBad: {
    borderColor: "var(--error)",
  },
  statValue: {
    fontSize: 32,
    fontWeight: 500,
    color: "var(--text-primary)",
    lineHeight: 1,
    marginBottom: 4,
  },
  statUnit: {
    fontSize: 13,
    color: "var(--text-secondary)",
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    color: "var(--text-secondary)",
  },
  listsRow: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 16,
    marginBottom: 20,
  },
  listCard: {
    backgroundColor: "var(--navy-card)",
    border: "1px solid var(--navy-border)",
    borderRadius: 8,
    padding: "20px 24px",
  },
  listTitle: {
    fontFamily: "'Inter', sans-serif",
    fontSize: 14,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    color: "var(--text-secondary)",
    marginBottom: 14,
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  checkGreen: { color: "var(--success)" },
  checkRed: { color: "var(--error)" },
  list: {
    listStyle: "none",
    display: "flex",
    flexDirection: "column",
    gap: 6,
  },
  listItemDone: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    fontSize: 13,
    color: "var(--text-primary)",
  },
  listItemMissing: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    fontSize: 13,
    color: "#ff8080",
  },
  courseCode: {
    fontSize: 12,
    backgroundColor: "rgba(255,255,255,0.06)",
    padding: "2px 6px",
    borderRadius: 3,
    flexShrink: 0,
    color: "var(--gold)",
  },
  courseName: {
    color: "inherit",
  },
  emptyList: {
    fontSize: 13,
    color: "var(--text-secondary)",
    fontStyle: "italic",
  },
  emptyListGood: {
    fontSize: 13,
    color: "var(--success)",
    fontStyle: "italic",
  },
  conditionsCard: {
    backgroundColor: "var(--error-bg)",
    border: "1px solid var(--error)",
    borderRadius: 8,
    padding: "20px 24px",
    marginBottom: 20,
  },
  conditionItem: {
    fontSize: 14,
    color: "#ff9999",
    display: "flex",
    alignItems: "flex-start",
    gap: 8,
    padding: "4px 0",
  },
  actions: {
    display: "flex",
    gap: 12,
    marginTop: 8,
  },
  backBtn: {
    backgroundColor: "var(--gold)",
    color: "#0b1120",
    border: "none",
    borderRadius: 6,
    padding: "10px 24px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
  },
  historyBtn: {
    backgroundColor: "transparent",
    color: "var(--text-secondary)",
    border: "1px solid var(--navy-border)",
    borderRadius: 6,
    padding: "10px 24px",
    fontSize: 14,
    fontWeight: 500,
    cursor: "pointer",
  },
  deleteResultBtn: {
    backgroundColor: "rgba(231,76,60,0.1)",
    color: "var(--error)",
    border: "1px solid rgba(231,76,60,0.3)",
    borderRadius: 6,
    padding: "10px 24px",
    fontSize: 14,
    fontWeight: 500,
    cursor: "pointer",
    marginLeft: "auto",
  },
  errorBox: {
    backgroundColor: "var(--error-bg)",
    border: "1px solid var(--error)",
    borderRadius: 8,
    padding: "20px 24px",
    color: "#ff6b6b",
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  loading: {
    color: "var(--text-secondary)",
    fontSize: 14,
  },
};
