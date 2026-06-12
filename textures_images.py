#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Charge les vraies images de texture si presentes, sinon fallback procedural"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()
backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_textures_images"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# Reperage de makeRoofMaterial par accolades
start = content.find("const makeRoofMaterial = (couv, surfX, surfY) => {")
if start == -1:
    print("[ERREUR] makeRoofMaterial introuvable"); exit(1)
bo = content.find("{", start); depth = 0; i = bo; end = -1
while i < len(content):
    if content[i] == "{": depth += 1
    elif content[i] == "}":
        depth -= 1
        if depth == 0: end = i; break
    i += 1
endp = end + 1
if content[endp:endp+1] == ";": endp += 1
old_fn = content[start:endp]

new_fn = '''const makeRoofMaterial = (couv, surfX, surfY) => {
    const mode = (opts && opts.mode) ? opts.mode : "technique";
    if (mode !== "realiste") {
      // Vue technique : couleur transparente
      return new THREE.MeshLambertMaterial({
        color: couv.couleur, transparent: true, opacity: 0.4, side: THREE.DoubleSide
      });
    }
    // Vue realiste : on tente l'image, fallback procedural
    const code = couv.code || "";
    const rx = Math.max(1, (surfX || 4) / 2.4);
    const ry = Math.max(1, (surfY || 4) / 2.4);

    // Materiau procedural par defaut (s'affiche immediatement)
    const ptex = makeCouvTexture(couv);
    ptex.repeat.set(rx, ry);
    const mat = new THREE.MeshLambertMaterial({ map: ptex, side: THREE.DoubleSide });

    // Tentative de chargement de l'image reelle (async, remplace si trouvee)
    if (code) {
      const loader = new THREE.TextureLoader();
      const tryLoad = (ext, onFail) => {
        loader.load(
          "/textures/" + code + "." + ext,
          (img) => {
            img.wrapS = THREE.RepeatWrapping;
            img.wrapT = THREE.RepeatWrapping;
            img.repeat.set(rx, ry);
            mat.map = img;
            mat.needsUpdate = true;
          },
          undefined,
          () => { if (onFail) onFail(); }
        );
      };
      // essaie .png puis .jpg
      tryLoad("png", () => tryLoad("jpg", null));
    }
    return mat;
  };'''

content = content.replace(old_fn, new_fn, 1)

# Il faut que couv.code existe : on l'injecte dans getCouverture
old_get = "const getCouverture = (code) => COUVERTURES[code] || COUVERTURES.tuile_terre;"
new_get = '''const getCouverture = (code) => {
    const c = COUVERTURES[code] || COUVERTURES.tuile_terre;
    const key = COUVERTURES[code] ? code : "tuile_terre";
    return { ...c, code: key };
  };'''
if old_get in content:
    content = content.replace(old_get, new_get, 1)
    print("[OK] getCouverture renvoie maintenant le 'code'")
else:
    print("[WARN] getCouverture non trouve sous la forme attendue")

open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] makeRoofMaterial charge les images + fallback procedural")
print("2 MODIFICATIONS APPLIQUEES")
