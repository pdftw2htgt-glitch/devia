#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D : Monopente couverture SEMI-TRANSPARENTE
Patch pour rendre la couverture de la monopente visible-a-travers
afin de voir la structure (chevrons, pannes, sablieres) qui etait masquee.
La couleur reste dynamique selon le type (bac_acier / tuile_terre / tuile_beton).
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_monopente_transparente"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

old = '''    const monopenteRoofMat = new THREE.MeshLambertMaterial({
      color: couvColor, side: THREE.DoubleSide
    });'''

new = '''    const monopenteRoofMat = new THREE.MeshLambertMaterial({
      color: couvColor, transparent: true, opacity: 0.4, side: THREE.DoubleSide
    });'''

if "color: couvColor, transparent: true, opacity: 0.4, side: THREE.DoubleSide" in content:
    print("[INFO] Couverture monopente deja semi-transparente")
elif old in content:
    content = content.replace(old, new, 1)
    print("[OK] Couverture monopente : opaque -> semi-transparente (opacity 0.4)")
    modifs += 1
else:
    print("[ERREUR] Bloc monopenteRoofMat non trouve")
    print("[INFO] Verifie que monopente_technique.py a bien ete applique avant.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATION APPLIQUEE")
print("=" * 60)
print()
print("La structure (chevrons, pannes, sablieres) sera maintenant")
print("visible a travers la couverture, qui garde sa couleur teintee.")
print()
print(f"BACKUP : {backup_name}")
