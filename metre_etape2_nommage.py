#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Metre etape 2 : nommer les pieces (monopente, appentis, 4pans)"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()
modifs = 0
def setp(comment_full, nom):
    global content, modifs
    n = content.count(comment_full)
    if n == 1:
        idx = content.find(comment_full)
        line_start = content.rfind("\n", 0, idx) + 1
        indent = content[line_start:idx]
        inject = f'{indent}setPiece("{nom}");\n'
        content = content[:line_start] + inject + content[line_start:]
        print(f"[OK] {nom}"); modifs += 1
    elif n == 0:
        print(f"[WARN] '{nom}' : ancre NON trouvee")
    else:
        print(f"[WARN] '{nom}' : ancre {n}x ambigu -> ignore")

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_metre_nommage"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# --- MONOPENTE ---
setp("    // ===== SABLIERES (basse avant + haute arriere) =====\n    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2, woodMat);", "Sabliere")
setp("    // ===== PANNES INTERMEDIAIRES (4, bien reparties entre sablieres) =====", "Panne")
setp("    // ===== CHEVRONS RAPPROCHES (espacement selon couverture) =====", "Chevron")
setp("    // ===== LITEAUX (perpendiculaires aux chevrons, ~tous les 0.35m) =====", "Liteau")

# --- APPENTIS ---
setp("    // ===== POTEAUX AVANT (cote ouvert, nb adaptatif) =====", "Poteau")
setp("    // ===== SABLIERES (basse avant + haute arriere contre mur) =====", "Sabliere")
setp("    // ===== PANNES INTERMEDIAIRES (nb adaptatif, bien reparties) =====", "Panne")
setp("    // ===== CHEVRONS (espacement + section adaptatifs) =====", "Chevron")
setp("    // ===== LITEAUX (perpendiculaires aux chevrons, espacement adaptatif) =====", "Liteau")
setp("    // ===== ECHANTIGNOLES (cale a chaque croisement chevron x panne) =====", "Echantignole")

# --- 4 PANS ---
setp("    // ===== SABLIERES DE CHAINAGE (haut des 4 murs) =====", "Sabliere")
setp("    // ===== FAITAGE (central) =====", "Faitage")
setp("    // ===== ARETIERS (faitage -> 4 coins) =====", "Aretier")
setp("    // ===== PANNES sur les 2 grands pans (nb adaptatif) =====", "Panne")
setp("    // ===== CHEVRONS sur les 2 grands pans (entre les aretiers) =====", "Chevron")
setp("    // ===== EMPANNONS (chevrons courts s'appuyant sur les aretiers) =====", "Empannon")
setp("    // ===== EMPANNONS DE CROUPE (sur les 2 triangles de bout) =====", "Empannon de croupe")

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
