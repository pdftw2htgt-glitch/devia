import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

A_MAT = '''      roughness: 0.9, metalness: 0.0,
      transparent: !modeReal, opacity: modeReal ? 1.0 : 0.12,
      side: THREE.DoubleSide
    });'''

B_MAT = A_MAT + '''
    if (modeReal) {
      const essB = ((opts && opts.essence) || (params && params.essence) || "sapin").toString().toLowerCase();
      let codeB = "bardage_sapin";
      if (essB.includes("chene")) codeB = "bardage_chene";
      else if (essB.includes("douglas")) codeB = "bardage_douglas";
      else if (essB.includes("sapin") || essB.includes("epicea")) codeB = "bardage_sapin";
      else if (essB.includes("pin")) codeB = "bardage_pin";
      const loaderB = new THREE.TextureLoader();
      const chargeB = (base, onFail) => {
        loaderB.load("/textures/" + base + ".png", (img) => {
          img.colorSpace = THREE.SRGBColorSpace;
          img.wrapS = THREE.RepeatWrapping;
          img.wrapT = THREE.RepeatWrapping;
          osbMat.map = img;
          osbMat.color.set(0xffffff);
          osbMat.needsUpdate = true;
        }, undefined, () => { if (onFail) onFail(); });
      };
      if (codeB === "bardage_sapin") { chargeB("bardage_sapin"); }
      else { chargeB(codeB, () => chargeB("bardage_sapin")); }
    }'''

A_SEG = '''        const g = axe === "x" ? new THREE.BoxGeometry(lS, hS, ep) : new THREE.BoxGeometry(ep, hS, lS);
        const m = new THREE.Mesh(g, osbMat);'''

B_SEG = '''        const g = axe === "x" ? new THREE.BoxGeometry(lS, hS, ep) : new THREE.BoxGeometry(ep, hS, lS);
        if (modeReal) {
          const posA = g.attributes.position;
          const uvA = g.attributes.uv;
          for (let vi = 0; vi < posA.count; vi++) {
            const la = (axe === "x") ? posA.getX(vi) : posA.getZ(vi);
            uvA.setXY(vi, (cm + la) / 2.4, (ym + posA.getY(vi)) / 1.6);
          }
          uvA.needsUpdate = true;
        }
        const m = new THREE.Mesh(g, osbMat);'''

REMPL = [(A_MAT, B_MAT), (A_SEG, B_SEG)]

ok = True
for a, b in REMPL:
    n = txt.count(a)
    if n != 1:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu 1 :", a[:70].replace(chr(10), " / "))
        ok = False
if ok == False:
    raise SystemExit(1)

for a, b in REMPL:
    txt = txt.replace(a, b)

shutil.copy(CHEMIN, CHEMIN + ".backup_bardage_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : bardage par essence sur les murs ossature bois (vue realiste)")
