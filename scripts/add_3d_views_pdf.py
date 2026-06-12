#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Ajout des vues 3D dans le PDF
- Fonction capture3DViews(params) qui retourne 3 images base64
- Modifie generatePDF pour inclure les 3 vues
- Vues : Face (avant), Cote (lateral), Perspective (3/4)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_3d_pdf"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter la fonction capture3DViews() AVANT generatePDF
# ================================================================

old_pdf_func_marker = '// ================================================================\n// GENERATEUR PDF PRO\n// ================================================================\nfunction generatePDF(result, params, zoneInfo, nomProjet) {'

new_with_capture = '''// ================================================================
// CAPTURE 3D - Genere 3 vues PNG en base64 pour le PDF
// ================================================================
function capture3DViews(view3DParams) {
  const W = 800;
  const H = 600;

  // Renderer offscreen avec fond transparent
  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    preserveDrawingBuffer: true
  });
  renderer.setSize(W, H);
  renderer.setClearColor(0xffffff, 0); // transparent

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, W / H, 0.1, 200);

  // Lumieres
  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const sun = new THREE.DirectionalLight(0xfff8e7, 1.2);
  sun.position.set(10, 20, 10);
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0xc4d4e8, 0.4);
  fill.position.set(-10, 10, -5);
  scene.add(fill);

  // Params
  const L = view3DParams.longueur || 8;
  const lg = view3DParams.largeur || 6;
  const Ht = view3DParams.hauteur || 3;
  const pente = view3DParams.pente || 35;
  const typeProjet = view3DParams.type_projet || "charpente_trad";

  // Materials (couleurs plus contrastees pour le PDF blanc)
  const woodMat = new THREE.MeshLambertMaterial({ color: 0xa8743a });
  const roofMat = new THREE.MeshLambertMaterial({ color: 0x6b4a3f, side: THREE.DoubleSide });
  const wallMat = new THREE.MeshLambertMaterial({ color: 0xd8d2c0, transparent: true, opacity: 0.25, side: THREE.DoubleSide });

  const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), mat || woodMat);
    m.position.set(px, py, pz);
    if (rot) m.rotation.set(...rot);
    scene.add(m);
  };

  // ============ CHARPENTE TRAD ============
  const drawCharpenteTrad = () => {
    const hf = lg / 2 * Math.tan((pente * Math.PI) / 180);
    [
      [L, Ht, 0.15, 0, Ht/2, lg/2],
      [L, Ht, 0.15, 0, Ht/2, -lg/2],
      [0.15, Ht, lg, -L/2, Ht/2, 0],
      [0.15, Ht, lg, L/2, Ht/2, 0]
    ].forEach(([sx, sy, sz, px, py, pz]) => addBox(sx, sy, sz, px, py, pz, wallMat));

    const nb = Math.max(2, Math.ceil(L / 2.5));
    for (let i = 0; i <= nb; i++) {
      const x = -L/2 + (i/nb) * L;
      const ang = Math.atan(hf / (lg/2));
      const pl = (lg/2) / Math.cos(ang);
      addBox(pl, 0.12, 0.12, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);
      addBox(pl, 0.12, 0.12, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);
      addBox(0.12, hf + 0.1, 0.12, x, Ht + hf/2, 0);
    }
    addBox(L + 0.4, 0.14, 0.14, 0, Ht + hf, 0);

    const ang2 = Math.atan(hf / (lg/2));
    const pl2 = (lg/2) / Math.cos(ang2);
    const rg = new THREE.PlaneGeometry(L + 0.6, pl2 + 0.2);
    const r1 = new THREE.Mesh(rg, roofMat);
    r1.position.set(0, Ht + hf/2, lg/4);
    r1.rotation.x = ang2 - Math.PI/2;
    scene.add(r1);
    const r2 = new THREE.Mesh(rg, roofMat);
    r2.position.set(0, Ht + hf/2, -lg/4);
    r2.rotation.x = -(ang2 - Math.PI/2);
    scene.add(r2);
  };

  // ============ CARPORT ============
  const drawCarport = () => {
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;
    const Hhaut = Ht + denivele;
    const sectionPotau = 0.18;

    addBox(sectionPotau, Hbas, sectionPotau, -L/2, Hbas/2, -lg/2);
    addBox(sectionPotau, Hbas, sectionPotau, L/2, Hbas/2, -lg/2);
    addBox(sectionPotau, Hhaut, sectionPotau, -L/2, Hhaut/2, lg/2);
    addBox(sectionPotau, Hhaut, sectionPotau, L/2, Hhaut/2, lg/2);

    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2);
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2);

    const nbPannes = 3;
    for (let i = 0; i < nbPannes; i++) {
      const t = i / (nbPannes - 1);
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele;
      addBox(L + 0.3, 0.14, 0.14, 0, y, z);
    }

    const nbChevrons = Math.max(3, Math.ceil(L / 1.0));
    const ang = Math.atan(denivele / lg);
    const longueurChevron = lg / Math.cos(ang);
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      const yCentre = Hbas + denivele/2;
      addBox(0.10, 0.10, longueurChevron + 0.2, x, yCentre, 0, woodMat, [ang, 0, 0]);
    }

    const rg = new THREE.PlaneGeometry(longueurChevron + 0.3, L + 0.4);
    const roof = new THREE.Mesh(rg, roofMat);
    roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
    roof.rotation.z = ang;
    roof.rotation.y = Math.PI/2;
    scene.add(roof);
  };

  if (typeProjet === "carport") {
    drawCarport();
  } else {
    drawCharpenteTrad();
  }

  // Pas de sol (sinon ca pollue les vues sur fond blanc)

  // Centre de la camera (selon type)
  const yCentre = typeProjet === "carport"
    ? Ht + (lg * Math.tan((pente * Math.PI) / 180)) / 2
    : Ht/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;

  // Distance camera proportionnelle a la taille
  const maxDim = Math.max(L, lg, Ht * 2);
  const dist = maxDim * 1.8;

  // ============ CAPTURE 3 VUES ============
  const views = {};

  // 1. FACE (regard depuis Z positif vers Z negatif)
  camera.position.set(0, yCentre, dist);
  camera.lookAt(0, yCentre, 0);
  renderer.render(scene, camera);
  views.face = renderer.domElement.toDataURL("image/png");

  // 2. COTE (regard depuis X positif vers X negatif)
  camera.position.set(dist, yCentre, 0);
  camera.lookAt(0, yCentre, 0);
  renderer.render(scene, camera);
  views.cote = renderer.domElement.toDataURL("image/png");

  // 3. PERSPECTIVE (3/4 classique)
  camera.position.set(dist * 0.7, yCentre + dist * 0.4, dist * 0.7);
  camera.lookAt(0, yCentre, 0);
  renderer.render(scene, camera);
  views.perspective = renderer.domElement.toDataURL("image/png");

  // Nettoyage
  renderer.dispose();

  return views;
}

// ================================================================
// GENERATEUR PDF PRO
// ================================================================
function generatePDF(result, params, zoneInfo, nomProjet, view3DParams) {'''

if "function capture3DViews(" in content:
    print("[INFO] Fonction capture3DViews deja presente")
elif old_pdf_func_marker in content:
    content = content.replace(old_pdf_func_marker, new_with_capture, 1)
    print("[OK] Fonction capture3DViews() ajoutee (3 vues PNG transparentes)")
    print("[OK] Signature generatePDF mise a jour pour accepter view3DParams")
    modifs += 1
else:
    print("[ERREUR] Marqueur generatePDF non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Inserer les 3 vues 3D dans le PDF
# Position : APRES infos client/projet, AVANT le tableau des postes
# ================================================================

old_table_marker = '''  y = Math.max(y, yClient) + 8;

  // ============ TABLEAU DES POSTES ============'''

new_with_3d = '''  y = Math.max(y, yClient) + 8;

  // ============ VUES 3D ============
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
  }

  // ============ TABLEAU DES POSTES ============'''

if "VUES DU PROJET" in content:
    print("[INFO] Bloc vues 3D deja present")
elif old_table_marker in content:
    content = content.replace(old_table_marker, new_with_3d, 1)
    print("[OK] Bloc 3 vues 3D insere avant le tableau des postes")
    modifs += 1
else:
    print("[ERREUR] Marqueur tableau postes non trouve")
    sys.exit(1)

# ================================================================
# MOD 3 : Modifier l'appel a generatePDF pour passer view3DParams
# ================================================================

old_pdf_call = 'onClick={() => generatePDF(result, params, zoneInfo, nomProjet)}'
new_pdf_call = 'onClick={() => generatePDF(result, params, zoneInfo, nomProjet, view3DParams)}'

if "generatePDF(result, params, zoneInfo, nomProjet, view3DParams)" in content:
    print("[INFO] Appel generatePDF deja a jour")
elif old_pdf_call in content:
    content = content.replace(old_pdf_call, new_pdf_call, 1)
    print("[OK] Appel generatePDF mis a jour pour passer view3DParams")
    modifs += 1
else:
    print("[ERREUR] Appel generatePDF non trouve")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Fonction capture3DViews() ajoutee (3 vues PNG en base64)")
print("  2. Bloc 'VUES DU PROJET' insere dans le PDF")
print("  3. Bouton PDF passe maintenant view3DParams")
print()
print("VUES GENEREES :")
print("  1. FACE       : camera devant le projet (Z+)")
print("  2. COTE       : camera laterale (X+)")
print("  3. PERSPECTIVE : camera 3/4 (classique)")
print()
print("STYLE :")
print("  - Fond transparent (s'integre au blanc du PDF)")
print("  - 800x600 px (haute qualite)")
print("  - 3 vues alignees horizontalement avec labels")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
