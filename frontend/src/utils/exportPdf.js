import jsPDF from "jspdf";

/* ── Palette (dark-safe, prints well on white) ── */
const C = {
  gold:       [180, 145, 40],
  goldLight:  [212, 175, 55],
  navy:       [11,  17,  32],
  success:    [22,  163, 74],
  error:      [220, 38,  38],
  gray1:      [15,  23,  42],   // headings
  gray2:      [71,  85,  105],  // body
  gray3:      [148, 163, 184],  // muted
  border:     [221, 227, 239],
  successBg:  [240, 253, 244],
  errorBg:    [254, 242, 242],
  cardBg:     [248, 250, 252],
};

/* ── Helpers ── */
function drawLine(doc, y, color = C.border) {
  doc.setDrawColor(...color);
  doc.line(20, y, 190, y);
}

/**
 * Replaces Turkish characters with English equivalents to ensure 
 * compatibility with default PDF fonts (Helvetica/Arial).
 */
function normalize(text) {
  if (typeof text !== "string") return text;
  return text
    .replace(/Ğ/g, "G").replace(/ğ/g, "g")
    .replace(/Ü/g, "U").replace(/ü/g, "u")
    .replace(/Ş/g, "S").replace(/ş/g, "s")
    .replace(/İ/g, "I").replace(/ı/g, "i")
    .replace(/Ö/g, "O").replace(/ö/g, "o")
    .replace(/Ç/g, "C").replace(/ç/g, "c");
}

function tag(doc, x, y, text, pass) {
  const bg   = pass ? C.successBg : C.errorBg;
  const fg   = pass ? C.success   : C.error;
  const bord = pass ? [187, 247, 208] : [254, 202, 202];
  const w = doc.getTextWidth(text) + 10;
  doc.setFillColor(...bg);
  doc.setDrawColor(...bord);
  doc.roundedRect(x, y - 5, w, 7, 2, 2, "FD");
  doc.setTextColor(...fg);
  doc.setFontSize(7.5);
  doc.setFont("helvetica", "bold");
  doc.text(text, x + 5, y);
  return w + 4;
}

function statBox(doc, x, y, w, label, value, unit, ok) {
  const fg = ok ? C.success : C.error;
  const bg = ok ? C.successBg : C.errorBg;
  const bd = ok ? [187,247,208] : [254,202,202];
  doc.setFillColor(...bg);
  doc.setDrawColor(...bd);
  doc.roundedRect(x, y, w, 28, 3, 3, "FD");
  doc.setFontSize(20);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...fg);
  doc.text(String(value), x + w / 2, y + 12, { align: "center" });
  doc.setFontSize(7);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...C.gray3);
  doc.text(unit, x + w / 2, y + 18, { align: "center" });
  doc.setFontSize(7.5);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...C.gray2);
  doc.text(label.toUpperCase(), x + w / 2, y + 25, { align: "center" });
}

function sectionHeading(doc, y, icon, title) {
  doc.setFontSize(9);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...C.gold);
  doc.text(`${icon}  ${title.toUpperCase()}`, 20, y);
  drawLine(doc, y + 2, C.gold);
  return y + 8;
}

function bulletList(doc, items, startY, color = C.gray1, fontSize = 9) {
  let y = startY;
  doc.setFontSize(fontSize);
  doc.setFont("helvetica", "normal");
  for (const item of items) {
    if (y > 270) { doc.addPage(); y = 20; }
    doc.setTextColor(...C.gold);
    doc.text("-", 22, y);
    doc.setTextColor(...color);
    const lines = doc.splitTextToSize(normalize(item), 160);
    doc.text(lines, 27, y);
    y += lines.length * (fontSize * 0.5) + 3;
  }
  return y;
}

/* ── Main export function ── */
/**
 * Generates an English-only graduation analysis PDF.
 * Turkish characters are transliterated to ensure readability without custom fonts.
 */
export async function exportToPdf(data) {
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const pageW = 210;
  const margin = 20;
  const contentW = pageW - margin * 2;
  let y = 0;

  const graduated = data.is_graduated;
  const verdicts  = data.agent_verdicts || {};
  const reportId  = Math.random().toString(36).substring(2, 10).toUpperCase();

  /* ════════ HEADER BAND ════════ */
  doc.setFillColor(...C.navy);
  doc.rect(0, 0, pageW, 42, "F");

  // Title
  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.setTextColor(232, 234, 240);
  doc.text("Virtual Academic Advisor", 14, 16);

  doc.setFontSize(8.5);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...C.gray3);
  doc.text("Galatasaray University - Computer Engineering Department", 14, 23);

  // Date
  const dateStr = new Date().toLocaleDateString("en-GB", {
    day: "2-digit", month: "long", year: "numeric",
  });
  doc.setFontSize(8);
  doc.setTextColor(...C.gray3);
  doc.text(dateStr, pageW - margin, 10, { align: "right" });
  doc.setFontSize(6.5);
  doc.text(`REF: ${reportId}`, pageW - margin, 14, { align: "right" });

  // Status badge in header
  const statusLabel = graduated ? "ELIGIBLE FOR GRADUATION" : "MISSING CONDITIONS";
  doc.setFillColor(...(graduated ? C.success : C.error));
  const badgeW = doc.getTextWidth(statusLabel) + 14;
  doc.roundedRect(pageW - margin - badgeW, 28, badgeW, 9, 2, 2, "F");
  doc.setFontSize(8);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(255, 255, 255);
  doc.text(statusLabel, pageW - margin - badgeW / 2, 34, { align: "center" });

  y = 50;

  /* ════════ STUDENT INFO ════════ */
  if (data.student_name || data.student_number) {
    doc.setFontSize(13);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...C.gray1);
    doc.text(normalize(data.student_name || "-"), margin, y);

    doc.setFontSize(9);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...C.gray2);
    doc.text(normalize(data.student_number || ""), margin, y + 6);
    y += 14;
    drawLine(doc, y);
    y += 6;
  }

  /* ════════ REPORT TEXT ════════ */
  if (data.report_text) {
    doc.setFontSize(10);
    doc.setFont("helvetica", "italic");
    doc.setTextColor(...C.gray2);
    const lines = doc.splitTextToSize(`"${normalize(data.report_text)}"`, contentW);
    doc.text(lines, margin, y);
    y += lines.length * 5 + 6;
    drawLine(doc, y);
    y += 8;
  }

  /* ════════ STAT BOXES ════════ */
  const boxW = (contentW - 9) / 4;
  statBox(doc, margin,                    y, boxW, "Cumulative GPA", data.gpa?.toFixed(2) ?? "-", "/ 4.00", (data.gpa ?? 0) >= 2.0);
  statBox(doc, margin + boxW + 3,         y, boxW, "Total ECTS",       data.transcript_total_ects ?? "-", `/ ${data.required_ects ?? 240}`, (data.transcript_total_ects ?? 0) >= (data.required_ects ?? 240));
  statBox(doc, margin + (boxW + 3) * 2,   y, boxW, "Mandatory Courses", data.completed_courses?.length ?? 0, "/ 43", (data.completed_courses?.length ?? 0) >= 43);
  statBox(doc, margin + (boxW + 3) * 3,   y, boxW, "Missing Conditions",    data.missing_conditions?.length ?? 0, "", !(data.missing_conditions?.length));
  y += 36;

  /* ════════ MISSING CONDITIONS ════════ */
  if (data.missing_conditions?.length > 0) {
    y = sectionHeading(doc, y, "!", "Unmet Conditions");
    y = bulletList(doc, data.missing_conditions, y, C.error, 9);
    y += 4;
  }

  /* ════════ AGENT VERDICTS ════════ */
  if (Object.keys(verdicts).length > 0) {
    y = sectionHeading(doc, y, "AI", "Agent Evaluations");

    const agentLabels = { 
      CourseVerifier: "Course Verifier", 
      ECTSVerifier: "ECTS Verifier", 
      RequirementsChecker: "Requirements Checker", 
      MasterAgent: "Master Agent" 
    };

    for (const [, v] of Object.entries(verdicts)) {
      if (y > 255) { doc.addPage(); y = 20; }
      const pass = v.verdict === "pass";
      const rowBg = pass ? C.successBg : C.errorBg;
      const rowBd = pass ? [187,247,208] : [254,202,202];

      const labelText = agentLabels[v.agent] || v.agent;
      const stmtLines = doc.splitTextToSize(normalize(v.statement || ""), contentW - 50);
      const cardH = 12 + stmtLines.length * 4.5 + (v.issues?.length ? v.issues.length * 5 + 4 : 0);

      doc.setFillColor(...rowBg);
      doc.setDrawColor(...rowBd);
      doc.roundedRect(margin, y, contentW, cardH, 2, 2, "FD");

      doc.setFontSize(9.5);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(...C.gray1);
      doc.text(labelText, margin + 4, y + 7);

      tag(doc, margin + contentW - 30, y + 5.5, pass ? "PASS" : "FAIL", pass);

      doc.setFontSize(8.5);
      doc.setFont("helvetica", "italic");
      doc.setTextColor(...C.gray2);
      doc.text(stmtLines, margin + 4, y + 13);
      let innerY = y + 13 + stmtLines.length * 4.5;

      if (v.issues?.length) {
        for (const issue of v.issues) {
          const iLines = doc.splitTextToSize(`- ${normalize(issue)}`, contentW - 12);
          doc.setFontSize(8);
          doc.setFont("helvetica", "normal");
          doc.setTextColor(...C.error);
          doc.text(iLines, margin + 4, innerY + 2);
          innerY += iLines.length * 4 + 2;
        }
      }
      y += cardH + 4;
    }
    y += 2;
  }

  /* ════════ COURSE LISTS ════════ */
  if (y > 240) { doc.addPage(); y = 20; }
  y = sectionHeading(doc, y, "V", "Completed Mandatory Courses");

  const completedMandatory = (data.completed_mandatory_courses ?? []);
  if (completedMandatory.length > 0) {
    y = bulletList(doc, completedMandatory, y, C.success, 8);
  } else {
    doc.setFontSize(8.5);
    doc.setFont("helvetica", "italic");
    doc.setTextColor(...C.gray3);
    doc.text("None found", margin + 4, y);
    y += 8;
  }
  y += 4;

  if (y > 240) { doc.addPage(); y = 20; }
  y = sectionHeading(doc, y, "X", "Missing Mandatory Courses");

  const missing = data.missing_courses ?? [];
  if (missing.length > 0) {
    y = bulletList(doc, missing, y, C.error, 8);
  } else {
    doc.setFontSize(8.5);
    doc.setFont("helvetica", "italic");
    doc.setTextColor(...C.success);
    doc.text("All mandatory courses completed", margin + 4, y);
    y += 8;
  }

  /* ════════ SIGNATURE SECTION ════════ */
  y += 15;
  if (y > 250) { doc.addPage(); y = 30; }
  
  const sigX = pageW - margin - 50;
  doc.setFontSize(8);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...C.gray1);
  doc.text("Academic Advisor Signature", sigX, y);
  
  doc.setDrawColor(...C.gray3);
  doc.setLineWidth(0.2);
  doc.line(sigX, y + 8, sigX + 50, y + 8);
  
  doc.setFontSize(7);
  doc.setFont("helvetica", "italic");
  doc.setTextColor(...C.gray3);
  doc.text("Generated by GSU Virtual Advisor", sigX, y + 12);

  /* ════════ FOOTER ════════ */
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    drawLine(doc, 285, C.border);
    doc.setFontSize(7.5);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...C.gray3);
    doc.text("GSU Virtual Academic Advisor - Graduation Analysis System", margin, 290);
    doc.setFontSize(6);
    doc.text("CONFIDENTIAL: This document is for advisory purposes only and does not constitute an official transcript or diploma.", margin, 294);
    doc.setFontSize(7.5);
    doc.text(`${i} / ${pageCount}`, pageW - margin, 290, { align: "right" });
  }

  /* ════════ SAVE ════════ */
  const safeName = (data.student_number || data.student_name || "transcript")
    .replace(/\s+/g, "_")
    .replace(/[^a-zA-Z0-9_-]/g, "");
  doc.save(`GSU_Analysis_${safeName}.pdf`);
}
