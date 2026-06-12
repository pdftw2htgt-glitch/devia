#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Fix IFC : appliquer la rotation rot (angles Euler) des pieces addBox"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()

# On remplace le bloc de calcul d'orientation pour gerer rot (Euler) sur les addBox
old = '''    // --- Determiner l'axe long (longueur) et la section (w,h), + direction longue en repere THREE ---
    let L, w, h;
    let longVecThree; // direction de la longueur dans le repere Three
    if (p.quat) {
      // Piece issue de addBeam : la longueur est selon l'axe Z LOCAL, oriente par le quaternion.
      // BoxGeometry(thick, thick, len) -> len selon z local. On applique le quat a (0,0,1).
      const [qx, qy, qz, qw] = p.quat;
      // rotation du vecteur (0,0,1) par le quaternion : formule v' = q * v * q^-1
      // pour v=(0,0,1) ca se simplifie :
      const vx = 2 * (qx*qz + qw*qy);
      const vy = 2 * (qy*qz - qw*qx);
      const vz = 1 - 2 * (qx*qx + qy*qy);
      longVecThree = [vx, vy, vz];
      // longueur = plus grande dim ; section = les 2 thick (egaux en general)
      const dimsSorted = [sx, sy, sz].sort((a,b) => b - a);
      L = dimsSorted[0]; w = dimsSorted[1]; h = dimsSorted[2];
    } else {
      // Piece issue de addBox : axe long = plus grande dimension, axes alignes au repere
      let axeLong = 0, Lmax = sx;
      if (sy > Lmax) { axeLong = 1; Lmax = sy; }
      if (sz > Lmax) { axeLong = 2; Lmax = sz; }
      L = Lmax;
      if (axeLong === 0) { w = sy; h = sz; longVecThree = [1,0,0]; }
      else if (axeLong === 1) { w = sx; h = sz; longVecThree = [0,1,0]; }
      else { w = sx; h = sy; longVecThree = [0,0,1]; }
    }'''

new = '''    // --- helper : rotation d'un vecteur par angles d'Euler Three (ordre XYZ) ---
    const rotEuler = (v, rx, ry, rz) => {
      let [x, y, z] = v;
      // rotation X
      let cy = Math.cos(rx), sy2 = Math.sin(rx);
      [y, z] = [y * cy - z * sy2, y * sy2 + z * cy];
      // rotation Y
      let cyy = Math.cos(ry), syy = Math.sin(ry);
      [x, z] = [x * cyy + z * syy, -x * syy + z * cyy];
      // rotation Z
      let cz = Math.cos(rz), sz2 = Math.sin(rz);
      [x, y] = [x * cz - y * sz2, x * sz2 + y * cz];
      return [x, y, z];
    };

    // --- Determiner l'axe long (longueur) et la section (w,h), + direction longue en repere THREE ---
    let L, w, h;
    let longVecThree; // direction de la longueur dans le repere Three
    if (p.quat) {
      // Piece issue de addBeam : longueur selon Z LOCAL oriente par le quaternion (applique a (0,0,1))
      const [qx, qy, qz, qw] = p.quat;
      const vx = 2 * (qx*qz + qw*qy);
      const vy = 2 * (qy*qz - qw*qx);
      const vz = 1 - 2 * (qx*qx + qy*qy);
      longVecThree = [vx, vy, vz];
      const dimsSorted = [sx, sy, sz].sort((a,b) => b - a);
      L = dimsSorted[0]; w = dimsSorted[1]; h = dimsSorted[2];
    } else {
      // Piece issue de addBox : axe long = plus grande dimension
      let axeLong = 0, Lmax = sx;
      if (sy > Lmax) { axeLong = 1; Lmax = sy; }
      if (sz > Lmax) { axeLong = 2; Lmax = sz; }
      L = Lmax;
      let baseVec;
      if (axeLong === 0) { w = sy; h = sz; baseVec = [1,0,0]; }
      else if (axeLong === 1) { w = sx; h = sz; baseVec = [0,1,0]; }
      else { w = sx; h = sy; baseVec = [0,0,1]; }
      // appliquer la rotation Euler si presente (ex chevrons : [ang,0,0])
      if (p.rot) {
        longVecThree = rotEuler(baseVec, p.rot[0] || 0, p.rot[1] || 0, p.rot[2] || 0);
      } else {
        longVecThree = baseVec;
      }
    }'''

n = content.count(old)
if n != 1:
    print(f"[ERREUR] ancre trouvee {n} fois (attendu 1) -> abandon")
    exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fix_ifc_euler"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")
content = content.replace(old, new, 1)
open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] Rotation Euler appliquee aux pieces addBox (chevrons inclines)")
print("1 MODIFICATION APPLIQUEE")
