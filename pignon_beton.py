import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

def remp(nom, ancre, nouveau):
    global src
    n = src.count(ancre)
    if n != 1:
        print("ABANDON " + nom + " : ancre trouvee " + str(n) + " fois")
        cle = ancre.strip().split("\n")[0][:45]
        for i, l in enumerate(src.split("\n")):
            if cle in l:
                print("  ligne " + str(i + 1) + " : " + l.strip()[:200])
        sys.exit(1)
    src = src.replace(ancre, nouveau)
    print("OK " + nom)

# 1) Le pignon maconne : triangle entre la sabliere et les deux rampants
remp("drawPignonBeton",
"""  const drawMursBeton = (Lb, lgb, Hb) => {""",
"""  // Pignon maconne : le triangle entre le haut des murs et les rampants.
  // Sans lui, un trou reste ouvert sous la toiture aux deux pignons.
  const drawPignonBeton = (xPos, lgb, Hb, htTri, ep) => {
    const shp = new THREE.Shape();
    shp.moveTo(-lgb / 2, 0);
    shp.lineTo(lgb / 2, 0);
    shp.lineTo(0, htTri);
    shp.closePath();
    const geo = new THREE.ExtrudeGeometry(shp, { depth: ep, bevelEnabled: false });
    const m = new THREE.Mesh(geo, betonMat);
    m.rotation.y = Math.PI / 2;            // le plan du triangle devient le plan du pignon
    m.position.set(xPos - ep / 2, Hb, 0);  // epaisseur centree sur le nu du mur
    m.castShadow = true;
    m.receiveShadow = true;
    scene.add(m);
    metre.push({
      matiere: "beton",
      nom: "Mur pignon beton",
      section: [Math.round(ep * 1000), Math.round(htTri * 1000)],
      longueur: lgb,
      volume: (lgb * htTri / 2) * ep,
      dimsBrutes: [ep, htTri, lgb],
      tri: { b: lgb, h: htTri, ep: ep },   // profil reel, repris tel quel a l export IFC
      pos: [xPos, Hb, 0],
      rot: null,
      quat: null,
    });
  };

  const drawMursBeton = (Lb, lgb, Hb) => {""")

# 2) On ferme les deux pignons
remp("appel des pignons",
"""    sansFace === "pignon_droit" ? null : murZ(Lb/2, true);
    sansFace === "pignon_gauche" ? null : murZ(-Lb/2, false);""",
"""    sansFace === "pignon_droit" ? null : murZ(Lb/2, true);
    sansFace === "pignon_gauche" ? null : murZ(-Lb/2, false);

    // --- TRIANGLES DE PIGNON : la maconnerie monte jusqu aux rampants ---
    const htTriangle = (lgb / 2) * Math.tan((pente * Math.PI) / 180);
    if (htTriangle > 0.05) {
      if ((sansFace === "pignon_droit") === false) drawPignonBeton(Lb / 2, lgb, Hb, htTriangle, ep);
      if ((sansFace === "pignon_gauche") === false) drawPignonBeton(-Lb / 2, lgb, Hb, htTriangle, ep);
      console.log("[DEVIA] Pignons fermes : triangle de " + htTriangle.toFixed(2) + " m de haut");
    }""")

# 3) L export IFC connait le profil triangulaire
remp("IFC profil triangle",
"""  piecesBois.forEach((p, iP) => {
    // --- Dimensions Three.js d'origine ---
    const sx = Math.abs(p.dimsBrutes[0]);""",
"""  piecesBois.forEach((p, iP) => {
    // --- Pignon maconne : profil triangulaire reel (pas une boite approchee) ---
    if (p.tri && p.tri.b > 0.05 && p.tri.h > 0.05 && p.tri.ep > 0.01) {
      const mRT = new THREE.Matrix4();
      if (p.quat) mRT.makeRotationFromQuaternion(new THREE.Quaternion(p.quat[0], p.quat[1], p.quat[2], p.quat[3]));
      else if (p.rot) mRT.makeRotationFromEuler(new THREE.Euler(p.rot[0] || 0, p.rot[1] || 0, p.rot[2] || 0, "XYZ"));
      const eT = mRT.elements;
      const axNormale = [eT[0], eT[1], eT[2]];   // X local : perpendiculaire au pignon
      const axBase = [eT[8], eT[9], eT[10]];     // Z local : base du triangle
      const dirT = (v) => {
        const n = Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]) || 1;
        return "(" + num(v[0]/n, 6) + "," + num(v[1]/n, 6) + "," + num(v[2]/n, 6) + ")";
      };
      const vIfcT = (v) => [v[0], -v[2], v[1]];
      const demiB = p.tri.b / 2;
      const ptA = nextId(); E(ptA, "IFCCARTESIANPOINT((" + num(-demiB) + ",0.));");
      const ptB = nextId(); E(ptB, "IFCCARTESIANPOINT((" + num(demiB) + ",0.));");
      const ptC = nextId(); E(ptC, "IFCCARTESIANPOINT((0.," + num(p.tri.h) + "));");
      const polyT = nextId(); E(polyT, "IFCPOLYLINE((#" + ptA + ",#" + ptB + ",#" + ptC + ",#" + ptA + "));");
      const profT = nextId(); E(profT, "IFCARBITRARYCLOSEDPROFILEDEF(.AREA.,$,#" + polyT + ");");
      const posT = nextId(); E(posT, "IFCCARTESIANPOINT((" + num(p.pos[0]) + "," + num(-p.pos[2]) + "," + num(p.pos[1]) + "));");
      const dzT = nextId(); E(dzT, "IFCDIRECTION(" + dirT(vIfcT(axNormale)) + ");");
      const dxT = nextId(); E(dxT, "IFCDIRECTION(" + dirT(vIfcT([-axBase[0], -axBase[1], -axBase[2]])) + ");");
      const axT = nextId(); E(axT, "IFCAXIS2PLACEMENT3D(#" + posT + ",#" + dzT + ",#" + dxT + ");");
      const plcT = nextId(); E(plcT, "IFCLOCALPLACEMENT(#" + storeyPlc + ",#" + axT + ");");
      const exPtT = nextId(); E(exPtT, "IFCCARTESIANPOINT((0.,0.," + num(-p.tri.ep / 2) + "));");
      const exAxT = nextId(); E(exAxT, "IFCAXIS2PLACEMENT3D(#" + exPtT + ",$,$);");
      const exDirT = nextId(); E(exDirT, "IFCDIRECTION((0.,0.,1.));");
      const solT = nextId(); E(solT, "IFCEXTRUDEDAREASOLID(#" + profT + ",#" + exAxT + ",#" + exDirT + "," + num(p.tri.ep) + ");");
      const repT = nextId(); E(repT, "IFCSHAPEREPRESENTATION(#" + bodyCtx + ",'Body','SweptSolid',(#" + solT + "));");
      const pdT = nextId(); E(pdT, "IFCPRODUCTDEFINITIONSHAPE($,$,(#" + repT + "));");
      const murT = nextId();
      E(murT, "IFCWALL('" + guid() + "',#" + owner + ",'" + txt(p.nom || "Mur pignon") + "',$,$,#" + plcT + ",#" + pdT + ",'" + (iP + 1) + "',.SOLIDWALL.);");
      memberIds.push(murT);
      idsBeton.push(murT);
      return;
    }
    // --- Dimensions Three.js d'origine ---
    const sx = Math.abs(p.dimsBrutes[0]);""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
