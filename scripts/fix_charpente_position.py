#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix positionnement charpente trad technique
PROBLEMES :
  1. Arbaletriers + chevrons trop hauts (depassent le faitage)
     => cause : "+ Math.PI/2" en trop dans la rotation
  2. Contrefiches (bras du poincon) ne touchent pas
     => fix : dessin point-a-point avec quaternion (touche forcement)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_fix_charpente_pos"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter un helper addBeam (poutre point-a-point) apres addBox
# ================================================================

old_addbox = '''  const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), mat || woodMat);
    m.position.set(px, py, pz);
    if (rot) m.rotation.set(...rot);
    m.castShadow = true;
    scene.add(m);
  };'''

new_addbox_with_beam = '''  const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), mat || woodMat);
    m.position.set(px, py, pz);
    if (rot) m.rotation.set(...rot);
    m.castShadow = true;
    scene.add(m);
  };

  // Poutre orientee entre 2 points (touche forcement les 2 extremites)
  const addBeam = (x1, y1, z1, x2, y2, z2, thick, mat) => {
    const dx = x2 - x1, dy = y2 - y1, dz = z2 - z1;
    const len = Math.sqrt(dx*dx + dy*dy + dz*dz);
    const m = new THREE.Mesh(new THREE.BoxGeometry(thick, thick, len), mat || woodMat);
    m.position.set((x1+x2)/2, (y1+y2)/2, (z1+z2)/2);
    const dir = new THREE.Vector3(dx, dy, dz).normalize();
    const q = new THREE.Quaternion();
    q.setFromUnitVectors(new THREE.Vector3(0, 0, 1), dir);
    m.quaternion.copy(q);
    m.castShadow = true;
    scene.add(m);
  };'''

if "const addBeam = (x1, y1, z1" in content:
    print("[INFO] Helper addBeam deja present")
elif old_addbox in content:
    content = content.replace(old_addbox, new_addbox_with_beam, 1)
    print("[OK] Helper addBeam ajoute")
    modifs += 1
else:
    print("[ERREUR] addBox non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Fix arbaletriers (retirer + Math.PI/2)
# ================================================================

old_arba = '''      // ARBALETRIERS (les 2 pans inclines, section forte)
      addBox(0.16, 0.16, pl, x, Ht + hf/2, lg/4, woodMat, [-ang + Math.PI/2, 0, 0]);
      addBox(0.16, 0.16, pl, x, Ht + hf/2, -lg/4, woodMat, [ang + Math.PI/2, 0, 0]);'''

new_arba = '''      // ARBALETRIERS (les 2 pans inclines, section forte)
      addBox(0.16, 0.16, pl, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);
      addBox(0.16, 0.16, pl, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);'''

if old_arba in content:
    content = content.replace(old_arba, new_arba, 1)
    print("[OK] Arbaletriers corriges (rotation [ang] / [-ang])")
    modifs += 1
else:
    print("[INFO] Arbaletriers deja corriges ou non trouves")

# ================================================================
# MOD 3 : Remplacer le bloc contrefiches par dessin point-a-point
# ================================================================

old_contrefiches = '''      // CONTREFICHES (jambes de force diagonales du poincon vers les arbaletriers)
      const cfLen = pl * 0.5;
      // Contrefiche cote Z+
      addBox(0.10, 0.10, cfLen, x, Ht + hf*0.28, lg*0.14, woodMat, [-ang + Math.PI/2, 0, 0]);
      // Contrefiche cote Z-
      addBox(0.10, 0.10, cfLen, x, Ht + hf*0.28, -lg*0.14, woodMat, [ang + Math.PI/2, 0, 0]);'''

new_contrefiches = '''      // CONTREFICHES (jambes de force du bas du poincon vers les arbaletriers)
      // Dessinees point-a-point : touchent forcement les 2 extremites
      const cfBaseY = Ht + hf * 0.15;           // depart : bas du poincon
      const cfT = 0.55;                          // arrivee : 55% le long de l'arbaletrier
      const cfEndY = Ht + cfT * hf;
      const cfEndZ = (lg/2) * (1 - cfT);
      addBeam(x, cfBaseY, 0, x, cfEndY, cfEndZ, 0.10, woodMat);   // vers pan Z+
      addBeam(x, cfBaseY, 0, x, cfEndY, -cfEndZ, 0.10, woodMat);  // vers pan Z-'''

if old_contrefiches in content:
    content = content.replace(old_contrefiches, new_contrefiches, 1)
    print("[OK] Contrefiches redessinees point-a-point (touchent maintenant)")
    modifs += 1
else:
    print("[INFO] Contrefiches deja corrigees ou non trouvees")

# ================================================================
# MOD 4 : Fix chevrons (retirer + Math.PI/2)
# ================================================================

old_chevrons = '''      // Chevron pan Z+ (section fine)
      addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, lg/4, woodMat, [-ang + Math.PI/2, 0, 0]);
      // Chevron pan Z-
      addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, -lg/4, woodMat, [ang + Math.PI/2, 0, 0]);'''

new_chevrons = '''      // Chevron pan Z+ (section fine)
      addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, lg/4, woodMat, [ang, 0, 0]);
      // Chevron pan Z-
      addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, -lg/4, woodMat, [-ang, 0, 0]);'''

if old_chevrons in content:
    content = content.replace(old_chevrons, new_chevrons, 1)
    print("[OK] Chevrons corriges (rotation [ang] / [-ang])")
    modifs += 1
else:
    print("[INFO] Chevrons deja corriges ou non trouves")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Helper addBeam ajoute (poutre entre 2 points)")
print("  2. Arbaletriers : rotation corrigee -> vont eave -> faitage exactement")
print("  3. Contrefiches : dessinees point-a-point -> touchent poincon + arbaletrier")
print("  4. Chevrons : rotation corrigee -> ne depassent plus le faitage")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
