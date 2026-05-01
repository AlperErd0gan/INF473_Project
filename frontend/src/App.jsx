import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { LangProvider } from "./contexts/LangContext";
import Layout from "./components/Layout";
import Upload from "./pages/Upload";
import Result from "./pages/Result";
import History from "./pages/History";

export default function App() {
  return (
    <LangProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Upload />} />
            <Route path="/result/:id" element={<Result />} />
            <Route path="/history" element={<History />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </LangProvider>
  );
}
