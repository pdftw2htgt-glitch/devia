import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

DEB = "  const drawPignonBeton = (xPos, lgb, Hb, htTri, ep, reservations) => {"
FIN = "\n\n  const drawMursBeton = (Lb, lgb, Hb, reservations) => {"

if src.count(DEB) != 1 or src.count(FIN) != 1:
    print("ABANDON : debut " + str(src.count(DEB)) + " fois, fin " + str(src.count(FIN)) + " fois")
    sys.exit(1)
d = src.find(DEB)
f = src.find(FIN, d)
print("Fonction reperee : " + str(src[d:f].count(chr(10))) + " lignes remplacees")

NOUVELLE = '''  const drawPignonBeton = (xPos, lgb, Hb, htTri, ep, reservations) => {
    // Le maçon ne laisse pas un trou ferme autour d une panne : il descend le mur sous elle.
    // Chaque panne donne donc une ENCOCHE ouverte par le haut, ou la panne vient se poser.
    const res = (reservations || [])
      .map((r) => ({
        x0: r.z - (r.b / 2 + 0.01),
        x1: r.z + (r.b / 2 + 0.01),
        yb: (r.y - r.h / 2 - 0.01) - Hb,   // sous-face de la panne, jeu compris
        yh: (r.y + r.h / 2 + 0.01) - Hb,   // dessus de la panne
      }))
      .filter((e) => e.x1 > -lgb / 2 + 0.02 && e.x0 < lgb / 2 - 0.02)
      .sort((a, b) => a.x0 - b.x0);
    // Le pignon monte au moins au-dessus de la panne la plus haute, sinon rien a encocher
    let hSommet = htTri;
    res.forEach((e) => { if (e.yh + 0.03 > hSommet) hSommet = e.yh + 0.03; });
    const hMur = (x) => hSommet * (1 - Math.abs(x) / (lgb / 2));
    // Contour superieur, de gauche a droite, creuse a chaque passage de panne
    const haut = [];
    let dernierX = -lgb / 2;
    let sommetPose = false;
    let nbEnc = 0;
    res.forEach((e) => {
      const a = Math.max(e.x0, -lgb / 2 + 0.02);
      const b = Math.min(e.x1, lgb / 2 - 0.02);
      if (b <= a || a < dernierX) return;               // encoches jointives : on garde la premiere
      if (a > 0 && dernierX < 0 && sommetPose === false) { haut.push([0, hMur(0)]); sommetPose = true; }
      if (a < 0 && b > 0) sommetPose = true;            // l encoche emporte le faitage
      const fond = Math.max(0.02, Math.min(e.yb, Math.min(hMur(a), hMur(b)) - 0.01));
      haut.push([a, hMur(a)]);
      haut.push([a, fond]);
      haut.push([b, fond]);
      haut.push([b, hMur(b)]);
      dernierX = b;
      nbEnc += 1;
    });
    if (sommetPose === false) haut.push([0, hMur(0)]);
    const shp = new THREE.Shape();
    shp.moveTo(-lgb / 2, 0);
    shp.lineTo(lgb / 2, 0);
    for (let i = haut.length - 1; i >= 0; i--) shp.lineTo(haut[i][0], haut[i][1]);
    shp.closePath();
    console.log("[DEVIA] Pignon : " + nbEnc + " encoche(s) de panne, sommet a " + hSommet.toFixed(2) + " m au-dessus du mur");
    const geo = new THREE.ExtrudeGeometry(shp, { depth: ep, bevelEnabled: false });
    const m = new THREE.Mesh(geo, betonMat);
    m.rotation.y = Math.PI / 2;            // le plan du pignon devient perpendiculaire au faitage
    m.position.set(xPos - ep / 2, Hb, 0);  // epaisseur centree sur le nu du mur
    m.castShadow = true;
    m.receiveShadow = true;
    scene.add(m);
    metre.push({
      matiere: "beton",
      nom: "Mur pignon beton",
      section: [Math.round(ep * 1000), Math.round(hSommet * 1000)],
      longueur: lgb,
      volume: (lgb * hSommet / 2) * ep,
      dimsBrutes: [ep, hSommet, lgb],
      tri: { b: lgb, h: hSommet, ep: ep },  // profil repris a l export IFC (encoches non exportees)
      pos: [xPos, Hb, 0],
      rot: null,
      quat: null,
    });
  };'''

src = src[:d] + NOUVELLE + src[f:]
open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit : pignon encoche ---")
