#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Baisse le seuil de confiance de l'API a 0.2 et log le score
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_lower_threshold"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# Baisser le seuil ET ajouter un log du score
old_check = '''if (!data.features || data.features.length === 0) return null;
      const feat = data.features[0];
      // Score de confiance entre 0 et 1, on prend que si > 0.4
      if (!feat.properties.score || feat.properties.score < 0.4) return null;'''

new_check = '''if (!data.features || data.features.length === 0) {
        console.log("[DEVIA] API n'a renvoye aucune feature");
        return null;
      }
      const feat = data.features[0];
      console.log("[DEVIA] API score:", feat.properties.score, "Label:", feat.properties.label, "Ville:", feat.properties.city);
      // Score de confiance entre 0 et 1, on accepte si >= 0.2 (assez permissif)
      if (!feat.properties.score || feat.properties.score < 0.2) {
        console.log("[DEVIA] Score trop bas, rejete");
        return null;
      }'''

if "Score trop bas, rejete" in content:
    print("[INFO] Fix deja applique")
elif old_check in content:
    content = content.replace(old_check, new_check, 1)
    print("[OK] Seuil baisse de 0.4 a 0.2 + logs ajoutes")
else:
    print("[ERREUR] Bloc original non trouve.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("PROCHAINE ETAPE :")
print("  npm run dev (relance ou attends que ca recharge)")
print("  Retape ton prompt dans DEVIA")
print("  Regarde la console : tu verras [DEVIA] API score: X.XX")
print()
print(f"BACKUP : {backup_name}")
