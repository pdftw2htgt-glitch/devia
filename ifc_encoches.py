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

remp("contour partage 3D / IFC",
"""    const shp = new THREE.Shape();
    shp.moveTo(-lgb / 2, 0);
    shp.lineTo(lgb / 2, 0);
    for (let i = haut.length - 1; i >= 0; i--) shp.lineTo(haut[i][0], haut[i][1]);
    shp.closePath();""",
"""    // Contour UNIQUE, partage par la 3D et par l export IFC : c est ce qui garantit que le
    // fichier remis au charpentier porte exactement les encoches vues a l ecran.
    const cont = [[-lgb / 2, 0], [lgb / 2, 0]];
    for (let i = haut.length - 1; i >= 0; i--) {
      const px = haut[i][0], py = haut[i][1];
      const prec = cont[cont.length - 1];
      if (Math.abs(px - prec[0]) > 0.0002 || Math.abs(py - prec[1]) > 0.0002) cont.push([px, py]);
    }
    const shp = new THREE.Shape();
    shp.moveTo(cont[0][0], cont[0][1]);
    for (let i = 1; i < cont.length; i++) shp.lineTo(cont[i][0], cont[i][1]);
    shp.closePath();""")

remp("contour au metre",
"""      tri: { b: lgb, h: hSommet, ep: ep },  // profil repris a l export IFC (encoches non exportees)""",
"""      tri: { b: lgb, h: hSommet, ep: ep, contour: cont },  // profil EXACT repris a l export IFC""")

remp("profil IFC avec encoches",
"""      const demiB = p.tri.b / 2;
      const ptA = nextId(); E(ptA, "IFCCARTESIANPOINT((" + num(-demiB) + ",0.));");
      const ptB = nextId(); E(ptB, "IFCCARTESIANPOINT((" + num(demiB) + ",0.));");
      const ptC = nextId(); E(ptC, "IFCCARTESIANPOINT((0.," + num(p.tri.h) + "));");
      const polyT = nextId(); E(polyT, "IFCPOLYLINE((#" + ptA + ",#" + ptB + ",#" + ptC + ",#" + ptA + "));");""",
"""      const demiB = p.tri.b / 2;
      // Le repere du profil IFC coincide point pour point avec celui de la Shape Three
      // (x du profil = x de la forme, y = hauteur), donc le contour se recopie tel quel.
      const contT = (Array.isArray(p.tri.contour) && p.tri.contour.length >= 3)
        ? p.tri.contour
        : [[-demiB, 0], [demiB, 0], [0, p.tri.h]];
      const idsT = contT.map((q) => {
        const idq = nextId();
        E(idq, "IFCCARTESIANPOINT((" + num(q[0]) + "," + num(q[1]) + "));");
        return idq;
      });
      const polyT = nextId(); E(polyT, "IFCPOLYLINE((#" + idsT.join(",#") + ",#" + idsT[0] + "));");
      if (contT.length > 3) console.log("[DEVIA] IFC : pignon exporte avec " + contT.length + " points, encoches de pannes comprises");""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
