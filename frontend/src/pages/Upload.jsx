import { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { uploadTranscript, analyzeTranscript } from "../api";
import { useLang } from "../contexts/LangContext";

export default function Upload() {
  const { t } = useLang();
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [error, setError] = useState(null);
  const [dragging, setDragging] = useState(false);
  const textareaRef = useRef(null);
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
      }, 2200);

      const { transcript_id } = await uploadTranscript(text);
      const result = await analyzeTranscript(transcript_id);

      clearInterval(stepTimer);
      navigate(`/result/${result.analysis_id}`);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    if (!file.name.endsWith(".txt") && file.type !== "text/plain") {
      setError(t.upload_err_filetype);
      return;
    }
    const reader = new FileReader();
    reader.onload = (ev) => setText(ev.target.result);
    reader.readAsText(file, "UTF-8");
  }, []);

  const handleDragOver = (e) => { e.preventDefault(); setDragging(true); };
  const handleDragLeave = () => setDragging(false);

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => setText(ev.target.result);
    reader.readAsText(file, "UTF-8");
  };

  const charCount = text.length;
  const lineCount = text ? text.split("\n").length : 0;
  const isEmpty = !text.trim();

  return (
    <div>
      <div style={styles.header}>
        <h1 style={styles.title}>{t.upload_title}</h1>
        <p style={styles.subtitle}>{t.upload_subtitle}</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div style={styles.textareaWrapper}>
          <div style={styles.labelRow}>
            <label style={styles.label}>{t.upload_label}</label>
            <label style={styles.fileLabel} title={t.upload_file_btn}>
              <input
                type="file"
                accept=".txt,text/plain"
                onChange={handleFileInput}
                style={{ display: "none" }}
              />
              {t.upload_file_btn}
            </label>
          </div>

          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            style={styles.dropZone}
          >
            <textarea
              ref={textareaRef}
              style={{
                ...styles.textarea,
                ...(dragging ? styles.textareaDragging : {}),
              }}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={t.upload_placeholder}
              rows={18}
              disabled={loading}
              spellCheck={false}
            />
            {dragging && (
              <div style={styles.dropOverlay}>
                <div style={styles.dropOverlayText}>{t.upload_drop_hint}</div>
              </div>
            )}
          </div>

          <div style={styles.metaRow}>
            <span className="mono" style={styles.meta}>
              {charCount > 0 ? t.upload_chars(charCount, lineCount) : t.upload_waiting}
            </span>
            {text && (
              <button
                type="button"
                onClick={() => setText("")}
                style={styles.clearBtn}
                disabled={loading}
              >
                {t.upload_clear}
              </button>
            )}
          </div>
        </div>

        {error && (
          <div style={styles.errorBox}>
            <span style={styles.errorIcon}>⚠</span>
            <div>
              <strong>Hata:</strong> {error}
            </div>
          </div>
        )}

        {loading ? (
          <div style={styles.loadingBox}>
            <div style={styles.spinner} />
            <div style={styles.loadingContent}>
              <div style={styles.loadingTitle}>{t.upload_analyzing}</div>
              <div style={styles.loadingSteps}>
                {t.steps.map((step, i) => (
                  <div
                    key={i}
                    style={{
                      ...styles.loadingStep,
                      ...(i === stepIndex ? styles.loadingStepActive : {}),
                      ...(i < stepIndex ? styles.loadingStepDone : {}),
                    }}
                  >
                    <span style={styles.stepIcon}>
                      {i < stepIndex ? "✓" : step.icon}
                    </span>
                    {step.label}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div style={styles.submitRow}>
            <button
              type="submit"
              style={{ ...styles.button, ...(isEmpty ? styles.buttonDisabled : {}) }}
              disabled={isEmpty}
            >
              {t.upload_submit}
            </button>
            <span style={styles.hint}>
              {isEmpty ? t.upload_hint_empty : t.upload_hint_ready(lineCount)}
            </span>
          </div>
        )}
      </form>

      <div style={styles.infoGrid}>
        {t.info_cards.map(({ icon, title, desc }) => (
          <div key={title} style={styles.infoCard}>
            <div style={styles.infoIcon}>{icon}</div>
            <div style={styles.infoTitle}>{title}</div>
            <div style={styles.infoDesc}>{desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  header: {
    marginBottom: 32,
  },
  title: {
    fontSize: 34,
    marginBottom: 10,
    lineHeight: 1.2,
  },
  subtitle: {
    color: "var(--text-secondary)",
    maxWidth: 620,
    lineHeight: 1.7,
    fontSize: 15,
  },
  textareaWrapper: {
    marginBottom: 20,
  },
  labelRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  label: {
    fontSize: 12,
    fontWeight: 600,
    color: "var(--text-secondary)",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
  },
  fileLabel: {
    fontSize: 12,
    color: "var(--gold)",
    cursor: "pointer",
    padding: "4px 10px",
    borderRadius: 4,
    border: "1px solid var(--gold-muted)",
    backgroundColor: "var(--gold-subtle)",
    transition: "all 0.15s",
    fontWeight: 500,
  },
  dropZone: {
    position: "relative",
  },
  textarea: {
    width: "100%",
    backgroundColor: "var(--card)",
    border: "1px solid var(--border)",
    borderRadius: 8,
    color: "var(--text-primary)",
    fontFamily: "'IBM Plex Mono', 'Fira Mono', monospace",
    fontSize: 12.5,
    lineHeight: 1.65,
    padding: "14px 16px",
    resize: "vertical",
    outline: "none",
    transition: "border-color 0.15s, box-shadow 0.15s, background-color 0.2s",
    display: "block",
  },
  textareaDragging: {
    borderColor: "var(--gold)",
    backgroundColor: "var(--gold-subtle)",
  },
  dropOverlay: {
    position: "absolute",
    inset: 0,
    borderRadius: 8,
    backgroundColor: "var(--gold-subtle)",
    border: "2px dashed var(--gold)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    pointerEvents: "none",
  },
  dropOverlayText: {
    fontSize: 18,
    fontWeight: 600,
    color: "var(--gold)",
  },
  metaRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 6,
  },
  meta: {
    fontSize: 11.5,
    color: "var(--text-muted)",
  },
  clearBtn: {
    background: "none",
    border: "none",
    fontSize: 12,
    color: "var(--text-muted)",
    cursor: "pointer",
    padding: "2px 6px",
    borderRadius: 3,
    transition: "color 0.15s",
  },
  errorBox: {
    backgroundColor: "var(--error-bg)",
    border: "1px solid var(--error-border)",
    borderRadius: 8,
    padding: "12px 16px",
    color: "var(--error)",
    marginBottom: 20,
    fontSize: 14,
    display: "flex",
    alignItems: "flex-start",
    gap: 10,
  },
  errorIcon: {
    fontSize: 16,
    flexShrink: 0,
    marginTop: 1,
  },
  submitRow: {
    display: "flex",
    alignItems: "center",
    gap: 16,
  },
  button: {
    backgroundColor: "var(--gold)",
    color: "#0b1120",
    border: "none",
    borderRadius: 7,
    padding: "12px 34px",
    fontSize: 15,
    fontWeight: 600,
    letterSpacing: "0.03em",
    transition: "opacity 0.15s, transform 0.1s",
  },
  buttonDisabled: {
    opacity: 0.45,
    cursor: "not-allowed",
  },
  hint: {
    fontSize: 13,
    color: "var(--text-muted)",
  },
  loadingBox: {
    display: "flex",
    alignItems: "flex-start",
    gap: 20,
    backgroundColor: "var(--card)",
    border: "1px solid var(--border)",
    borderRadius: 10,
    padding: "22px 26px",
  },
  spinner: {
    width: 22,
    height: 22,
    border: "2px solid var(--border)",
    borderTopColor: "var(--gold)",
    borderRadius: "50%",
    animation: "spin 0.75s linear infinite",
    flexShrink: 0,
    marginTop: 3,
  },
  loadingContent: {
    flex: 1,
  },
  loadingTitle: {
    fontSize: 14,
    fontWeight: 600,
    color: "var(--text-primary)",
    marginBottom: 12,
  },
  loadingSteps: {
    display: "flex",
    flexDirection: "column",
    gap: 8,
  },
  loadingStep: {
    fontSize: 13.5,
    color: "var(--text-muted)",
    display: "flex",
    alignItems: "center",
    gap: 10,
    transition: "color 0.3s",
  },
  loadingStepActive: {
    color: "var(--gold)",
    fontWeight: 500,
  },
  loadingStepDone: {
    color: "var(--success)",
  },
  stepIcon: {
    width: 20,
    textAlign: "center",
    fontSize: 14,
  },
  infoGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 12,
    marginTop: 48,
    paddingTop: 32,
    borderTop: "1px solid var(--border)",
  },
  infoCard: {
    backgroundColor: "var(--card)",
    border: "1px solid var(--border)",
    borderRadius: 8,
    padding: "16px 18px",
    textAlign: "center",
  },
  infoIcon: {
    fontSize: 22,
    marginBottom: 8,
  },
  infoTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: "var(--text-primary)",
    marginBottom: 4,
  },
  infoDesc: {
    fontSize: 12,
    color: "var(--text-secondary)",
    lineHeight: 1.5,
  },
};
