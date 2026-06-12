#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Inverser la pente carport (avant BAS, arriere HAUT)
Le precedent fix avait inverse dans le mauvais sens.
On corrige : avant (rouge) = BAS, arriere (bleu) = HAUT.

A lancer depuis ~/Desktop/devia :
    python3 fix_carport_pente_v2.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("package.json"):
    print("ERREUR : package.json introuvable. Lance depuis ~/Desktop/devia")
    sys.exit(1)

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_fix_pente_v2"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# Trouver et remplacer le bloc drawCarport entier
# ================================================================

old_drawcarport_marker_start = "const drawCarport = () => {"
old_drawcarport_marker_end = "      scene.add(debugBlue);\n    };"

if old_drawcarport_marker_start not in content:
    print("ERREUR : drawCarport introuvable.")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

start_idx = content.find(old_drawcarport_marker_start)
end_search = content.find(old_drawcarport_marker_end, start_idx)
if end_search == -1:
    print("ERREUR : fin de drawCarport (avec debugBlue) introuvable.")
    print("Le precedent script n'a peut-etre pas applique les reperes.")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

end_idx = end_search + len(old_drawcarport_marker_end)
old_block = content[start_idx:end_idx]
print(f"[INFO] Bloc drawCarport detecte : {len(old_block)} caracteres")

# Nouveau bloc : pente AVANT BAS, ARRIERE HAUT
new_block = '''const drawCarport = () => {
      // Carport : la pente descend de l'ARRIERE (Z=+lg/2, haut) vers l'AVANT (Z=-lg/2, bas)
      // C'est l'inverse du fix precedent.
      const denivele = lg * Math.tan((pente * Math.PI) / 180);
      const Hbas = H;
      const Hhaut = H + denivele;

      // 4 POTAUX
      // AVANT (Z negatif, cube ROUGE) = potaux BAS
      // ARRIERE (Z positif, cube BLEU) = potaux HAUTS
      const sectionPotau = 0.18;
      // Potau avant gauche (BAS)
      addBox(sectionPotau, Hbas, sectionPotau, -L/2, Hbas/2, -lg/2);
      // Potau avant droit (BAS)
      addBox(sectionPotau, Hbas, sectionPotau, L/2, Hbas/2, -lg/2);
      // Potau arriere gauche (HAUT)
      addBox(sectionPotau, Hhaut, sectionPotau, -L/2, Hhaut/2, lg/2);
      // Potau arriere droit (HAUT)
      addBox(sectionPotau, Hhaut, sectionPotau, L/2, Hhaut/2, lg/2);

      // 2 SABLIERES
      // Sabliere avant (en bas)
      addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2);
      // Sabliere arriere (en haut)
      addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2);

      // PANNES (entre sablieres, suivent la pente)
      const nbPannes = 3;
      for (let i = 0; i < nbPannes; i++) {
        const t = i / (nbPannes - 1); // 0 a 1
        const z = -lg/2 + t * lg;       // de avant a arriere
        const y = Hbas + t * denivele;  // de bas a haut (pente montante avant->arriere)
        addBox(L + 0.3, 0.14, 0.14, 0, y, z);
      }

      // CHEVRONS (sens largeur, en pente)
      const nbChevrons = Math.max(3, Math.ceil(L / 1.0));
      const ang = Math.atan(denivele / lg);
      const longueurChevron = lg / Math.cos(ang);
      for (let i = 0; i <= nbChevrons; i++) {
        const x = -L/2 + (i / nbChevrons) * L;
        const yCentre = Hbas + denivele/2;
        // Rotation X positive pour pente avant bas -> arriere haut
        addBox(0.10, 0.10, longueurChevron + 0.2, x, yCentre, 0, woodMat, [ang, 0, 0]);
      }

      // TOITURE (1 seul pan)
      const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
      const roof = new THREE.Mesh(rg, roofMat);
      roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
      // Rotation positive pour que la pente monte vers l'arriere
      roof.rotation.x = ang - Math.PI/2;
      scene.add(roof);

      // ============================================================
      // REPERES VISUELS DEBUG (a enlever quand orientation validee)
      // ROUGE = avant (Z negatif) ; BLEU = arriere (Z positif)
      // ============================================================
      const debugRedMat = new THREE.MeshLambertMaterial({ color: 0xff3344 });
      const debugBlueMat = new THREE.MeshLambertMaterial({ color: 0x3399ff });
      const debugRed = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 0.4), debugRedMat);
      debugRed.position.set(0, 0.2, -lg/2 - 0.5);
      scene.add(debugRed);
      const debugBlue = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 0.4), debugBlueMat);
      debugBlue.position.set(0, 0.2, lg/2 + 0.5);
      scene.add(debugBlue);
    };'''

content = content[:start_idx] + new_block + content[end_idx:]
print("[OK] drawCarport corrige : avant BAS, arriere HAUT")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("FIX V2 APPLIQUE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  - AVANT (cube ROUGE) = potaux BAS")
print("  - ARRIERE (cube BLEU) = potaux HAUTS")
print("  - Pente descend du BLEU (arriere haut) vers le ROUGE (avant bas)")
print()
print("PROCHAINE ETAPE :")
print("  git add devia.jsx")
print("  git commit -m 'Fix sens pente carport v2'")
print("  git push")
print()
print(f"BACKUP : {backup_name}")
