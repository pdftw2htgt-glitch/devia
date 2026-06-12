#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D : Monopente TECHNIQUE
Remplace drawMonopente :
- Murs conserves (specificite monopente : batiment ferme)
- Sablieres (haute arriere + basse avant)
- Pannes intermediaires (suivent la pente, sections plus fines)
- Chevrons rapproches (~tous les 0.6m, section 0.08x0.08)
- Couverture OPAQUE avec couleur dynamique selon type :
    * bac_acier   -> anthracite (0x3a3a3f)
    * tuile_beton -> brun-gris (0x8b6355)
    * tuile_terre -> orange tuile (0xc87650) [defaut]
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_monopente_technique"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# Remplacer drawMonopente par la version technique
# ================================================================

old_monopente = '''  const drawMonopente = () => {
    // Calcul deniveles
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;            // hauteur mur avant
    const Hhaut = Ht + denivele; // hauteur mur arriere

    // 4 MURS (avec hauteurs variables sur les cotes)
    // Mur arriere (Z+, haut)
    addBox(L, Hhaut, 0.15, 0, Hhaut/2, lg/2, wallMat);
    // Mur avant (Z-, bas)
    addBox(L, Hbas, 0.15, 0, Hbas/2, -lg/2, wallMat);

    // Mur lateral gauche (forme trapezoidale - approxime avec 2 boxes)
    // Partie basse : rectangle Hbas
    addBox(0.15, Hbas, lg, -L/2, Hbas/2, 0, wallMat);
    // Partie haute : triangle (approxime par un prisme)
    const triGeo = new THREE.BufferGeometry();
    const triVertices = new Float32Array([
      // Triangle gauche
      -L/2, Hbas, -lg/2,
      -L/2, Hbas, lg/2,
      -L/2, Hhaut, lg/2,
    ]);
    triGeo.setAttribute("position", new THREE.BufferAttribute(triVertices, 3));
    triGeo.computeVertexNormals();
    const triMeshG = new THREE.Mesh(triGeo, wallMat);
    scene.add(triMeshG);

    // Mur lateral droit
    addBox(0.15, Hbas, lg, L/2, Hbas/2, 0, wallMat);
    const triGeo2 = new THREE.BufferGeometry();
    const triVertices2 = new Float32Array([
      L/2, Hbas, -lg/2,
      L/2, Hbas, lg/2,
      L/2, Hhaut, lg/2,
    ]);
    triGeo2.setAttribute("position", new THREE.BufferAttribute(triVertices2, 3));
    triGeo2.computeVertexNormals();
    const triMeshD = new THREE.Mesh(triGeo2, wallMat);
    scene.add(triMeshD);

    // SABLIERES
    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2);  // sabliere avant
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2);  // sabliere arriere

    // PANNES (3 pannes entre sablieres)
    const nbPannes = 3;
    for (let i = 0; i < nbPannes; i++) {
      const t = i / (nbPannes - 1);
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele;
      addBox(L + 0.3, 0.14, 0.14, 0, y, z);
    }

    // CHEVRONS (en pente, sens largeur)
    const nbChevrons = Math.max(3, Math.ceil(L / 1.0));
    const ang = Math.atan(denivele / lg);
    const longueurChevron = lg / Math.cos(ang);
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      const yCentre = Hbas + denivele/2;
      addBox(0.10, 0.10, longueurChevron + 0.2, x, yCentre, 0, woodMat, [-ang, 0, 0]);
    }

    // TOITURE (1 pan)
    const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
    const roof = new THREE.Mesh(rg, roofMat);
    roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);
  };'''

new_monopente = '''  const drawMonopente = () => {
    // Calcul deniveles
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;             // hauteur mur avant
    const Hhaut = Ht + denivele; // hauteur mur arriere
    const ang = Math.atan(denivele / lg);
    const longueurChevron = lg / Math.cos(ang);

    // ===== CHOIX COUVERTURE (bac acier / tuiles) =====
    const typeCouv = (opts && opts.couverture) ? opts.couverture : "tuile_terre";
    let couvColor;
    if (typeCouv === "bac_acier") {
      couvColor = 0x3a3a3f;  // anthracite
    } else if (typeCouv === "tuile_beton") {
      couvColor = 0x8b6355;  // brun-gris
    } else {
      couvColor = 0xc87650;  // tuile terre cuite (defaut)
    }
    const monopenteRoofMat = new THREE.MeshLambertMaterial({
      color: couvColor, side: THREE.DoubleSide
    });

    // ===== 4 MURS (hauteurs variables sur les cotes) =====
    // Mur arriere (Z+, haut)
    addBox(L, Hhaut, 0.15, 0, Hhaut/2, lg/2, wallMat);
    // Mur avant (Z-, bas)
    addBox(L, Hbas, 0.15, 0, Hbas/2, -lg/2, wallMat);

    // Mur lateral gauche (partie basse + triangle haut)
    addBox(0.15, Hbas, lg, -L/2, Hbas/2, 0, wallMat);
    const triGeo = new THREE.BufferGeometry();
    const triVertices = new Float32Array([
      -L/2, Hbas, -lg/2,
      -L/2, Hbas, lg/2,
      -L/2, Hhaut, lg/2,
    ]);
    triGeo.setAttribute("position", new THREE.BufferAttribute(triVertices, 3));
    triGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(triGeo, wallMat));

    // Mur lateral droit (partie basse + triangle haut)
    addBox(0.15, Hbas, lg, L/2, Hbas/2, 0, wallMat);
    const triGeo2 = new THREE.BufferGeometry();
    const triVertices2 = new Float32Array([
      L/2, Hbas, -lg/2,
      L/2, Hbas, lg/2,
      L/2, Hhaut, lg/2,
    ]);
    triGeo2.setAttribute("position", new THREE.BufferAttribute(triVertices2, 3));
    triGeo2.computeVertexNormals();
    scene.add(new THREE.Mesh(triGeo2, wallMat));

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

    // ===== COUVERTURE (1 pan, opaque, couleur selon type) =====
    const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
    const roof = new THREE.Mesh(rg, monopenteRoofMat);
    roof.position.set(0, yCentre + 0.16, 0);
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);
  };'''

# Marker unique a la monopente technique (pas present dans carport ni hangar)
if "CHOIX COUVERTURE (bac acier / tuiles)" in content:
    print("[INFO] Monopente technique deja en place")
elif old_monopente in content:
    content = content.replace(old_monopente, new_monopente, 1)
    print("[OK] drawMonopente remplace par version technique")
    modifs += 1
else:
    print("[ERREUR] drawMonopente original non trouve exactement")
    print("[INFO] Verifie si la monopente a deja ete modifiee.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATION APPLIQUEE")
print("=" * 60)
print()
print("MONOPENTE TECHNIQUE :")
print("  - 4 murs conserves (specificite monopente)")
print("  - Sablieres (basse avant + haute arriere)")
print("  - 3 pannes qui suivent la pente (section 12x12)")
print("  - Chevrons rapproches (~tous les 0.6m, section 8x8)")
print("  - Couverture OPAQUE avec couleur dynamique :")
print("      bac_acier   -> anthracite")
print("      tuile_beton -> brun-gris")
print("      tuile_terre -> orange tuile (defaut)")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
