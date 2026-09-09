# fix_page_blanche_plancher.py — modeReal n existe que dans drawMursOssature :
# le panneau de plancher doit calculer le mode lui-meme (sinon ReferenceError
# au rendu -> page blanche sur la vue 3D)
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''    const panMat = new THREE.MeshStandardMaterial({
      color: modeReal === true ? 0xc9a978 : 0xb99a6a,
      roughness: 0.9,
      transparent: modeReal === false,
      opacity: modeReal === true ? 1.0 : 0.28,
      depthWrite: modeReal === true,
    });'''
R1 = r'''    const realPan = (opts && opts.mode) === "realiste";
    const panMat = new THREE.MeshStandardMaterial({
      color: realPan === true ? 0xc9a978 : 0xb99a6a,
      roughness: 0.9,
      transparent: realPan === false,
      opacity: realPan === true ? 1.0 : 0.28,
      depthWrite: realPan === true,
    });'''

n = src.count(A1)
if n == 1:
    print("OK ancre : materiau du panneau")
else:
    print("ANCRE : " + str(n) + " occurrence(s) au lieu de 1 — ABANDON, rien ecrit.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
src = src.replace(A1, R1)
open(F, "w", encoding="utf-8").write(src)
print("1 modification ecrite. Backup : " + F + ".bak_" + tag)
