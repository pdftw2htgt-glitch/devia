#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Sections D2 : entrait + arbaletriers HANGAR (par numero de ligne, ~514-517)"""
import shutil
from datetime import datetime

lines = open("devia.jsx", encoding="utf-8").read().split("\n")

# Reperer la fonction hangar pour securiser (entre drawHangar et fin)
idx_hangar = None
for i, l in enumerate(lines):
    if "const drawHangar" in l:
        idx_hangar = i; break
if idx_hangar is None:
    print("[ERREUR] drawHangar introuvable"); exit(1)

# Chercher l'entrait du hangar (1ere occurrence APRES drawHangar)
entrait_line = None
arba_line = None
for i in range(idx_hangar, len(lines)):
    if entrait_line is None and "addBox(0.16, 0.16, lg, x, Ht, 0, woodMat);" in lines[i]:
        entrait_line = i
    if arba_line is None and "addBox(0.16, 0.16, pl, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);" in lines[i]:
        arba_line = i
    if entrait_line and arba_line:
        break

if entrait_line is None or arba_line is None:
    print("[ERREUR] pieces hangar introuvables"); exit(1)
print(f"[INFO] Entrait hangar ligne {entrait_line+1}, Arbaletrier ligne {arba_line+1}")

# Verif : l'arbaletrier ligne suivante doit etre le -lg/4
arba_line2 = arba_line + 1
if "addBox(0.16, 0.16, pl, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);" not in lines[arba_line2]:
    print(f"[ERREUR] 2e arbaletrier pas a la ligne {arba_line2+1}"); exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_sectionsD2"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# Indentation
ind_e = lines[entrait_line][:len(lines[entrait_line]) - len(lines[entrait_line].lstrip())]
ind_a = lines[arba_line][:len(lines[arba_line]) - len(lines[arba_line].lstrip())]

# Remplacer entrait (ligne entrait_line) par 2 lignes
lines[entrait_line] = (
    f'{ind_e}const [enB, enH] = sec("Ferme", 0.16, 0.16);\n'
    f'{ind_e}addBox(enB, enH, lg, x, Ht, 0, woodMat);'
)
# Remplacer les 2 arbaletriers
lines[arba_line] = (
    f'{ind_a}const [arB, arH] = sec("Ferme", 0.16, 0.16);\n'
    f'{ind_a}addBox(arB, arH, pl, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);'
)
lines[arba_line2] = f'{ind_a}addBox(arB, arH, pl, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);'

open("devia.jsx", "w", encoding="utf-8").write("\n".join(lines))
print("[OK] Entrait + arbaletriers hangar avec section EC5")
print("MODIFICATION APPLIQUEE")
