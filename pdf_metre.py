import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_pdf_metre_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ===== V1 : helper de rotation 90 dans la capture =====
remplacer('''  // ============ CAPTURE 3 VUES ============
  const views = {};''',
'''  // ============ CAPTURE 3 VUES ============
  const views = {};
  // Version pivotee de 90 degres du rendu courant (pour les pages pleine feuille)
  const tourner90 = () => {
    const src = renderer.domElement;
    const c2 = document.createElement("canvas");
    c2.width = src.height;
    c2.height = src.width;
    const ctx = c2.getContext("2d");
    ctx.translate(c2.width / 2, c2.height / 2);
    ctx.rotate(Math.PI / 2);
    ctx.drawImage(src, -src.width / 2, -src.height / 2);
    return c2.toDataURL("image/png");
  };''', "V1")

remplacer('''  views.face = renderer.domElement.toDataURL("image/png");''',
'''  views.face = renderer.domElement.toDataURL("image/png");
  views.faceRot = tourner90();''', "V2")

remplacer('''  views.cote = renderer.domElement.toDataURL("image/png");''',
'''  views.cote = renderer.domElement.toDataURL("image/png");
  views.coteRot = tourner90();''', "V3")

# ===== V4 : pages pleine feuille PORTRAIT avec 3D pivote et agrandi =====
remplacer('''  // ============ VUES 3D PLEINE PAGE PAYSAGE (a la suite du devis) ============
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
  }''',
'''  // ============ VUES 3D PLEINE PAGE : 3D pivote de 90 degres et agrandi ============
  if (viewsPdf) {
    const vuesFin = [
      { img: viewsPdf.faceRot || viewsPdf.face, titre: "Vue de face" },
      { img: viewsPdf.coteRot || viewsPdf.cote, titre: "Vue de cote" },
    ];
    vuesFin.forEach((v) => {
      if (v.img === undefined || v.img === null) return;
      doc.addPage();
      doc.setFontSize(11);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(...C_TEXTE);
      doc.text(v.titre, margin, 20);
      doc.setLineWidth(0.4);
      doc.setDrawColor(...C_OR);
      doc.line(margin, 22.5, margin + 30, 22.5);
      let imgW3 = pageW - 2 * margin;
      let imgH3 = imgW3 * (4 / 3);
      const dispo = pageH - 27 - 22;
      if (imgH3 > dispo) { imgH3 = dispo; imgW3 = imgH3 * 0.75; }
      doc.addImage(v.img, "PNG", (pageW - imgW3) / 2, 27, imgW3, imgH3);
    });
  }''', "V4")

# ===== M1 : helper module -> metre moteur en texte =====
remplacer('''function harmoniserSectionsDevis(parsed, sk, dS) {''',
'''// ================================================================
// METRE MOTEUR -> TEXTE : quantites reelles issues de la 3D, imposees a la generation
// ================================================================
function metreTexteDepuisParams(p) {
  try {
    const MAP_TYPE = { traditionnelle: "charpente_trad", fermette: "charpente_trad", monopente: "monopente", carport: "carport", hangar: "hangar", appentis: "appentis", "4_pans": "4_pans", terrasse: "terrasse", etage: "etage", balcon: "balcon", garde_corps: "garde_corps", sas: "sas_liaison" };
    const paramsCalc = {
      type_projet: p.type_projet || MAP_TYPE[p.type] || "charpente_trad",
      longueur: Number(p.longueur) || 8,
      largeur: Number(p.largeur) || 6,
      hauteur: Number(p.hauteur) || 3,
      pente: Number(p.pente) || 35,
      couverture: p.couverture || "tuile_terre",
      debord: p.debord || 0,
      murs: p.murs,
    };
    const tmp = new THREE.Group();
    const pre = buildScene3D(tmp, paramsCalc, { couverture: paramsCalc.couverture, mode: "technique" });
    tmp.traverse((obj) => { if (obj.isMesh && obj.geometry) obj.geometry.dispose(); });
    const agg = agregerMetre(pre.metre, pre.densiteBois || 450);
    if (agg === null || agg === undefined || (agg.groupes || []).length === 0) return "";
    const lignes = agg.groupes.map((g) => "- " + g.nom + " " + g.section[0] + "x" + g.section[1] + " mm : " + g.nombre + " piece(s), " + g.longueurTotale.toFixed(1) + " ml au total");
    return "METRE EXACT DU MOTEUR 3D (source de verite : utilise EXACTEMENT ces quantites pour les postes bois, n'en invente aucune) :\\n" + lignes.join("\\n");
  } catch (eMet) {
    return "";
  }
}

function harmoniserSectionsDevis(parsed, sk, dS) {''', "M1")

# ===== M2 : devis SOLO -> metre ajoute au message de generation =====
remplacer('''let userContent = finalParams.description || prompt || "Genere un devis pour ce projet de charpente.";''',
'''let userContent = finalParams.description || prompt || "Genere un devis pour ce projet de charpente.";
try {
  const texteMetre = metreTexteDepuisParams(finalParams);
  if (texteMetre) userContent += "\\n\\n" + texteMetre;
} catch (eM) { console.warn("[DEVIA] Metre moteur indisponible pour la generation", eM); }''', "M2")

# ===== M3 : devis MULTI -> metre par ouvrage =====
remplacer('''        const { systemPrompt, catalogSource } = buildDeviaPrompt(fp);
        catalogSourceGlobal = catalogSource;
        const { parsed, data } = await callDeviaIA(systemPrompt, fp.description);''',
'''        const { systemPrompt, catalogSource } = buildDeviaPrompt(fp);
        catalogSourceGlobal = catalogSource;
        let contenuOuvrage = fp.description || "Genere un devis pour cet ouvrage.";
        try {
          const texteMetreO = metreTexteDepuisParams(fp);
          if (texteMetreO) contenuOuvrage += "\\n\\n" + texteMetreO;
        } catch (eMO) { console.warn("[DEVIA] Metre moteur indisponible (ouvrage)", eMO); }
        const { parsed, data } = await callDeviaIA(systemPrompt, contenuOuvrage);''', "M3")

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : 3D pivote pleine page portrait + metre moteur impose a la generation (solo et multi).")
