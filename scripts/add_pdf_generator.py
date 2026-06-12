#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Modif 3 : Bouton PDF fonctionnel
- Import jsPDF + jspdf-autotable
- Fonction generatePDF() qui cree un PDF pro vectoriel
- Brancher au bouton existant
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_pdf_gen"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter imports jsPDF + autoTable apres UserMenu
# ================================================================

old_imports_end = 'import UserMenu from "./src/components/UserMenu.jsx";'

new_imports = '''import UserMenu from "./src/components/UserMenu.jsx";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";'''

if "import jsPDF" in content:
    print("[INFO] Imports jsPDF deja presents")
elif old_imports_end in content:
    content = content.replace(old_imports_end, new_imports, 1)
    print("[OK] Imports jsPDF + autoTable ajoutes")
    modifs += 1
else:
    print("[ERREUR] Ligne UserMenu non trouvee")
    sys.exit(1)

# ================================================================
# MOD 2 : Ajouter la fonction generatePDF() apres T (config theme)
# Position : juste avant ZONES_DB
# ================================================================

old_zones_marker = 'const ZONES_DB = {'

new_with_pdf_func = '''// ================================================================
// GENERATEUR PDF PRO
// ================================================================
function generatePDF(result, params, zoneInfo, nomProjet) {
  const doc = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4"
  });

  const pageW = 210; // largeur A4 mm
  const pageH = 297; // hauteur A4 mm
  const margin = 15;
  let y = 0; // position verticale courante

  // Couleurs
  const C_OR = [240, 192, 64];        // or DEVIA
  const C_NOIR = [25, 28, 38];        // noir profond
  const C_TEXTE = [44, 44, 44];       // texte principal
  const C_GRIS = [120, 120, 130];     // gris secondaire
  const C_GRIS_LIGHT = [220, 220, 225]; // gris clair (separateurs)

  // ============ EN-TETE BANDEAU NOIR ============
  doc.setFillColor(...C_NOIR);
  doc.rect(0, 0, pageW, 45, "F");

  // Logo DEVIA (texte stylise)
  doc.setTextColor(...C_OR);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  doc.text("DEVIA", margin, 18);
  doc.setFontSize(8);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(180, 180, 190);
  doc.text("Devis charpente IA", margin, 23);

  // Bloc droit : numero devis + date
  const numDevis = "DEV-" + new Date().getFullYear() + "-" + String(Date.now()).slice(-4);
  const dateDevis = new Date().toLocaleDateString("fr-FR");
  const dateValid = new Date(Date.now() + 30 * 24 * 3600 * 1000).toLocaleDateString("fr-FR");

  doc.setTextColor(255, 255, 255);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.text("DEVIS " + numDevis, pageW - margin, 14, { align: "right" });
  doc.setFontSize(8);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(200, 200, 210);
  doc.text("Date : " + dateDevis, pageW - margin, 22, { align: "right" });
  doc.text("Valide jusqu'au : " + dateValid, pageW - margin, 28, { align: "right" });

  // Ligne or sous bandeau
  doc.setDrawColor(...C_OR);
  doc.setLineWidth(0.8);
  doc.line(0, 45, pageW, 45);

  y = 55;

  // ============ INFOS ENTREPRISE (gauche) + CLIENT (droite) ============
  doc.setTextColor(...C_GRIS);
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text("ENTREPRISE", margin, y);
  doc.text("CLIENT / PROJET", pageW / 2 + 5, y);

  doc.setLineWidth(0.3);
  doc.setDrawColor(...C_OR);
  doc.line(margin, y + 1.5, margin + 22, y + 1.5);
  doc.line(pageW / 2 + 5, y + 1.5, pageW / 2 + 5 + 30, y + 1.5);

  y += 8;
  doc.setTextColor(...C_TEXTE);
  doc.setFontSize(10);
  doc.setFont("helvetica", "bold");
  doc.text(params.entreprise || "Non renseigne", margin, y);

  doc.setFontSize(9);
  doc.setFont("helvetica", "bold");
  const projetDesc = result.projet && result.projet.description ? result.projet.description : (nomProjet || "Devis charpente");
  const projetLines = doc.splitTextToSize(projetDesc, 80);
  doc.text(projetLines, pageW / 2 + 5, y);

  y += 6;
  doc.setFontSize(8);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...C_GRIS);

  if (params.adresse) {
    const adrLines = doc.splitTextToSize(params.adresse, 80);
    doc.text(adrLines, margin, y);
    y += adrLines.length * 4;
  }
  if (params.siret) {
    doc.text("SIRET : " + params.siret, margin, y);
    y += 4;
  }

  // Bloc client : infos projet
  let yClient = y - (params.siret ? 4 : 0) - (params.adresse ? 4 : 0);
  doc.setFontSize(8);
  doc.setTextColor(...C_GRIS);
  if (result.projet) {
    if (result.projet.commune) {
      doc.text("Chantier : " + result.projet.commune, pageW / 2 + 5, yClient);
      yClient += 4;
    }
    if (result.projet.longueur && result.projet.largeur) {
      doc.text("Dimensions : " + result.projet.longueur + " x " + result.projet.largeur + " m", pageW / 2 + 5, yClient);
      yClient += 4;
    }
    if (result.projet.surface) {
      doc.text("Surface : " + result.projet.surface + " m²", pageW / 2 + 5, yClient);
      yClient += 4;
    }
    if (result.projet.pente) {
      doc.text("Pente : " + result.projet.pente + "°", pageW / 2 + 5, yClient);
      yClient += 4;
    }
  }

  y = Math.max(y, yClient) + 8;

  // ============ TABLEAU DES POSTES ============
  const postes = result.postes || [];
  const tableBody = postes.map(p => [
    p.designation || "",
    p.quantite ? String(p.quantite) : "—",
    p.unite || "—",
    p.prix_unitaire ? Number(p.prix_unitaire).toFixed(2) + " EUR" : "—",
    p.total ? Number(p.total).toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " EUR" : "—"
  ]);

  autoTable(doc, {
    startY: y,
    head: [["Designation", "Qte", "Unite", "PU HT", "Total HT"]],
    body: tableBody,
    theme: "striped",
    styles: {
      font: "helvetica",
      fontSize: 9,
      cellPadding: 3,
      textColor: C_TEXTE,
      lineColor: C_GRIS_LIGHT,
      lineWidth: 0.1
    },
    headStyles: {
      fillColor: C_NOIR,
      textColor: C_OR,
      fontStyle: "bold",
      fontSize: 9,
      cellPadding: 4
    },
    alternateRowStyles: {
      fillColor: [248, 248, 250]
    },
    columnStyles: {
      0: { cellWidth: 80 },
      1: { cellWidth: 18, halign: "right" },
      2: { cellWidth: 18, halign: "center" },
      3: { cellWidth: 30, halign: "right" },
      4: { cellWidth: 34, halign: "right", fontStyle: "bold" }
    },
    margin: { left: margin, right: margin }
  });

  y = doc.lastAutoTable.finalY + 6;

  // ============ ESTIMATION TEMPS (si presente) ============
  if (result.temps_fabrication_h !== undefined || result.temps_pose_h !== undefined) {
    const fab = Number(result.temps_fabrication_h) || 0;
    const pose = Number(result.temps_pose_h) || 0;
    const totalH = fab + pose;
    const jours = Math.ceil(totalH / 8);

    // Verifier si on a la place sur la page
    if (y > pageH - 60) { doc.addPage(); y = 20; }

    doc.setFillColor(248, 248, 250);
    doc.setDrawColor(...C_GRIS_LIGHT);
    doc.setLineWidth(0.2);
    doc.roundedRect(margin, y, pageW - 2 * margin, 22, 2, 2, "FD");

    doc.setTextColor(...C_TEXTE);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9);
    doc.text("Estimation temps", margin + 4, y + 6);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(...C_GRIS);
    doc.text("Fabrication atelier : ", margin + 4, y + 13);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...C_TEXTE);
    doc.text(fab + " h", margin + 38, y + 13);

    doc.setFont("helvetica", "normal");
    doc.setTextColor(...C_GRIS);
    doc.text("Pose chantier : ", margin + 60, y + 13);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...C_TEXTE);
    doc.text(pose + " h", margin + 88, y + 13);

    doc.setFont("helvetica", "normal");
    doc.setTextColor(...C_GRIS);
    doc.text("Total : ", margin + 110, y + 13);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...C_OR);
    doc.text(totalH + " h (" + jours + " jour" + (jours > 1 ? "s" : "") + ")", margin + 122, y + 13);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(7);
    doc.setTextColor(...C_GRIS);
    doc.text("Estimation basee sur ratios standards charpente. Sur 8h/jour.", margin + 4, y + 19);

    y += 28;
  }

  // ============ TOTAUX (bloc droit aligne) ============
  if (y > pageH - 50) { doc.addPage(); y = 20; }

  const totaux = result.totaux || {};
  const xTotaux = pageW - margin - 70;

  doc.setDrawColor(...C_GRIS_LIGHT);
  doc.setLineWidth(0.2);
  doc.line(xTotaux, y, pageW - margin, y);

  y += 6;
  doc.setTextColor(...C_TEXTE);
  doc.setFontSize(10);
  doc.setFont("helvetica", "normal");
  doc.text("Total HT", xTotaux, y);
  doc.setFont("helvetica", "bold");
  const totalHTstr = (totaux.totalHT || 0).toLocaleString("fr-FR", { minimumFractionDigits: 2 }) + " EUR";
  doc.text(totalHTstr, pageW - margin, y, { align: "right" });

  y += 6;
  doc.setFont("helvetica", "normal");
  doc.text("TVA " + (params.tva || 20) + "%", xTotaux, y);
  doc.setFont("helvetica", "bold");
  const tvaStr = (totaux.tva || 0).toLocaleString("fr-FR", { minimumFractionDigits: 2 }) + " EUR";
  doc.text(tvaStr, pageW - margin, y, { align: "right" });

  y += 4;
  doc.setDrawColor(...C_OR);
  doc.setLineWidth(0.5);
  doc.line(xTotaux, y, pageW - margin, y);

  y += 8;
  doc.setFillColor(...C_OR);
  doc.rect(xTotaux, y - 5, pageW - margin - xTotaux, 9, "F");
  doc.setTextColor(...C_NOIR);
  doc.setFontSize(11);
  doc.setFont("helvetica", "bold");
  doc.text("TOTAL TTC", xTotaux + 2, y + 1);
  const totalTTCstr = (totaux.totalTTC || 0).toLocaleString("fr-FR", { minimumFractionDigits: 2 }) + " EUR";
  doc.text(totalTTCstr, pageW - margin - 2, y + 1, { align: "right" });

  y += 12;

  // ============ NOTES ============
  if (result.notes && result.notes.length > 0) {
    if (y > pageH - 40) { doc.addPage(); y = 20; }

    doc.setTextColor(...C_GRIS);
    doc.setFontSize(7);
    doc.setFont("helvetica", "bold");
    doc.text("NOTES", margin, y);
    doc.setLineWidth(0.3);
    doc.setDrawColor(...C_OR);
    doc.line(margin, y + 1.5, margin + 12, y + 1.5);

    y += 7;
    doc.setFontSize(9);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...C_TEXTE);
    result.notes.forEach(note => {
      if (y > pageH - 25) { doc.addPage(); y = 20; }
      const lines = doc.splitTextToSize("- " + note, pageW - 2 * margin);
      doc.text(lines, margin, y);
      y += lines.length * 4 + 1;
    });
  }

  // ============ PIED DE PAGE (sur chaque page) ============
  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setDrawColor(...C_GRIS_LIGHT);
    doc.setLineWidth(0.2);
    doc.line(margin, pageH - 15, pageW - margin, pageH - 15);

    doc.setFontSize(7);
    doc.setTextColor(...C_GRIS);
    doc.setFont("helvetica", "normal");
    doc.text("Genere par DEVIA - " + dateDevis, margin, pageH - 10);
    doc.text(params.mentions || "Devis valable 30 jours", pageW / 2, pageH - 10, { align: "center" });
    doc.text("Page " + i + "/" + totalPages, pageW - margin, pageH - 10, { align: "right" });
  }

  // ============ TELECHARGER ============
  const fileName = "Devis_" + (params.entreprise || "DEVIA").replace(/\\s+/g, "_") + "_" + numDevis + ".pdf";
  doc.save(fileName);
}

const ZONES_DB = {'''

if "function generatePDF(" in content:
    print("[INFO] Fonction generatePDF deja presente")
elif old_zones_marker in content:
    content = content.replace(old_zones_marker, new_with_pdf_func, 1)
    print("[OK] Fonction generatePDF() ajoutee (avec design pro)")
    modifs += 1
else:
    print("[ERREUR] Marqueur ZONES_DB non trouve")
    sys.exit(1)

# ================================================================
# MOD 3 : Brancher le bouton PDF a generatePDF
# ================================================================

old_pdf_button = '''                  <button style={btnPrimary}>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                      </svg>
                      PDF
                    </span>
                  </button>'''

new_pdf_button = '''                  <button style={btnPrimary} onClick={() => generatePDF(result, params, zoneInfo, nomProjet)}>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                      </svg>
                      PDF
                    </span>
                  </button>'''

if "onClick={() => generatePDF" in content:
    print("[INFO] Bouton PDF deja branche")
elif old_pdf_button in content:
    content = content.replace(old_pdf_button, new_pdf_button, 1)
    print("[OK] Bouton PDF branche a generatePDF()")
    modifs += 1
else:
    print("[ERREUR] Bouton PDF non trouve exactement")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Imports jsPDF + autoTable ajoutes")
print("  2. Fonction generatePDF() ajoutee (style pro)")
print("  3. Bouton 'PDF' branche au generateur")
print()
print("STRUCTURE DU PDF :")
print("  - En-tete bandeau noir + or DEVIA (logo + n° devis)")
print("  - Bloc Entreprise (gauche) + Client/Projet (droite)")
print("  - Tableau des postes (vectoriel, recherchable)")
print("  - Estimation temps (si presente)")
print("  - Totaux HT / TVA / TTC (bandeau or)")
print("  - Notes (si presentes)")
print("  - Pied de page (numerotation, mentions)")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
