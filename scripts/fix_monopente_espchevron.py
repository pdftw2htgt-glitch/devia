#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()

# Ancre unique = commentaire monopente + ligne espChevron
old = '''    // ===== CHEVRONS RAPPROCHES (~tous les 0.5m) =====
    const espChevron = 0.5;'''
new = '''    // ===== CHEVRONS RAPPROCHES (espacement selon couverture) =====
    const espChevron = couv.espChevron;'''

n = content.count(old)
if n == 0:
    print("[WARN] Ancre monopente non trouvee (deja fait ?)"); sys.exit(0)
if n > 1:
    print(f"[ERREUR] Ancre trouvee {n} fois, trop risque -> abandon"); sys.exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_mono_espchevron"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

content = content.replace(old, new, 1)
open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] Monopente : espChevron branche sur le registre")
print("1 MODIFICATION APPLIQUEE")
