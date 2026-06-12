#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Enlever les cubes de debug (rouge/bleu) du carport
On les avait mis pour valider l'orientation, on les enleve maintenant.

A lancer depuis ~/Desktop/devia :
    python3 remove_debug_cubes.py
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

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_remove_debug"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# Enlever le bloc des reperes visuels debug
# ================================================================

old_debug_block = '''      // ============================================================
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

new_clean_end = '    };'

if old_debug_block not in content:
    print("ERREUR : bloc debug introuvable.")
    print("Les cubes ont peut-etre deja ete enleves.")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

content = content.replace(old_debug_block, new_clean_end, 1)
print("[OK] Cubes de debug retires")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("CUBES DE DEBUG SUPPRIMES")
print("=" * 60)
print()
print("PROCHAINE ETAPE :")
print("  git add devia.jsx")
print("  git commit -m 'Retirer cubes de debug carport'")
print("  git push")
print()
print(f"BACKUP : {backup_name}")
