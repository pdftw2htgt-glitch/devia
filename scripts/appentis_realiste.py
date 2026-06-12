#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D : Appentis REALISTE (charpente complete adossee)
Remplace drawAppentis par une version enrichie :
- Mur d'adossement (specificite appentis) conserve
- Poteaux avant densifies si batiment long
- Murs lateraux trapezoidaux conserves
- Pannes intermediaires bien reparties (3)
- Chevrons denses (~0.5m)
- LITEAUX : grille fine perpendiculaire aux chevrons
- AISSELIERS : 4 jambes de force aux pignons
- Couverture dynamique (bac_acier / tuile_terre / tuile_beton)
  semi-transparente pour voir la structure
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_appentis_realiste"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# Remplacer drawAppentis par la version realiste
# ================================================================

old_appentis = '''  const drawAppentis = () => {
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;            // hauteur cote avant (libre)
    const Hhaut = Ht + denivele; // hauteur mur arriere (simule mur maison)

    // MUR ARRIERE PLEIN ET HAUT (simule un mur existant)
    // On le rend opaque et un peu plus epais pour bien le distinguer
    const murArriereMat = new THREE.MeshLambertMaterial({
      color: 0xd4ccb6,
      transparent: true,
      opacity: 0.85,
      side: THREE.DoubleSide
    });
    addBox(L + 0.5, Hhaut + 0.3, 0.25, 0, (Hhaut + 0.3)/2, lg/2, murArriereMat);

    // 2 POTEAUX AVANT (pour soutenir le toit)
    const sectionPotau = 0.18;
    addBox(sectionPotau, Hbas, sectionPotau, -L/2, Hbas/2, -lg/2);
    addBox(sectionPotau, Hbas, sectionPotau, L/2, Hbas/2, -lg/2);

    // PETITS MURS LATERAUX TRAPEZOIDAUX (option : peuvent etre transparents)
    // Cote gauche
    const triGeoL = new THREE.BufferGeometry();
    const triVertL = new Float32Array([
      -L/2, 0, -lg/2,
      -L/2, Hbas, -lg/2,
      -L/2, Hhaut, lg/2,
      -L/2, 0, -lg/2,
      -L/2, Hhaut, lg/2,
      -L/2, 0, lg/2,
    ]);
    triGeoL.setAttribute("position", new THREE.BufferAttribute(triVertL, 3));
    triGeoL.computeVertexNormals();
    const triMeshL = new THREE.Mesh(triGeoL, wallMat);
    scene.add(triMeshL);

    // Cote droit
    const triGeoR = new THREE.BufferGeometry();
    const triVertR = new Float32Array([
      L/2, 0, -lg/2,
      L/2, Hbas, -lg/2,
      L/2, Hhaut, lg/2,
      L/2, 0, -lg/2,
      L/2, Hhaut, lg/2,
      L/2, 0, lg/2,
    ]);
    triGeoR.setAttribute("position", new THREE.BufferAttribute(triVertR, 3));
    triGeoR.computeVertexNormals();
    const triMeshR = new THREE.Mesh(triGeoR, wallMat);
    scene.add(triMeshR);

    // SABLIERES
    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2);   // sabliere avant (basse)
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2);   // sabliere arriere (haute, contre mur)

    // CHEVRONS en pente (du mur arriere vers l'avant)
    const nbChevrons = Math.max(3, Math.ceil(L / 1.0));
    const ang = Math.atan(denivele / lg);
    const longueurChevron = lg / Math.cos(ang);
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      const yCentre = Hbas + denivele/2;
      addBox(0.10, 0.10, longueurChevron + 0.2, x, yCentre, 0, woodMat, [-ang, 0, 0]);
    }

    // 2 PANNES intermediaires
    const nbPannes = 2;
    for (let i = 0; i < nbPannes; i++) {
      const t = (i + 1) / (nbPannes + 1);
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele;
      addBox(L + 0.3, 0.12, 0.12, 0, y, z);
    }

    // TOITURE 1 pan
    const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
    const roof = new THREE.Mesh(rg, roofMat);
    roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);
  };'''

new_appentis = '''  const drawAppentis = () => {
    // ============================================================
    // APPENTIS REALISTE - charpente complete adossee
    // ============================================================
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;             // hauteur cote avant (libre)
    const Hhaut = Ht + denivele; // hauteur mur arriere (mur maison)
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
    const appentisRoofMat = new THREE.MeshLambertMaterial({
      color: couvColor, transparent: true, opacity: 0.4, side: THREE.DoubleSide
    });

    // ===== MUR ARRIERE D'ADOSSEMENT (simule mur existant maison) =====
    const murArriereMat = new THREE.MeshLambertMaterial({
      color: 0xd4ccb6,
      transparent: true,
      opacity: 0.85,
      side: THREE.DoubleSide
    });
    addBox(L + 0.5, Hhaut + 0.3, 0.25, 0, (Hhaut + 0.3)/2, lg/2, murArriereMat);

    // ===== POTEAUX AVANT (specificite appentis : cote ouvert) =====
    // Poteaux intermediaires si appentis long
    const sectionPotau = 0.18;
    const nbPoteauxLong = Math.max(1, Math.ceil(L / 4));
    for (let i = 0; i <= nbPoteauxLong; i++) {
      const x = -L/2 + (i / nbPoteauxLong) * L;
      addBox(sectionPotau, Hbas, sectionPotau, x, Hbas/2, -lg/2, woodMat);
    }

    // ===== PETITS MURS LATERAUX TRAPEZOIDAUX =====
    // Cote gauche
    const triGeoL = new THREE.BufferGeometry();
    const triVertL = new Float32Array([
      -L/2, 0, -lg/2,
      -L/2, Hbas, -lg/2,
      -L/2, Hhaut, lg/2,
      -L/2, 0, -lg/2,
      -L/2, Hhaut, lg/2,
      -L/2, 0, lg/2,
    ]);
    triGeoL.setAttribute("position", new THREE.BufferAttribute(triVertL, 3));
    triGeoL.computeVertexNormals();
    scene.add(new THREE.Mesh(triGeoL, wallMat));

    // Cote droit
    const triGeoR = new THREE.BufferGeometry();
    const triVertR = new Float32Array([
      L/2, 0, -lg/2,
      L/2, Hbas, -lg/2,
      L/2, Hhaut, lg/2,
      L/2, 0, -lg/2,
      L/2, Hhaut, lg/2,
      L/2, 0, lg/2,
    ]);
    triGeoR.setAttribute("position", new THREE.BufferAttribute(triVertR, 3));
    triGeoR.computeVertexNormals();
    scene.add(new THREE.Mesh(triGeoR, wallMat));

    // ===== SABLIERES (basse avant + haute arriere contre mur) =====
    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2, woodMat);
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2, woodMat);

    // ===== PANNES INTERMEDIAIRES (3, bien reparties) =====
    const nbPannes = 3;
    const pannePositions = [];
    for (let i = 0; i < nbPannes; i++) {
      const t = (i + 1) / (nbPannes + 1);
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
    const espLiteau = 0.35;
    const nbLiteaux = Math.max(4, Math.floor(longueurChevron / espLiteau));
    for (let i = 0; i <= nbLiteaux; i++) {
      const t = i / nbLiteaux;
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele + 0.15;  // au-dessus des chevrons
      addBox(L + 0.4, 0.025, 0.04, 0, y, z, woodMat);
    }

    // ===== AISSELIERS (jambes de force obliques aux pignons) =====
    const aisselierAngles = [pannePositions[0], pannePositions[1]];
    [-1, 1].forEach((cote) => {
      const xMur = cote * (L/2 - 0.08);
      aisselierAngles.forEach((p) => {
        // Point bas : sur le mur lateral au niveau Hbas/2
        const xb = xMur;
        const yb = Hbas * 0.5;
        const zb = -lg/2 + (p.t * lg) * 0.4;
        // Point haut : sous la panne
        const xh = xMur;
        const yh = p.y - 0.08;
        const zh = p.z;
        const dy = yh - yb;
        const dz = zh - zb;
        const longueur = Math.sqrt(dy*dy + dz*dz);
        const rotX = Math.atan2(dy, dz) - Math.PI/2;
        const xc = (xb + xh) / 2;
        const yc = (yb + yh) / 2;
        const zc = (zb + zh) / 2;
        addBox(0.10, 0.10, longueur, xc, yc, zc, woodMat, [rotX, 0, 0]);
      });
    });

    // ===== COUVERTURE (1 pan, semi-transparente, couleur selon type) =====
    const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
    const roof = new THREE.Mesh(rg, appentisRoofMat);
    roof.position.set(0, yCentre + 0.20, 0);  // plus haut a cause des liteaux
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);
  };'''

# Marker unique a la version realiste appentis
if "APPENTIS REALISTE - charpente complete adossee" in content:
    print("[INFO] Appentis realiste deja en place")
elif old_appentis in content:
    content = content.replace(old_appentis, new_appentis, 1)
    print("[OK] drawAppentis enrichi -> version realiste")
    modifs += 1
else:
    print("[ERREUR] drawAppentis actuel non trouve exactement")
    print("[INFO] Verifie qu'aucune modif manuelle n'a ete faite sur drawAppentis.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATION APPLIQUEE")
print("=" * 60)
print()
print("APPENTIS REALISTE :")
print("  - Mur d'adossement (specificite) conserve")
print("  - Poteaux avant intermediaires si L > 4m")
print("  - Murs lateraux trapezoidaux conserves")
print("  - 2 sablieres (basse avant + haute contre mur)")
print("  - 3 PANNES intermediaires bien reparties (vs 2 avant)")
print("  - ~13 chevrons espaces de 0.5m (vs ~6 avant)")
print("  - LITEAUX : ~12 planchettes fines (section 2.5x4 cm)")
print("  - AISSELIERS : 4 jambes de force aux pignons")
print("  - Couverture semi-transparente, couleur selon type :")
print("      bac_acier   -> anthracite")
print("      tuile_beton -> brun-gris")
print("      tuile_terre -> orange (defaut)")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
