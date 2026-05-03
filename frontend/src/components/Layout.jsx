import { useState, useEffect, useCallback } from "react";
import { Outlet, NavLink, useLocation } from "react-router-dom";
import { useLang } from "../contexts/LangContext";
import gsuLogo from "../assets/gsu-university-logo.png";

function SunIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="1" x2="12" y2="3"/>
      <line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/>
      <line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  );
}

function Toast({ message, type, onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 3500);
    return () => clearTimeout(t);
  }, [onClose]);

  return (
    <div className={`toast toast-${type}`} onClick={onClose}>
      {message}
    </div>
  );
}

export const ToastContext = { listeners: [] };
export function showToast(message, type = "info") {
  ToastContext.listeners.forEach((fn) => fn({ message, type, id: Date.now() }));
}

export default function Layout() {
  const { lang, toggle: toggleLang, t } = useLang();
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");
  const [toasts, setToasts] = useState([]);
  const location = useLocation();
  const isResultPage = location.pathname.startsWith("/result");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const addToast = useCallback((toast) => {
    setToasts((prev) => [...prev, toast]);
  }, []);

  useEffect(() => {
    ToastContext.listeners.push(addToast);
    return () => {
      ToastContext.listeners = ToastContext.listeners.filter((fn) => fn !== addToast);
    };
  }, [addToast]);

  const removeToast = (id) => setToasts((prev) => prev.filter((t) => t.id !== id));

  const toggleTheme = () => setTheme((t) => (t === "dark" ? "light" : "dark"));

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div style={styles.brand}>
            <img src={gsuLogo} alt="Galatasaray Üniversitesi logosu" style={styles.brandLogo} />
            <div>
              <div style={styles.brandTitle}>{t.brand_title}</div>
              <div style={styles.brandSub}>{t.brand_sub}</div>
            </div>
          </div>

          <div style={styles.headerRight}>
            <nav style={styles.nav}>
              <NavLink
                to="/"
                end
                style={({ isActive }) => ({ ...styles.navLink, ...(isActive ? styles.navLinkActive : {}) })}
              >
                {t.nav_analyze}
              </NavLink>
              <NavLink
                to="/history"
                style={({ isActive }) => ({ ...styles.navLink, ...(isActive ? styles.navLinkActive : {}) })}
              >
                {t.nav_history}
              </NavLink>
            </nav>

            <button
              onClick={toggleLang}
              style={{ ...styles.langBtn, ...(isResultPage ? styles.langBtnDisabled : {}) }}
              title={lang === "tr" ? "Switch to English" : "Türkçeye geç"}
              aria-label="Change language"
              disabled={isResultPage}
            >
              {lang === "tr" ? "EN" : "TR"}
            </button>

            <button
              onClick={toggleTheme}
              style={styles.themeBtn}
              title={theme === "dark" ? t.theme_to_light : t.theme_to_dark}
              aria-label="Toggle theme"
            >
              {theme === "dark" ? <SunIcon /> : <MoonIcon />}
            </button>
          </div>
        </div>
      </header>

      <main style={styles.main}>
        <div className="fade-in">
          <Outlet />
        </div>
      </main>

      <footer style={styles.footer}>
        <span>{t.footer_uni} &mdash; {t.footer_sys}</span>
        <span style={styles.footerSep}>·</span>
        <span>{t.footer_dept}</span>
      </footer>

      {toasts.map((t) => (
        <Toast key={t.id} message={t.message} type={t.type} onClose={() => removeToast(t.id)} />
      ))}
    </div>
  );
}

const styles = {
  header: {
    backgroundColor: "var(--bg-raised)",
    borderBottom: "1px solid var(--border)",
    padding: "0 24px",
    position: "sticky",
    top: 0,
    zIndex: 100,
    backdropFilter: "blur(8px)",
  },
  headerInner: {
    maxWidth: 1040,
    margin: "0 auto",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    height: 68,
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: 14,
  },
  brandLogo: {
    width: 44,
    height: 44,
    objectFit: "contain",
    flexShrink: 0,
  },
  brandTitle: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 16,
    fontWeight: 600,
    color: "var(--text-primary)",
    lineHeight: 1.25,
  },
  brandSub: {
    fontSize: 11,
    color: "var(--text-secondary)",
    marginTop: 2,
    letterSpacing: "0.03em",
  },
  headerRight: {
    display: "flex",
    alignItems: "center",
    gap: 12,
  },
  nav: {
    display: "flex",
    gap: 4,
  },
  navLink: {
    padding: "6px 14px",
    fontSize: 14,
    fontWeight: 500,
    color: "var(--text-secondary)",
    borderRadius: 6,
    border: "1px solid transparent",
    transition: "all 0.15s",
    textDecoration: "none",
  },
  navLinkActive: {
    color: "var(--gold)",
    border: "1px solid var(--gold-muted)",
    backgroundColor: "var(--gold-subtle)",
  },
  langBtn: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    height: 36,
    padding: "0 12px",
    borderRadius: 8,
    border: "1px solid var(--border)",
    backgroundColor: "var(--overlay)",
    color: "var(--text-secondary)",
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: "0.06em",
    cursor: "pointer",
    transition: "all 0.15s",
    flexShrink: 0,
    fontFamily: "'Inter', sans-serif",
  },
  langBtnDisabled: {
    opacity: 0.5,
    cursor: "not-allowed",
  },
  themeBtn: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    width: 36,
    height: 36,
    borderRadius: 8,
    border: "1px solid var(--border)",
    backgroundColor: "var(--overlay)",
    color: "var(--text-secondary)",
    transition: "all 0.15s",
    flexShrink: 0,
  },
  main: {
    flex: 1,
    maxWidth: 1040,
    width: "100%",
    margin: "0 auto",
    padding: "40px 24px",
  },
  footer: {
    textAlign: "center",
    padding: "14px 24px",
    fontSize: 12,
    color: "var(--text-muted)",
    borderTop: "1px solid var(--border)",
    display: "flex",
    justifyContent: "center",
    gap: 8,
    alignItems: "center",
  },
  footerSep: {
    opacity: 0.4,
  },
};
