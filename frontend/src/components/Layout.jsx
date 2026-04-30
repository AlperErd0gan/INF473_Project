import { Outlet, NavLink } from "react-router-dom";

export default function Layout() {
  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div style={styles.brand}>
            <span style={styles.brandInitials}>GSU</span>
            <div>
              <div style={styles.brandTitle}>Sanal Akademik Danışman</div>
              <div style={styles.brandSub}>Bilgisayar Mühendisliği Bölümü</div>
            </div>
          </div>
          <nav style={styles.nav}>
            <NavLink
              to="/"
              end
              style={({ isActive }) => ({ ...styles.navLink, ...(isActive ? styles.navLinkActive : {}) })}
            >
              Analiz
            </NavLink>
            <NavLink
              to="/history"
              style={({ isActive }) => ({ ...styles.navLink, ...(isActive ? styles.navLinkActive : {}) })}
            >
              Geçmiş
            </NavLink>
          </nav>
        </div>
      </header>

      <main style={styles.main}>
        <Outlet />
      </main>

      <footer style={styles.footer}>
        <span>Galatasaray Üniversitesi &mdash; Mezuniyet Analiz Sistemi</span>
      </footer>
    </div>
  );
}

const styles = {
  header: {
    backgroundColor: "var(--navy-light)",
    borderBottom: "1px solid var(--navy-border)",
    padding: "0 24px",
  },
  headerInner: {
    maxWidth: 960,
    margin: "0 auto",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    height: 72,
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: 14,
  },
  brandInitials: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 22,
    fontWeight: 700,
    color: "var(--gold)",
    border: "2px solid var(--gold)",
    padding: "4px 10px",
    letterSpacing: 2,
  },
  brandTitle: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 17,
    fontWeight: 600,
    color: "var(--text-primary)",
    lineHeight: 1.2,
  },
  brandSub: {
    fontSize: 12,
    color: "var(--text-secondary)",
    marginTop: 2,
  },
  nav: {
    display: "flex",
    gap: 8,
  },
  navLink: {
    padding: "6px 16px",
    fontSize: 14,
    fontWeight: 500,
    color: "var(--text-secondary)",
    borderRadius: 4,
    border: "1px solid transparent",
    transition: "all 0.15s",
  },
  navLinkActive: {
    color: "var(--gold)",
    border: "1px solid var(--gold-muted)",
    backgroundColor: "rgba(212,175,55,0.08)",
  },
  main: {
    flex: 1,
    maxWidth: 960,
    width: "100%",
    margin: "0 auto",
    padding: "40px 24px",
  },
  footer: {
    textAlign: "center",
    padding: "16px 24px",
    fontSize: 13,
    color: "var(--text-secondary)",
    borderTop: "1px solid var(--navy-border)",
  },
};
