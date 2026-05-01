import { createContext, useContext, useState, useEffect } from "react";
import t from "../i18n";

const LangContext = createContext(null);

export function LangProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem("lang") || "tr");

  useEffect(() => {
    localStorage.setItem("lang", lang);
    document.documentElement.setAttribute("lang", lang);
  }, [lang]);

  const toggle = () => setLang((l) => (l === "tr" ? "en" : "tr"));

  return (
    <LangContext.Provider value={{ lang, toggle, t: t[lang] }}>
      {children}
    </LangContext.Provider>
  );
}

export function useLang() {
  return useContext(LangContext);
}
