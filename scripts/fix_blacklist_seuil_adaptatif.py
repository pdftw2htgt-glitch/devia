#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix faux positifs extraction adresse :
1. Blacklist elargie (adjectifs courants : Petit, Grand, Nouveau, etc.)
2. Seuil 0.85 pour les candidats a UN seul mot (eviter "Petit 40550 Leon")
3. Seuil 0.5 pour les candidats avec plusieurs mots (code postal+ville, adresse...)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_blacklist_fix"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# FIX 1 : Elargir la blacklist
# ================================================================

old_blacklist = '''const blacklist = new Set([
      "Carport", "Charpente", "Garage", "Maison", "Toiture", "Abri",
      "Sapin", "Douglas", "Chene", "Pin", "Epicea", "Ardoise",
      "Tuile", "Bardeau", "Bac", "Acier", "Zinc", "Cuivre",
      "Traditionnelle", "Fermette", "Industriel", "Metalique",
      "Neuve", "Renovation", "Combles"
    ]);'''

new_blacklist = '''const blacklist = new Set([
      // Types de constructions
      "Carport", "Charpente", "Garage", "Maison", "Toiture", "Abri", "Pergola",
      "Hangar", "Veranda", "Extension", "Ossature", "Cabanon", "Atelier",
      // Materiaux
      "Sapin", "Douglas", "Chene", "Pin", "Epicea", "Melèze", "Meleze",
      "Ardoise", "Tuile", "Bardeau", "Bac", "Acier", "Zinc", "Cuivre", "Plomb",
      "Beton", "Terre", "Cuite", "Lauze", "Shingle",
      // Types de charpente
      "Traditionnelle", "Fermette", "Industriel", "Industrielle", "Metalique", "Metallique",
      "Lamelle", "Lamellee", "Colle", "Massif", "Bois",
      // Etat travaux
      "Neuve", "Neuf", "Renovation", "Refection", "Combles", "Perdus",
      "Amenagees", "Amenageables",
      // Adjectifs courants (faux positifs)
      "Petit", "Petite", "Grand", "Grande", "Nouveau", "Nouvelle",
      "Vieux", "Vieille", "Ancien", "Ancienne", "Beau", "Belle", "Bel",
      "Premier", "Premiere", "Second", "Seconde",
      // Autres
      "Pente", "Pentes", "Toit", "Faite", "Faitage", "Pignon", "Pignons",
      "Sablieres", "Sabliere", "Chevrons", "Chevron", "Pannes", "Panne",
      "Liteaux", "Liteau", "Arbaletriers", "Arbaletrier"
    ]);'''

if '"Pergola"' in content and '"Petit"' in content:
    print("[INFO] Blacklist deja elargie")
elif old_blacklist in content:
    content = content.replace(old_blacklist, new_blacklist, 1)
    print("[OK] Blacklist elargie (Petit, Grand, Carport, materiaux, etc.)")
    modifs += 1
else:
    print("[WARN] Blacklist non trouvee")

# ================================================================
# FIX 2 : Seuil adaptatif (0.85 pour 1 mot, 0.5 pour plusieurs mots)
# ================================================================

old_seuil_check = '''console.log("[DEVIA] Query:", query, "-> Score:", feat.properties.score, "Label:", feat.properties.label);

        // Seuil 0.5 (plus exigeant car on cherche sur des candidats deja propres)
        if (!feat.properties.score || feat.properties.score < 0.5) {
          console.log("[DEVIA] Score trop bas pour:", query);
          continue;
        }'''

new_seuil_check = '''console.log("[DEVIA] Query:", query, "-> Score:", feat.properties.score, "Label:", feat.properties.label);

        // Seuil adaptatif : 0.85 pour 1 mot seul, 0.5 pour plusieurs mots
        const motsCandidat = query.trim().split(/\\s+/).length;
        const seuilMin = motsCandidat === 1 ? 0.85 : 0.5;
        if (!feat.properties.score || feat.properties.score < seuilMin) {
          console.log("[DEVIA] Score", feat.properties.score, "<", seuilMin, "pour:", query, "(", motsCandidat, "mot(s)) -> rejete");
          continue;
        }'''

if "seuilMin" in content:
    print("[INFO] Seuil adaptatif deja en place")
elif old_seuil_check in content:
    content = content.replace(old_seuil_check, new_seuil_check, 1)
    print("[OK] Seuil adaptatif : 0.85 pour 1 mot, 0.5 pour plusieurs")
    modifs += 1
else:
    print("[WARN] Bloc seuil non trouve")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("LOGIQUE FINALE :")
print("  - Blacklist : Petit/Grand/Carport/Ardoise/Sapin/etc. ignores")
print("  - 1 mot seul : score >= 0.85 (tres exigeant, doit etre une vraie ville)")
print("  - Plusieurs mots : score >= 0.5 (permissif, on a deja filtre)")
print()
print(f"BACKUP : {backup_name}")
