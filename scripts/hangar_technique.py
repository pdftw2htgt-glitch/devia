#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D : Hangar TECHNIQUE
Remplace drawHangar par une version detaillee :
- Poteaux (specificite hangar, conserves)
- Fermes completes (entrait + arbaletriers + poincon + contrefiches via addBeam)
- Pannes (sablieres + intermediaires + faitiere)
- Chevrons rapproches (~tous les 0.6m)
- Couverture semi-transparente
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_hangar_technique"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# Remplacer drawHangar par la version technique
# ================================================================

old_hangar = '''  const drawHangar = () => {
    const hf = lg / 2 * Math.tan((pente * Math.PI) / 180);
    const sectionPotau = 0.22; // poteaux plus gros pour hangar

    // POTEAUX (4 coins + intermediaires selon longueur)
    const nbPoteauxLong = Math.max(2, Math.ceil(L / 4)); // 1 poteau tous les 4m max
    for (let i = 0; i <= nbPoteauxLong; i++) {
      const x = -L/2 + (i / nbPoteauxLong) * L;
      // Poteau cote Z+
      addBox(sectionPotau, Ht, sectionPotau, x, Ht/2, lg/2);
      // Poteau cote Z-
      addBox(sectionPotau, Ht, sectionPotau, x, Ht/2, -lg/2);
    }

    // SABLIERES (2 longues poutres entre les poteaux)
    addBox(L + 0.4, 0.20, 0.20, 0, Ht, lg/2);   // sabliere Z+
    addBox(L + 0.4, 0.20, 0.20, 0, Ht, -lg/2);  // sabliere Z-

    // FERMES (assemblees comme charpente trad mais sans murs)
    const nbFermes = Math.max(2, Math.ceil(L / 3)); // 1 ferme tous les 3m
    for (let i = 0; i <= nbFermes; i++) {
      const x = -L/2 + (i / nbFermes) * L;
      const ang = Math.atan(hf / (lg/2));
      const pl = (lg/2) / Math.cos(ang);
      // Arbaletriers (les 2 pans inclines)
      addBox(pl, 0.14, 0.14, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);
      addBox(pl, 0.14, 0.14, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);
      // Entrait (poutre horizontale en bas)
      addBox(0.14, 0.14, lg, x, Ht, 0);
      // Poincon (vertical central)
      addBox(0.14, hf, 0.14, x, Ht + hf/2, 0);
    }

    // FAITAGE
    addBox(L + 0.5, 0.16, 0.16, 0, Ht + hf, 0);

    // PANNES (le long de la longueur, sur les pans)
    const nbPannes = 3;
    for (let i = 1; i < nbPannes; i++) {
      const t = i / nbPannes;
      const yPanne = Ht + hf * (1 - t);
      const zPanne = (lg/2) * t;
      addBox(L + 0.4, 0.12, 0.12, 0, yPanne, zPanne);
      addBox(L + 0.4, 0.12, 0.12, 0, yPanne, -zPanne);
    }

    // TOITURE (2 pans)
    const ang = Math.atan(hf / (lg/2));
    const pl = (lg/2) / Math.cos(ang);
    const rg = new THREE.PlaneGeometry(L + 0.8, pl + 0.3);
    const r1 = new THREE.Mesh(rg, roofMat);
    r1.position.set(0, Ht + hf/2, lg/4);
    r1.rotation.x = ang - Math.PI/2;
    scene.add(r1);
    const r2 = new THREE.Mesh(rg, roofMat);
    r2.position.set(0, Ht + hf/2, -lg/4);
    r2.rotation.x = -(ang - Math.PI/2);
    scene.add(r2);
  };'''

new_hangar = '''  const drawHangar = () => {
    const hf = lg / 2 * Math.tan((pente * Math.PI) / 180);
    const ang = Math.atan(hf / (lg/2));
    const pl = (lg/2) / Math.cos(ang);
    const yFait = Ht + hf;
    const sectionPotau = 0.22; // poteaux plus gros pour hangar

    // ===== POTEAUX (specificite hangar : 4 coins + intermediaires) =====
    const nbPoteauxLong = Math.max(2, Math.ceil(L / 4));
    for (let i = 0; i <= nbPoteauxLong; i++) {
      const x = -L/2 + (i / nbPoteauxLong) * L;
      addBox(sectionPotau, Ht, sectionPotau, x, Ht/2, lg/2);   // cote Z+
      addBox(sectionPotau, Ht, sectionPotau, x, Ht/2, -lg/2);  // cote Z-
    }

    // ===== SABLIERES (longues poutres sur les poteaux) =====
    addBox(L + 0.4, 0.20, 0.20, 0, Ht, lg/2, woodMat);
    addBox(L + 0.4, 0.20, 0.20, 0, Ht, -lg/2, woodMat);

    // ===== FERMES COMPLETES (tous les ~3m) =====
    const nbFermes = Math.max(2, Math.ceil(L / 3));
    for (let i = 0; i <= nbFermes; i++) {
      const x = -L/2 + (i / nbFermes) * L;

      // Entrait (poutre horizontale basse)
      addBox(0.16, 0.16, lg, x, Ht, 0, woodMat);
      // Arbaletriers (pans inclines, section forte)
      addBox(0.16, 0.16, pl, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);
      addBox(0.16, 0.16, pl, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);
      // Poincon (vertical central)
      addBox(0.14, hf, 0.14, x, Ht + hf/2, 0, woodMat);
      // Contrefiches (jambes de force, point-a-point)
      const cfBaseY = Ht + hf * 0.15;
      const cfT = 0.55;
      const cfEndY = Ht + cfT * hf;
      const cfEndZ = (lg/2) * (1 - cfT);
      addBeam(x, cfBaseY, 0, x, cfEndY, cfEndZ, 0.10, woodMat);
      addBeam(x, cfBaseY, 0, x, cfEndY, -cfEndZ, 0.10, woodMat);
    }

    // ===== PANNE FAITIERE + INTERMEDIAIRES =====
    addBox(L + 0.5, 0.16, 0.16, 0, yFait, 0, woodMat);
    const nbPannesParPan = 2;
    for (let p = 1; p <= nbPannesParPan; p++) {
      const t = p / (nbPannesParPan + 1);
      const yPanne = Ht + hf * t;
      const zPanne = (lg/2) * (1 - t);
      addBox(L + 0.4, 0.12, 0.12, 0, yPanne, zPanne, woodMat);
      addBox(L + 0.4, 0.12, 0.12, 0, yPanne, -zPanne, woodMat);
    }

    // ===== CHEVRONS RAPPROCHES (~tous les 0.6m) =====
    const espChevron = 0.6;
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, lg/4, woodMat, [ang, 0, 0]);
      addBox(0.07, 0.07, pl, x, Ht + hf/2 + 0.08, -lg/4, woodMat, [-ang, 0, 0]);
    }

    // ===== COUVERTURE (2 pans, semi-transparente) =====
    const roofTransMat = new THREE.MeshLambertMaterial({
      color: roofColor, transparent: true, opacity: 0.45, side: THREE.DoubleSide
    });
    const rg = new THREE.PlaneGeometry(L + 0.8, pl + 0.3);
    const r1 = new THREE.Mesh(rg, roofTransMat);
    r1.position.set(0, Ht + hf/2 + 0.12, lg/4);
    r1.rotation.x = ang - Math.PI/2;
    scene.add(r1);
    const r2 = new THREE.Mesh(rg, roofTransMat);
    r2.position.set(0, Ht + hf/2 + 0.12, -lg/4);
    r2.rotation.x = -(ang - Math.PI/2);
    scene.add(r2);
  };'''

if "CHEVRONS RAPPROCHES (~tous les 0.6m)" in content:
    print("[INFO] Hangar technique deja en place")
elif old_hangar in content:
    content = content.replace(old_hangar, new_hangar, 1)
    print("[OK] drawHangar remplace par version technique complete")
    modifs += 1
else:
    print("[ERREUR] drawHangar original non trouve exactement")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATION APPLIQUEE")
print("=" * 60)
print()
print("HANGAR TECHNIQUE :")
print("  - Poteaux (4 coins + intermediaires) - specificite hangar")
print("  - Sablieres longues")
print("  - Fermes completes : entrait + arbaletriers + poincon + contrefiches")
print("  - Panne faitiere + 2 pannes intermediaires par pan")
print("  - Chevrons rapproches (~tous les 0.6m)")
print("  - Couverture SEMI-TRANSPARENTE")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
