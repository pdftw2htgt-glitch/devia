#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D : Monopente REALISTE (charpente complete)
Enrichit drawMonopente avec :
- Pannes intermediaires CORRECTEMENT reparties (4 entre les 2 sablieres)
- Chevrons plus denses (~0.5m)
- LITEAUX : grille fine perpendiculaire aux chevrons (~0.35m)
- AISSELIERS : jambes de force obliques aux pignons (gauche + droit)
- Couverture semi-transparente conservee (couleur dynamique selon type)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_monopente_realiste"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# Remplacer drawMonopente (version transparente actuelle) par
# la version realiste complete
# ================================================================

old_monopente = '''  const drawMonopente = () => {
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
      color: couvColor, transparent: true, opacity: 0.4, side: THREE.DoubleSide
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

new_monopente = '''  const drawMonopente = () => {
    // ============================================================
    // MONOPENTE REALISTE - charpente complete
    // ============================================================
    // Calcul deniveles
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;             // hauteur mur avant
    const Hhaut = Ht + denivele; // hauteur mur arriere
    const ang = Math.atan(denivele / lg);
    const longueurChevron = lg / Math.cos(ang);
    const yCentre = Hbas + denivele/2;

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
      color: couvColor, transparent: true, opacity: 0.4, side: THREE.DoubleSide
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

    // ===== PANNES INTERMEDIAIRES (4, bien reparties entre sablieres) =====
    const nbPannes = 4;
    const pannePositions = [];
    for (let i = 0; i < nbPannes; i++) {
      const t = (i + 1) / (nbPannes + 1);  // evite superposition aux sablieres
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele;
      addBox(L + 0.3, 0.14, 0.14, 0, y, z, woodMat);
      pannePositions.push({ y, z, t });
    }

    // ===== CHEVRONS RAPPROCHES (~tous les 0.5m) =====
    const espChevron = 0.5;
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      addBox(0.08, 0.08, longueurChevron + 0.2, x, yCentre + 0.07, 0, woodMat, [-ang, 0, 0]);
    }

    // ===== LITEAUX (perpendiculaires aux chevrons, ~tous les 0.35m) =====
    // Petites planchettes paralleles aux sablieres, sur toute la longueur
    const espLiteau = 0.35;
    const nbLiteaux = Math.max(4, Math.floor(longueurChevron / espLiteau));
    for (let i = 0; i <= nbLiteaux; i++) {
      const t = i / nbLiteaux;
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele + 0.15;  // au-dessus des chevrons
      addBox(L + 0.4, 0.025, 0.04, 0, y, z, woodMat);
    }

    // ===== AISSELIERS (jambes de force obliques aux pignons) =====
    // Sur chaque mur lateral, 2 jambes obliques qui soutiennent les pannes
    // Partent du mur en haut (Hbas + 0.3) vers une panne intermediaire
    const aisselierAngles = [pannePositions[1], pannePositions[2]];  // 2eme et 3eme panne
    [-1, 1].forEach((cote) => {
      const xMur = cote * (L/2 - 0.08);
      aisselierAngles.forEach((p) => {
        // Point bas : sur le mur lateral, a 80% de Hbas, decale vers z=0
        const xb = xMur;
        const yb = Hbas * 0.5;
        const zb = -lg/2 + (p.t * lg) * 0.4;  // decale vers la sabliere basse
        // Point haut : sous la panne, a la position de la panne
        const xh = xMur;
        const yh = p.y - 0.08;
        const zh = p.z;
        // Calculs de la jambe oblique (centre + longueur + rotation autour de X)
        const dy = yh - yb;
        const dz = zh - zb;
        const longueur = Math.sqrt(dy*dy + dz*dz);
        const rotX = Math.atan2(dy, dz) - Math.PI/2;  // rotation autour de X
        const xc = (xb + xh) / 2;
        const yc = (yb + yh) / 2;
        const zc = (zb + zh) / 2;
        addBox(0.10, 0.10, longueur, xc, yc, zc, woodMat, [rotX, 0, 0]);
      });
    });

    // ===== COUVERTURE (1 pan, semi-transparente, couleur selon type) =====
    const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
    const roof = new THREE.Mesh(rg, monopenteRoofMat);
    roof.position.set(0, yCentre + 0.20, 0);  // plus haut a cause des liteaux
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);
  };'''

# Marker unique a la version realiste
if "MONOPENTE REALISTE - charpente complete" in content:
    print("[INFO] Monopente realiste deja en place")
elif old_monopente in content:
    content = content.replace(old_monopente, new_monopente, 1)
    print("[OK] drawMonopente enrichi -> version realiste")
    modifs += 1
else:
    print("[ERREUR] drawMonopente actuel non trouve exactement")
    print("[INFO] Verifie que monopente_technique.py + monopente_couverture_transparente.py")
    print("       ont bien ete appliques avant.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATION APPLIQUEE")
print("=" * 60)
print()
print("MONOPENTE REALISTE :")
print("  - 2 sablieres (basse avant + haute arriere)")
print("  - 4 PANNES intermediaires bien reparties (bug corrige)")
print("  - ~13 chevrons espaces de 0.5m (section 8x8)")
print("  - LITEAUX : ~12 planchettes fines (section 2.5x4 cm)")
print("  - AISSELIERS : 4 jambes de force aux pignons (2 par cote)")
print("  - Couverture semi-transparente conservee")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
