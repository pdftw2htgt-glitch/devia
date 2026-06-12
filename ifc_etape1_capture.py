#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - IFC etape 1 : enrichir metre[] avec position + rotation + dims brutes"""
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

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_ifc_capture"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) logPiece accepte des infos de placement optionnelles (pos, rot, quaternion, dims brutes)
apply(
    '''  const logPiece = (a, b, c) => {
    const dims = [a, b, c].sort((u, v) => v - u);
    const longueur = dims[0];
    const sx = dims[1], sy = dims[2];
    const volume = a * b * c;
    metre.push({
      nom: currentPiece,
      section: [Math.round(sx*1000), Math.round(sy*1000)], // mm
      longueur: longueur,                                   // m
      volume: volume,                                       // m3
    });
  };''',
    '''  const logPiece = (a, b, c, place) => {
    const dims = [a, b, c].sort((u, v) => v - u);
    const longueur = dims[0];
    const sx = dims[1], sy = dims[2];
    const volume = a * b * c;
    metre.push({
      nom: currentPiece,
      section: [Math.round(sx*1000), Math.round(sy*1000)], // mm
      longueur: longueur,                                   // m
      volume: volume,                                       // m3
      // placement 3D pour export IFC (optionnel)
      dimsBrutes: [a, b, c],          // sx, sy, sz d'origine (m)
      pos: place ? place.pos : null,  // [x, y, z] centre (m)
      rot: place ? place.rot : null,  // [rx, ry, rz] euler (rad) ou null
      quat: place ? place.quat : null,// [x, y, z, w] quaternion ou null
    });
  };'''
    ,
    "logPiece enrichi (place optionnel)"
)

# 2) addBox transmet sa position + rotation
apply(
    '''    m.castShadow = true;
    scene.add(m);
    if (!mat || mat === woodMat) logPiece(sx, sy, sz); // bois uniquement
  };''',
    '''    m.castShadow = true;
    scene.add(m);
    if (!mat || mat === woodMat) logPiece(sx, sy, sz, { pos: [px, py, pz], rot: rot || null, quat: null }); // bois uniquement
  };''',
    "addBox transmet pos + rot"
)

# 3) addBeam transmet sa position + quaternion
apply(
    '''    m.castShadow = true;
    scene.add(m);
    if (!mat || mat === woodMat) logPiece(thick, thick, len);
  };''',
    '''    m.castShadow = true;
    scene.add(m);
    if (!mat || mat === woodMat) logPiece(thick, thick, len, { pos: [(x1+x2)/2, (y1+y2)/2, (z1+z2)/2], rot: null, quat: [q.x, q.y, q.z, q.w] });
  };''',
    "addBeam transmet pos + quaternion"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
