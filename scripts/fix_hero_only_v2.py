#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix hero v2 (sans test syntaxe esbuild qui plantait)
Le script precedent marchait, mais le test syntaxe etait foireux et restorait
le backup. On garde les memes modifs, on enleve le test.

A lancer depuis ~/Desktop/devia :
    python3 fix_hero_only_v2.py

Apres : npm run build pour tester la syntaxe.
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_fix_hero_v2"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# MOD 1 : Supprimer l'emoji
old_emoji = '<div style={{ fontSize: 48, marginBottom: 12 }}>🏗️</div>\n              '
if old_emoji in content:
    content = content.replace(old_emoji, '', 1)
    print("[OK] Emoji 🏗️ supprime")
    modifs += 1
else:
    old_emoji_alt = '<div style={{ fontSize: 48, marginBottom: 12 }}>🏗️</div>'
    if old_emoji_alt in content:
        content = content.replace(old_emoji_alt, '', 1)
        print("[OK] Emoji 🏗️ supprime (alt)")
        modifs += 1
    else:
        print("[INFO] Emoji deja supprime ou pas trouve")

# MOD 2 : Wrapper
old_wrapper = '<div style={{ textAlign: "center", marginBottom: 32 }}>'
new_wrapper = '<div style={{ textAlign: "center", marginBottom: 40, paddingTop: 16 }}>'
if new_wrapper in content:
    print("[INFO] Wrapper deja modifie")
elif old_wrapper in content:
    content = content.replace(old_wrapper, new_wrapper, 1)
    print("[OK] Wrapper hero : margin + padding")
    modifs += 1
else:
    print("[INFO] Wrapper hero non trouve")

# MOD 3 : Titre avec gradient
old_title = '<h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>Generez votre devis charpente</h1>'
new_title = '<h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 12, letterSpacing: "-0.02em", lineHeight: 1.1 }}>Generez votre devis <span style={{ background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>charpente</span></h1>'

if "WebkitBackgroundClip" in content:
    print("[INFO] Titre deja avec gradient")
elif old_title in content:
    content = content.replace(old_title, new_title, 1)
    print("[OK] Titre : gradient jaune sur 'charpente'")
    modifs += 1
else:
    print("[INFO] Titre non trouve")

# MOD 4 : Sous-titre
old_subtitle = '<p style={{ color: "#545870", fontSize: 15 }}>Decrivez votre projet - DEVIA genere un devis professionnel et une visualisation 3D</p>'
new_subtitle = '<p style={{ color: "#7a7d92", fontSize: 15, maxWidth: 520, margin: "0 auto", lineHeight: 1.55 }}>Decrivez votre projet en langage naturel. DEVIA genere un devis professionnel et une visualisation 3D.</p>'

if "en langage naturel" in content:
    print("[INFO] Sous-titre deja modifie")
elif old_subtitle in content:
    content = content.replace(old_subtitle, new_subtitle, 1)
    print("[OK] Sous-titre plus narratif")
    modifs += 1
else:
    print("[INFO] Sous-titre non trouve")

# MOD 5 : Label Documents
old_doc_label = '<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Documents - max 5</label>'
new_doc_label = '<label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Documents <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>(max 5)</span></label>'

if 'Documents <span style={{ color: "#545870", textTransform: "none"' in content:
    print("[INFO] Label Documents deja refondu")
elif old_doc_label in content:
    content = content.replace(old_doc_label, new_doc_label, 1)
    print("[OK] Label 'Documents - max 5' uppercase")
    modifs += 1
else:
    print("[INFO] Label Documents non trouve")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print(f"=== {modifs} modifications appliquees ===")
print()
print("=" * 60)
print("FIX HERO V2 APPLIQUE - SANS TEST SYNTAXE FOIREUX")
print("=" * 60)
print()
print("PROCHAINE ETAPE - IMPORTANT :")
print("  1. npm run build")
print("     -> Si OK : on commit")
print("     -> Si erreur : tu m'envoies l'erreur, je corrige")
print()
print("  2. SI BUILD OK :")
print("     git add devia.jsx")
print("     git commit -m 'Fix hero v2'")
print("     git push")
print()
print(f"BACKUP : {backup_name}")
