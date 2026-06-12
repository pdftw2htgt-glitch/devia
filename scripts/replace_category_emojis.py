#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Remplacement des emojis HTML des en-tetes de categories
Les emojis etaient stockes en HTML entities et rendus via dangerouslySetInnerHTML.
On les remplace par des SVG inline pour un style coherent.
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_cat_icons"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Remplacer l'objet icons HTML par des SVG inline
# + Ajouter Outillage + Retirer Main d'oeuvre
# + Mettre a jour orderedCats
# ================================================================

# Strategie : on remplace TOUTE la section icons + le span dangerouslySetInnerHTML
# par une fonction qui retourne un SVG

old_icons_block = '''                  const orderedCats = ["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie"];
                  const icons = {
                    "Charpente": "&#x1FAB5;",
                    "Bardage": "&#x1F3E0;",
                    "Couverture": "&#x1F7EB;",
                    "Isolation": "&#x1F9CA;",
                    "Quincaillerie": "&#x1F529;",
                    "Main d'oeuvre": "&#x1F477;"
                  };'''

new_icons_block = '''                  const orderedCats = ["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie", "Outillage"];
                  const catColors = {
                    "Charpente": "#a78bfa",
                    "Bardage": "#fb923c",
                    "Couverture": "#60a5fa",
                    "Isolation": "#3ecf8e",
                    "Quincaillerie": "#fcd34d",
                    "Outillage": "#f0c040"
                  };
                  const renderCatIcon = (cat) => {
                    const c = catColors[cat] || "#7a7d92";
                    const sw = "2";
                    switch(cat) {
                      case "Charpente":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M12 2l4 6h-2l3 5h-2l3 5H6l3-5H7l3-5H8l4-6z"/><line x1="12" y1="18" x2="12" y2="22"/></svg>;
                      case "Bardage":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>;
                      case "Couverture":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M2 12l10-9 10 9"/><path d="M5 10v10h14V10"/></svg>;
                      case "Isolation":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20"/><path d="M2 6l10 6 10-6"/><path d="M2 12l10 6 10-6"/><path d="M2 18l10 6 10-6"/></svg>;
                      case "Quincaillerie":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4M5 5l3 3M16 16l3 3M5 19l3-3M16 8l3-3"/></svg>;
                      case "Outillage":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>;
                      default:
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9"/></svg>;
                    }
                  };'''

if "renderCatIcon" in content:
    print("[INFO] renderCatIcon deja en place")
elif old_icons_block in content:
    content = content.replace(old_icons_block, new_icons_block, 1)
    print("[OK] Objet icons HTML remplace par renderCatIcon() avec SVG")
    modifs += 1
else:
    print("[ERREUR] Bloc icons non trouve exactement")
    sys.exit(1)

# ================================================================
# MOD 2 : Remplacer le span dangerouslySetInnerHTML par l'appel a renderCatIcon
# ================================================================

old_span = '<span dangerouslySetInnerHTML={{ __html: icons[cat] || "" }} />'
new_span = '<span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 22, height: 22 }}>{renderCatIcon(cat)}</span>'

if "renderCatIcon(cat)" in content:
    print("[INFO] Span deja remplace")
elif old_span in content:
    content = content.replace(old_span, new_span, 1)
    print("[OK] Span dangerouslySetInnerHTML remplace par renderCatIcon SVG")
    modifs += 1
else:
    print("[WARN] Span dangerouslySetInnerHTML non trouve")

# ================================================================
# MOD 3 : Aussi remplacer le 🪵 ligne 317 (Charpente traditionnelle dans Questions)
# par "tree-log" (on l'avait oublie)
# ================================================================

old_log_emoji = '{ val: "traditionnelle", label: "Charpente traditionnelle", icon: "🪵" }'
new_log_id = '{ val: "traditionnelle", label: "Charpente traditionnelle", icon: "tree-log" }'

if "icon: \"tree-log\"" in content:
    print("[INFO] tree-log deja remplace")
elif old_log_emoji in content:
    content = content.replace(old_log_emoji, new_log_id, 1)
    print("[OK] Emoji 🪵 remplace par 'tree-log' dans QUESTIONS")
    modifs += 1
else:
    print("[INFO] Emoji 🪵 deja absent de QUESTIONS")

# ================================================================
# MOD 4 : Ajouter 'tree-log' au renderIcon() existant
# ================================================================

old_svgs_dict = '"tree-conifer": <svg width={size} height={size}'
new_svgs_with_log = '''"tree-log": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="6" rx="9" ry="3"/><path d="M3 6v12c0 1.66 4.03 3 9 3s9-1.34 9-3V6"/><line x1="12" y1="9" x2="12" y2="9.01"/><line x1="9" y1="8.5" x2="9" y2="8.51"/><line x1="15" y1="8.5" x2="15" y2="8.51"/></svg>,
    "tree-conifer": <svg width={size} height={size}'''

if '"tree-log":' in content:
    print("[INFO] tree-log deja dans renderIcon")
elif old_svgs_dict in content:
    content = content.replace(old_svgs_dict, new_svgs_with_log, 1)
    print("[OK] SVG 'tree-log' ajoute au renderIcon")
    modifs += 1
else:
    print("[WARN] Dictionnaire SVG non trouve")

# ================================================================
# MOD 5 : Aussi remplacer le ⬜ ligne 326 (Tuile beton)
# ================================================================

old_square_emoji = '{ val: "tuile_beton", label: "Tuile béton", icon: "⬜" }'
new_square_id = '{ val: "tuile_beton", label: "Tuile béton", icon: "square" }'

if 'val: "tuile_beton", label: "Tuile béton", icon: "square"' in content:
    print("[INFO] square deja en place pour Tuile beton")
elif old_square_emoji in content:
    content = content.replace(old_square_emoji, new_square_id, 1)
    print("[OK] Emoji ⬜ remplace par 'square' pour Tuile beton")
    modifs += 1
else:
    print("[INFO] Emoji ⬜ deja absent")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. renderCatIcon() ajoute (6 SVGs colores pour chaque categorie)")
print("  2. Span dangerouslySetInnerHTML remplace par SVG inline")
print("  3. Emoji 🪵 -> 'tree-log' dans QUESTIONS")
print("  4. SVG tree-log ajoute au renderIcon")
print("  5. Emoji ⬜ -> 'square' pour Tuile beton")
print()
print("STYLES DES CATEGORIES :")
print("  Charpente    -> Sapin violet")
print("  Bardage      -> Maison orange")
print("  Couverture   -> Toit bleu")
print("  Isolation    -> Couches vert")
print("  Quincaillerie -> Engrenage jaune")
print("  Outillage    -> Clef or")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
