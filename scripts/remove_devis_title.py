#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Enlever le titre 'Generez votre devis charpente'
Garde le sous-titre comme indication discrete.

A lancer depuis ~/Desktop/devia :
    python3 remove_devis_title.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_remove_title"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD : Enlever le H1 (le titre), garder juste le sous-titre
# ================================================================

old_hero = '''<div style={{ textAlign: "center", marginBottom: 40, paddingTop: 16 }}>
              <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 12, letterSpacing: "-0.02em", lineHeight: 1.1 }}>Generez votre devis <span style={{ background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>charpente</span></h1>
              <p style={{ color: "#7a7d92", fontSize: 15, maxWidth: 520, margin: "0 auto", lineHeight: 1.55 }}>Decrivez votre projet en langage naturel. DEVIA genere un devis professionnel et une visualisation 3D.</p>
            </div>'''

new_hero = '''<div style={{ marginBottom: 24, paddingTop: 4 }}>
              <p style={{ color: "#7a7d92", fontSize: 14, lineHeight: 1.55 }}>Decrivez votre projet en langage naturel. DEVIA genere un devis professionnel et une visualisation 3D.</p>
            </div>'''

if 'Generez votre devis' not in content:
    print("[INFO] Titre deja enleve")
elif old_hero in content:
    content = content.replace(old_hero, new_hero, 1)
    print("[OK] Titre H1 enleve, sous-titre conserve (plus discret, aligne a gauche)")
else:
    print("[ERREUR] Bloc hero non trouve exactement.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("TITRE ENLEVE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  - Plus de gros titre 'Generez votre devis charpente'")
print("  - Sous-titre conserve mais plus discret et aligne a gauche")
print("  - Espace blanc reduit (plus pro)")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Enleve titre hero page Devis'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
