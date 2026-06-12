#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Fix : deplacer le bloc EC5 (constantes + fonctions) AVANT buildScene3D"""
import shutil, re
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()
lines = content.split("\n")

# 1) Reperer le bloc EC5 : du commentaire/const EC5_BOIS jusqu'a la fin de calculerSectionsCharpente
start = next((i for i,l in enumerate(lines) if l.startswith("const EC5_BOIS")), None)
if start is None:
    print("[ERREUR] EC5_BOIS introuvable"); exit(1)
# remonter pour inclure un eventuel commentaire juste au-dessus
while start > 0 and (lines[start-1].strip().startswith("//") or lines[start-1].strip()==""):
    start -= 1

# trouver la fin de calculerSectionsCharpente : compter les accolades a partir de sa declaration
fn_start = next((i for i,l in enumerate(lines) if "function calculerSectionsCharpente" in l), None)
if fn_start is None:
    print("[ERREUR] calculerSectionsCharpente introuvable"); exit(1)
depth = 0; started = False; end = None
for i in range(fn_start, len(lines)):
    depth += lines[i].count("{") - lines[i].count("}")
    if "{" in lines[i]: started = True
    if started and depth == 0:
        end = i; break
if end is None:
    print("[ERREUR] fin de calculerSectionsCharpente introuvable"); exit(1)

bloc = lines[start:end+1]
print(f"[INFO] Bloc EC5 : lignes {start+1} a {end+1} ({len(bloc)} lignes)")

# 2) Retirer le bloc de sa position actuelle
del lines[start:end+1]

# 3) Inserer le bloc juste AVANT buildScene3D
ins = next((i for i,l in enumerate(lines) if "function buildScene3D" in l), None)
# remonter pour passer au-dessus d'un commentaire de buildScene3D
j = ins
while j > 0 and (lines[j-1].strip().startswith("//") or lines[j-1].strip()==""):
    j -= 1
insert_at = j

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fix_ordre_ec5"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

new_lines = lines[:insert_at] + ["// ===== MOTEUR EC5 (deplace avant buildScene3D pour init) ====="] + bloc + [""] + lines[insert_at:]
open("devia.jsx", "w", encoding="utf-8").write("\n".join(new_lines))
print(f"[OK] Bloc EC5 deplace avant buildScene3D (ligne {insert_at+1})")
print("1 MODIFICATION APPLIQUEE")
