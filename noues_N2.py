# Noues N2 : chevrons d'emprunt (empannons) + couverture de la greffe taillee sur les noues
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''    setPiece("Panne faitiere");
    addBox(dR, 0.24, 0.12, xw + s * dR / 2, hF - 0.12, 0, woodMat);
    console.log("[DEVIA] Penetration : 2 noues + faitiere prolongee (profondeur " + dR.toFixed(2) + " m)");
  };'''
NEW1 = '''    setPiece("Panne faitiere");
    addBox(dR, 0.24, 0.12, xw + s * dR / 2, hF - 0.12, 0, woodMat);

    // ===== N2 : chevrons d'emprunt entre faitiere et noues =====
    const couvPen = getCouverture(opts && opts.couverture);
    const esp = (couvPen && couvPen.espChevron) ? couvPen.espChevron : 0.5;
    const plage = (dR - dPied) > 0.01 ? (dR - dPied) : 0.01;
    setPiece("Chevron");
    const nEmp = Math.max(1, Math.floor(dR / esp));
    for (let ie = 1; ie <= nEmp; ie++) {
      const dE2 = dPied + (ie / (nEmp + 1)) * plage;
      const zN = zE * (dR - dE2) / plage;
      const yN = hF - zN * Math.tan(aRad);
      const xE2 = xw + s * dE2;
      for (const sz of [-1, 1]) {
        addBeam(xE2, hF - 0.02, 0, xE2, yN, sz * zN, 0.07, woodMat);
      }
    }

    // ===== N2 : couverture de la greffe (un pan taille en pointe de chaque cote) =====
    const matPen = makeRoofMaterial(couvPen, dR, zE + 0.3);
    matPen.side = THREE.DoubleSide;
    const dec2 = 0.08;
    for (const sz of [-1, 1]) {
      const g = new THREE.BufferGeometry();
      const pts = [
        xw, hF + dec2, 0,
        xw + s * dR, hF + dec2, 0,
        xw + s * dPied, yPied + dec2, sz * zE,
        xw, hF + dec2, 0,
        xw + s * dPied, yPied + dec2, sz * zE,
        xw, yPied + dec2, sz * zE,
      ];
      g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pts), 3));
      g.computeVertexNormals();
      scene.add(new THREE.Mesh(g, matPen));
    }
    console.log("[DEVIA] Penetration : noues + faitiere + " + (nEmp * 2) + " empannons + couverture de greffe");
  };'''

n = c.count(OLD1)
if n != 1:
    print("ERREUR ancre (fin drawPenetration) : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
    sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_noues_N2")
c = c.replace(OLD1, NEW1)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK N2 : empannons + couverture de greffe sur les noues")
