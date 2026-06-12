#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Sections EC5 dans la 3D : appentis (zone 580-709)"""
import shutil
from datetime import datetime

lines = open("devia.jsx", encoding="utf-8").read().split("\n")
idx0 = next((i for i,l in enumerate(lines) if "const drawAppentis" in l), None)
idx1 = next((i for i,l in enumerate(lines) if "const draw4Pans" in l), None)
if idx0 is None or idx1 is None:
    print("[ERREUR] bornes appentis introuvables"); exit(1)
print(f"[INFO] Zone appentis : {idx0+1} a {idx1+1}")

def ind_of(s): return s[:len(s)-len(s.lstrip())]

repl = [
    ('addBox(L + 0.3, secSabliere, secSabliere, 0, Hbas, -lg/2, woodMat);',
     lambda ind: f'{ind}const [sbB, sbH] = sec("Sabliere", secSabliere, secSabliere);\n{ind}addBox(L + 0.3, sbH, sbB, 0, Hbas, -lg/2, woodMat);'),
    ('addBox(L + 0.3, secSabliere, secSabliere, 0, Hhaut, lg/2, woodMat);',
     lambda ind: f'{ind}addBox(L + 0.3, sbH, sbB, 0, Hhaut, lg/2, woodMat);'),
    ('addBox(L + 0.3, secPanne, secPanne, 0, y, z, woodMat);',
     lambda ind: f'{ind}const [pnB, pnH] = sec("Panne", secPanne, secPanne);\n{ind}addBox(L + 0.3, pnH, pnB, 0, y, z, woodMat);'),
    ('addBox(secChevron, secChevron, longueurRampant + 0.2, x, yCentre + secChevron*0.8, 0, woodMat, [-ang, 0, 0]);',
     lambda ind: f'{ind}const [chB, chH] = sec("Chevron", secChevron, secChevron);\n{ind}addBox(chB, chH, longueurRampant + 0.2, x, yCentre + secChevron*0.8, 0, woodMat, [-ang, 0, 0]);'),
]

modifs = 0
for needle, builder in repl:
    found = False
    for i in range(idx0, idx1):
        if needle in lines[i]:
            lines[i] = builder(ind_of(lines[i])); found = True; modifs += 1; break
    print(("[OK] " if found else "[WARN] NON trouve : ") + needle[:55])

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_sectionsApp"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")
open("devia.jsx", "w", encoding="utf-8").write("\n".join(lines))
print(f"\n{modifs} REMPLACEMENT(S) APPLIQUE(S)")
