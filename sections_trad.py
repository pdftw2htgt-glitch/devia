#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Sections EC5 dans la 3D : charpente trad (zone 213-306)"""
import shutil
from datetime import datetime

raw = open("devia.jsx", encoding="utf-8").read()
lines = raw.split("\n")

# Bornes de la zone trad
idx_trad = next((i for i,l in enumerate(lines) if "const drawCharpenteTrad" in l), None)
idx_end  = next((i for i,l in enumerate(lines) if ("const drawCarport" in l or "const drawHangar" in l) and i > idx_trad), None)
if idx_trad is None or idx_end is None:
    print("[ERREUR] bornes trad introuvables"); exit(1)
print(f"[INFO] Zone trad : lignes {idx_trad+1} a {idx_end+1}")

def ind_of(s): return s[:len(s)-len(s.lstrip())]

# Remplacements cibles UNIQUEMENT dans la zone trad [idx_trad, idx_end]
repl = [
    # (texte a trouver, fonction qui retourne le remplacement multi-lignes via indentation)
    ('addBox(0.16, 0.16, lg, x, Ht, 0, woodMat);',
     lambda ind: f'{ind}const [enB, enH] = sec("Ferme", 0.16, 0.16);\n{ind}addBox(enB, enH, lg, x, Ht, 0, woodMat);'),
    ('addBox(0.16, 0.16, pl, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);',
     lambda ind: f'{ind}const [arB, arH] = sec("Ferme", 0.16, 0.16);\n{ind}addBox(arB, arH, pl, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);'),
    ('addBox(0.16, 0.16, pl, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);',
     lambda ind: f'{ind}addBox(arB, arH, pl, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);'),
    ('addBox(L + 0.3, 0.14, 0.14, 0, Ht, lg/2, woodMat);',
     lambda ind: f'{ind}const [sbB, sbH] = sec("Sabliere", 0.14, 0.14);\n{ind}addBox(L + 0.3, sbH, sbB, 0, Ht, lg/2, woodMat);'),
    ('addBox(L + 0.3, 0.14, 0.14, 0, Ht, -lg/2, woodMat);',
     lambda ind: f'{ind}addBox(L + 0.3, sbH, sbB, 0, Ht, -lg/2, woodMat);'),
    ('addBox(L + 0.4, 0.14, 0.14, 0, yFait, 0, woodMat);',
     lambda ind: f'{ind}const [pfB, pfH] = sec("Panne faitiere", 0.14, 0.14);\n{ind}addBox(L + 0.4, pfH, pfB, 0, yFait, 0, woodMat);'),
    ('addBox(L + 0.3, 0.12, 0.12, 0, yPanne, zPanne, woodMat);',
     lambda ind: f'{ind}const [pnB, pnH] = sec("Panne", 0.12, 0.12);\n{ind}addBox(L + 0.3, pnH, pnB, 0, yPanne, zPanne, woodMat);'),
    ('addBox(L + 0.3, 0.12, 0.12, 0, yPanne, -zPanne, woodMat);',
     lambda ind: f'{ind}addBox(L + 0.3, pnH, pnB, 0, yPanne, -zPanne, woodMat);'),
    ('addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, lg/4, woodMat, [ang, 0, 0]);',
     lambda ind: f'{ind}const [chB, chH] = sec("Chevron", 0.07, 0.07);\n{ind}addBox(chB, chH, pl, x, Ht + hf/2 + 0.08, lg/4, woodMat, [ang, 0, 0]);'),
    ('addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, -lg/4, woodMat, [-ang, 0, 0]);',
     lambda ind: f'{ind}addBox(chB, chH, pl, x, Ht + hf/2 + 0.08, -lg/4, woodMat, [-ang, 0, 0]);'),
]

modifs = 0
for needle, builder in repl:
    found = False
    for i in range(idx_trad, idx_end):
        if needle in lines[i]:
            lines[i] = builder(ind_of(lines[i]))
            found = True; modifs += 1
            break
    print(("[OK] " if found else "[WARN] NON trouve : ") + needle[:50])

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_sectionsTrad"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")
open("devia.jsx", "w", encoding="utf-8").write("\n".join(lines))
print(f"\n{modifs} REMPLACEMENT(S) APPLIQUE(S)")
