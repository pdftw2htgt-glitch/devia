#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D : Appentis PARAMETRIQUE (charpente complete adaptative)

Reecrit entierement drawAppentis avec une charpente qui s'adapte aux
dimensions (L, lg, pente, hauteur) et a la couverture demandee :
  - nb de pannes calcule (un chevron ne franchit pas > ~2.2 m sans appui)
  - espacement chevrons selon la couverture (bac acier / tuiles)
  - sections (chevrons, pannes, sablieres) qui grossissent avec la portee
  - nb de poteaux avant selon la longueur
  - liteaux espaces selon la couverture
  - echantignoles a chaque croisement chevron x panne

NB : les sections sont INDICATIVES (proportions realistes), pas un
calcul structurel certifie -> ca, c'est la phase 2.B (validation prof).

Reperage robuste : trouve la fonction par comptage d'accolades, donc
independant du contenu exact actuel de drawAppentis.
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_appentis_parametrique"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# Reperage de drawAppentis par comptage d'accolades
# ================================================================
start_marker = "const drawAppentis = () => {"
start_pos = content.find(start_marker)
if start_pos == -1:
    print("[ERREUR] 'const drawAppentis = () => {' introuvable.")
    sys.exit(1)

# Inclure l'indentation en debut de ligne
line_start = content.rfind("\n", 0, start_pos) + 1

# Position de l'accolade ouvrante de la fonction
brace_open = content.find("{", start_pos)
depth = 0
i = brace_open
end_brace = -1
while i < len(content):
    c = content[i]
    if c == "{":
        depth += 1
    elif c == "}":
        depth -= 1
        if depth == 0:
            end_brace = i
            break
    i += 1

if end_brace == -1:
    print("[ERREUR] Accolade fermante de drawAppentis introuvable.")
    sys.exit(1)

# Inclure le ';' apres '}'
end_pos = end_brace + 1
if end_pos < len(content) and content[end_pos] == ";":
    end_pos += 1

old_function = content[line_start:end_pos]

# Sanity checks
if "const drawAppentis" not in old_function or not old_function.rstrip().endswith("};"):
    print("[ERREUR] Extraction suspecte, abandon (pas de modif).")
    print("--- Extrait debut ---")
    print(old_function[:120])
    print("--- Extrait fin ---")
    print(old_function[-120:])
    sys.exit(1)

print(f"[OK] drawAppentis reperee ({old_function.count(chr(10))+1} lignes)")

# ================================================================
# Nouvelle fonction parametrique
# ================================================================
new_function = '''  const drawAppentis = () => {
    // ============================================================
    // APPENTIS PARAMETRIQUE - charpente complete adaptative
    // S'adapte aux dimensions et a la couverture demandees.
    // (sections indicatives - calcul structurel = phase 2.B)
    // ============================================================
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;             // hauteur cote avant (libre)
    const Hhaut = Ht + denivele; // hauteur mur arriere (mur maison)
    const ang = Math.atan(denivele / lg);
    const longueurRampant = lg / Math.cos(ang);  // longueur du pan incline
    const yCentre = Hbas + denivele/2;

    // ===== REGLES METIER ADAPTATIVES =====
    // 1) Couverture -> couleur + espacement chevrons + espacement liteaux
    const typeCouv = (opts && opts.couverture) ? opts.couverture : "tuile_terre";
    let couvColor, espChevron, espLiteau;
    if (typeCouv === "bac_acier") {
      couvColor = 0x3a3a3f;  espChevron = 0.70;  espLiteau = 0.50;  // porte loin
    } else if (typeCouv === "tuile_beton") {
      couvColor = 0x8b6355;  espChevron = 0.45;  espLiteau = 0.32;  // lourde
    } else {
      couvColor = 0xc87650;  espChevron = 0.50;  espLiteau = 0.35;  // tuile terre
    }
    const appentisRoofMat = new THREE.MeshLambertMaterial({
      color: couvColor, transparent: true, opacity: 0.4, side: THREE.DoubleSide
    });

    // 2) Nb de pannes : un chevron ne franchit pas plus de ~2.2 m sans appui
    const porteeMaxChevron = 2.2;
    const nbPannes = Math.max(1, Math.ceil(longueurRampant / porteeMaxChevron) - 1);

    // 3) Section chevrons : grossit avec la longueur du rampant
    const secChevron = longueurRampant > 4.5 ? 0.10 : (longueurRampant > 3 ? 0.09 : 0.08);

    // 4) Poteaux avant : 1 tous les ~3.5 m
    const nbPoteauxLong = Math.max(1, Math.ceil(L / 3.5));

    // 5) Section pannes : grossit avec la portee entre poteaux
    const porteePanne = L / nbPoteauxLong;
    const secPanne = porteePanne > 3.5 ? 0.18 : (porteePanne > 2 ? 0.15 : 0.13);

    // 6) Section sablieres : un peu plus fortes que les pannes
    const secSabliere = Math.min(0.20, secPanne + 0.02);

    // ===== MUR ARRIERE D'ADOSSEMENT (mur existant maison) =====
    const murArriereMat = new THREE.MeshLambertMaterial({
      color: 0xd4ccb6, transparent: true, opacity: 0.85, side: THREE.DoubleSide
    });
    addBox(L + 0.5, Hhaut + 0.3, 0.25, 0, (Hhaut + 0.3)/2, lg/2, murArriereMat);

    // ===== POTEAUX AVANT (cote ouvert, nb adaptatif) =====
    const secPoteau = 0.18;
    for (let i = 0; i <= nbPoteauxLong; i++) {
      const x = -L/2 + (i / nbPoteauxLong) * L;
      addBox(secPoteau, Hbas, secPoteau, x, Hbas/2, -lg/2, woodMat);
    }

    // ===== MURS LATERAUX TRAPEZOIDAUX (translucides) =====
    const triGeoL = new THREE.BufferGeometry();
    const triVertL = new Float32Array([
      -L/2, 0, -lg/2,  -L/2, Hbas, -lg/2,  -L/2, Hhaut, lg/2,
      -L/2, 0, -lg/2,  -L/2, Hhaut, lg/2,  -L/2, 0, lg/2,
    ]);
    triGeoL.setAttribute("position", new THREE.BufferAttribute(triVertL, 3));
    triGeoL.computeVertexNormals();
    scene.add(new THREE.Mesh(triGeoL, wallMat));

    const triGeoR = new THREE.BufferGeometry();
    const triVertR = new Float32Array([
      L/2, 0, -lg/2,  L/2, Hbas, -lg/2,  L/2, Hhaut, lg/2,
      L/2, 0, -lg/2,  L/2, Hhaut, lg/2,  L/2, 0, lg/2,
    ]);
    triGeoR.setAttribute("position", new THREE.BufferAttribute(triVertR, 3));
    triGeoR.computeVertexNormals();
    scene.add(new THREE.Mesh(triGeoR, wallMat));

    // ===== SABLIERES (basse avant + haute arriere contre mur) =====
    addBox(L + 0.3, secSabliere, secSabliere, 0, Hbas, -lg/2, woodMat);
    addBox(L + 0.3, secSabliere, secSabliere, 0, Hhaut, lg/2, woodMat);

    // ===== PANNES INTERMEDIAIRES (nb adaptatif, bien reparties) =====
    const pannePositions = [];
    for (let i = 0; i < nbPannes; i++) {
      const t = (i + 1) / (nbPannes + 1);
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele;
      addBox(L + 0.3, secPanne, secPanne, 0, y, z, woodMat);
      pannePositions.push({ y, z });
    }

    // ===== CHEVRONS (espacement + section adaptatifs) =====
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    const chevronXs = [];
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      chevronXs.push(x);
      addBox(secChevron, secChevron, longueurRampant + 0.2, x, yCentre + secChevron*0.8, 0, woodMat, [-ang, 0, 0]);
    }

    // ===== LITEAUX (perpendiculaires aux chevrons, espacement adaptatif) =====
    const nbLiteaux = Math.max(4, Math.floor(longueurRampant / espLiteau));
    for (let i = 0; i <= nbLiteaux; i++) {
      const t = i / nbLiteaux;
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele + secChevron + 0.07;
      addBox(L + 0.4, 0.025, 0.04, 0, y, z, woodMat);
    }

    // ===== ECHANTIGNOLES (cale a chaque croisement chevron x panne) =====
    // Petits taquets qui calent le chevron sur chaque panne (cote aval)
    chevronXs.forEach((x) => {
      pannePositions.forEach((p) => {
        const yEch = p.y + secPanne/2 + 0.03;
        const zEch = p.z - 0.07;
        addBox(secChevron * 0.9, 0.06, 0.10, x, yEch, zEch, woodMat);
      });
    });

    // ===== COUVERTURE (1 pan, semi-transparente, couleur selon type) =====
    const rg = new THREE.PlaneGeometry(L + 0.4, longueurRampant + 0.3);
    const roof = new THREE.Mesh(rg, appentisRoofMat);
    roof.position.set(0, yCentre + secChevron + 0.12, 0);
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);
  };'''

content = content[:line_start] + new_function + content[end_pos:]

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print("[OK] drawAppentis remplacee par la version parametrique")
print()
print("=" * 60)
print("1 MODIFICATION APPLIQUEE")
print("=" * 60)
print()
print("APPENTIS PARAMETRIQUE - tout s'adapte :")
print("  - Nb pannes      : selon longueur du rampant (max 2.2m/chevron)")
print("  - Esp. chevrons  : bac=0.70 / tuile beton=0.45 / tuile terre=0.50")
print("  - Section chevron: 0.08 -> 0.10 selon rampant")
print("  - Section panne  : 0.13 -> 0.18 selon portee entre poteaux")
print("  - Nb poteaux     : 1 tous les ~3.5m")
print("  - Liteaux        : espacement selon couverture")
print("  - Echantignoles  : 1 par croisement chevron x panne")
print()
print("PROCHAINE ETAPE :  npm run build")
print()
print(f"BACKUP : {backup}")
