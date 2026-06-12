#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pose le setPiece Sabliere manquant dans la monopente (ancre unique)"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()

# Ancre UNIQUE : sablieres monopente + le setPiece("Panne") + commentaire pannes monopente
old = '''    // ===== SABLIERES (basse avant + haute arriere) =====
    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2, woodMat);
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2, woodMat);

setPiece("Panne");
    // ===== PANNES INTERMEDIAIRES (4, bien reparties entre sablieres) ====='''

new = '''    setPiece("Sabliere");
    // ===== SABLIERES (basse avant + haute arriere) =====
    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2, woodMat);
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2, woodMat);

    setPiece("Panne");
    // ===== PANNES INTERMEDIAIRES (4, bien reparties entre sablieres) ====='''

n = content.count(old)
if n != 1:
    print(f"[ERREUR] ancre trouvee {n}x (attendu 1) -> abandon"); exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fix_sabliere_mono"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

content = content.replace(old, new, 1)
open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] Sabliere monopente posee + indentation Panne corrigee")
print("1 MODIFICATION APPLIQUEE")
