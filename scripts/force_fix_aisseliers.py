#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix robuste aisseliers
Le script precedent utilisait un pattern strict sur un gros bloc et a rate
l'appentis (1 modif sur 2). Ici on cible directement les 3 lignes critiques
avec str.replace global -> beaucoup plus robuste, idempotent.
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_force_fix_aisseliers"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# --- FIX 1 : rotation (le bug critique) ---
n_avant = content.count("Math.atan2(dy, dz) - Math.PI/2")
content = content.replace("Math.atan2(dy, dz) - Math.PI/2", "-Math.atan2(dy, dz)")
n_apres = content.count("Math.atan2(dy, dz) - Math.PI/2")
n_fix = n_avant - n_apres
if n_fix > 0:
    print(f"[OK] {n_fix} rotation(s) corrigee(s)")
    modifs += n_fix
else:
    print("[INFO] Aucune rotation buggee a corriger (deja OK)")

# --- FIX 2 : point bas plus haut (yb) ---
n_avant = content.count("const yb = Hbas * 0.5;")
content = content.replace("const yb = Hbas * 0.5;", "const yb = Hbas * 0.7;")
n_apres = content.count("const yb = Hbas * 0.5;")
n_fix = n_avant - n_apres
if n_fix > 0:
    print(f"[OK] {n_fix} point bas remonte(s) (Hbas*0.5 -> Hbas*0.7)")
    modifs += n_fix
else:
    print("[INFO] Aucun yb a remonter (deja OK)")

# --- FIX 3 : point bas en Z fixe (effet fan) ---
n_avant = content.count("const zb = -lg/2 + (p.t * lg) * 0.4;")
content = content.replace("const zb = -lg/2 + (p.t * lg) * 0.4;", "const zb = -lg/2 + 0.3;")
n_apres = content.count("const zb = -lg/2 + (p.t * lg) * 0.4;")
n_fix = n_avant - n_apres
if n_fix > 0:
    print(f"[OK] {n_fix} point bas en Z fixe(s)")
    modifs += n_fix
else:
    print("[INFO] Aucun zb a fixer (deja OK)")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATION(S) APPLIQUEE(S) AU TOTAL")
print("=" * 60)
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup}")
