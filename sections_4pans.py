#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Sections EC5 dans la 3D : 4 pans (zone 715 -> drawCarport ou fin)"""
import shutil
from datetime import datetime

lines = open("devia.jsx", encoding="utf-8").read().split("\n")
idx0 = next((i for i,l in enumerate(lines) if "const draw4Pans" in l), None)
# fin = prochaine fonction de meme niveau apres les sous-fonctions empannons
# on prend une borne large : jusqu'a la prochaine "const draw" qui n'est PAS une sous-fonction empannon
idx1 = None
for i in range(idx0+1, len(lines)):
    if "const draw" in lines[i] and "Empannon" not in lines[i]:
        idx1 = i; break
if idx1 is None: idx1 = len(lines)
print(f"[INFO] Zone 4 pans : {idx0+1} a {idx1+1}")

def ind_of(s): return s[:len(s)-len(s.lstrip())]

# helper sec renvoie [b,h] ; pour addBeam on veut la hauteur -> sec(...)[1]
repl = [
    # --- SABLIERES (4) : 2 selon X (L+0.2) + 2 selon Z (lg) ---
    ('addBox(L + 0.2, 0.16, 0.16, 0, Ht, lg/2, woodMat);',
     lambda ind: f'{ind}const [sbB, sbH] = sec("Sabliere", 0.16, 0.16);\n{ind}addBox(L + 0.2, sbH, sbB, 0, Ht, lg/2, woodMat);'),
    ('addBox(L + 0.2, 0.16, 0.16, 0, Ht, -lg/2, woodMat);',
     lambda ind: f'{ind}addBox(L + 0.2, sbH, sbB, 0, Ht, -lg/2, woodMat);'),
    ('addBox(0.16, 0.16, lg, -L/2, Ht, 0, woodMat);',
     lambda ind: f'{ind}addBox(sbB, sbH, lg, -L/2, Ht, 0, woodMat);'),
    ('addBox(0.16, 0.16, lg, L/2, Ht, 0, woodMat);',
     lambda ind: f'{ind}addBox(sbB, sbH, lg, L/2, Ht, 0, woodMat);'),
    # --- FAITAGE : addBox selon X ---
    ('addBox(Lfait, 0.15, 0.15, 0, yFait, 0, woodMat);',
     lambda ind: f'{ind}const [ftB, ftH] = sec("Faitage", 0.15, 0.15);\n{ind}addBox(Lfait, ftH, ftB, 0, yFait, 0, woodMat);'),
    # --- ARETIER : addBeam, epaisseur = hauteur EC5 ---
    ('addBeam(cxp, cyp, czp, xf, yFait, 0, 0.12, woodMat);',
     lambda ind: f'{ind}addBeam(cxp, cyp, czp, xf, yFait, 0, sec("Aretier", 0.12, 0.12)[1], woodMat);'),
    # --- PANNES : addBox ---
    ('addBox(lenPanne, 0.12, 0.12, 0, yPanne, zPanne, woodMat);',
     lambda ind: f'{ind}const [pnB, pnH] = sec("Panne", 0.12, 0.12);\n{ind}addBox(lenPanne, pnH, pnB, 0, yPanne, zPanne, woodMat);'),
    ('addBox(lenPanne, 0.12, 0.12, 0, yPanne, -zPanne, woodMat);',
     lambda ind: f'{ind}addBox(lenPanne, pnH, pnB, 0, yPanne, -zPanne, woodMat);'),
    # --- CHEVRONS : addBeam, epaisseur = hauteur Chevron ---
    ('addBeam(x, Ht, lg/2, x, yFait, 0, secChevron, woodMat);',
     lambda ind: f'{ind}addBeam(x, Ht, lg/2, x, yFait, 0, sec("Chevron", secChevron, secChevron)[1], woodMat);'),
    ('addBeam(x, Ht, -lg/2, x, yFait, 0, secChevron, woodMat);',
     lambda ind: f'{ind}addBeam(x, Ht, -lg/2, x, yFait, 0, sec("Chevron", secChevron, secChevron)[1], woodMat);'),
    # --- EMPANNONS : addBeam ---
    ('addBeam(xb, Ht, zb, xh, yh, zh, secChevron * 0.9, woodMat);',
     lambda ind: f'{ind}addBeam(xb, Ht, zb, xh, yh, zh, sec("Empannon", secChevron, secChevron)[1] * 0.9, woodMat);'),
    ('addBeam(xb, Ht, zb, xh, yh, zh, secChevron * 0.85, woodMat);',
     lambda ind: f'{ind}addBeam(xb, Ht, zb, xh, yh, zh, sec("Empannon de croupe", secChevron, secChevron)[1] * 0.85, woodMat);'),
]

modifs = 0
for needle, builder in repl:
    found = False
    for i in range(idx0, idx1):
        if needle in lines[i]:
            lines[i] = builder(ind_of(lines[i])); found = True; modifs += 1; break
    print(("[OK] " if found else "[WARN] NON trouve : ") + needle[:50])

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_sections4pans"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")
open("devia.jsx", "w", encoding="utf-8").write("\n".join(lines))
print(f"\n{modifs} REMPLACEMENT(S) APPLIQUE(S)")
