#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Metre etape 1 : capture des pieces dans addBox/addBeam"""
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

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_metre_capture"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) Declarer metre + currentPiece + densites, juste apres la signature
apply(
    '''  const woodMat = new THREE.MeshLambertMaterial({ color: woodColor });''',
    '''  // ===== METRE : capture des pieces dessinees =====
  const DENSITES_BOIS = { sapin: 450, epicea: 450, douglas: 520, chene: 700, pin: 510 };
  const essence = (params && params.essence) ? params.essence : "sapin";
  const densiteBois = DENSITES_BOIS[essence] || 450;
  const metre = [];
  let currentPiece = "Divers";
  const setPiece = (nom) => { currentPiece = nom; };
  // longueur estimee = plus grande dimension de la piece
  const logPiece = (a, b, c) => {
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
  };

  const woodMat = new THREE.MeshLambertMaterial({ color: woodColor });''',
    "Declaration metre + densites + helpers"
)

# 2) addBox : logguer la piece (seulement si c'est du bois -> mat woodMat ou non precise)
apply(
    '''  const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), mat || woodMat);
    m.position.set(px, py, pz);
    if (rot) m.rotation.set(...rot);
    m.castShadow = true;
    scene.add(m);
  };''',
    '''  const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), mat || woodMat);
    m.position.set(px, py, pz);
    if (rot) m.rotation.set(...rot);
    m.castShadow = true;
    scene.add(m);
    if (!mat || mat === woodMat) logPiece(sx, sy, sz); // bois uniquement
  };''',
    "addBox : capture piece bois"
)

# 3) addBeam : logguer (toujours du bois)
apply(
    '''    const dir = new THREE.Vector3(dx, dy, dz).normalize();
    const q = new THREE.Quaternion();
    q.setFromUnitVectors(new THREE.Vector3(0, 0, 1), dir);
    m.quaternion.copy(q);
    m.castShadow = true;
    scene.add(m);
  };''',
    '''    const dir = new THREE.Vector3(dx, dy, dz).normalize();
    const q = new THREE.Quaternion();
    q.setFromUnitVectors(new THREE.Vector3(0, 0, 1), dir);
    m.quaternion.copy(q);
    m.castShadow = true;
    scene.add(m);
    if (!mat || mat === woodMat) logPiece(thick, thick, len);
  };''',
    "addBeam : capture piece bois"
)

# 4) return : faire remonter metre + densite
apply(
    "  return { yCentre };",
    "  return { yCentre, metre, densiteBois, essence };",
    "return enrichi avec metre"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
