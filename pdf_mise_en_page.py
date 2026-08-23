import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_pdf_mep_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ===== R1 : en-tete -> perspective seule, a droite =====
remplacer('''  // ============ VUES 3D ============
  if (view3DParams) {
    try {
      const views = capture3DViews(view3DParams);

      // Verifier qu'on a la place sur la page
      if (y > pageH - 90) { doc.addPage(); y = 20; }

      // Titre section
      doc.setTextColor(...C_GRIS);
      doc.setFontSize(7);
      doc.setFont("helvetica", "bold");
      doc.text("VUES DU PROJET", margin, y);
      doc.setLineWidth(0.3);
      doc.setDrawColor(...C_OR);
      doc.line(margin, y + 1.5, margin + 25, y + 1.5);

      y += 6;

      // 3 vues alignees horizontalement
      const viewW = (pageW - 2 * margin - 8) / 3; // 3 colonnes + 2 gaps de 4
      const viewH = viewW * 0.65; // ratio 800x600 -> 4:3

      // FACE
      try {
        doc.addImage(views.face, "PNG", margin, y, viewW, viewH);
      } catch(e) { console.warn("Erreur vue face :", e); }

      // COTE
      try {
        doc.addImage(views.cote, "PNG", margin + viewW + 4, y, viewW, viewH);
      } catch(e) { console.warn("Erreur vue cote :", e); }

      // PERSPECTIVE
      try {
        doc.addImage(views.perspective, "PNG", margin + 2 * (viewW + 4), y, viewW, viewH);
      } catch(e) { console.warn("Erreur vue perspective :", e); }

      // Labels sous chaque vue
      y += viewH + 4;
      doc.setFontSize(7);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(...C_GRIS);
      doc.text("Vue de face", margin + viewW/2, y, { align: "center" });
      doc.text("Vue de cote", margin + viewW + 4 + viewW/2, y, { align: "center" });
      doc.text("Perspective", margin + 2 * (viewW + 4) + viewW/2, y, { align: "center" });

      y += 8;
    } catch (e) {
      console.error("Erreur capture 3D :", e);
    }
  }''',
'''  // ============ VUE 3D EN-TETE : perspective seule, en haut a droite ============
  let viewsPdf = null;
  if (view3DParams) {
    try {
      viewsPdf = capture3DViews(view3DParams);
      const persW = 78;
      const persH = persW * 0.75; // ratio 800x600
      if (y > pageH - (persH + 20)) { doc.addPage(); y = 20; }
      const persX = pageW - margin - persW;
      doc.addImage(viewsPdf.perspective, "PNG", persX, y, persW, persH);
      doc.setFontSize(7);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(...C_GRIS);
      doc.text("Perspective du projet", persX + persW / 2, y + persH + 4, { align: "center" });
      y += persH + 10;
    } catch (e) {
      console.error("Erreur capture 3D :", e);
    }
  }''', "R1")

# ===== R2a : postes regroupes par categorie, prix au sous-total seulement =====
remplacer('''  const postes = result.postes || [];
  const posteRow = (p) => [
    (p.designation || "").replace(/^Ouvrage \\d+ - /, ""),
    p.quantite ? String(p.quantite) : "-",
    p.unite || "-",
    p.prixUnitaireHT ? Number(p.prixUnitaireHT).toFixed(2) + " EUR" : "-",
    p.totalHT ? fmtEUR(p.totalHT) : "-"
  ];
  let tableBody;
  if (result._ouvrages && result._ouvrages.length > 1) {
    tableBody = [];
    result._ouvrages.forEach((ouv, oi) => {
      const desc = (ouv.projet && ouv.projet.description) || "";
      tableBody.push([{
        content: "OUVRAGE " + (oi + 1) + (desc ? " - " + desc : ""),
        colSpan: 5,
        styles: { fillColor: [240, 192, 64], textColor: [25, 28, 38], fontStyle: "bold", fontSize: 8.5 }
      }]);
      (ouv.postes || []).forEach(p => tableBody.push(posteRow(p)));
      const sousHT = (ouv.postes || []).reduce((acc, p) => acc + (Number(p.totalHT) || 0), 0);
      tableBody.push([
        { content: "Sous-total Ouvrage " + (oi + 1), colSpan: 4, styles: { halign: "right", fontStyle: "bold", textColor: [90, 90, 100], fillColor: [245, 245, 247] } },
        { content: fmtEUR(sousHT), styles: { halign: "right", fontStyle: "bold", fillColor: [245, 245, 247] } }
      ]);
    });
  } else {
    tableBody = postes.map(posteRow);
  }''',
'''  const postes = result.postes || [];
  const ligneDetail = (p) => [
    (p.designation || "").replace(/^Ouvrage \\d+ - /, ""),
    p.quantite ? String(p.quantite) : "-",
    p.unite || "-",
    ""
  ];
  // Regroupe une liste de postes par categorie (ordre d'apparition conserve)
  const lignesParCategorie = (liste, corps) => {
    const ordre = [];
    const parCat = new Map();
    liste.forEach((p) => {
      const cat = p.categorie || "Autres";
      if (parCat.has(cat) === false) { parCat.set(cat, []); ordre.push(cat); }
      parCat.get(cat).push(p);
    });
    ordre.forEach((cat) => {
      const lignes = parCat.get(cat);
      corps.push([{
        content: cat.toUpperCase(),
        colSpan: 4,
        styles: { fillColor: [245, 245, 247], textColor: [90, 90, 100], fontStyle: "bold", fontSize: 8 }
      }]);
      lignes.forEach((p) => corps.push(ligneDetail(p)));
      const totalCat = lignes.reduce((acc, p) => acc + (Number(p.totalHT) || 0), 0);
      corps.push([
        { content: cat + " : ", colSpan: 3, styles: { halign: "right", fontStyle: "bold" } },
        { content: fmtEUR(totalCat), styles: { halign: "right", fontStyle: "bold" } }
      ]);
    });
  };
  let tableBody;
  if (result._ouvrages && result._ouvrages.length > 1) {
    tableBody = [];
    result._ouvrages.forEach((ouv, oi) => {
      const desc = (ouv.projet && ouv.projet.description) || "";
      tableBody.push([{
        content: "OUVRAGE " + (oi + 1) + (desc ? " - " + desc : ""),
        colSpan: 4,
        styles: { fillColor: [240, 192, 64], textColor: [25, 28, 38], fontStyle: "bold", fontSize: 8.5 }
      }]);
      lignesParCategorie(ouv.postes || [], tableBody);
      const sousHT = (ouv.postes || []).reduce((acc, p) => acc + (Number(p.totalHT) || 0), 0);
      tableBody.push([
        { content: "Sous-total Ouvrage " + (oi + 1), colSpan: 3, styles: { halign: "right", fontStyle: "bold", textColor: [25, 28, 38], fillColor: [250, 242, 214] } },
        { content: fmtEUR(sousHT), styles: { halign: "right", fontStyle: "bold", fillColor: [250, 242, 214] } }
      ]);
    });
  } else {
    tableBody = [];
    lignesParCategorie(postes, tableBody);
  }''', "R2a")

# ===== R2b : en-tete et colonnes du tableau (4 colonnes) =====
remplacer('''    head: [["Designation", "Qte", "Unite", "PU HT", "Total HT"]],''',
'''    head: [["Designation", "Qte", "Unite", "Montant HT"]],''', "R2b")

remplacer('''    columnStyles: {
      0: { cellWidth: 72 },
      1: { cellWidth: 16, halign: "right" },
      2: { cellWidth: 16, halign: "center" },
      3: { cellWidth: 36, halign: "right" },
      4: { cellWidth: 40, halign: "right", fontStyle: "bold" }
    },''',
'''    columnStyles: {
      0: { cellWidth: 96 },
      1: { cellWidth: 18, halign: "right" },
      2: { cellWidth: 22, halign: "center" },
      3: { cellWidth: 44, halign: "right", fontStyle: "bold" }
    },''', "R2c")

# ===== R3 : vues face et cote en pleine page A4 a la suite du devis =====
remplacer('''  // ============ PIED DE PAGE (sur chaque page) ============''',
'''  // ============ VUES 3D PLEINE PAGE (a la suite du devis) ============
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
  }

  // ============ PIED DE PAGE (sur chaque page) ============''', "R3")

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : perspective en haut a droite, prix par categorie, vues face/cote en pleine page.")
