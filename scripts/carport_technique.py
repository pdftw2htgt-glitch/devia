#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D : Carport TECHNIQUE
Remplace drawCarport :
- Poteaux conserves (specificite carport)
- Sablieres (haute + basse)
- Pannes intermediaires (suivent la pente)
- Chevrons rapproches (~tous les 0.6m)
- Couverture semi-transparente
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_carport_technique"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# Remplacer drawCarport par la version technique
# ================================================================

old_carport = '''  const drawCarport = () => {
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
      addBox(0.10, 0.10, longueurChevron + 0.2, x, yCentre, 0, woodMat, [-ang, 0, 0]);
    }

    const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
    const roof = new THREE.Mesh(rg, roofMat);
    roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);
  };'''

new_carport = '''  const drawCarport = () => {
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;
    const Hhaut = Ht + denivele;
    const sectionPotau = 0.18;
    const ang = Math.atan(denivele / lg);
    const longueurChevron = lg / Math.cos(ang);

    // ===== POTEAUX (specificite carport) =====
    // Poteaux intermediaires aussi si carport long
    const nbPoteauxLong = Math.max(1, Math.ceil(L / 4));
    for (let i = 0; i <= nbPoteauxLong; i++) {
      const x = -L/2 + (i / nbPoteauxLong) * L;
      addBox(sectionPotau, Hbas, sectionPotau, x, Hbas/2, -lg/2);   // avant (bas)
      addBox(sectionPotau, Hhaut, sectionPotau, x, Hhaut/2, lg/2);  // arriere (haut)
    }

    // ===== SABLIERES (basse avant + haute arriere) =====
    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2, woodMat);
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2, woodMat);

    // ===== PANNES INTERMEDIAIRES (suivent la pente) =====
    const nbPannes = 3;
    for (let i = 0; i < nbPannes; i++) {
      const t = i / (nbPannes - 1);
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele;
      addBox(L + 0.3, 0.12, 0.12, 0, y, z, woodMat);
    }

    // ===== CHEVRONS RAPPROCHES (~tous les 0.6m) =====
    const espChevron = 0.6;
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    const yCentre = Hbas + denivele/2;
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      addBox(0.08, 0.08, longueurChevron + 0.2, x, yCentre + 0.06, 0, woodMat, [-ang, 0, 0]);
    }

    // ===== COUVERTURE (1 pan, semi-transparente) =====
    const roofTransMat = new THREE.MeshLambertMaterial({
      color: roofColor, transparent: true, opacity: 0.45, side: THREE.DoubleSide
    });
    const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
    const roof = new THREE.Mesh(rg, roofTransMat);
    roof.position.set(0, yCentre + 0.16, 0);
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);
  };'''

if "CHEVRONS RAPPROCHES (~tous les 0.6m)" in content and "drawCarport" in content and content.count("CHEVRONS RAPPROCHES (~tous les 0.6m)") >= 2 and "POTEAUX (specificite carport)" in content:
    print("[INFO] Carport technique deja en place")
elif old_carport in content:
    content = content.replace(old_carport, new_carport, 1)
    print("[OK] drawCarport remplace par version technique")
    modifs += 1
else:
    print("[ERREUR] drawCarport original non trouve exactement")
    print("[INFO] Verifie si le carport a deja ete modifie.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATION APPLIQUEE")
print("=" * 60)
print()
print("CARPORT TECHNIQUE :")
print("  - Poteaux (4 coins + intermediaires si long)")
print("  - Sablieres (basse avant + haute arriere)")
print("  - 3 pannes qui suivent la pente")
print("  - Chevrons rapproches (~tous les 0.6m)")
print("  - Couverture SEMI-TRANSPARENTE (1 pan)")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
