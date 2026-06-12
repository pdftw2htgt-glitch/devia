#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Renommer le champ en 'Localisation' avec placeholder clair

A lancer depuis ~/Desktop/devia :
    python3 rename_to_localisation.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_localisation"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# MOD 1 : Label - remplacer Commune / Adresse par Localisation
old_label_v2 = '<label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Commune <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>/ Adresse</span></label>'
new_label = '<label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Localisation</label>'

old_label_v1 = '<label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Commune</label>'

if '>Localisation</label>' in content:
    print("[INFO] Label deja en 'Localisation'")
elif old_label_v2 in content:
    content = content.replace(old_label_v2, new_label, 1)
    print("[OK] Label 'Commune / Adresse' -> 'Localisation'")
    modifs += 1
elif old_label_v1 in content:
    content = content.replace(old_label_v1, new_label, 1)
    print("[OK] Label 'Commune' -> 'Localisation'")
    modifs += 1
else:
    print("[WARN] Label non trouve.")

# MOD 2 : Placeholder
old_placeholder_v2 = 'placeholder="Ex: Lyon ou 12 rue de Paris, 75001 Paris"'
old_placeholder_v1 = 'placeholder="Lyon, Grenoble, Paris..."'
new_placeholder = 'placeholder="Ville, code postal ou adresse complete"'

if new_placeholder in content:
    print("[INFO] Placeholder deja a jour")
elif old_placeholder_v2 in content:
    content = content.replace(old_placeholder_v2, new_placeholder, 1)
    print("[OK] Placeholder mis a jour")
    modifs += 1
elif old_placeholder_v1 in content:
    content = content.replace(old_placeholder_v1, new_placeholder, 1)
    print("[OK] Placeholder mis a jour")
    modifs += 1
else:
    print("[WARN] Placeholder non trouve.")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print(f"=== {modifs} modifications appliquees ===")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print('    git commit -m "Renomme Commune en Localisation"')
print("    git push")
print()
print(f"BACKUP : {backup_name}")
