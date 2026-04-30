import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadTranscript, analyzeTranscript } from "../api";

const STEPS = [
  "Transkript yükleniyor...",
  "Metin ayrıştırılıyor...",
  "Mezuniyet koşulları kontrol ediliyor...",
  "Rapor hazırlanıyor...",
];

export default function Upload() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim()) return;

    setError(null);
    setLoading(true);
    setStepIndex(0);

    try {
      const stepTimer = setInterval(() => {
        setStepIndex((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
      }, 2500);

      const { transcript_id } = await uploadTranscript(text);
      const result = await analyzeTranscript(transcript_id);

      clearInterval(stepTimer);
      navigate(`/result/${result.analysis_id}`);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div>
      <div style={styles.header}>
        <h1 style={styles.title}>Mezuniyet Analizi</h1>
        <p style={styles.subtitle}>
          Transkriptinizi aşağıya yapıştırın. Sistem GSU Bilgisayar Mühendisliği
          mezuniyet gereksinimlerini otomatik olarak değerlendirecektir.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div style={styles.textareaWrapper}>
          <label style={styles.label}>Transkript Metni</label>
          <textarea
            style={styles.textarea}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Transkript metnini buraya yapıştırın..."
            rows={16}
            disabled={loading}
          />
          <div style={styles.charCount} className="mono">
            {text.length} karakter
          </div>
        </div>

        {error && (
          <div style={styles.errorBox}>
            <strong>Hata:</strong> {error}
          </div>
        )}

        {loading ? (
          <div style={styles.loadingBox}>
            <div style={styles.spinner} />
            <div style={styles.loadingSteps}>
              {STEPS.map((step, i) => (
                <div
                  key={i}
                  style={{
                    ...styles.loadingStep,
                    ...(i === stepIndex ? styles.loadingStepActive : {}),
                    ...(i < stepIndex ? styles.loadingStepDone : {}),
                  }}
                >
                  <span style={styles.stepDot}>
                    {i < stepIndex ? "✓" : i === stepIndex ? "›" : "·"}
                  </span>
                  {step}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <button
            type="submit"
            style={{ ...styles.button, ...(text.trim() ? {} : styles.buttonDisabled) }}
            disabled={!text.trim()}
          >
            Analiz Et
          </button>
        )}
      </form>
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
    maxWidth: 600,
    lineHeight: 1.7,
  },
  label: {
    display: "block",
    fontSize: 13,
    fontWeight: 600,
    color: "var(--text-secondary)",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    marginBottom: 8,
  },
  textareaWrapper: {
    marginBottom: 24,
  },
  textarea: {
    width: "100%",
    backgroundColor: "var(--navy-card)",
    border: "1px solid var(--navy-border)",
    borderRadius: 8,
    color: "var(--text-primary)",
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: 13,
    lineHeight: 1.6,
    padding: "14px 16px",
    resize: "vertical",
    outline: "none",
    transition: "border-color 0.15s",
  },
  charCount: {
    marginTop: 6,
    fontSize: 12,
    color: "var(--text-secondary)",
    textAlign: "right",
  },
  button: {
    backgroundColor: "var(--gold)",
    color: "#0b1120",
    border: "none",
    borderRadius: 6,
    padding: "12px 32px",
    fontSize: 15,
    fontWeight: 600,
    letterSpacing: "0.03em",
    transition: "background-color 0.15s",
  },
  buttonDisabled: {
    backgroundColor: "var(--gold-muted)",
    color: "#555",
    cursor: "not-allowed",
  },
  errorBox: {
    backgroundColor: "var(--error-bg)",
    border: "1px solid var(--error)",
    borderRadius: 6,
    padding: "12px 16px",
    color: "#ff6b6b",
    marginBottom: 20,
    fontSize: 14,
  },
  loadingBox: {
    display: "flex",
    alignItems: "flex-start",
    gap: 20,
    backgroundColor: "var(--navy-card)",
    border: "1px solid var(--navy-border)",
    borderRadius: 8,
    padding: "20px 24px",
  },
  spinner: {
    width: 20,
    height: 20,
    border: "2px solid var(--navy-border)",
    borderTopColor: "var(--gold)",
    borderRadius: "50%",
    animation: "spin 0.8s linear infinite",
    flexShrink: 0,
    marginTop: 2,
  },
  loadingSteps: {
    display: "flex",
    flexDirection: "column",
    gap: 8,
  },
  loadingStep: {
    fontSize: 14,
    color: "var(--text-secondary)",
    display: "flex",
    alignItems: "center",
    gap: 8,
    transition: "color 0.3s",
  },
  loadingStepActive: {
    color: "var(--gold)",
    fontWeight: 500,
  },
  loadingStepDone: {
    color: "var(--success)",
  },
  stepDot: {
    fontFamily: "monospace",
    width: 16,
    textAlign: "center",
  },
};
