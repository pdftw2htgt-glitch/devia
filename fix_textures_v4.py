#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Textures couverture v4 : vraies tuiles ecaille avec relief + repeat correct"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()
backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_textures_v4"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# Reperage makeCouvTexture par accolades
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
endp = end + 1
if content[endp:endp+1] == ";": endp += 1
old_fn = content[start:endp]

new_fn = '''const makeCouvTexture = (couv) => {
    const S = 512;
    const c = document.createElement("canvas");
    c.width = S; c.height = S;
    const x = c.getContext("2d");
    const r = (couv.couleur >> 16) & 255, g = (couv.couleur >> 8) & 255, b = couv.couleur & 255;
    const shade = (f) => `rgb(${Math.min(255,Math.max(0,Math.round(r*f)))},${Math.min(255,Math.max(0,Math.round(g*f)))},${Math.min(255,Math.max(0,Math.round(b*f)))})`;
    const lab = couv.label || "";

    const rr = (px, py, pw, ph, rad, col) => {
      x.fillStyle = col;
      x.beginPath();
      x.moveTo(px+rad, py);
      x.arcTo(px+pw, py, px+pw, py+ph, rad);
      x.arcTo(px+pw, py+ph, px, py+ph, rad);
      x.arcTo(px, py+ph, px, py, rad);
      x.arcTo(px, py, px+pw, py, rad);
      x.closePath(); x.fill();
    };

    if (lab.indexOf("Bac") >= 0 || lab.indexOf("Zinc") >= 0) {
      x.fillStyle = shade(1); x.fillRect(0, 0, S, S);
      const step = 46;
      for (let i = 0; i < S; i += step) {
        x.fillStyle = shade(0.6); x.fillRect(i, 0, 5, S);
        x.fillStyle = shade(1.28); x.fillRect(i + step/2, 0, 3, S);
      }
    } else if (lab.indexOf("Fibrociment") >= 0) {
      const step = 50;
      for (let i = 0; i < S; i += step) {
        const grad = x.createLinearGradient(i, 0, i + step, 0);
        grad.addColorStop(0, shade(0.65)); grad.addColorStop(0.5, shade(1.2)); grad.addColorStop(1, shade(0.65));
        x.fillStyle = grad; x.fillRect(i, 0, step, S);
      }
    } else {
      // TUILES / ARDOISE / SHINGLE : ecailles bombees avec relief
      x.fillStyle = shade(0.5); x.fillRect(0, 0, S, S);
      const w = 74, h = 58;
      const rows = Math.ceil(S / (h * 0.62)) + 2;
      for (let row = 0; row < rows; row++) {
        const py = Math.round(row * h * 0.62);
        const off = (row % 2) * (w / 2);
        const cols = Math.ceil(S / w) + 2;
        for (let col = -1; col < cols; col++) {
          const px = Math.round(col * w + off);
          const v = 0.82 + ((row * 5 + col * 7) % 6) * 0.06;
          rr(px + 2, py, w - 4, h, Math.round(w * 0.42), shade(v));         // corps
          rr(px + 4, py + 2, w - 8, Math.round(h * 0.4), Math.round(w * 0.3), shade(v * 1.18)); // lumiere haut
          x.strokeStyle = shade(0.45); x.lineWidth = 4;                      // ombre bas
          x.beginPath();
          x.arc(px + w/2, py + h * 0.62, w/2, 0.35, Math.PI - 0.35, false);
          x.stroke();
        }
      }
    }
    const tex = new THREE.CanvasTexture(c);
    tex.wrapS = THREE.RepeatWrapping; tex.wrapT = THREE.RepeatWrapping;
    tex.needsUpdate = true;
    return tex;
  };'''

content = content.replace(old_fn, new_fn, 1)

# Repeat : 1 texture = ~8 rangees de tuiles (~0.30m chacune) -> ~2.4m de pan par tuile-image
# Pour un pan de surY metres : surY / 2.4 repetitions (borne mini 1)
import re
old_rep_pattern = re.compile(r"tex\.repeat\.set\([^;]*\);")
m = old_rep_pattern.search(content)
if m:
    content = content[:m.start()] + "tex.repeat.set(Math.max(1, (surfX||4)/2.4), Math.max(1, (surfY||4)/2.4));" + content[m.end():]
    print("[OK] Repeat recalibre (1 image ~ 2.4m)")
else:
    print("[WARN] repeat non trouve")

open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] Texture v4 appliquee")
print("1 MODIFICATION APPLIQUEE")
