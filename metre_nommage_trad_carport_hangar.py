#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Nommage pieces : charpente trad + carport + hangar"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()
modifs = 0

def setp_unique(anchor, nom):
    """Insere setPiece avant une ancre UNIQUE dans tout le fichier."""
    global content, modifs
    n = content.count(anchor)
    if n == 1:
        idx = content.find(anchor)
        ls = content.rfind("\n", 0, idx) + 1
        indent = content[ls:idx]
        content = content[:ls] + f'{indent}setPiece("{nom}");\n' + content[ls:]
        print(f"[OK] {nom}"); modifs += 1
    elif n == 0:
        print(f"[WARN] '{nom}' : ancre NON trouvee")
    else:
        print(f"[WARN] '{nom}' : ancre {n}x ambigu -> ignore (besoin ancre + longue)")

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_nommage_tch"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# ---------- CHARPENTE TRAD (commentaires uniques) ----------
setp_unique("    // ===== FERMES (tous les ~3.5m) =====", "Ferme")
setp_unique("    // ===== SABLIERES (poutres basses sur les murs longs) =====", "Sabliere")
setp_unique("    // ===== PANNE FAITIERE =====\n", "Panne faitiere")
setp_unique("    // ===== PANNES INTERMEDIAIRES (le long du toit, sur les 2 pans) =====", "Panne")
setp_unique("    // ===== CHEVRONS RAPPROCHES (tous les ~0.5m, sur les pannes) =====", "Chevron")

# ---------- CARPORT (CHEVRONS 0.6m existe aussi dans hangar -> ancre multi-lignes) ----------
setp_unique("    // ===== POTEAUX (specificite carport) =====", "Poteau")
setp_unique("    // ===== SABLIERES (basse avant + haute arriere) =====\n    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2);", "Sabliere")
setp_unique("    // ===== PANNES INTERMEDIAIRES (suivent la pente) =====", "Panne")
setp_unique("    // ===== CHEVRONS RAPPROCHES (~tous les 0.6m) =====\n    const espChevron = 0.6;\n    const nbChevrons = Math.max(2, Math.floor(L / espChevron));\n    const yCentre", "Chevron")

# ---------- HANGAR ----------
setp_unique("    // ===== POTEAUX (specificite hangar : 4 coins + intermediaires) =====", "Poteau")
setp_unique("    // ===== SABLIERES (longues poutres sur les poteaux) =====", "Sabliere")
setp_unique("    // ===== FERMES COMPLETES (tous les ~3m) =====", "Ferme")
setp_unique("    // ===== PANNE FAITIERE + INTERMEDIAIRES =====", "Panne")
# chevrons hangar : ancre multi-lignes differente du carport
setp_unique("    // ===== CHEVRONS RAPPROCHES (~tous les 0.6m) =====\n    const espChevron = 0.6;\n    const nbChevrons = Math.max(2, Math.ceil", "Chevron")

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
