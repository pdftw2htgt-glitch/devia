#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Desactive les aisseliers (monopente + appentis)
Les aisseliers en eventail dans le plan des pignons creaient du visuel sale.
On vide le tableau aisselierAngles -> la boucle forEach ne dessine plus rien.
Robuste : cible juste 2 lignes precises.
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_disable_aisseliers"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# Monopente : aisselierAngles = [pannePositions[1], pannePositions[2]]
old_mono = "const aisselierAngles = [pannePositions[1], pannePositions[2]];"
new_mono = "const aisselierAngles = [];  // aisseliers desactives (rendu plus propre)"
if old_mono in content:
    content = content.replace(old_mono, new_mono, 1)
    print("[OK] Aisseliers monopente desactives")
    modifs += 1
else:
    print("[INFO] Aisseliers monopente : ligne non trouvee (deja desactives ?)")

# Appentis : aisselierAngles = [pannePositions[0], pannePositions[1]]
old_app = "const aisselierAngles = [pannePositions[0], pannePositions[1]];"
new_app = "const aisselierAngles = [];  // aisseliers desactives (rendu plus propre)"
if old_app in content:
    content = content.replace(old_app, new_app, 1)
    print("[OK] Aisseliers appentis desactives")
    modifs += 1
else:
    print("[INFO] Aisseliers appentis : ligne non trouvee (deja desactives ?)")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)")
print("=" * 60)
print()
print("STRUCTURE CONSERVEE (propre et complete) :")
print("  - Chevrons denses (~0.5m)")
print("  - Pannes intermediaires bien reparties")
print("  - Liteaux (grille fine)")
print("  - Sablieres")
print("  - + specificites du type (murs / poteaux / mur d'adossement)")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup}")
