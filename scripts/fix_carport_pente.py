#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix sens pente carport + repere visuel debug
Modifie devia.jsx pour :
1. Inverser le sens de pente du carport (avant en haut, arriere en bas)
2. Ajouter 2 cubes de repere : ROUGE = avant, BLEU = arriere

Les cubes de repere sont temporaires pour debug.
A enlever quand l'orientation sera 100% validee.

A lancer depuis ~/Desktop/devia :
    python3 fix_carport_pente.py
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

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_fix_pente"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# Trouver et remplacer le bloc drawCarport entier
# ================================================================

old_drawcarport_marker_start = "const drawCarport = () => {"
old_drawcarport_marker_end = "      scene.add(roof);\n    };"

if old_drawcarport_marker_start not in content:
    print("ERREUR : drawCarport introuvable.")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

start_idx = content.find(old_drawcarport_marker_start)
end_search = content.find(old_drawcarport_marker_end, start_idx)
if end_search == -1:
    print("ERREUR : fin de drawCarport introuvable.")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

end_idx = end_search + len(old_drawcarport_marker_end)
old_block = content[start_idx:end_idx]
print(f"[INFO] Bloc drawCarport detecte : {len(old_block)} caracteres")

# Nouveau bloc drawCarport avec pente inversee + reperes
new_block = '''const drawCarport = () => {
      // Carport : la pente descend de l'AVANT (Z=-lg/2, haut) vers l'ARRIERE (Z=+lg/2, bas)
      const denivele = lg * Math.tan((pente * Math.PI) / 180);
      const Hbas = H;
      const Hhaut = H + denivele;

      // 4 POTAUX (un a chaque coin)
      // AVANT (Z negatif) = potaux HAUTS
      // ARRIERE (Z positif) = potaux BAS
      const sectionPotau = 0.18;
      // Potau avant gauche (HAUT)
      addBox(sectionPotau, Hhaut, sectionPotau, -L/2, Hhaut/2, -lg/2);
      // Potau avant droit (HAUT)
      addBox(sectionPotau, Hhaut, sectionPotau, L/2, Hhaut/2, -lg/2);
      // Potau arriere gauche (BAS)
      addBox(sectionPotau, Hbas, sectionPotau, -L/2, Hbas/2, lg/2);
      // Potau arriere droit (BAS)
      addBox(sectionPotau, Hbas, sectionPotau, L/2, Hbas/2, lg/2);

      // 2 SABLIERES (poutres horizontales hautes, sens longueur)
      // Sabliere avant (en haut)
      addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, -lg/2);
      // Sabliere arriere (en bas)
      addBox(L + 0.3, 0.16, 0.16, 0, Hbas, lg/2);

      // PANNES (entre sablieres, suivent la pente decroissante)
      const nbPannes = 3;
      for (let i = 0; i < nbPannes; i++) {
        const t = i / (nbPannes - 1); // 0 a 1
        const z = -lg/2 + t * lg;       // de avant a arriere
        const y = Hhaut - t * denivele; // de haut a bas (pente descendante)
        addBox(L + 0.3, 0.14, 0.14, 0, y, z);
      }

      // CHEVRONS (sens largeur, en pente)
      const nbChevrons = Math.max(3, Math.ceil(L / 1.0));
      const ang = Math.atan(denivele / lg);
      const longueurChevron = lg / Math.cos(ang);
      for (let i = 0; i <= nbChevrons; i++) {
        const x = -L/2 + (i / nbChevrons) * L;
        const yCentre = Hbas + denivele/2;
        // Rotation X negative pour pente descendante avant->arriere
        addBox(0.10, 0.10, longueurChevron + 0.2, x, yCentre, 0, woodMat, [-ang, 0, 0]);
      }

      // TOITURE (1 seul pan, pente descendante avant->arriere)
      const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
      const roof = new THREE.Mesh(rg, roofMat);
      roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
      // Rotation negative pour que la pente descende vers l'arriere
      roof.rotation.x = -(ang - Math.PI/2);
      scene.add(roof);

      // ============================================================
      // REPERES VISUELS DEBUG (a enlever quand orientation validee)
      // Cube ROUGE = avant (Z negatif)
      // Cube BLEU = arriere (Z positif)
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
print("[OK] drawCarport corrige + reperes ajoutes")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("FIX APPLIQUE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Pente du carport INVERSEE :")
print("     - Avant (cote rouge) = HAUT")
print("     - Arriere (cote bleu) = BAS")
print("  2. Cubes de repere ajoutes :")
print("     - ROUGE devant le carport (avant)")
print("     - BLEU derriere le carport (arriere)")
print()
print("PROCHAINE ETAPE :")
print("  1. git add devia.jsx")
print("  2. git commit -m 'Fix sens pente carport + reperes debug'")
print("  3. git push")
print("  4. Tester sur devia-iota.vercel.app : refaire un carport")
print("  5. Verifier : pente descend du ROUGE vers le BLEU")
print()
print("REMARQUE : les cubes rouge et bleu sont TEMPORAIRES.")
print("Une fois l'orientation validee, on les enlevera.")
print()
print(f"BACKUP : {backup_name}")
