#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix : z-index dropdown groupe projet
Le dropdown passait derriere les cards suivantes
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_zindex_fix"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# Le dropdown projet a maxHeight: 280 - on cible ce contexte precis
old_dropdown_style = '''maxHeight: 280,
                                overflowY: "auto",
                                boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
                                zIndex: 20'''

new_dropdown_style = '''maxHeight: 280,
                                overflowY: "auto",
                                boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
                                zIndex: 100'''

if "zIndex: 100" in content and "maxHeight: 280" in content:
    print("[INFO] Fix deja applique")
elif old_dropdown_style in content:
    content = content.replace(old_dropdown_style, new_dropdown_style, 1)
    print("[OK] z-index dropdown projet passe de 20 a 100")
else:
    print("[ERREUR] Bloc dropdown non trouve")
    sys.exit(1)

# Ajouter aussi position: relative + zIndex eleve sur le wrapper de la card
# au moment ou le dropdown est ouvert (pour que la card soit AU-DESSUS des autres)
# Mais on ne touche pas a ca, on garde simple : un z-index de 100 sur le dropdown
# devrait suffire vu que les cards n'ont pas de stacking context

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK, recharger Safari et retester")
print()
print(f"BACKUP : {backup_name}")
