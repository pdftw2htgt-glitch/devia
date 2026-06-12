#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Vrai fix : surelever la card quand son dropdown est ouvert
Sans cela, le dropdown reste prisonnier du stacking context de sa card.
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_card_zindex"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# On modifie la card pour ajouter un z-index dynamique quand son dropdown est ouvert
# La card commence par : <div key={p.id} style={{ ... }}
# On cible le style precis de la card projet

old_card_style = '''<div key={p.id} style={{
                ...cardStyle,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: "pointer",
                marginBottom: 0,
                padding: 18,
                transition: "all 0.18s",
                gap: 14
              }}'''

new_card_style = '''<div key={p.id} style={{
                ...cardStyle,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: "pointer",
                marginBottom: 0,
                padding: 18,
                transition: "all 0.18s",
                gap: 14,
                position: "relative",
                zIndex: openProjectGroupDropdown === p.id ? 50 : 1
              }}'''

if "zIndex: openProjectGroupDropdown === p.id" in content:
    print("[INFO] Fix card z-index deja applique")
elif old_card_style in content:
    content = content.replace(old_card_style, new_card_style, 1)
    print("[OK] Card prend z-index 50 quand son dropdown est ouvert")
else:
    print("[ERREUR] Style de la card non trouve exactement")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Recharger Safari et retester")
print()
print(f"BACKUP : {backup_name}")
