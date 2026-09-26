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

# 1) Le pignon accepte des reservations et les perce vraiment
remp("pignon perce",
"""  const drawPignonBeton = (xPos, lgb, Hb, htTri, ep) => {
    const shp = new THREE.Shape();
    shp.moveTo(-lgb / 2, 0);
    shp.lineTo(lgb / 2, 0);
    shp.lineTo(0, htTri);
    shp.closePath();""",
"""  const drawPignonBeton = (xPos, lgb, Hb, htTri, ep, reservations) => {
    const shp = new THREE.Shape();
    shp.moveTo(-lgb / 2, 0);
    shp.lineTo(lgb / 2, 0);
    shp.lineTo(0, htTri);
    shp.closePath();
    // RESERVATIONS : le mur est perce au passage de chaque panne (1 cm de jeu au pourtour).
    // Un trou n est ouvert que s il tient entierement dans le triangle, rampants compris.
    let nbPerces = 0;
    (reservations || []).forEach((r) => {
      const hx = r.b / 2 + 0.01;
      const hy = r.h / 2 + 0.01;
      const yc = r.y - Hb;
      const xg = r.z - hx, xd = r.z + hx;
      const hautDispo = (xx) => htTri * (1 - Math.abs(xx) / (lgb / 2));
      const tient = (yc - hy) > 0.02
        && (yc + hy) < hautDispo(xg) - 0.02
        && (yc + hy) < hautDispo(xd) - 0.02;
      if (tient) {
        const ph = new THREE.Path();
        ph.moveTo(xg, yc - hy);
        ph.lineTo(xd, yc - hy);
        ph.lineTo(xd, yc + hy);
        ph.lineTo(xg, yc + hy);
        ph.closePath();
        shp.holes.push(ph);
        nbPerces += 1;
      }
    });
    if (nbPerces > 0) console.log("[DEVIA] Pignon : " + nbPerces + " reservation(s) percee(s) pour les pannes");""")

# 2) Les murs transmettent les reservations au pignon
remp("signature drawMursBeton",
"""  const drawMursBeton = (Lb, lgb, Hb) => {""",
"""  const drawMursBeton = (Lb, lgb, Hb, reservations) => {""")

remp("appel du pignon avec reservations",
"""        if ((sansFace === "pignon_droit") === false) drawPignonBeton(Lb / 2, lgb, Hb, htTriangle, ep);
        if ((sansFace === "pignon_gauche") === false) drawPignonBeton(-Lb / 2, lgb, Hb, htTriangle, ep);""",
"""        if ((sansFace === "pignon_droit") === false) drawPignonBeton(Lb / 2, lgb, Hb, htTriangle, ep, reservations);
        if ((sansFace === "pignon_gauche") === false) drawPignonBeton(-Lb / 2, lgb, Hb, htTriangle, ep, reservations);""")

# 3) La charpente trad calcule ou passent ses pannes, avant de dessiner les murs
remp("calcul des reservations",
"""    console.log("[DEVIA] Murs montes a " + hMurSousSabliere.toFixed(3) + " m (sous-face de la sabliere)");
    if (params.murs === "ossature_bois") { drawMursOssature(L, lg, hMurSousSabliere); } else { drawMursBeton(L, lg, hMurSousSabliere); }""",
"""    console.log("[DEVIA] Murs montes a " + hMurSousSabliere.toFixed(3) + " m (sous-face de la sabliere)");
    // Ou passent les pannes dans le pignon : memes formules que leur pose plus bas.
    // (la sabliere sort du triangle par les cotes, elle n a pas de reservation)
    const sinA0 = Math.sin(ang);
    const [pfB0, pfH0] = sec("Panne faitiere", 0.14, 0.14);
    const reservPignon = [];
    const nbPannesPan0 = 2;
    for (let p0 = 1; p0 <= nbPannesPan0; p0++) {
      const t0 = p0 / (nbPannesPan0 + 1);
      const yRef0 = Ht + hf * t0 + (arH0 / 2) * cosA0;
      const zRef0 = (lg / 2) * (1 - t0) + (arH0 / 2) * sinA0;
      const yP0 = yRef0 + (pnB0 / 2) * tanA0 + 0.03 + pnH0 / 2;
      reservPignon.push({ z: zRef0, y: yP0, b: pnB0, h: pnH0 });
      reservPignon.push({ z: -zRef0, y: yP0, b: pnB0, h: pnH0 });
    }
    reservPignon.push({ z: 0, y: Ht + hf + dPerp0 / cosA0 - pfH0 / 2, b: pfB0, h: pfH0 });
    if (params.murs === "ossature_bois") { drawMursOssature(L, lg, hMurSousSabliere); } else { drawMursBeton(L, lg, hMurSousSabliere, reservPignon); }""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
