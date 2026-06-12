#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Vue REALISTE avec textures procedurales + toggle Technique/Realiste
"""
import os, sys, shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()
modifs = 0

def apply(old, new, label):
    global content, modifs
    n = content.count(old)
    if n == 1:
        content = content.replace(old, new, 1); print(f"[OK] {label}"); modifs += 1
    elif n == 0:
        print(f"[WARN] {label} : NON trouve")
    else:
        print(f"[WARN] {label} : trouve {n}x (ambigu) -> ignore")

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_vue_realiste"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) Helpers textures + materiau, inseres juste apres getCouverture
helpers = '''  // ============================================================
  // TEXTURES PROCEDURALES DE COUVERTURE (mode realiste)
  // ============================================================
  const makeCouvTexture = (couv) => {
    const c = document.createElement("canvas");
    c.width = 256; c.height = 256;
    const x = c.getContext("2d");
    const hex = "#" + couv.couleur.toString(16).padStart(6, "0");
    x.fillStyle = hex; x.fillRect(0, 0, 256, 256);
    const lab = couv.label || "";
    const darker = (f) => {
      const r = (couv.couleur >> 16) & 255, g = (couv.couleur >> 8) & 255, b = couv.couleur & 255;
      return `rgb(${Math.round(r*f)},${Math.round(g*f)},${Math.round(b*f)})`;
    };
    if (lab.indexOf("Bac") >= 0 || lab.indexOf("Zinc") >= 0) {
      // Rainures verticales (nervures du bac/zinc)
      for (let i = 0; i < 256; i += 16) {
        x.fillStyle = darker(0.78); x.fillRect(i, 0, 6, 256);
        x.fillStyle = darker(1.12); x.fillRect(i + 6, 0, 2, 256);
      }
    } else if (lab.indexOf("Fibrociment") >= 0) {
      // Ondulations verticales douces
      for (let i = 0; i < 256; i += 22) {
        x.fillStyle = darker(0.85); x.fillRect(i, 0, 11, 256);
        x.fillStyle = darker(1.08); x.fillRect(i + 11, 0, 11, 256);
      }
    } else if (lab.indexOf("Ardoise") >= 0) {
      // Ecailles fines decalees (ardoise)
      const w = 34, h = 26;
      for (let row = 0; row * h < 280; row++) {
        const off = (row % 2) * (w / 2);
        for (let col = -1; col * w < 280; col++) {
          x.fillStyle = darker(0.9 + (((row + col) % 2) * 0.12));
          x.fillRect(col * w + off, row * h, w - 3, h - 3);
        }
      }
    } else {
      // Tuiles : ecailles arrondies decalees (terre cuite / beton / shingle)
      const w = 40, h = 30;
      for (let row = 0; row * h < 300; row++) {
        const off = (row % 2) * (w / 2);
        for (let col = -1; col * w < 300; col++) {
          x.fillStyle = darker(0.86 + (((row + col) % 2) * 0.16));
          x.beginPath();
          x.moveTo(col * w + off, row * h);
          x.lineTo(col * w + off + w, row * h);
          x.lineTo(col * w + off + w, row * h + h * 0.6);
          x.quadraticCurveTo(col * w + off + w/2, row * h + h, col * w + off, row * h + h*0.6);
          x.closePath(); x.fill();
        }
      }
    }
    const tex = new THREE.CanvasTexture(c);
    tex.wrapS = THREE.RepeatWrapping; tex.wrapT = THREE.RepeatWrapping;
    return tex;
  };

  // Materiau de couverture selon le mode (technique = transparent / realiste = texture opaque)
  const makeRoofMaterial = (couv, surfX, surfY) => {
    const mode = (opts && opts.mode) ? opts.mode : "technique";
    if (mode === "realiste") {
      const tex = makeCouvTexture(couv);
      tex.repeat.set(Math.max(1, (surfX || 4) / 1.2), Math.max(1, (surfY || 4) / 1.2));
      return new THREE.MeshLambertMaterial({ map: tex, side: THREE.DoubleSide });
    }
    return new THREE.MeshLambertMaterial({
      color: couv.couleur, transparent: true, opacity: 0.4, side: THREE.DoubleSide
    });
  };

'''
apply(
    "  const getCouverture = (code) => COUVERTURES[code] || COUVERTURES.tuile_terre;\n",
    "  const getCouverture = (code) => COUVERTURES[code] || COUVERTURES.tuile_terre;\n\n" + helpers,
    "Helpers makeCouvTexture + makeRoofMaterial inseres"
)

# 2) Remplacer les 3 materiaux de couverture (monopente, appentis, 4pans)
#    Les 3 blocs sont identiques sauf le nom de la variable de gauche.
for var, surf in [("monopenteRoofMat", "L, longueurChevron"),
                  ("appentisRoofMat", "L, longueurRampant"),
                  ("roof4Mat", "L, plLong")]:
    old = f'''    const {var} = new THREE.MeshLambertMaterial({{
      color: couvColor, transparent: true, opacity: 0.4, side: THREE.DoubleSide
    }});'''
    new = f"    const {var} = makeRoofMaterial(couv, {surf});"
    apply(old, new, f"Materiau {var} -> makeRoofMaterial")

# 3) Viewer3D : passer le mode dans opts
apply(
    "buildScene3D(scene, params, { couverture: params.couverture });",
    "buildScene3D(scene, params, { couverture: params.couverture, mode: params.mode3D });",
    "Viewer3D : mode transmis a buildScene3D"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
