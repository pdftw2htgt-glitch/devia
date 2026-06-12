#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Fix boucle re-render Viewer3D (zoom/rotation casses)"""
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

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fix_3d_loop"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) Stocker onMetre dans un ref (ne participe pas aux deps)
apply(
    '''function Viewer3D({ params, onMetre }) {
  const mountRef = useRef(null);''',
    '''function Viewer3D({ params, onMetre }) {
  const mountRef = useRef(null);
  const onMetreRef = useRef(onMetre);
  onMetreRef.current = onMetre;''',
    "onMetre stocke dans un ref"
)

# 2) Utiliser le ref dans le useEffect
apply(
    '''    if (onMetre && buildResultViewer.metre) {
      onMetre(agregerMetre(buildResultViewer.metre, buildResultViewer.densiteBois || 450));
    }''',
    '''    if (onMetreRef.current && buildResultViewer.metre) {
      onMetreRef.current(agregerMetre(buildResultViewer.metre, buildResultViewer.densiteBois || 450));
    }''',
    "Appel via onMetreRef"
)

# 3) Remplacer la dependance [params] par les valeurs primitives
apply(
    "  }, [params]);",
    "  }, [params.longueur, params.largeur, params.hauteur, params.pente, params.type_projet, params.couverture, params.mode3D]);",
    "Dependances primitives (fin de boucle)"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
