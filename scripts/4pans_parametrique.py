#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D : Toit 4 PANS / CROUPE PARAMETRIQUE (charpente complete)

Reecrit entierement draw4Pans avec la vraie charpente de croupe :
  - Faitage central (longueur correcte = L - 2*recul, recul = profondeur croupe)
  - 4 aretiers (faitage -> 4 coins) conserves
  - EMPANNONS : chevrons courts s'appuyant sur les aretiers (signature croupe)
  - Chevrons sur les 2 grands pans (densite adaptative)
  - Pannes sur les grands pans (nb adaptatif)
  - Sablieres de chainage sur les 4 murs
  - Liteaux sur les pans
  - Couverture 4 pans SEMI-TRANSPARENTE (couleur selon couverture)

Reperage robuste par comptage d'accolades (independant du contenu exact).
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_4pans_parametrique"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# Reperage de draw4Pans par comptage d'accolades
# ================================================================
start_marker = "const draw4Pans = () => {"
start_pos = content.find(start_marker)
if start_pos == -1:
    print("[ERREUR] 'const draw4Pans = () => {' introuvable.")
    sys.exit(1)

line_start = content.rfind("\n", 0, start_pos) + 1
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
    print("[ERREUR] Accolade fermante de draw4Pans introuvable.")
    sys.exit(1)

end_pos = end_brace + 1
if end_pos < len(content) and content[end_pos] == ";":
    end_pos += 1

old_function = content[line_start:end_pos]

if "const draw4Pans" not in old_function or not old_function.rstrip().endswith("};"):
    print("[ERREUR] Extraction suspecte, abandon (pas de modif).")
    print("--- debut ---"); print(old_function[:120])
    print("--- fin ---");   print(old_function[-120:])
    sys.exit(1)

print(f"[OK] draw4Pans reperee ({old_function.count(chr(10))+1} lignes)")

# ================================================================
# Nouvelle fonction parametrique
# ================================================================
new_function = '''  const draw4Pans = () => {
    // ============================================================
    // TOIT 4 PANS / CROUPE PARAMETRIQUE - charpente complete
    // S'adapte aux dimensions et a la couverture demandees.
    // (sections indicatives - calcul structurel = phase 2.B)
    // ============================================================
    const hf = (lg / 2) * Math.tan((pente * Math.PI) / 180); // hauteur faitage
    const yFait = Ht + hf;

    // Recul de croupe = profondeur horizontale du pan de croupe.
    // Par convention on prend la meme pente que les grands pans -> recul = lg/2.
    // Mais on borne pour garder un faitage visible meme si L est court.
    const reculCroupe = Math.min(lg / 2, (L - 0.6) / 2);
    const Lfait = Math.max(0.4, L - 2 * reculCroupe);
    const xFaitGauche = -Lfait / 2;
    const xFaitDroit = Lfait / 2;

    // ===== REGLES METIER ADAPTATIVES =====
    const typeCouv = (opts && opts.couverture) ? opts.couverture : "tuile_terre";
    let couvColor, espChevron, espLiteau;
    if (typeCouv === "bac_acier") {
      couvColor = 0x3a3a3f;  espChevron = 0.70;  espLiteau = 0.50;
    } else if (typeCouv === "tuile_beton") {
      couvColor = 0x8b6355;  espChevron = 0.45;  espLiteau = 0.32;
    } else {
      couvColor = 0xc87650;  espChevron = 0.50;  espLiteau = 0.35;
    }
    const roof4Mat = new THREE.MeshLambertMaterial({
      color: couvColor, transparent: true, opacity: 0.4, side: THREE.DoubleSide
    });

    // Geometrie des grands pans
    const angLong = Math.atan(hf / (lg / 2));
    const plLong = (lg / 2) / Math.cos(angLong);   // longueur rampant grand pan
    const secChevron = plLong > 4.5 ? 0.10 : (plLong > 3 ? 0.09 : 0.08);

    // Nb de pannes par pan (un chevron ne franchit pas > ~2.2 m)
    const nbPannes = Math.max(1, Math.ceil(plLong / 2.2) - 1);

    // ===== MURS (4 cotes) =====
    [
      [L, Ht, 0.15, 0, Ht/2, lg/2],
      [L, Ht, 0.15, 0, Ht/2, -lg/2],
      [0.15, Ht, lg, -L/2, Ht/2, 0],
      [0.15, Ht, lg, L/2, Ht/2, 0]
    ].forEach(([sx, sy, sz, px, py, pz]) => addBox(sx, sy, sz, px, py, pz, wallMat));

    // ===== SABLIERES DE CHAINAGE (haut des 4 murs) =====
    addBox(L + 0.2, 0.16, 0.16, 0, Ht, lg/2, woodMat);
    addBox(L + 0.2, 0.16, 0.16, 0, Ht, -lg/2, woodMat);
    addBox(0.16, 0.16, lg, -L/2, Ht, 0, woodMat);
    addBox(0.16, 0.16, lg, L/2, Ht, 0, woodMat);

    // ===== FAITAGE (central) =====
    addBox(Lfait, 0.15, 0.15, 0, yFait, 0, woodMat);

    // ===== ARETIERS (faitage -> 4 coins) =====
    const coins = [
      [xFaitGauche, [-L/2, Ht, lg/2]],
      [xFaitGauche, [-L/2, Ht, -lg/2]],
      [xFaitDroit,  [L/2, Ht, lg/2]],
      [xFaitDroit,  [L/2, Ht, -lg/2]],
    ];
    coins.forEach(([xf, [cxp, cyp, czp]]) => {
      addBeam(cxp, cyp, czp, xf, yFait, 0, 0.12, woodMat);
    });

    // ===== PANNES sur les 2 grands pans (nb adaptatif) =====
    // Longueur de la panne diminue en montant (les pans se rapprochent du faitage)
    for (let i = 1; i <= nbPannes; i++) {
      const t = i / (nbPannes + 1);
      const yPanne = Ht + hf * t;
      const zPanne = (lg / 2) * (1 - t);
      const lenPanne = Lfait + (L - Lfait) * (1 - t);
      addBox(lenPanne, 0.12, 0.12, 0, yPanne, zPanne, woodMat);   // pan avant
      addBox(lenPanne, 0.12, 0.12, 0, yPanne, -zPanne, woodMat);  // pan arriere
    }

    // ===== CHEVRONS sur les 2 grands pans (entre les aretiers) =====
    // Uniquement dans la zone du faitage (au-dela, ce sont les empannons)
    const nbChevGrandPan = Math.max(2, Math.floor(Lfait / espChevron));
    for (let i = 0; i <= nbChevGrandPan; i++) {
      const x = xFaitGauche + (i / nbChevGrandPan) * Lfait;
      // pan avant (Z+)
      addBeam(x, Ht, lg/2, x, yFait, 0, secChevron, woodMat);
      // pan arriere (Z-)
      addBeam(x, Ht, -lg/2, x, yFait, 0, secChevron, woodMat);
    }

    // ===== EMPANNONS (chevrons courts s'appuyant sur les aretiers) =====
    // Signature de la croupe : sur chaque pan, des chevrons de longueur
    // decroissante qui butent sur l'aretier au lieu d'atteindre le faitage.
    const empannonsParCote = Math.max(2, Math.floor(reculCroupe / espChevron));

    // Helper local : projette un point du bas de pan vers l'aretier correspondant
    const drawEmpannonsGrandPan = (signZ) => {
      // Cote gauche (vers aretier gauche) et droit (vers aretier droit)
      [[-1, xFaitGauche, -L/2], [1, xFaitDroit, L/2]].forEach(([signX, xf, xCoin]) => {
        for (let i = 1; i <= empannonsParCote; i++) {
          const f = i / (empannonsParCote + 1);
          // point bas : sur la sabliere, entre le coin et le debut du faitage
          const xb = xCoin + (xf - xCoin) * f;
          const zb = signZ * (lg/2);
          // point haut : sur l'aretier, a la meme fraction
          const xh = xCoin + (xf - xCoin) * f;
          const yh = Ht + hf * f;
          const zh = signZ * (lg/2) * (1 - f);
          addBeam(xb, Ht, zb, xh, yh, zh, secChevron * 0.9, woodMat);
        }
      });
    };
    drawEmpannonsGrandPan(1);   // grand pan avant
    drawEmpannonsGrandPan(-1);  // grand pan arriere

    // ===== EMPANNONS DE CROUPE (sur les 2 triangles de bout) =====
    const drawEmpannonsCroupe = (signX) => {
      const xCoinAv = signX * (L/2);
      const xf = signX * (Lfait/2);
      const nbEmp = Math.max(2, Math.floor((lg/2) / espChevron));
      for (let i = 1; i <= nbEmp; i++) {
        const f = i / (nbEmp + 1);
        // point bas sur la sabliere de pignon (varie en Z)
        const zb = -lg/2 + f * lg;
        const xb = signX * (L/2);
        // point haut : sur l'aretier le plus proche
        // aretier avant si zb>0, arriere si zb<0
        const signZ = zb >= 0 ? 1 : -1;
        const fAr = 1 - Math.abs(zb) / (lg/2);  // fraction le long de l'aretier
        const xh = xCoinAv + (xf - xCoinAv) * fAr;
        const yh = Ht + hf * fAr;
        const zh = signZ * (lg/2) * (1 - fAr);
        addBeam(xb, Ht, zb, xh, yh, zh, secChevron * 0.85, woodMat);
      }
    };
    drawEmpannonsCroupe(-1);  // croupe gauche
    drawEmpannonsCroupe(1);   // croupe droite

    // ===== COUVERTURE 4 PANS (semi-transparente) =====
    // Grand pan avant
    const panAvGeo = new THREE.BufferGeometry();
    panAvGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array([
      -L/2, Ht, lg/2,   L/2, Ht, lg/2,   xFaitDroit, yFait, 0,
      -L/2, Ht, lg/2,   xFaitDroit, yFait, 0,   xFaitGauche, yFait, 0,
    ]), 3));
    panAvGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(panAvGeo, roof4Mat));

    // Grand pan arriere
    const panArGeo = new THREE.BufferGeometry();
    panArGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array([
      -L/2, Ht, -lg/2,   xFaitGauche, yFait, 0,   xFaitDroit, yFait, 0,
      -L/2, Ht, -lg/2,   xFaitDroit, yFait, 0,   L/2, Ht, -lg/2,
    ]), 3));
    panArGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(panArGeo, roof4Mat));

    // Croupe gauche
    const croupeGGeo = new THREE.BufferGeometry();
    croupeGGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array([
      -L/2, Ht, -lg/2,   -L/2, Ht, lg/2,   xFaitGauche, yFait, 0,
    ]), 3));
    croupeGGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(croupeGGeo, roof4Mat));

    // Croupe droite
    const croupeDGeo = new THREE.BufferGeometry();
    croupeDGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array([
      L/2, Ht, -lg/2,   xFaitDroit, yFait, 0,   L/2, Ht, lg/2,
    ]), 3));
    croupeDGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(croupeDGeo, roof4Mat));
  };'''

content = content[:line_start] + new_function + content[end_pos:]

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print("[OK] draw4Pans remplacee par la version parametrique")
print()
print("=" * 60)
print("1 MODIFICATION APPLIQUEE")
print("=" * 60)
print()
print("TOIT 4 PANS / CROUPE - charpente complete :")
print("  - Faitage central (longueur correcte, bornee)")
print("  - Sablieres de chainage (4 murs)")
print("  - 4 aretiers (faitage -> coins)")
print("  - Pannes sur grands pans (nb adaptatif)")
print("  - Chevrons grands pans (zone faitage)")
print("  - EMPANNONS sur grands pans + croupes (signature croupe)")
print("  - Couverture 4 pans semi-transparente (couleur selon type)")
print()
print("PROCHAINE ETAPE :  npm run build")
print()
print(f"BACKUP : {backup}")
