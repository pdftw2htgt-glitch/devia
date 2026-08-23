import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_pdf_assemblage_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()

def unique(txt, nom):
    n = c.count(txt)
    if n != 1:
        print("ERREUR " + nom + " : marqueur trouve " + str(n) + " fois (attendu 1). Rien ecrit.")
        raise SystemExit(1)

# ===== 1) Extraire le bloc d'assemblage du viewer (ANCRAGE -> recentrage) =====
mStart = "      // ===== ANCRAGE SEMANTIQUE : balcons/appentis ancres, monopente accolee ====="
mEnd = """      // Recentrage de l'ensemble sur l'origine (sol et camera)
      if (groupes.length > 1) {
        const boite = new THREE.Box3();
        groupes.forEach((g) => { boite.expandByObject(g); });
        if (boite.isEmpty() === false) {
          const centre = new THREE.Vector3();
          boite.getCenter(centre);
          groupes.forEach((g) => { g.position.x -= centre.x; g.position.z -= centre.z; });
        }
      }"""
unique(mStart, "debut bloc")
unique(mEnd, "fin bloc")
iA = c.find(mStart)
iB = c.find(mEnd) + len(mEnd)
bloc = c[iA:iB]

# Renommages pour la fonction commune
blocFn = bloc.replace("params.ouvrages", "listeOuvrages").replace("buildOuvrage(", "construire(")
if "params." in blocFn:
    print("ERREUR : reference residuelle a params dans le bloc extrait. Rien ecrit.")
    raise SystemExit(1)

fonction = """// ================================================================
// ASSEMBLAGE MULTI-OUVRAGES (fonction commune viewer / capture PDF)
// construireOuvrage(o, extraOpts, decoupes) doit construire, ajouter a la
// scene et renvoyer le THREE.Group de l'ouvrage. Retourne les groupes places.
// ================================================================
function assemblerOuvrages(listeOuvrages, construireOuvrage) {
      const gap = 2.0;
      const groupes = [];
      const construire = (o, extraOpts) => {
        const grp = construireOuvrage(o, extraOpts, decoupesParOuvrage.get(o) || null);
        groupes.push(grp);
        return grp;
      };
""" + blocFn + """
      return groupes;
}

"""

# ===== 2) Remplacer le bloc du viewer par l'appel a la fonction commune =====
vStart = """      const gap = 2.0;
      const metresAll = [];"""
unique(vStart, "debut viewer")
iV = c.find(vStart)
nouveauViewer = """      const metresAll = [];
      const proprietairePiece = []; // groupe d'origine de chaque piece (bake IFC)
      let densiteRef = 450;
      // Helper : preBuild EC5 + build final d'un ouvrage dans un groupe
      const buildOuvrage = (o, extraOpts, decoupes) => {
        const oParams = { ...params, ...o };
        const tmpGrp = new THREE.Group();
        const pre = buildScene3D(tmpGrp, oParams, { couverture: oParams.couverture, mode: params.mode3D, ...(extraOpts || {}) });
        let secs = {};
        try {
          const agg = agregerMetre(pre.metre, pre.densiteBois || 450);
          secs = calculerSectionsCharpente(agg, oParams, params.sk);
        } catch (e) { secs = {}; }
        tmpGrp.traverse((obj) => { if (obj.isMesh && obj.geometry) obj.geometry.dispose(); });
        const grp = new THREE.Group();
        const res = buildScene3D(grp, oParams, {
          couverture: oParams.couverture, mode: params.mode3D,
          sections: secs, sectionMode: params.sectionMode || "conseillee",
          decoupesDebord: decoupes || null,
          ...(extraOpts || {}),
        });
        scene.add(grp);
        const iDebutMetre = metresAll.length;
        metresAll.push(...res.metre);
        for (let iP = iDebutMetre; iP < metresAll.length; iP++) proprietairePiece[iP] = grp;
        densiteRef = res.densiteBois || 450;
        return grp;
      };
      // ===== ASSEMBLAGE : fonction commune viewer / capture PDF =====
      assemblerOuvrages(params.ouvrages, buildOuvrage);"""
c = c[:iV] + nouveauViewer + c[iB:]

# ===== 3) Inserer la fonction commune avant capture3DViews =====
anc = "function capture3DViews(view3DParams) {"
unique(anc, "capture3DViews")
c = c.replace(anc, fonction + anc)

# ===== 4) Remplacer la branche multi de la capture PDF =====
pStart = "  if (view3DParams.ouvrages && view3DParams.ouvrages.length > 1) {"
pEnd = """  } else {
    const buildResult = buildScene3D(scene, view3DParams, pdfOpts);
    yCentre = buildResult.yCentre;
  }"""
unique(pStart, "debut capture multi")
unique(pEnd, "fin capture multi")
iP0 = c.find(pStart)
iP1 = c.find(pEnd) + len(pEnd)
nouvelleCapture = """  if (view3DParams.ouvrages && view3DParams.ouvrages.length > 1) {
    // ===== MULTI-OUVRAGES : MEME assemblage que le viewer (fonction commune) =====
    const construirePdf = (o, extraOpts, decoupes) => {
      const grp = new THREE.Group();
      buildScene3D(grp, { ...view3DParams, ...o }, {
        ...pdfOpts,
        couverture: o.couverture || view3DParams.couverture,
        decoupesDebord: decoupes || null,
        ...(extraOpts || {}),
      });
      scene.add(grp);
      return grp;
    };
    const groupesPdf = assemblerOuvrages(view3DParams.ouvrages, construirePdf);
    const boitePdf = new THREE.Box3();
    groupesPdf.forEach((g) => { boitePdf.expandByObject(g); });
    if (boitePdf.isEmpty() === false) {
      const taillePdf = new THREE.Vector3();
      boitePdf.getSize(taillePdf);
      empriseL = Math.max(taillePdf.x, 6);
      empriseLg = Math.max(taillePdf.z, 6);
      yCentre = boitePdf.max.y * 0.5;
    } else {
      yCentre = Ht;
    }
  } else {
    const buildResult = buildScene3D(scene, view3DParams, pdfOpts);
    yCentre = buildResult.yCentre;
  }"""
c = c[:iP0] + nouvelleCapture + c[iP1:]

open(f, "w").write(c)
print("OK : assemblage extrait en fonction commune, viewer branche dessus, capture PDF alignee.")
