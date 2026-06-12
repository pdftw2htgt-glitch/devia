#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix prompt IA : ajouter monopente + appentis dans la detection type_projet
Le prompt ne proposait que carport/charpente_trad/hangar/abri/autre.
On ajoute monopente et appentis (+ on prepare 4_pans, fermette, mezzanine pour plus tard).
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_fix_prompt_types"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Mettre a jour le bloc DETECTION DU TYPE
# ================================================================

old_detection_block = '''"DETECTION DU TYPE DE PROJET : analyse la description et choisis 1 valeur pour type_projet : " +
"'carport' (si carport, abri voiture, auvent ouvert sans murs, structure sur potaux), " +
"'charpente_trad' (charpente traditionnelle de maison, toit 2 pans avec murs), " +
"'hangar' (hangar agricole, batiment industriel, grand volume couvert), " +
"'abri' (abri jardin, abri petit volume), " +
"'autre' (si rien ne correspond clairement). " +'''

new_detection_block = '''"DETECTION DU TYPE DE PROJET : analyse la description et choisis 1 valeur pour type_projet : " +
"'carport' (carport, abri voiture, auvent ouvert sans murs, structure sur poteaux, toit 1 pan), " +
"'charpente_trad' (charpente traditionnelle de maison, toit 2 pans avec murs), " +
"'monopente' (batiment ferme avec murs et toit a 1 SEULE pente, atelier, garage), " +
"'hangar' (hangar agricole, batiment industriel, grand volume couvert, poteaux + 2 pans sans murs), " +
"'appentis' (toit 1 pan ACCOLE a un mur existant, terrasse couverte, abri a bois contre une maison), " +
"'abri' (abri jardin, abri petit volume), " +
"'autre' (si rien ne correspond clairement). " +
"IMPORTANT : si la description mentionne 'monopente' ou '1 seule pente' avec des murs, utilise 'monopente'. Si elle mentionne 'accole', 'contre un mur', 'contre la maison', utilise 'appentis'. " +'''

if "'monopente' (batiment ferme" in content:
    print("[INFO] Bloc detection deja a jour")
elif old_detection_block in content:
    content = content.replace(old_detection_block, new_detection_block, 1)
    print("[OK] Bloc DETECTION DU TYPE enrichi (monopente + appentis)")
    modifs += 1
else:
    print("[ERREUR] Bloc detection non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Mettre a jour l'exemple JSON type_projet
# ================================================================

old_json_type = '\'"type_projet":"carport_OU_charpente_trad_OU_hangar_OU_abri_OU_autre"},\''
new_json_type = '\'"type_projet":"carport_OU_charpente_trad_OU_monopente_OU_hangar_OU_appentis_OU_abri_OU_autre"},\''

if "monopente_OU_hangar_OU_appentis" in content:
    print("[INFO] Exemple JSON type_projet deja a jour")
elif old_json_type in content:
    content = content.replace(old_json_type, new_json_type, 1)
    print("[OK] Exemple JSON type_projet mis a jour")
    modifs += 1
else:
    print("[WARN] Exemple JSON type_projet non trouve exactement")

# ================================================================
# MOD 3 : Nettoyer le doublon de ratio hangar dans le prompt
# (il y avait "Pour un hangar : 0.3-0.5h..." en double)
# ================================================================

old_hangar_dup = ''' Pour un hangar (batiment agricole, grande portee, poteaux + 2 pans) : 0.3-0.5h fabrication par m2 + 0.25-0.4h pose par m2. Pour un appentis (toit accole a mur existant, terrasse couverte, abri a bois) : 0.4-0.6h fabrication par m2 + 0.35-0.5h pose par m2. " +
"Pour un hangar : 0.3-0.5h fabrication par m2 + 0.2-0.4h pose par m2. " +'''

new_hangar_clean = ''' Pour un hangar (batiment agricole, grande portee, poteaux + 2 pans) : 0.3-0.5h fabrication par m2 + 0.25-0.4h pose par m2. Pour un appentis (toit accole a mur existant, terrasse couverte, abri a bois) : 0.4-0.6h fabrication par m2 + 0.35-0.5h pose par m2. " +'''

if old_hangar_dup in content:
    content = content.replace(old_hangar_dup, new_hangar_clean, 1)
    print("[OK] Doublon ratio hangar nettoye")
    modifs += 1
else:
    print("[INFO] Pas de doublon hangar a nettoyer (ou deja fait)")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Bloc DETECTION enrichi : monopente + appentis ajoutes avec descriptions")
print("  2. Exemple JSON type_projet : liste complete")
print("  3. Doublon ratio hangar nettoye")
print()
print("MAINTENANT L'IA PEUT RETOURNER :")
print("  carport, charpente_trad, monopente, hangar, appentis, abri, autre")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
