#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D : Charpente traditionnelle TECHNIQUE complete
Remplace drawCharpenteTrad par une version detaillee :
- Fermes completes (entrait + arbaletriers + poincon + contrefiches)
- Pannes (sabliere + intermediaires + faitiere)
- Chevrons rapproches (~tous les 0.5m)
- Couverture semi-transparente (pour voir l'ossature)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_charpente_technique"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# Remplacer drawCharpenteTrad par la version technique
# ================================================================

old_charpente = '''  const drawCharpenteTrad = () => {
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
  };'''

new_charpente = '''  const drawCharpenteTrad = () => {
    const hf = lg / 2 * Math.tan((pente * Math.PI) / 180); // hauteur faitage
    const ang = Math.atan(hf / (lg/2));                    // angle de pente
    const pl = (lg/2) / Math.cos(ang);                     // longueur d'un arbaletrier
    const yFait = Ht + hf;                                  // hauteur du faitage

    // ===== MURS (4 cotes) =====
    [
      [L, Ht, 0.15, 0, Ht/2, lg/2],
      [L, Ht, 0.15, 0, Ht/2, -lg/2],
      [0.15, Ht, lg, -L/2, Ht/2, 0],
      [0.15, Ht, lg, L/2, Ht/2, 0]
    ].forEach(([sx, sy, sz, px, py, pz]) => addBox(sx, sy, sz, px, py, pz, wallMat));

    // ===== FERMES (tous les ~3.5m) =====
    // Chaque ferme = entrait + 2 arbaletriers + poincon + 2 contrefiches
    const nbFermes = Math.max(2, Math.ceil(L / 3.5));
    const fermeXs = [];
    for (let i = 0; i <= nbFermes; i++) {
      const x = -L/2 + (i / nbFermes) * L;
      fermeXs.push(x);

      // ENTRAIT (poutre horizontale basse, sur toute la largeur)
      addBox(0.16, 0.16, lg, x, Ht, 0, woodMat);

      // ARBALETRIERS (les 2 pans inclines, section forte)
      addBox(0.16, 0.16, pl, x, Ht + hf/2, lg/4, woodMat, [-ang + Math.PI/2, 0, 0]);
      addBox(0.16, 0.16, pl, x, Ht + hf/2, -lg/4, woodMat, [ang + Math.PI/2, 0, 0]);

      // POINCON (poteau vertical central, du faitage a l'entrait)
      addBox(0.14, hf, 0.14, x, Ht + hf/2, 0, woodMat);

      // CONTREFICHES (jambes de force diagonales du poincon vers les arbaletriers)
      const cfLen = pl * 0.5;
      // Contrefiche cote Z+
      addBox(0.10, 0.10, cfLen, x, Ht + hf*0.28, lg*0.14, woodMat, [-ang + Math.PI/2, 0, 0]);
      // Contrefiche cote Z-
      addBox(0.10, 0.10, cfLen, x, Ht + hf*0.28, -lg*0.14, woodMat, [ang + Math.PI/2, 0, 0]);
    }

    // ===== SABLIERES (poutres basses sur les murs longs) =====
    addBox(L + 0.3, 0.14, 0.14, 0, Ht, lg/2, woodMat);
    addBox(L + 0.3, 0.14, 0.14, 0, Ht, -lg/2, woodMat);

    // ===== PANNE FAITIERE =====
    addBox(L + 0.4, 0.14, 0.14, 0, yFait, 0, woodMat);

    // ===== PANNES INTERMEDIAIRES (le long du toit, sur les 2 pans) =====
    const nbPannesParPan = 2;
    for (let p = 1; p <= nbPannesParPan; p++) {
      const t = p / (nbPannesParPan + 1); // position le long de l'arbaletrier
      const yPanne = Ht + hf * t;
      const zPanne = (lg/2) * (1 - t);
      addBox(L + 0.3, 0.12, 0.12, 0, yPanne, zPanne, woodMat);   // pan Z+
      addBox(L + 0.3, 0.12, 0.12, 0, yPanne, -zPanne, woodMat);  // pan Z-
    }

    // ===== CHEVRONS RAPPROCHES (tous les ~0.5m, sur les pannes) =====
    const espChevron = 0.5;
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      // Chevron pan Z+ (section fine)
      addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, lg/4, woodMat, [-ang + Math.PI/2, 0, 0]);
      // Chevron pan Z-
      addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, -lg/4, woodMat, [ang + Math.PI/2, 0, 0]);
    }

    // ===== COUVERTURE (2 pans, semi-transparente pour voir l'ossature) =====
    const roofTransMat = new THREE.MeshLambertMaterial({
      color: roofColor, transparent: true, opacity: 0.45, side: THREE.DoubleSide
    });
    const rg = new THREE.PlaneGeometry(L + 0.6, pl + 0.2);
    const r1 = new THREE.Mesh(rg, roofTransMat);
    r1.position.set(0, Ht + hf/2 + 0.12, lg/4);
    r1.rotation.x = ang - Math.PI/2;
    scene.add(r1);
    const r2 = new THREE.Mesh(rg, roofTransMat);
    r2.position.set(0, Ht + hf/2 + 0.12, -lg/4);
    r2.rotation.x = -(ang - Math.PI/2);
    scene.add(r2);
  };'''

if "POINCON (poteau vertical central" in content:
    print("[INFO] Charpente technique deja en place")
elif old_charpente in content:
    content = content.replace(old_charpente, new_charpente, 1)
    print("[OK] drawCharpenteTrad remplacee par version technique complete")
    modifs += 1
else:
    print("[ERREUR] drawCharpenteTrad original non trouve exactement")
    print("[INFO] La fonction a peut-etre deja ete modifiee.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATION APPLIQUEE")
print("=" * 60)
print()
print("CHARPENTE TRADITIONNELLE TECHNIQUE :")
print("  - Fermes completes (tous les ~3.5m) :")
print("      * Entrait (poutre horizontale basse)")
print("      * 2 Arbaletriers (pans inclines, section forte)")
print("      * Poincon (poteau vertical central)")
print("      * 2 Contrefiches (jambes de force diagonales)")
print("  - Sablieres (poutres basses sur murs)")
print("  - Panne faitiere + 2 pannes intermediaires par pan")
print("  - Chevrons rapproches (tous les ~0.5m)")
print("  - Couverture SEMI-TRANSPARENTE (voir l'ossature dessous)")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
