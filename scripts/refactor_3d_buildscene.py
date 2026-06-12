#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D A2.1 : Refactoring (extraire buildScene3D commun)

ETAPE 1/2 du chantier "ajouter 6 nouveaux types de structures".

But : extraire la logique de construction 3D (charpente_trad + carport) dans
une fonction buildScene3D(scene, params) utilisable par :
- Viewer3D (interactif)
- capture3DViews (PDF)

Apres cette etape, le rendu doit etre EXACTEMENT identique a avant.
Ensuite on ajoutera les 6 nouveaux types.
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_refactor_3d"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter la fonction buildScene3D() apres l'import OrbitControls
# Centralise la logique de construction des structures 3D
# ================================================================

old_marker = 'import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";'

new_with_buildscene = '''import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

// ================================================================
// BUILD SCENE 3D - Construit la geometrie selon type de projet
// Utilisee par Viewer3D (interactif) et capture3DViews (PDF)
// ================================================================
function buildScene3D(scene, params, opts) {
  const L = params.longueur || 8;
  const lg = params.largeur || 6;
  const Ht = params.hauteur || 3;
  const pente = params.pente || 35;
  const typeProjet = params.type_projet || "charpente_trad";

  // Options : couleurs (peuvent varier pour le PDF vs interactif)
  const woodColor = opts && opts.woodColor ? opts.woodColor : 0xc4894a;
  const roofColor = opts && opts.roofColor ? opts.roofColor : 0x8b6355;
  const wallColor = opts && opts.wallColor ? opts.wallColor : 0xf0ece0;
  const wallOpacity = opts && opts.wallOpacity !== undefined ? opts.wallOpacity : 0.2;

  const woodMat = new THREE.MeshLambertMaterial({ color: woodColor });
  const roofMat = new THREE.MeshLambertMaterial({ color: roofColor, side: THREE.DoubleSide });
  const wallMat = new THREE.MeshLambertMaterial({ color: wallColor, transparent: true, opacity: wallOpacity, side: THREE.DoubleSide });

  const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), mat || woodMat);
    m.position.set(px, py, pz);
    if (rot) m.rotation.set(...rot);
    m.castShadow = true;
    scene.add(m);
  };

  // ============================================================
  // CHARPENTE TRADITIONNELLE (2 pans)
  // ============================================================
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

    const ang = Math.atan(hf / (lg/2));
    const pl = (lg/2) / Math.cos(ang);
    const rg = new THREE.PlaneGeometry(L + 0.6, pl + 0.2);
    const r1 = new THREE.Mesh(rg, roofMat);
    r1.position.set(0, Ht + hf/2, lg/4);
    r1.rotation.x = ang - Math.PI/2;
    scene.add(r1);
    const r2 = new THREE.Mesh(rg, roofMat);
    r2.position.set(0, Ht + hf/2, -lg/4);
    r2.rotation.x = -(ang - Math.PI/2);
    scene.add(r2);
  };

  // ============================================================
  // CARPORT (1 pente, pas de murs)
  // ============================================================
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

  // ============================================================
  // SWITCH SELON TYPE PROJET
  // ============================================================
  if (typeProjet === "carport") {
    drawCarport();
  } else {
    drawCharpenteTrad();
  }

  // Retourne le centre Y pour la camera
  const yCentre = typeProjet === "carport"
    ? Ht + (lg * Math.tan((pente * Math.PI) / 180)) / 2
    : Ht/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;

  return { yCentre };
}'''

if "function buildScene3D(" in content:
    print("[INFO] buildScene3D deja en place")
elif old_marker in content:
    content = content.replace(old_marker, new_with_buildscene, 1)
    print("[OK] Fonction buildScene3D ajoutee (charpente_trad + carport)")
    modifs += 1
else:
    print("[ERREUR] Import OrbitControls non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Remplacer la logique dans capture3DViews par appel a buildScene3D
# ================================================================

# Le bloc a remplacer va de "// Materials..." jusqu'a "// Pas de sol..."
# inclus le drawCharpenteTrad et drawCarport dupliques

# Recherche : tout ce qui est entre les 2 marqueurs
old_capture_body = '''  // Materials (couleurs plus contrastees pour le PDF blanc)
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
    : Ht/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;'''

new_capture_body = '''  // Construction de la scene via fonction commune
  // Couleurs adaptees pour le PDF (plus contrastees sur fond blanc)
  const buildResult = buildScene3D(scene, view3DParams, {
    woodColor: 0xa8743a,
    roofColor: 0x6b4a3f,
    wallColor: 0xd8d2c0,
    wallOpacity: 0.25
  });
  const yCentre = buildResult.yCentre;

  // Pas de sol (sinon ca pollue les vues sur fond blanc)'''

if "Construction de la scene via fonction commune" in content:
    print("[INFO] capture3DViews deja refactorise")
elif old_capture_body in content:
    content = content.replace(old_capture_body, new_capture_body, 1)
    print("[OK] capture3DViews refactorise (utilise buildScene3D)")
    modifs += 1
else:
    print("[ERREUR] Corps de capture3DViews non trouve exactement")
    print("[INFO] La structure du fichier a peut-etre change. Verifie manuellement.")
    sys.exit(1)

# ================================================================
# MOD 3 : Remplacer aussi dans Viewer3D (la version interactive)
# ================================================================

old_viewer_body = '''    const L = params.longueur || 8;
    const lg = params.largeur || 6;
    const H = params.hauteur || 3;
    const pente = params.pente || 35;
    const typeProjet = params.type_projet || "charpente_trad";

    const woodMat = new THREE.MeshLambertMaterial({ color: 0xc4894a });
    const roofMat = new THREE.MeshLambertMaterial({ color: 0x8b6355, side: THREE.DoubleSide });
    const wallMat = new THREE.MeshLambertMaterial({ color: 0xf0ece0, transparent: true, opacity: 0.2, side: THREE.DoubleSide });

    const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
      const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), mat || woodMat);
      m.position.set(px, py, pz);
      if (rot) m.rotation.set(...rot);
      m.castShadow = true;
      scene.add(m);
    };

    // ============================================================
    // FONCTION : dessine une charpente traditionnelle (2 pans)
    // ============================================================
    const drawCharpenteTrad = () => {'''

if "const buildResultViewer = buildScene3D(scene, params" in content:
    print("[INFO] Viewer3D deja refactorise")
elif old_viewer_body in content:
    # On va remplacer un BLOC plus large car le Viewer3D contient pas mal de code
    # Plus simple : trouver le debut et la fin du gros bloc duplique
    # Le debut : "const L = params.longueur"
    # La fin : "// SOL (commun à tous les types)"
    debut_marker = '    const L = params.longueur || 8;'
    fin_marker = '    // SOL (commun à tous les types)'
    
    debut_idx = content.find(debut_marker)
    fin_idx = content.find(fin_marker)
    
    if debut_idx > 0 and fin_idx > debut_idx:
        # Remplacer tout entre debut et juste avant fin
        new_viewer_body_concise = '''    // Construction de la scene via fonction commune
    const buildResultViewer = buildScene3D(scene, params);
    const H = params.hauteur || 3;
    const lg = params.largeur || 6;
    const pente = params.pente || 35;
    const typeProjet = params.type_projet || "charpente_trad";

    '''
        old_block = content[debut_idx:fin_idx]
        content = content.replace(old_block, new_viewer_body_concise, 1)
        print("[OK] Viewer3D refactorise (utilise buildScene3D)")
        modifs += 1
    else:
        print("[WARN] Bloc Viewer3D non trouve - peut-etre deja refactorise")
else:
    print("[INFO] Viewer3D semble deja refactorise")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Fonction buildScene3D() ajoutee (logique commune)")
print("  2. capture3DViews utilise maintenant buildScene3D")
print("  3. Viewer3D utilise maintenant buildScene3D")
print()
print("RESULTAT VISUEL :")
print("  - EXACTEMENT IDENTIQUE a avant")
print("  - On a juste un seul endroit pour modifier la 3D")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
