# panneau_transparent.py — le panneau de plancher devient translucide en vue
# technique (on voit le solivage et les sabots dessous) et reste plein en
# vue realiste.
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''    setPiece("Panneau plancher");
    addBox(L, 0.022, lg, 0, hPlancher + 0.011, 0, woodMat);'''
R1 = r'''    setPiece("Panneau plancher");
    const panMat = new THREE.MeshStandardMaterial({
      color: modeReal === true ? 0xc9a978 : 0xb99a6a,
      roughness: 0.9,
      transparent: modeReal === false,
      opacity: modeReal === true ? 1.0 : 0.28,
      depthWrite: modeReal === true,
    });
    addBox(L, 0.022, lg, 0, hPlancher + 0.011, 0, panMat);'''

n = src.count(A1)
if n == 1:
    print("OK ancre : panneau de plancher")
else:
    print("ANCRE : " + str(n) + " occurrence(s) au lieu de 1 — ABANDON, rien ecrit.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
src = src.replace(A1, R1)
open(F, "w", encoding="utf-8").write(src)
print("1 modification ecrite. Backup : " + F + ".bak_" + tag)
