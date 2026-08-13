import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_ifc_orientation_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ---- A1 : registre du groupe proprietaire de chaque piece (mode multi) ----
remplacer(
"""      const gap = 2.0;
      const metresAll = [];
      const groupes = [];""",
"""      const gap = 2.0;
      const metresAll = [];
      const proprietairePiece = []; // groupe d'origine de chaque piece (bake IFC)
      const groupes = [];""", "A1")

# ---- A2 : enregistrement des pieces de chaque ouvrage ----
remplacer(
"""        scene.add(grp);
        groupes.push(grp);
        metresAll.push(...res.metre);""",
"""        scene.add(grp);
        groupes.push(grp);
        const iDebutMetre = metresAll.length;
        metresAll.push(...res.metre);
        for (let iP = iDebutMetre; iP < metresAll.length; iP++) proprietairePiece[iP] = grp;""", "A2")

# ---- A3 : bake des transformations de groupe APRES le recentrage ----
remplacer(
"""      if (onMetreRef.current && metresAll.length) {
        onMetreRef.current(agregerMetre(metresAll, densiteRef), metresAll);
      }""",
"""      // ===== BAKE IFC : coordonnees MONDE pour chaque piece du metre =====
      // Applique la transformation finale du groupe (rotation cardinale + accolage + recentrage)
      // a la position ET a l'orientation de chaque piece -> l'export IFC voit l'assemblage reel.
      metresAll.forEach((p, iP) => {
        const grpP = proprietairePiece[iP];
        if (grpP === undefined || p.pos === null || p.pos === undefined) return;
        grpP.updateMatrixWorld(true);
        const vPos = new THREE.Vector3(p.pos[0], p.pos[1], p.pos[2]).applyMatrix4(grpP.matrixWorld);
        p.pos = [vPos.x, vPos.y, vPos.z];
        const qGrp = new THREE.Quaternion();
        grpP.getWorldQuaternion(qGrp);
        const qPiece = new THREE.Quaternion();
        if (p.quat) qPiece.set(p.quat[0], p.quat[1], p.quat[2], p.quat[3]);
        else if (p.rot) qPiece.setFromEuler(new THREE.Euler(p.rot[0] || 0, p.rot[1] || 0, p.rot[2] || 0, "XYZ"));
        qGrp.multiply(qPiece);
        p.quat = [qGrp.x, qGrp.y, qGrp.z, qGrp.w];
        p.rot = null;
      });
      if (onMetreRef.current && metresAll.length) {
        onMetreRef.current(agregerMetre(metresAll, densiteRef), metresAll);
      }""", "A3")

# ---- B0 : commentaire de convention en tete du generateur ----
remplacer(
"// Note conventions axes : Three.js Y=haut -> IFC Z=haut. Conversion (x,y,z)->(x,z,y).",
"// Note conventions axes : Three.js Y=haut -> IFC Z=haut. Conversion (x,y,z)->(x,-z,y) SANS miroir ; nord scene (-Z) -> +Y IFC.", "B0")

# ---- B : reecriture du coeur orientation (region delimitee par 2 marqueurs) ----
debut = "    // helper : convertit un vecteur Three (x,y,z) -> IFC (x, z, y) et normalise"
fin = '    if (Math.abs(izComp) > 0.9) { refX = "(1.,0.,0.)"; }\n    else { refX = "(0.,0.,1.)"; }'
nd, nf = c.count(debut), c.count(fin)
if nd != 1 or nf != 1:
    erreurs.append("B : marqueurs trouves debut=" + str(nd) + " fin=" + str(nf) + " (attendu 1 et 1)")
else:
    i0 = c.find(debut)
    i1 = c.find(fin) + len(fin)
    nouveau_b = """    // --- Repere local COMPLET de la piece : axe long + roulis de section conserves ---
    // Conversion Three (x,y,z) -> IFC (x,-z,y) : Y haut -> Z haut, nord scene (-Z) -> +Y IFC.
    // (l'ancienne conversion (x,z,y) inversait la chiralite : batiment exporte en MIROIR)
    const fmtDir = (v) => {
      const nrm = Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]) || 1;
      return "(" + (v[0]/nrm).toFixed(6) + "," + (v[1]/nrm).toFixed(6) + "," + (v[2]/nrm).toFixed(6) + ")";
    };
    const toIfcVec = (v) => [v[0], -v[2], v[1]];
    // Matrice de rotation de la piece (quaternion prioritaire, sinon euler XYZ Three, sinon identite)
    const mRot = new THREE.Matrix4();
    if (p.quat) {
      mRot.makeRotationFromQuaternion(new THREE.Quaternion(p.quat[0], p.quat[1], p.quat[2], p.quat[3]));
    } else if (p.rot) {
      mRot.makeRotationFromEuler(new THREE.Euler(p.rot[0] || 0, p.rot[1] || 0, p.rot[2] || 0, "XYZ"));
    }
    const elm = mRot.elements; // colonne-major
    const axesLoc = [
      [elm[0], elm[1], elm[2]],   // axe X local exprime dans le repere Three
      [elm[4], elm[5], elm[6]],   // axe Y local
      [elm[8], elm[9], elm[10]],  // axe Z local
    ];
    // Axe long = plus grande dimension ; les 2 autres = la section
    const dims3 = [sx, sy, sz];
    let iLong = 0;
    if (dims3[1] > dims3[iLong]) iLong = 1;
    if (dims3[2] > dims3[iLong]) iLong = 2;
    const iX = (iLong + 1) % 3;
    const iY = (iLong + 2) % 3;
    const L = dims3[iLong];
    const w = dims3[iX];
    const h = dims3[iY];
    // Placement IFC : Z local = axe long REEL de la piece, X local = axe de section REEL (roulis conserve)
    const axisZ = fmtDir(toIfcVec(axesLoc[iLong]));
    const refX = fmtDir(toIfcVec(axesLoc[iX]));
    // Position du centre, Three (x,y,z) -> IFC (x,-z,y)
    const px = p.pos[0], py = -p.pos[2], pz = p.pos[1];"""
    c = c[:i0] + nouveau_b + c[i1:]

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : export IFC renforce (assemblage monde + sans miroir + roulis des sections).")
