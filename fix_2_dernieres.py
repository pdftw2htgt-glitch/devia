#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil
from datetime import datetime
content = open("devia.jsx", encoding="utf-8").read()
modifs = 0
def apply(old, new, label):
    global content, modifs
    n = content.count(old)
    if n == 1:
        content = content.replace(old, new, 1); print(f"[OK] {label}"); modifs += 1
    elif n == 0: print(f"[WARN] {label} : NON trouve")
    else: print(f"[WARN] {label} : {n}x ambigu")

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fix2"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) Sabliere carport (avec woodMat)
apply(
    '''    // ===== SABLIERES (basse avant + haute arriere) =====
    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2, woodMat);
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2, woodMat);''',
    '''    setPiece("Sabliere");
    // ===== SABLIERES (basse avant + haute arriere) =====
    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2, woodMat);
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2, woodMat);''',
    "Sabliere carport"
)

# 2) Chevrons hangar : le seul bloc CHEVRONS 0.6m SANS setPiece au-dessus
#    (le carport a deja "setPiece(\\"Chevron\\");" juste avant son commentaire)
apply(
    '''    }

    // ===== CHEVRONS RAPPROCHES (~tous les 0.6m) =====
    const espChevron = 0.6;
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;''',
    '''    }

    setPiece("Chevron");
    // ===== CHEVRONS RAPPROCHES (~tous les 0.6m) =====
    const espChevron = 0.6;
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;''',
    "Chevrons hangar"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
