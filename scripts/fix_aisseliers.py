#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D : Fix orientation aisseliers (monopente + appentis)

Bug : rotation incorrecte (Math.atan2(dy, dz) - Math.PI/2)
      -> aisseliers orientes de travers, sortant du batiment

Fix : rotation correcte (-Math.atan2(dy, dz))
      + point bas remonte (Hbas * 0.7) pour realisme
      + point bas fixe en Z -> effet "fan" vers les pannes
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_fix_aisseliers"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# FIX MONOPENTE
# ================================================================

old_aisselier_monopente = '''    // ===== AISSELIERS (jambes de force obliques aux pignons) =====
    const aisselierAngles = [pannePositions[1], pannePositions[2]];  // 2eme et 3eme panne
    [-1, 1].forEach((cote) => {
      const xMur = cote * (L/2 - 0.08);
      aisselierAngles.forEach((p) => {
        // Point bas : sur le mur lateral, a 80% de Hbas, decale vers z=0
        const xb = xMur;
        const yb = Hbas * 0.5;
        const zb = -lg/2 + (p.t * lg) * 0.4;  // decale vers la sabliere basse
        // Point haut : sous la panne, a la position de la panne
        const xh = xMur;
        const yh = p.y - 0.08;
        const zh = p.z;
        // Calculs de la jambe oblique (centre + longueur + rotation autour de X)
        const dy = yh - yb;
        const dz = zh - zb;
        const longueur = Math.sqrt(dy*dy + dz*dz);
        const rotX = Math.atan2(dy, dz) - Math.PI/2;  // rotation autour de X
        const xc = (xb + xh) / 2;
        const yc = (yb + yh) / 2;
        const zc = (zb + zh) / 2;
        addBox(0.10, 0.10, longueur, xc, yc, zc, woodMat, [rotX, 0, 0]);
      });
    });'''

new_aisselier_monopente = '''    // ===== AISSELIERS (jambes de force obliques aux pignons) =====
    // Effet "fan" : tous partent du meme point bas et rayonnent vers les pannes
    const aisselierAngles = [pannePositions[1], pannePositions[2]];  // 2eme et 3eme panne
    [-1, 1].forEach((cote) => {
      const xMur = cote * (L/2 - 0.08);
      aisselierAngles.forEach((p) => {
        // Point bas : haut du mur lateral, pres du coin avant
        const xb = xMur;
        const yb = Hbas * 0.7;
        const zb = -lg/2 + 0.3;
        // Point haut : juste sous la panne
        const xh = xMur;
        const yh = p.y - 0.08;
        const zh = p.z;
        const dy = yh - yb;
        const dz = zh - zb;
        const longueur = Math.sqrt(dy*dy + dz*dz);
        const rotX = -Math.atan2(dy, dz);  // FIX : rotation correcte autour de X
        const xc = (xb + xh) / 2;
        const yc = (yb + yh) / 2;
        const zc = (zb + zh) / 2;
        addBox(0.10, 0.10, longueur, xc, yc, zc, woodMat, [rotX, 0, 0]);
      });
    });'''

if "Effet \"fan\" : tous partent du meme point bas" in content and content.count("Effet \"fan\" : tous partent du meme point bas") >= 1 and old_aisselier_monopente not in content:
    print("[INFO] Aisseliers monopente deja corriges")
elif old_aisselier_monopente in content:
    content = content.replace(old_aisselier_monopente, new_aisselier_monopente, 1)
    print("[OK] Aisseliers monopente : rotation corrigee")
    modifs += 1
else:
    print("[WARN] Bloc aisseliers monopente non trouve (peut-etre deja modifie ou structure differente)")

# ================================================================
# FIX APPENTIS
# ================================================================

old_aisselier_appentis = '''    // ===== AISSELIERS (jambes de force obliques aux pignons) =====
    const aisselierAngles = [pannePositions[0], pannePositions[1]];
    [-1, 1].forEach((cote) => {
      const xMur = cote * (L/2 - 0.08);
      aisselierAngles.forEach((p) => {
        // Point bas : sur le mur lateral au niveau Hbas/2
        const xb = xMur;
        const yb = Hbas * 0.5;
        const zb = -lg/2 + (p.t * lg) * 0.4;
        // Point haut : sous la panne
        const xh = xMur;
        const yh = p.y - 0.08;
        const zh = p.z;
        const dy = yh - yb;
        const dz = zh - zb;
        const longueur = Math.sqrt(dy*dy + dz*dz);
        const rotX = Math.atan2(dy, dz) - Math.PI/2;
        const xc = (xb + xh) / 2;
        const yc = (yb + yh) / 2;
        const zc = (zb + zh) / 2;
        addBox(0.10, 0.10, longueur, xc, yc, zc, woodMat, [rotX, 0, 0]);
      });
    });'''

new_aisselier_appentis = '''    // ===== AISSELIERS (jambes de force obliques aux pignons) =====
    // Effet "fan" : tous partent du meme point bas et rayonnent vers les pannes
    const aisselierAngles = [pannePositions[0], pannePositions[1]];
    [-1, 1].forEach((cote) => {
      const xMur = cote * (L/2 - 0.08);
      aisselierAngles.forEach((p) => {
        // Point bas : haut du mur lateral, pres du coin avant
        const xb = xMur;
        const yb = Hbas * 0.7;
        const zb = -lg/2 + 0.3;
        // Point haut : juste sous la panne
        const xh = xMur;
        const yh = p.y - 0.08;
        const zh = p.z;
        const dy = yh - yb;
        const dz = zh - zb;
        const longueur = Math.sqrt(dy*dy + dz*dz);
        const rotX = -Math.atan2(dy, dz);  // FIX : rotation correcte autour de X
        const xc = (xb + xh) / 2;
        const yc = (yb + yh) / 2;
        const zc = (zb + zh) / 2;
        addBox(0.10, 0.10, longueur, xc, yc, zc, woodMat, [rotX, 0, 0]);
      });
    });'''

if old_aisselier_appentis in content:
    content = content.replace(old_aisselier_appentis, new_aisselier_appentis, 1)
    print("[OK] Aisseliers appentis : rotation corrigee")
    modifs += 1
elif "Effet \"fan\"" in content and content.count("Effet \"fan\"") >= 2:
    print("[INFO] Aisseliers appentis deja corriges")
else:
    print("[WARN] Bloc aisseliers appentis non trouve (peut-etre deja modifie ou structure differente)")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)")
print("=" * 60)
print()
print("AISSELIERS CORRIGES :")
print("  - Rotation : -Math.atan2(dy, dz) [au lieu de atan2(dy,dz)-PI/2]")
print("  - Point bas : Hbas * 0.7 (vs 0.5) -> plus realiste")
print("  - Point bas fixe en Z -> effet 'fan' vers les pannes")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
