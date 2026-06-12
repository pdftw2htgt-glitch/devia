#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 2 fixes extraction adresse :
1. Seuil baisse a 0.1 (pour villes seules)
2. Utiliser le label complet (au lieu de juste la ville)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_threshold_label_fix"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# FIX 1 : Baisser le seuil de 0.2 a 0.1
# ================================================================

old_threshold = '''// Score de confiance entre 0 et 1, on accepte si >= 0.2 (assez permissif)
      if (!feat.properties.score || feat.properties.score < 0.2) {
        console.log("[DEVIA] Score trop bas, rejete");
        return null;
      }'''

new_threshold = '''// Score de confiance entre 0 et 1, on accepte si >= 0.1 (tres permissif pour les villes seules)
      if (!feat.properties.score || feat.properties.score < 0.1) {
        console.log("[DEVIA] Score trop bas, rejete");
        return null;
      }'''

if "feat.properties.score < 0.1" in content:
    print("[INFO] Seuil deja a 0.1")
elif old_threshold in content:
    content = content.replace(old_threshold, new_threshold, 1)
    print("[OK] Seuil baisse de 0.2 a 0.1")
    modifs += 1
else:
    print("[WARN] Seuil 0.2 non trouve")

# ================================================================
# FIX 2 : Utiliser le label complet au lieu de juste la ville
# ================================================================

old_fill = '''if (extracted && (!commune || commune.trim() === "")) {
        const villeDetectee = extracted.ville || extracted.label;
        console.log("[DEVIA] Remplissage du champ Localisation avec:", villeDetectee);
        setCommune(villeDetectee);
        setAddressData(extracted);
      }'''

new_fill = '''if (extracted && (!commune || commune.trim() === "")) {
        // On utilise le label complet (adresse complete si l'user en a tape une, sinon juste la ville)
        const valeurChamp = extracted.label || extracted.ville;
        console.log("[DEVIA] Remplissage du champ Localisation avec:", valeurChamp);
        setCommune(valeurChamp);
        setAddressData(extracted);
      }'''

if "extracted.label || extracted.ville" in content:
    print("[INFO] Label deja en place")
elif old_fill in content:
    content = content.replace(old_fill, new_fill, 1)
    print("[OK] Champ Localisation remplit avec label complet")
    modifs += 1
else:
    print("[WARN] Bloc remplissage non trouve")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Seuil API baisse a 0.1 (plus permissif)")
print("     -> Detecte aussi 'Marseille', 'Annecy', etc.")
print("  2. Le champ Localisation affiche le label complet :")
print("     - Adresse complete si tapee (ex: 'Rue Merciere 69001 Lyon')")
print("     - Juste la ville sinon (ex: 'Marseille')")
print()
print(f"BACKUP : {backup_name}")
