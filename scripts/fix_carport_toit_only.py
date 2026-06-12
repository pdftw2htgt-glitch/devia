#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Inverser UNIQUEMENT l'orientation du toit du carport
La structure (potaux, sablieres, chevrons) reste telle quelle.
Seul le toit (le plan de couverture) est tourne sur l'autre axe.

A lancer depuis ~/Desktop/devia :
    python3 fix_carport_toit_only.py
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

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_toit_only"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# Trouver et remplacer UNIQUEMENT la section TOITURE de drawCarport
# ================================================================

# La section actuelle de la toiture du carport (apres modif precedente)
old_toiture = '''      // TOITURE (1 seul pan)
      const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
      const roof = new THREE.Mesh(rg, roofMat);
      roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
      // Rotation positive pour que la pente monte vers l'arriere
      roof.rotation.x = ang - Math.PI/2;
      scene.add(roof);'''

new_toiture = '''      // TOITURE (1 seul pan, rotation sur axe X au lieu de Z)
      // Le toit est tourne dans l'autre dimension par rapport a la structure
      const rg = new THREE.PlaneGeometry(longueurChevron + 0.3, L + 0.4);
      const roof = new THREE.Mesh(rg, roofMat);
      roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
      // Combinaison de rotations pour que le toit penche cote gauche/droite
      roof.rotation.z = ang;
      roof.rotation.y = Math.PI/2;
      scene.add(roof);'''

if old_toiture not in content:
    # Tentative avec une variante plus laxiste
    print("ERREUR : section TOITURE introuvable avec le pattern attendu.")
    print("Le code a peut-etre ete modifie autrement.")
    print("Restoration du backup...")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

content = content.replace(old_toiture, new_toiture, 1)
print("[OK] Section TOITURE inversee")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("FIX TOITURE APPLIQUE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  - Seule la rotation du toit est modifiee")
print("  - Le toit penche maintenant cote gauche/droite (axe X)")
print("  - La structure (potaux, sablieres, chevrons) reste telle quelle")
print()
print("PROCHAINE ETAPE :")
print("  git add devia.jsx")
print("  git commit -m 'Inverser orientation toit carport'")
print("  git push")
print()
print(f"BACKUP : {backup_name}")
