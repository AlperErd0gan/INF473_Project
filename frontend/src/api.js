const BASE_URL = "http://localhost:8000";

export async function uploadTranscript(text) {
  const res = await fetch(`${BASE_URL}/transcripts/upload`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Yükleme hatası");
  return res.json();
}

export async function analyzeTranscript(transcriptId, lang = "tr") {
  const res = await fetch(`${BASE_URL}/analysis/analyze/${transcriptId}?lang=${lang}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Analiz hatası");
  return res.json();
}

export async function getAnalysis(analysisId) {
  const res = await fetch(`${BASE_URL}/analysis/${analysisId}`);
  if (!res.ok) throw new Error((await res.json()).detail || "Analiz bulunamadı");
  return res.json();
}

export async function getHistory() {
  const res = await fetch(`${BASE_URL}/analysis/history`);
  if (!res.ok) throw new Error("Geçmiş yüklenemedi");
  return res.json();
}

export async function deleteAnalysis(analysisId) {
  const res = await fetch(`${BASE_URL}/analysis/${analysisId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Silme hatası");
  return res.json();
}
