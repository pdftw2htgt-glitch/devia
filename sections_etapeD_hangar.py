#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Sections etape D : sections EC5 sur sabliere/entrait/arbaletrier/chevron du hangar"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()
modifs = 0
def apply(old, new, label):
    global content, modifs
    n = content.count(old)
    if n == 1:
        content = content.replace(old, new, 1); print(f"[OK] {label}"); modifs += 1
    elif n == 0: print(f"[WARN] {label} : NON trouve")
    else: print(f"[WARN] {label} : {n}x ambigu -> ignore")

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_sectionsD"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) SABLIERE hangar : axe long X, section sur Y(haut)/Z. Sur chant : h vertical (Y), b sur Z.
apply(
    '''    addBox(L + 0.4, 0.20, 0.20, 0, Ht, lg/2, woodMat);
    addBox(L + 0.4, 0.20, 0.20, 0, Ht, -lg/2, woodMat);''',
    '''    const [sbB, sbH] = sec("Sabliere", 0.20, 0.20);
    addBox(L + 0.4, sbH, sbB, 0, Ht, lg/2, woodMat);
    addBox(L + 0.4, sbH, sbB, 0, Ht, -lg/2, woodMat);''',
    "Sabliere hangar section EC5 (sur chant)"
)

# 2) ENTRAIT (Ferme) : axe long Z (lg). Section sur X,Y. Sur chant : h sur Y, b sur X.
apply(
    '''      addBox(0.16, 0.16, lg, x, Ht, 0, woodMat);''',
    '''      const [enB, enH] = sec("Ferme", 0.16, 0.16);
      addBox(enB, enH, lg, x, Ht, 0, woodMat);''',
    "Entrait hangar section EC5"
)

# 3) ARBALETRIERS (Ferme) : axe long Z incline [ang]. Section sur X,Y. Sur chant : h sur Y, b sur X.
apply(
    '''      addBox(0.16, 0.16, pl, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);
      addBox(0.16, 0.16, pl, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);''',
    '''      const [arB, arH] = sec("Ferme", 0.16, 0.16);
      addBox(arB, arH, pl, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);
      addBox(arB, arH, pl, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);''',
    "Arbaletriers hangar section EC5"
)

# 4) CHEVRONS : axe long Z incline. Section sur X,Y. Sur chant : h sur Y, b sur X.
apply(
    '''      addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, lg/4, woodMat, [ang, 0, 0]);
      addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, -lg/4, woodMat, [-ang, 0, 0]);''',
    '''      const [chB, chH] = sec("Chevron", 0.07, 0.07);
      addBox(chB, chH, pl, x, Ht + hf/2 + 0.08, lg/4, woodMat, [ang, 0, 0]);
      addBox(chB, chH, pl, x, Ht + hf/2 + 0.08, -lg/4, woodMat, [-ang, 0, 0]);''',
    "Chevrons hangar section EC5"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
