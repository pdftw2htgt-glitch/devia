#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Sections EC5 dans la 3D : monopente (zone 368-580)"""
import shutil
from datetime import datetime

lines = open("devia.jsx", encoding="utf-8").read().split("\n")
idx0 = next((i for i,l in enumerate(lines) if "const drawMonopente" in l), None)
idx1 = next((i for i,l in enumerate(lines) if "const drawAppentis" in l), None)
if idx0 is None or idx1 is None:
    print("[ERREUR] bornes monopente introuvables"); exit(1)
print(f"[INFO] Zone monopente : {idx0+1} a {idx1+1}")

def ind_of(s): return s[:len(s)-len(s.lstrip())]

repl = [
    ('addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2, woodMat);',
     lambda ind: f'{ind}const [sbB, sbH] = sec("Sabliere", 0.16, 0.16);\n{ind}addBox(L + 0.3, sbH, sbB, 0, Hbas, -lg/2, woodMat);'),
    ('addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2, woodMat);',
     lambda ind: f'{ind}addBox(L + 0.3, sbH, sbB, 0, Hhaut, lg/2, woodMat);'),
    ('addBox(L + 0.3, 0.14, 0.14, 0, y, z, woodMat);',
     lambda ind: f'{ind}const [pnB, pnH] = sec("Panne", 0.14, 0.14);\n{ind}addBox(L + 0.3, pnH, pnB, 0, y, z, woodMat);'),
    ('addBox(0.08, 0.08, longueurChevron + 0.2, x, yCentre + 0.07, 0, woodMat, [-ang, 0, 0]);',
     lambda ind: f'{ind}const [chB, chH] = sec("Chevron", 0.08, 0.08);\n{ind}addBox(chB, chH, longueurChevron + 0.2, x, yCentre + 0.07, 0, woodMat, [-ang, 0, 0]);'),
]

modifs = 0
for needle, builder in repl:
    found = False
    for i in range(idx0, idx1):
        if needle in lines[i]:
            lines[i] = builder(ind_of(lines[i])); found = True; modifs += 1; break
    print(("[OK] " if found else "[WARN] NON trouve : ") + needle[:55])

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_sectionsMono"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")
open("devia.jsx", "w", encoding="utf-8").write("\n".join(lines))
print(f"\n{modifs} REMPLACEMENT(S) APPLIQUE(S)")
