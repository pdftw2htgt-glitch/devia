#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix cible pour le hero seulement
Le script precedent a partiellement skippe le hero.
Ce script ne fait QUE le hero, par micro-modifications.

A lancer depuis ~/Desktop/devia :
    python3 fix_hero_only.py
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_fix_hero"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Supprimer la div de l'emoji
# ================================================================

old_emoji = '<div style={{ fontSize: 48, marginBottom: 12 }}>🏗️</div>\n              '
if old_emoji in content:
    content = content.replace(old_emoji, '', 1)
    print("[OK] Emoji 🏗️ supprime")
    modifs += 1
else:
    print("[WARN] Emoji non trouve exactement, tentative alternative...")
    old_emoji_alt = '<div style={{ fontSize: 48, marginBottom: 12 }}>🏗️</div>'
    if old_emoji_alt in content:
        content = content.replace(old_emoji_alt, '', 1)
        print("[OK] Emoji 🏗️ supprime (alt)")
        modifs += 1
    else:
        print("[ERREUR] Emoji introuvable")

# ================================================================
# MOD 2 : Wrapper div - changer marginBottom
# ================================================================

old_wrapper = '<div style={{ textAlign: "center", marginBottom: 32 }}>'
new_wrapper = '<div style={{ textAlign: "center", marginBottom: 40, paddingTop: 16 }}>'

if new_wrapper in content:
    print("[INFO] Wrapper deja modifie, skip")
elif old_wrapper in content:
    content = content.replace(old_wrapper, new_wrapper, 1)
    print("[OK] Wrapper hero : margin augmente + padding top")
    modifs += 1
else:
    print("[WARN] Wrapper hero non trouve")

# ================================================================
# MOD 3 : Titre avec gradient sur "charpente"
# ================================================================

old_title = '<h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>Generez votre devis charpente</h1>'
new_title = '<h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 12, letterSpacing: "-0.02em", lineHeight: 1.1 }}>Generez votre devis <span style={{ background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>charpente</span></h1>'

if "WebkitBackgroundClip" in content:
    print("[INFO] Titre deja avec gradient, skip")
elif old_title in content:
    content = content.replace(old_title, new_title, 1)
    print("[OK] Titre : gradient jaune sur 'charpente' + typo plus grande")
    modifs += 1
else:
    print("[WARN] Titre hero non trouve exactement")

# ================================================================
# MOD 4 : Sous-titre
# ================================================================

old_subtitle = '<p style={{ color: "#545870", fontSize: 15 }}>Decrivez votre projet - DEVIA genere un devis professionnel et une visualisation 3D</p>'
new_subtitle = '<p style={{ color: "#7a7d92", fontSize: 15, maxWidth: 520, margin: "0 auto", lineHeight: 1.55 }}>Decrivez votre projet en langage naturel. DEVIA genere un devis professionnel et une visualisation 3D.</p>'

if "en langage naturel" in content:
    print("[INFO] Sous-titre deja modifie, skip")
elif old_subtitle in content:
    content = content.replace(old_subtitle, new_subtitle, 1)
    print("[OK] Sous-titre : plus narratif + meilleure lisibilite")
    modifs += 1
else:
    print("[WARN] Sous-titre hero non trouve")

# ================================================================
# MOD 5 : Label Documents (qui manquait)
# ================================================================

old_doc_label = '<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Documents - max 5</label>'
new_doc_label = '<label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Documents <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>(max 5)</span></label>'

if 'Documents <span style={{ color: "#545870", textTransform: "none"' in content:
    print("[INFO] Label Documents deja refondu, skip")
elif old_doc_label in content:
    content = content.replace(old_doc_label, new_doc_label, 1)
    print("[OK] Label 'Documents - max 5' style uppercase")
    modifs += 1
else:
    print("[WARN] Label Documents non trouve (peut-etre deja modifie autrement)")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print(f"=== {modifs} modifications appliquees ===")

# ================================================================
# TEST SYNTAXE
# ================================================================
print()
print("TEST SYNTAXE...")
try:
    result = subprocess.run(
        ["npx", "esbuild", "devia.jsx", "--loader=jsx", "--bundle=false"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        print("[OK] Syntaxe JSX valide")
    else:
        print("ERREUR SYNTAXE :")
        print(result.stderr[:2000])
        print()
        print("RESTORE AUTO...")
        shutil.copy(backup_name, "devia.jsx")
        print(f"[OK] devia.jsx restaure depuis : {backup_name}")
        sys.exit(1)
except FileNotFoundError:
    print("[INFO] esbuild non dispo, test syntaxe skip")
except subprocess.TimeoutExpired:
    print("[INFO] esbuild trop lent, test syntaxe skip")

print()
print("=" * 60)
print("FIX HERO APPLIQUE")
print("=" * 60)
print()
print("ETAPES :")
print("  1. npm run build  # tester en local")
print("  2. Si OK : git add devia.jsx && git commit -m 'Fix hero' && git push")
print()
print(f"BACKUP : {backup_name}")
