#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Suppression complete du type 'main_oeuvre' dans devia.jsx
- DEVIA ne facture plus la pose, juste les fournitures
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_remove_mo"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Supprimer le type main_oeuvre de MATERIAL_TYPES
# ================================================================

old_mo_block = '''  main_oeuvre: {
    label: "Main d'oeuvre",
    color: "#f0c040",
    keywords: ["main d'oeuvre", "main doeuvre", "charpentier", "manoeuvre", "pose", "depose", "installation", "demontage", "ouvrier", "chef equipe", "compagnon"],
    showDimensions: false,
    suggestedUnits: ["h", "forfait", "m2"],
    defaultUnit: "h",
    placeholder: ""
  },
'''

if old_mo_block in content:
    content = content.replace(old_mo_block, "", 1)
    print("[OK] Type main_oeuvre supprime de MATERIAL_TYPES")
    modifs += 1
elif "main_oeuvre: {" not in content:
    print("[INFO] Type main_oeuvre deja supprime")
else:
    print("[WARN] Bloc main_oeuvre non trouve exactement - peut-etre format different")

# ================================================================
# MOD 2 : Retirer main_oeuvre du typeToCategorie
# ================================================================

old_mapping = '''    main_oeuvre: "Main d'oeuvre",
'''
if old_mapping in content:
    content = content.replace(old_mapping, "", 1)
    print("[OK] Mapping main_oeuvre supprime de typeToCategorie")
    modifs += 1
else:
    print("[INFO] Mapping main_oeuvre deja absent de typeToCategorie")

# ================================================================
# MOD 3 : Retirer "Main d'oeuvre" du reverseMap categorieToType
# ================================================================

old_reverse = '''    "Main d'oeuvre": "main_oeuvre",
'''
if old_reverse in content:
    content = content.replace(old_reverse, "", 1)
    print("[OK] Reverse mapping Main d'oeuvre supprime de categorieToType")
    modifs += 1
else:
    print("[INFO] Reverse mapping deja absent")

# ================================================================
# MOD 4 : Retirer "Main d'oeuvre" de la liste isStandardCat dans openEditCatalogModal
# ================================================================

old_standard = '["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie", "Main d\'oeuvre", "Outillage"]'
new_standard = '["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie", "Outillage"]'

if old_standard in content:
    content = content.replace(old_standard, new_standard, 1)
    print("[OK] Main d'oeuvre retire de isStandardCat")
    modifs += 1
elif "[\"Charpente\", \"Bardage\", \"Couverture\", \"Isolation\", \"Quincaillerie\", \"Outillage\"]" in content:
    print("[INFO] isStandardCat deja sans Main d'oeuvre")
else:
    print("[WARN] Liste isStandardCat non trouvee")

# Tentative avec l'autre format (sans Outillage, version originale)
old_standard_orig = '["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie", "Main d\'oeuvre"]'
new_standard_orig = '["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie"]'

if old_standard_orig in content:
    content = content.replace(old_standard_orig, new_standard_orig, 1)
    print("[OK] Variante isStandardCat (originale) corrigee")
    modifs += 1

# ================================================================
# MOD 5 : Retirer la couleur "240, 192, 64" liee a main_oeuvre dans le badge
# La couleur est partagee avec l'or general, on adapte la condition
# ================================================================

# La ligne actuelle :
# activeType === "main_oeuvre" ? "240, 192, 64" : activeType === "outillage" ? ...
# Devient :
# activeType === "outillage" ? "251, 146, 60" : ...

old_color_condition = 'activeType === "main_oeuvre" ? "240, 192, 64" : activeType === "outillage" ? "251, 146, 60"'
new_color_condition = 'activeType === "outillage" ? "251, 146, 60"'

if old_color_condition in content:
    content = content.replace(old_color_condition, new_color_condition, 1)
    print("[OK] Condition de couleur main_oeuvre retiree du badge")
    modifs += 1
elif old_color_condition not in content and "activeType === \"main_oeuvre\"" not in content:
    print("[INFO] Couleur main_oeuvre deja absente")
else:
    print("[WARN] Condition de couleur main_oeuvre non trouvee exactement")

# ================================================================
# MOD 6 : Retirer l'option Main d'oeuvre dans le selecteur de categorie
# (au cas ou il y aurait encore une reference dans l'ancien dropdown)
# ================================================================

old_option = '              <option value="Main d\'oeuvre">Main d\'oeuvre</option>\n'
if old_option in content:
    content = content.replace(old_option, "", 1)
    print("[OK] Option Main d'oeuvre du dropdown categorie supprimee")
    modifs += 1
else:
    print("[INFO] Option dropdown Main d'oeuvre deja absente (champ deja supprime)")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Type main_oeuvre retire de MATERIAL_TYPES")
print("  2. Mapping main_oeuvre retire de typeToCategorie")
print("  3. Reverse mapping Main d'oeuvre retire de categorieToType")
print("  4. Main d'oeuvre retire de isStandardCat (mode edition)")
print("  5. Couleur or pour main_oeuvre retiree du badge")
print("  6. Option dropdown Main d'oeuvre supprimee si presente")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
