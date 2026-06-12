#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Modif 5 : Remplacement des emojis par icones SVG
- Style coherent avec les stat cards (line icons, stroke 2px)
- Couleurs adaptees au theme (or, bleu, vert, etc.)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_emoji_svg"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Remplacer les "icon: emoji" par "icon: identifiant"
# Dans les definitions QUESTIONS
# ================================================================

emoji_to_id = {
    '"🏭"': '"factory"',
    '"✨"': '"sparkles"',
    '"⚙️"': '"gear"',
    '"🟤"': '"circle-brown"',
    '"🔲"': '"square"',
    '"📐"': '"ruler"',
    '"🌲"': '"tree-conifer"',
    '"🌳"': '"tree-leaf"',
    '"📦"': '"box"',
    '"🏠"': '"home"',
    '"🛋️"': '"sofa"',
}

# La 2eme occurrence de "🌲" est pour Douglas - on garde tree-conifer
# La 2eme occurrence de "🌳" est pour Chene - on garde tree-leaf

for emoji, name in emoji_to_id.items():
    if emoji in content:
        nb = content.count(emoji)
        content = content.replace(emoji, name)
        print(f"[OK] {nb}x emoji {emoji} -> {name}")
        modifs += nb

# ================================================================
# MOD 2 : Creer une fonction renderIcon() qui retourne le bon SVG
# On l'ajoute juste avant QuestionsScreen
# ================================================================

old_questions_marker = 'function QuestionsScreen({ detected, onValidate }) {'

new_with_render_icon = '''// Mapping des identifiants vers des SVG (style line icons, stroke 2px)
function renderIcon(name, size = 20, color = "#e8eaf2") {
  const stroke = color;
  const sw = "2";
  const svgs = {
    "factory": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M2 20a2 2 0 002 2h16a2 2 0 002-2V8l-7 5V8l-7 5V4a2 2 0 00-2-2H4a2 2 0 00-2 2z"/></svg>,
    "sparkles": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z"/><path d="M5 18l.75 2.25L8 21l-2.25.75L5 24l-.75-2.25L2 21l2.25-.75L5 18z"/></svg>,
    "gear": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>,
    "circle-brown": <svg width={size} height={size} viewBox="0 0 24 24" fill="#a8841f" stroke="#a8841f" strokeWidth={sw}><circle cx="12" cy="12" r="9"/></svg>,
    "square": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/></svg>,
    "ruler": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M16 2l6 6L8 22l-6-6L16 2z"/><path d="M7.5 10.5l2 2"/><path d="M10.5 7.5l2 2"/><path d="M13.5 4.5l2 2"/></svg>,
    "tree-conifer": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M12 2l4 6h-2l3 5h-2l3 5H6l3-5H7l3-5H8l4-6z"/><line x1="12" y1="18" x2="12" y2="22"/></svg>,
    "tree-leaf": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M12 22V12"/><path d="M12 12c-3 0-7-2-7-7 0 0 4-1 7 4 3-5 7-4 7-4 0 5-4 7-7 7z"/></svg>,
    "box": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>,
    "home": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>,
    "sofa": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M20 9V7a2 2 0 00-2-2H6a2 2 0 00-2 2v2"/><path d="M2 11v5a2 2 0 002 2h16a2 2 0 002-2v-5a2 2 0 00-4 0v3H6v-3a2 2 0 00-4 0z"/><line x1="6" y1="18" x2="6" y2="20"/><line x1="18" y1="18" x2="18" y2="20"/></svg>,
    "help-circle": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
    "paperclip": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>,
  };
  return svgs[name] || null;
}

function QuestionsScreen({ detected, onValidate }) {'''

if "function renderIcon(" in content:
    print("[INFO] Fonction renderIcon deja presente")
elif old_questions_marker in content:
    content = content.replace(old_questions_marker, new_with_render_icon, 1)
    print("[OK] Fonction renderIcon() ajoutee avec 13 SVGs")
    modifs += 1
else:
    print("[ERREUR] QuestionsScreen non trouve")
    sys.exit(1)

# ================================================================
# MOD 3 : Remplacer {opt.icon} (ligne 374) par renderIcon(opt.icon)
# ================================================================

old_opt_icon = '<span style={{ fontSize: 20 }}>{opt.icon}</span>{opt.label}'
new_opt_icon = '<span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 20, height: 20 }}>{renderIcon(opt.icon, 18, "#e8eaf2")}</span>{opt.label}'

if "renderIcon(opt.icon" in content:
    print("[INFO] {opt.icon} deja remplace")
elif old_opt_icon in content:
    content = content.replace(old_opt_icon, new_opt_icon, 1)
    print("[OK] {opt.icon} remplace par renderIcon SVG")
    modifs += 1
else:
    print("[WARN] {opt.icon} non trouve exactement")

# ================================================================
# MOD 4 : Remplacer 🤔 dans QuestionsScreen par help-circle
# ================================================================

old_thinking = '<div style={{ fontSize: 40, marginBottom: 8 }}>🤔</div>'
new_thinking = '<div style={{ marginBottom: 8, display: "flex", justifyContent: "center" }}>{renderIcon("help-circle", 40, "#f0c040")}</div>'

if "renderIcon(\"help-circle\"" in content:
    print("[INFO] Emoji 🤔 deja remplace")
elif old_thinking in content:
    content = content.replace(old_thinking, new_thinking, 1)
    print("[OK] Emoji 🤔 remplace par help-circle SVG (couleur or)")
    modifs += 1
else:
    print("[WARN] Emoji 🤔 non trouve exactement")

# ================================================================
# MOD 5 : Remplacer 📎 dans zone upload par paperclip
# ================================================================

old_paperclip = '<div style={{ fontSize: 24, marginBottom: 6 }}>📎</div>'
new_paperclip = '<div style={{ marginBottom: 6, display: "flex", justifyContent: "center" }}>{renderIcon("paperclip", 24, "#7a7d92")}</div>'

if "renderIcon(\"paperclip\"" in content:
    print("[INFO] Emoji 📎 deja remplace")
elif old_paperclip in content:
    content = content.replace(old_paperclip, new_paperclip, 1)
    print("[OK] Emoji 📎 remplace par paperclip SVG")
    modifs += 1
else:
    print("[WARN] Emoji 📎 non trouve exactement")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. 11 emojis remplaces par des identifiants ('tree-conifer', 'box'...)")
print("  2. Fonction renderIcon() ajoutee (13 SVGs disponibles)")
print("  3. {opt.icon} dans QuestionsScreen utilise maintenant renderIcon()")
print("  4. Emoji 🤔 remplace par icone help-circle (or)")
print("  5. Emoji 📎 remplace par icone paperclip (gris)")
print()
print("STYLE DES ICONES :")
print("  - Line icons, stroke 2px")
print("  - Coherent avec les stat cards de la page Compte")
print("  - Couleurs : or pour le focus, gris pour neutre")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
