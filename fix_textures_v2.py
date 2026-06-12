#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Textures couverture v2 : plus de contraste, joints marques, repeat correct"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_textures_v2"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# Reperage de la fonction makeCouvTexture par accolades
start = content.find("const makeCouvTexture = (couv) => {")
if start == -1:
    print("[ERREUR] makeCouvTexture introuvable"); exit(1)
bo = content.find("{", start); depth = 0; i = bo; end = -1
while i < len(content):
    if content[i] == "{": depth += 1
    elif content[i] == "}":
        depth -= 1
        if depth == 0: end = i; break
    i += 1
# inclure le ';' final
endp = end + 1
if content[endp:endp+1] == ";": endp += 1
old_fn = content[start:endp]

new_fn = '''const makeCouvTexture = (couv) => {
    const S = 512;
    const c = document.createElement("canvas");
    c.width = S; c.height = S;
    const x = c.getContext("2d");
    const r = (couv.couleur >> 16) & 255, g = (couv.couleur >> 8) & 255, b = couv.couleur & 255;
    const shade = (f) => `rgb(${Math.min(255,Math.round(r*f))},${Math.min(255,Math.round(g*f))},${Math.min(255,Math.round(b*f))})`;
    const lab = couv.label || "";
    x.fillStyle = shade(1); x.fillRect(0, 0, S, S);

    if (lab.indexOf("Bac") >= 0 || lab.indexOf("Zinc") >= 0) {
      // Nervures verticales franches
      const step = 42;
      for (let i = 0; i < S; i += step) {
        x.fillStyle = shade(0.62); x.fillRect(i, 0, 4, S);          // creux sombre
        x.fillStyle = shade(1.25); x.fillRect(i + step/2 - 1, 0, 3, S); // arete claire
      }
    } else if (lab.indexOf("Fibrociment") >= 0) {
      const step = 46;
      for (let i = 0; i < S; i += step) {
        const grad = x.createLinearGradient(i, 0, i + step, 0);
        grad.addColorStop(0, shade(0.7)); grad.addColorStop(0.5, shade(1.15)); grad.addColorStop(1, shade(0.7));
        x.fillStyle = grad; x.fillRect(i, 0, step, S);
      }
    } else if (lab.indexOf("Ardoise") >= 0) {
      // Ardoises : rectangles fins, joints noirs nets
      const w = 64, h = 42;
      for (let row = 0; row * h < S + h; row++) {
        const off = (row % 2) * (w / 2);
        for (let col = -1; col * w < S + w; col++) {
          const px = col * w + off, py = row * h;
          x.fillStyle = shade(0.80 + ((row * 7 + col * 3) % 5) * 0.05);
          x.fillRect(px, py, w, h);
          x.strokeStyle = shade(0.45); x.lineWidth = 3;
          x.strokeRect(px, py, w, h);
        }
      }
    } else {
      // Tuiles : rangees d'ecailles arrondies, joints marques + ombre basse
      const w = 70, h = 50;
      for (let row = 0; row * (h*0.7) < S + h; row++) {
        const off = (row % 2) * (w / 2);
        const py = row * (h * 0.7);
        for (let col = -1; col * w < S + w; col++) {
          const px = col * w + off;
          // corps de tuile
          x.fillStyle = shade(0.92 + ((row + col) % 2) * 0.10);
          x.beginPath();
          x.moveTo(px, py);
          x.lineTo(px + w, py);
          x.lineTo(px + w, py + h * 0.45);
          x.arc(px + w/2, py + h*0.45, w/2, 0, Math.PI, false);
          x.lineTo(px, py);
          x.closePath(); x.fill();
          // ombre en bas de tuile (relief)
          x.fillStyle = shade(0.6);
          x.beginPath();
          x.arc(px + w/2, py + h*0.45, w/2, 0.15, Math.PI - 0.15, false);
          x.lineWidth = 4; x.strokeStyle = shade(0.55); x.stroke();
        }
      }
    }
    const tex = new THREE.CanvasTexture(c);
    tex.wrapS = THREE.RepeatWrapping; tex.wrapT = THREE.RepeatWrapping;
    tex.needsUpdate = true;
    return tex;
  };'''

content = content.replace(old_fn, new_fn, 1)

# Corriger le repeat dans makeRoofMaterial : taille de tuile reelle ~0.30 m
old_rep = "tex.repeat.set(Math.max(1, (surfX || 4) / 1.2), Math.max(1, (surfY || 4) / 1.2));"
new_rep = "tex.repeat.set(Math.max(2, Math.round((surfX || 4) / 0.55)), Math.max(2, Math.round((surfY || 4) / 0.55)));"
if old_rep in content:
    content = content.replace(old_rep, new_rep, 1)
    print("[OK] Repeat corrige (taille de motif reelle)")
else:
    print("[WARN] Ligne repeat non trouvee")

open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] Texture v2 appliquee")
print("1 MODIFICATION APPLIQUEE")
