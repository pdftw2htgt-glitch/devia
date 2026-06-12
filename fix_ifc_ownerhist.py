#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Fix IFC : supprime l'entite invalide #n=$ (ownerHist) qui casse le chargement"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()

old = '''  const ownerHist = nextId(); E(ownerHist, "$"); // simplifie (pas d'historique)

'''
new = ''

n = content.count(old)
if n != 1:
    # tentative sans la ligne vide finale
    old2 = '''  const ownerHist = nextId(); E(ownerHist, "$"); // simplifie (pas d'historique)'''
    n2 = content.count(old2)
    if n2 == 1:
        backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fix_ifc_owner"
        shutil.copy("devia.jsx", backup)
        print(f"[OK] Backup : {backup}")
        content = content.replace(old2, "", 1)
        open("devia.jsx", "w", encoding="utf-8").write(content)
        print("[OK] Ligne ownerHist supprimee (variante)")
        print("1 MODIFICATION APPLIQUEE")
    else:
        print(f"[ERREUR] ancre trouvee {n} / variante {n2} fois -> abandon")
        exit(1)
else:
    backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fix_ifc_owner"
    shutil.copy("devia.jsx", backup)
    print(f"[OK] Backup : {backup}")
    content = content.replace(old, new, 1)
    open("devia.jsx", "w", encoding="utf-8").write(content)
    print("[OK] Ligne ownerHist supprimee")
    print("1 MODIFICATION APPLIQUEE")
