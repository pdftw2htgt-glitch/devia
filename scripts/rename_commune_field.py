#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Renommer 'Commune' en 'Commune / Adresse'
Modifie 2 endroits :
1. Le label du champ
2. Le placeholder pour suggerer adresses complete

A lancer depuis ~/Desktop/devia :
    python3 rename_commune_field.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_rename_commune"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# MOD 1 : Label
old_label = '<label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Commune</label>'
new_label = '<label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Commune <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>/ Adresse</span></label>'

if 'Commune <span style={{ color: "#545870", textTransform: "none"' in content:
    print("[INFO] Label deja modifie")
elif old_label in content:
    content = content.replace(old_label, new_label, 1)
    print("[OK] Label : 'Commune' -> 'Commune / Adresse'")
    modifs += 1
else:
    print("[WARN] Label Commune non trouve exactement")

# MOD 2 : Placeholder
old_placeholder = 'placeholder="Lyon, Grenoble, Paris..."'
new_placeholder = 'placeholder="Ex: Lyon ou 12 rue de Paris, 75001 Paris"'

if 'Ex: Lyon ou 12 rue' in content:
    print("[INFO] Placeholder deja modifie")
elif old_placeholder in content:
    content = content.replace(old_placeholder, new_placeholder, 1)
    print("[OK] Placeholder : adresses completes suggerees")
    modifs += 1
else:
    print("[WARN] Placeholder Commune non trouve")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print(f"=== {modifs} modifications appliquees ===")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Champ Commune accepte adresse complete'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
