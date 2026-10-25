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

# 1. le poincon a tete encochee, a cote des autres helpers de dessin
rempl("1. fonction du poincon encoche",
"""  // Poutre orientee entre 2 points (touche forcement les 2 extremites)
  const addBeam = (x1, y1, z1, x2, y2, z2, thick, mat) => {""",
"""  // ===== POINCON A TETE ENCOCHEE =====
  // Le poincon monte jusqu au DESSUS de la panne faitiere et la recoit dans une encoche :
  // deux joues de part et d autre, la faitiere assise entre elles. C est l assemblage de base
  // d une ferme latine. Prisme file selon X, section dessinee dans le plan (z, y) : elle n est
  // pas convexe a cause de l encoche, d ou l extrusion plutot qu un eventail de triangles.
  const addPoinconEncoche = (x, b, h, yBas, yHaut, encB, encH) => {
    const encBr = Math.min(encB, h - 0.02);                  // au moins 1 cm de joue de chaque cote
    const encHr = Math.min(encH, (yHaut - yBas) - 0.05);     // l encoche n avale jamais tout le poincon
    const cont = [
      [-h / 2, yBas], [h / 2, yBas], [h / 2, yHaut],
      [encBr / 2, yHaut], [encBr / 2, yHaut - encHr], [-encBr / 2, yHaut - encHr], [-encBr / 2, yHaut],
      [-h / 2, yHaut],
    ];
    const shp = new THREE.Shape();
    shp.moveTo(cont[0][0], cont[0][1]);
    for (let i = 1; i < cont.length; i++) shp.lineTo(cont[i][0], cont[i][1]);
    shp.closePath();
    const geo = new THREE.ExtrudeGeometry(shp, { depth: b, bevelEnabled: false });
    const m = new THREE.Mesh(geo, woodMat);
    m.rotation.y = Math.PI / 2;                              // le contour part sur Z, l extrusion sur X
    m.position.set(x - b / 2, 0, 0);
    m.castShadow = true;
    scene.add(m);
    // Metre : section nominale et longueur hors tout. L encoche est un usinage, comme le delardement.
    logPiece(b, h, yHaut - yBas, { pos: [x, (yBas + yHaut) / 2, 0], rot: null, quat: null });
  };

  // Poutre orientee entre 2 points (touche forcement les 2 extremites)
  const addBeam = (x1, y1, z1, x2, y2, z2, thick, mat) => {""")

# 2. les arbaletriers s arretent sur les joues du poincon
rempl("2a. section du poincon connue avant les arbaletriers",
"""    // Arbaletrier = prisme a COUPES VERTICALES, comme les chevrons : onglet au faitage (les deux
    // pans s emboitent au lieu de se traverser) et coupe d aplomb a l egout.
    const addArbaOnglet = (x, signZ, arBw, arHw) => {
      const cosAa = Math.cos(ang), tanAa = Math.tan(ang);
      const dvA = (arHw / 2) / cosAa;                 // demi-hauteur mesuree a la verticale
      const yAxe = (z) => Ht + hf - z * tanAa;        // axe du rampant
      const zE = lg / 2;
      const yB0 = yAxe(0) - dvA, yH0 = yAxe(0) + dvA;    // about faitage
""",
"""    // Arbaletrier = prisme a COUPES VERTICALES : il ne monte plus jusqu a l axe du faitage,
    // il vient MOURIR SUR LA JOUE DU POINCON, ou il serait tenonne. Coupe d aplomb a l egout.
    const [poBa, poHa] = sec("Poincon", 0.18, 0.18);
    const addArbaOnglet = (x, signZ, arBw, arHw) => {
      const cosAa = Math.cos(ang), tanAa = Math.tan(ang);
      const dvA = (arHw / 2) / cosAa;                 // demi-hauteur mesuree a la verticale
      const yAxe = (z) => Ht + hf - z * tanAa;        // axe du rampant
      const zE = lg / 2;
      const z0 = poHa / 2;                            // joue du poincon : la ou l arbaletrier s arrete
      const yB0 = yAxe(z0) - dvA, yH0 = yAxe(z0) + dvA;  // about contre le poincon
""")

rempl("2b. sommets contre le poincon",
"      const A1=[xa,yB0,0], B1=[xa,yH0,0], C1=[xa,yHE,s*zE], D1=[xa,yBE,s*zE];\n"
"      const A2=[xb,yB0,0], B2=[xb,yH0,0], C2=[xb,yHE,s*zE], D2=[xb,yBE,s*zE];\n",
"      const A1=[xa,yB0,s*z0], B1=[xa,yH0,s*z0], C1=[xa,yHE,s*zE], D1=[xa,yBE,s*zE];\n"
"      const A2=[xb,yB0,s*z0], B2=[xb,yH0,s*z0], C2=[xb,yHE,s*zE], D2=[xb,yBE,s*zE];\n")

rempl("2c. longueur reelle au metre",
'      quad(A1,A2,B2,B1);                              // about faitage (coupe d onglet verticale)\n',
'      quad(A1,A2,B2,B1);                              // about contre le poincon (coupe verticale)\n')

rempl("2d. metre de l arbaletrier",
"      logPiece(arBw, arHw, zE / cosAa, { pos: [x, (yB0 + yHE) / 2, s * zE / 2], rot: [s * ang, 0, 0], quat: null });\n",
"      logPiece(arBw, arHw, (zE - z0) / cosAa, { pos: [x, (yB0 + yHE) / 2, s * (z0 + zE) / 2], rot: [s * ang, 0, 0], quat: null });\n")

# 3. la tete du poincon, calculee avant la boucle des fermes
rempl("3. hauteur de tete",
"    const fermeXs = [];\n    const fermesDessinees = [];\n",
"""    // Tete du poincon : il monte jusqu au DESSUS de la panne faitiere. Memes formules que la
    // pose de la faitiere plus bas - dPerp0 vaut dPerpSousChevron, elles sont calculees pareil.
    const yFaitierePoincon = Ht + hf + dPerp0 / cosA0 - (pfB0 / 2) * tanA0 + delardement - pfH0 / 2;
    const yTetePoincon = yFaitierePoincon + pfH0 / 2;
    const fermeXs = [];
    const fermesDessinees = [];
""")

rempl("4. pose du poincon",
"""      // POINCON (poteau vertical central, du faitage a l'entrait)
      setPiece("Poincon");
      const [poB, poH] = sec("Poincon", 0.18, 0.18);
      addBox(poB, hf, poH, x, Ht + hf/2, 0, woodMat);
""",
"""      // POINCON : de l entrait jusqu au dessus de la faitiere, qu il porte dans son encoche.
      setPiece("Poincon");
      const [poB, poH] = sec("Poincon", 0.18, 0.18);
      addPoinconEncoche(x, poB, poH, Ht, yTetePoincon, pfB0, pfH0);
""")

io.open(chemin, "w", encoding="utf-8").write(s)
for t, n, a in etapes:
    print("  " + t + " : " + str(n) + "/" + str(a))
print("OK poincon et arbaletriers")
