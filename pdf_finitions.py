import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_pdf_finitions_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ===== S1 : charges de calcul dans la zone vide a gauche de la perspective =====
remplacer('''      doc.text("Perspective du projet", persX + persW / 2, y + persH + 4, { align: "center" });
      y += persH + 10;''',
'''      doc.text("Perspective du projet", persX + persW / 2, y + persH + 4, { align: "center" });
      // Charges de calcul dans la zone gauche
      if (zoneInfo) {
        let yC = y + 4;
        doc.setFontSize(7);
        doc.setFont("helvetica", "bold");
        doc.setTextColor(...C_GRIS);
        doc.text("CHARGES DE CALCUL", margin, yC);
        doc.setLineWidth(0.3);
        doc.setDrawColor(...C_OR);
        doc.line(margin, yC + 1.5, margin + 25, yC + 1.5);
        yC += 7;
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8.5);
        doc.setTextColor(...C_TEXTE);
        const skPdf = (zoneInfo.skAltitude === null || zoneInfo.skAltitude === undefined) ? zoneInfo.sk : zoneInfo.skAltitude;
        const lignesCharges = [
          "Zone de neige " + (zoneInfo.neige || "-") + "  -  sk " + skPdf + " kN/m2",
          "Zone de vent " + (zoneInfo.vent || "-") + "  -  qb " + zoneInfo.qb + " kN/m2",
          "Zone sismique " + (zoneInfo.sismique || "-") + "  -  " + zoneInfo.ag + " g",
          "Dimensionnement selon Eurocode 5",
          "(EN 1990 / 1991 / 1995)",
        ];
        lignesCharges.forEach((lc) => { doc.text(lc, margin, yC); yC += 5.5; });
      }
      y += persH + 10;''', "S1")

# ===== S2 : vues de fin en pleine page PAYSAGE =====
remplacer('''  // ============ VUES 3D PLEINE PAGE (a la suite du devis) ============
  if (viewsPdf) {
    const vuesFin = [
      { img: viewsPdf.face, titre: "Vue de face" },
      { img: viewsPdf.cote, titre: "Vue de cote" },
    ];
    vuesFin.forEach((v) => {
      if (v.img === undefined || v.img === null) return;
      doc.addPage();
      doc.setFontSize(11);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(...C_TEXTE);
      doc.text(v.titre, margin, 22);
      doc.setLineWidth(0.4);
      doc.setDrawColor(...C_OR);
      doc.line(margin, 24.5, margin + 30, 24.5);
      const imgPleineW = pageW - 2 * margin;
      const imgPleineH = imgPleineW * 0.75;
      doc.addImage(v.img, "PNG", margin, 32, imgPleineW, imgPleineH);
    });
  }''',
'''  // ============ VUES 3D PLEINE PAGE PAYSAGE (a la suite du devis) ============
  if (viewsPdf) {
    const vuesFin = [
      { img: viewsPdf.face, titre: "Vue de face" },
      { img: viewsPdf.cote, titre: "Vue de cote" },
    ];
    vuesFin.forEach((v) => {
      if (v.img === undefined || v.img === null) return;
      doc.addPage("a4", "landscape");
      const pwV = doc.internal.pageSize.getWidth();
      const phV = doc.internal.pageSize.getHeight();
      doc.setFontSize(11);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(...C_TEXTE);
      doc.text(v.titre, margin, 20);
      doc.setLineWidth(0.4);
      doc.setDrawColor(...C_OR);
      doc.line(margin, 22.5, margin + 30, 22.5);
      let imgH2 = phV - 50;
      let imgW2 = imgH2 / 0.75;
      if (imgW2 > pwV - 2 * margin) { imgW2 = pwV - 2 * margin; imgH2 = imgW2 * 0.75; }
      doc.addImage(v.img, "PNG", (pwV - imgW2) / 2, 27, imgW2, imgH2);
    });
  }''', "S2")

# ===== S3 : pied de page adapte a l'orientation de chaque page =====
remplacer('''  const totalPages = doc.internal.getNumberOfPages();
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
  }''',
'''  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    const pwF = doc.internal.pageSize.getWidth();
    const phF = doc.internal.pageSize.getHeight();
    doc.setDrawColor(...C_GRIS_LIGHT);
    doc.setLineWidth(0.2);
    doc.line(margin, phF - 15, pwF - margin, phF - 15);

    doc.setFontSize(7);
    doc.setTextColor(...C_GRIS);
    doc.setFont("helvetica", "normal");
    doc.text("Genere par DEVIA - " + dateDevis, margin, phF - 10);
    doc.text(params.mentions || "Devis valable 30 jours", pwF / 2, phF - 10, { align: "center" });
    doc.text("Page " + i + "/" + totalPages, pwF - margin, phF - 10, { align: "right" });
  }''', "S3")

# ===== S4 : categories imposees a l'IA de generation =====
remplacer("""'\"postes\":[{\"categorie\":\"Charpente\",\"designation\":\"Exemple\",\"unite\":\"ml\",\"quantite\":10,\"prixUnitaireHT\":45,\"totalHT\":450}],' +""",
"""'\"postes\":[{\"categorie\":\"Etude|Charpente|Couverture|Etancheite|Quincaillerie|Bardage|Pose\",\"designation\":\"Exemple\",\"unite\":\"ml\",\"quantite\":10,\"prixUnitaireHT\":45,\"totalHT\":450}],' +
\"REGLE CATEGORIES : chaque poste porte une categorie parmi Etude, Charpente, Couverture, Etancheite, Quincaillerie, Bardage, Pose. Repartis finement : ecran sous-toiture et membranes en Etancheite, sabots/connecteurs/visserie en Quincaillerie, main d'oeuvre en Pose, calculs et plans en Etude. \" +""", "S4")

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : charges dans l en-tete, vues paysage, pied de page adaptatif, categories imposees.")
