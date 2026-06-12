#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Remplacer le logo 'D' par l'image logo-devia.png dans le header

A lancer depuis ~/Desktop/devia :
    python3 update_logo_header.py

Apres : npm run build
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

if not os.path.exists("public/logo-devia.jpeg"):
    print("ERREUR : public/logo-devia.jpeg introuvable.")
    print("Verifie que tu as bien mis le logo dans le dossier public/")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_logo_image"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD : Remplacer le div carre jaune avec 'D' par une img
# ================================================================

old_logo = '''<div style={{
        width: 30,
        height: 30,
        background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)",
        borderRadius: 9,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 15,
        fontWeight: 800,
        color: "#0a0a0a",
        boxShadow: "0 2px 8px rgba(240,192,64,0.25)"
      }}>D</div>'''

new_logo = '''<img
        src="/logo-devia.jpeg"
        alt="DEVIA"
        style={{
          width: 32,
          height: 32,
          borderRadius: 9,
          objectFit: "cover",
          boxShadow: "0 2px 8px rgba(0,0,0,0.3)"
        }}
      />'''

if 'src="/logo-devia.jpeg"' in content:
    print("[INFO] Logo image deja en place")
elif old_logo in content:
    content = content.replace(old_logo, new_logo, 1)
    print("[OK] Logo 'D' remplace par image logo-devia.png")
else:
    print("[ERREUR] Logo actuel non trouve.")
    print("Verifie que tu n'as pas deja modifie le header autrement.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("LOGO REMPLACE")
print("=" * 60)
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx public/logo-devia.jpeg")
print("    git commit -m 'Logo perso dans le header'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
