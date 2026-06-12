#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix geometrie toit 1 pan (carport + monopente + appentis)

BUG : le toit utilisait rotation.z = ang + rotation.y = Math.PI/2
      => la couverture etait a la VERTICALE au lieu de suivre la pente.
      Et les chevrons avaient le mauvais signe d'angle.

FIX (geometrie recalculee proprement) :
  - Toit : PlaneGeometry(L, longueurChevron) + rotation.x = Math.PI/2 - ang
           (un seul axe, le plan suit exactement la pente)
  - Chevrons : rotation [-ang, 0, 0] (montent du cote bas vers le cote haut)

Ces 3 structures partagent le meme code => on corrige les 3 d'un coup.
On ne touche PAS au toit 2 pans (charpente_trad / hangar) qui fonctionne.
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_fix_toit_1pan"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Corriger le bloc TOIT 1 pan (3 occurrences : carport, monopente, appentis)
# ================================================================

old_roof_block = '''    const rg = new THREE.PlaneGeometry(longueurChevron + 0.3, L + 0.4);
    const roof = new THREE.Mesh(rg, roofMat);
    roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
    roof.rotation.z = ang;
    roof.rotation.y = Math.PI/2;
    scene.add(roof);'''

new_roof_block = '''    const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
    const roof = new THREE.Mesh(rg, roofMat);
    roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);'''

nb_roof = content.count(old_roof_block)
if nb_roof == 0:
    if "roof.rotation.x = Math.PI/2 - ang" in content:
        print("[INFO] Toit 1 pan deja corrige")
    else:
        print("[ERREUR] Bloc toit 1 pan non trouve")
        sys.exit(1)
else:
    content = content.replace(old_roof_block, new_roof_block)
    print(f"[OK] Toit 1 pan corrige ({nb_roof} occurrences : carport + monopente + appentis)")
    modifs += nb_roof

# ================================================================
# MOD 2 : Corriger le signe d'angle des chevrons 1 pan (3 occurrences)
# On cible la ligne specifique aux chevrons 1 pan (section 0.10x0.10 + longueurChevron)
# pour ne PAS toucher aux arbaletriers 2 pans qui utilisent [ang, 0, 0]
# ================================================================

old_chevron = 'longueurChevron + 0.2, x, yCentre, 0, woodMat, [ang, 0, 0])'
new_chevron = 'longueurChevron + 0.2, x, yCentre, 0, woodMat, [-ang, 0, 0])'

nb_chevron = content.count(old_chevron)
if nb_chevron == 0:
    if 'longueurChevron + 0.2, x, yCentre, 0, woodMat, [-ang, 0, 0])' in content:
        print("[INFO] Chevrons 1 pan deja corriges")
    else:
        print("[WARN] Ligne chevrons 1 pan non trouvee")
else:
    content = content.replace(old_chevron, new_chevron)
    print(f"[OK] Chevrons 1 pan corriges ({nb_chevron} occurrences)")
    modifs += nb_chevron

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} CORRECTIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  - Toit 1 pan : suit maintenant la pente (plus a la verticale)")
print("  - Chevrons 1 pan : montent du cote bas vers le cote haut")
print("  - Touche : carport, monopente, appentis")
print("  - NON touche : charpente_trad et hangar (toit 2 pans, OK)")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
