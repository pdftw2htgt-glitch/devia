# -*- coding: utf-8 -*-
import io, sys

chemin = sys.argv[1] if len(sys.argv) > 1 else "devia.jsx"
s = io.open(chemin, encoding="utf-8").read()
etapes = []

def rempl(titre, ancre, nouveau, attendu=1):
    global s
    n = s.count(ancre)
    etapes.append((titre, n, attendu))
    if n > attendu or n < attendu:
        raise SystemExit("ABANDON sur '" + titre + "' : " + str(n) + " occurrence(s), attendu " + str(attendu))
    s = s.replace(ancre, nouveau)

# 1. la fonction de coupe + le parametre onglets
rempl("1. coupe d onglet",
"  const drawMurPerce = (axe, posFixe, contour, trous, ep, nom) => {\n",
"""  // ===== COUPE D ONGLET AUX ANGLES =====
  // Deux murs qui se croisent a un angle se recouvrent sur une demi-epaisseur et laissent
  // le quart exterieur VIDE : d ou l angle qui ne se ferme pas. L onglet corrige les deux :
  // a l extremite concernee, la face EXTERIEURE s allonge d une demi-epaisseur et la face
  // INTERIEURE se raccourcit d autant. Les deux murs se rejoignent alors exactement, sur un
  // joint a 45 degres, sans vide ni recouvrement - et le volume ne change pas d un litre,
  // ce que l un perd, l autre le gagne.
  // sensEp : +1 si la face exterieure du mur est du cote des coordonnees croissantes.
  const couperOnglet = (geo, ep, sensEp, uMin, uMax, ongMin, ongMax) => {
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const u = pos.getX(i), w = pos.getZ(i);
      // w va de 0 a ep (sens de l extrusion) : dehors vaut +0,5 sur la face exterieure
      // et -0,5 sur l interieure.
      const dehors = (sensEp > 0) ? (w / ep - 0.5) : (0.5 - w / ep);
      if (ongMax === true && Math.abs(u - uMax) < 0.000001) pos.setX(i, u + ep * dehors);
      else if (ongMin === true && Math.abs(u - uMin) < 0.000001) pos.setX(i, u - ep * dehors);
    }
    pos.needsUpdate = true;
    geo.computeVertexNormals();
  };

  const drawMurPerce = (axe, posFixe, contour, trous, ep, nom, onglets) => {
""")

rempl("2. application apres extrusion",
"    const geo = new THREE.ExtrudeGeometry(shp, { depth: ep, bevelEnabled: false });\n",
"""    const geo = new THREE.ExtrudeGeometry(shp, { depth: ep, bevelEnabled: false });
    if (onglets && (onglets.min === true || onglets.max === true)) {
      let uMin = contour[0][0], uMax = contour[0][0];
      contour.forEach((q) => { if (q[0] < uMin) uMin = q[0]; if (q[0] > uMax) uMax = q[0]; });
      couperOnglet(geo, ep, posFixe >= 0 ? 1 : -1, uMin, uMax, onglets.min, onglets.max);
    }
""")

# 3. le pignon transmet ses onglets
rempl("3a. signature du pignon",
"  const drawPignonBeton = (xPos, lgb, Hb, htTri, ep, reservations, avecPorte) => {\n",
"  const drawPignonBeton = (xPos, lgb, Hb, htTri, ep, reservations, avecPorte, onglets) => {\n")

rempl("3b. transmission au trace",
'    drawMurPerce("x", xPos, cont, trous, ep, "Mur pignon beton");\n',
'    drawMurPerce("x", xPos, cont, trous, ep, "Mur pignon beton", onglets);\n')

# 4. qui se rejoint avec qui
rempl("4a. presence des quatre murs",
"""    const rectMur = [[-Lb / 2, 0], [Lb / 2, 0], [Lb / 2, Hb], [-Lb / 2, Hb]];
""",
"""    const rectMur = [[-Lb / 2, 0], [Lb / 2, 0], [Lb / 2, Hb], [-Lb / 2, Hb]];
    // Un bout de mur ne se coupe en onglet que s il a vraiment un voisin a rencontrer :
    // au droit d un volume accole, il n y a pas de mur en face et le biseau resterait en l air.
    const pignonsLa = ((params && params.pignon) || "plein") !== "aucun";
    const aPignonG = pignonsLa && (sansFace === "pignon_gauche") === false;
    const aPignonD = pignonsLa && (sansFace === "pignon_droit") === false;
    const aGouttAv = (sansFace === "gouttereau_avant") === false;
    const aGouttAr = (sansFace === "gouttereau_arriere") === false;
    // Gouttereau : son contour va de -Lb/2 (pignon gauche) a +Lb/2 (pignon droit).
    const ongGout = { min: aPignonG, max: aPignonD };
    // Pignon : son contour va de -lgb/2 a +lgb/2, et le quart de tour envoie le MIN sur le
    // gouttereau avant (z positif) et le MAX sur l arriere.
    const ongPign = { min: aGouttAv, max: aGouttAr };
""")

rempl("4b. gouttereaux en onglet",
'    if ((sansFace === "gouttereau_avant") === false) drawMurPerce("z", lgb / 2, rectMur, baiesEnTrous(baiesAv), ep, "Mur beton");\n'
'    if ((sansFace === "gouttereau_arriere") === false) drawMurPerce("z", -lgb / 2, rectMur, baiesEnTrous(baiesAr), ep, "Mur beton");\n',
'    if (aGouttAv) drawMurPerce("z", lgb / 2, rectMur, baiesEnTrous(baiesAv), ep, "Mur beton", ongGout);\n'
'    if (aGouttAr) drawMurPerce("z", -lgb / 2, rectMur, baiesEnTrous(baiesAr), ep, "Mur beton", ongGout);\n')

rempl("4c. pignons en onglet",
'      if ((sansFace === "pignon_droit") === false) {\n'
'        drawPignonBeton(Lb / 2, lgb, Hb, triActif ? htTriangle : 0, ep, triActif ? reservations : [], true);\n'
'      }\n'
'      if ((sansFace === "pignon_gauche") === false) {\n'
'        drawPignonBeton(-Lb / 2, lgb, Hb, triActif ? htTriangle : 0, ep, triActif ? reservations : [], false);\n'
'      }\n',
'      if (aPignonD) {\n'
'        drawPignonBeton(Lb / 2, lgb, Hb, triActif ? htTriangle : 0, ep, triActif ? reservations : [], true, ongPign);\n'
'      }\n'
'      if (aPignonG) {\n'
'        drawPignonBeton(-Lb / 2, lgb, Hb, triActif ? htTriangle : 0, ep, triActif ? reservations : [], false, ongPign);\n'
'      }\n')

io.open(chemin, "w", encoding="utf-8").write(s)
for t, n, a in etapes:
    print("  " + t + " : " + str(n) + "/" + str(a))
print("OK onglets poses")
