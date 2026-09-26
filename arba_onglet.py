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

# 1) Le mur monte jusqu a la sous-face de la sabliere (plus de vide sous la panne basse)
remp("mur jusqu a la sabliere",
"""    // ===== MURS BETON (porte pignon + fenetres) =====
    if (params.murs === "ossature_bois") { drawMursOssature(L, lg, Ht); } else { drawMursBeton(L, lg, Ht); }
    drawDalleBeton(L, lg, 0);""",
"""    // ===== MURS : ils montent jusqu a la SOUS-FACE DE LA SABLIERE =====
    // La sabliere est calee dans le plan porteur des chevrons, donc au-dessus de l arase brute :
    // sans cela un vide reste ouvert entre le haut du mur et la panne basse.
    const [sbB0, sbH0] = sec("Sabliere", 0.14, 0.14);
    const [arB0, arH0] = sec("Arbaletrier", 0.16, 0.16);
    const [pnB0, pnH0] = sec("Panne", 0.12, 0.12);
    const cosA0 = Math.cos(ang), tanA0 = Math.tan(ang);
    const dPerp0 = arH0 / 2 + (pnH0 + 0.03) * cosA0;
    const hMurSousSabliere = Ht + dPerp0 / cosA0 + (sbB0 / 2) * tanA0 - sbH0;
    console.log("[DEVIA] Murs montes a " + hMurSousSabliere.toFixed(3) + " m (sous-face de la sabliere)");
    if (params.murs === "ossature_bois") { drawMursOssature(L, lg, hMurSousSabliere); } else { drawMursBeton(L, lg, hMurSousSabliere); }
    drawDalleBeton(L, lg, 0);""")

# 2) Arbaletriers coupes d onglet au faitage, d aplomb a l egout
remp("addArbaOnglet",
"""    const fermeXs = [];""",
"""    // Arbaletrier = prisme a COUPES VERTICALES, comme les chevrons : onglet au faitage (les deux
    // pans s emboitent au lieu de se traverser) et coupe d aplomb a l egout.
    const addArbaOnglet = (x, signZ, arBw, arHw) => {
      const cosAa = Math.cos(ang), tanAa = Math.tan(ang);
      const dvA = (arHw / 2) / cosAa;                 // demi-hauteur mesuree a la verticale
      const yAxe = (z) => Ht + hf - z * tanAa;        // axe du rampant
      const zE = lg / 2;
      const yB0 = yAxe(0) - dvA, yH0 = yAxe(0) + dvA;    // about faitage
      const yBE = yAxe(zE) - dvA, yHE = yAxe(zE) + dvA;  // about egout
      const xa = x - arBw / 2, xb = x + arBw / 2;
      const s = signZ;
      const pos = [];
      const quad = (a, b, c, d) => { pos.push(...a, ...b, ...c, ...a, ...c, ...d); };
      const A1=[xa,yB0,0], B1=[xa,yH0,0], C1=[xa,yHE,s*zE], D1=[xa,yBE,s*zE];
      const A2=[xb,yB0,0], B2=[xb,yH0,0], C2=[xb,yHE,s*zE], D2=[xb,yBE,s*zE];
      quad(A1,B1,C1,D1); quad(A2,D2,C2,B2);          // 2 joues
      quad(B1,B2,C2,C1);                              // extrados
      quad(A1,D1,D2,A2);                              // intrados
      quad(A1,A2,B2,B1);                              // about faitage (coupe d onglet verticale)
      quad(D1,C1,C2,D2);                              // about egout (coupe d aplomb)
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pos), 3));
      g.computeVertexNormals();
      const m = new THREE.Mesh(g, woodMat);
      m.castShadow = true;
      scene.add(m);
      logPiece(arBw, arHw, zE / cosAa, { pos: [x, (yB0 + yHE) / 2, s * zE / 2], rot: [s * ang, 0, 0], quat: null });
    };
    const fermeXs = [];""")

remp("arbaletriers en onglet",
"""      // ARBALETRIERS (les 2 pans inclines, section forte)
      setPiece("Arbaletrier");
      const [arB, arH] = sec("Arbaletrier", 0.16, 0.16);
      addBox(arB, arH, pl, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);
      addBox(arB, arH, pl, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);""",
"""      // ARBALETRIERS (les 2 pans inclines, section forte) : aboutes en onglet au faitage
      setPiece("Arbaletrier");
      const [arB, arH] = sec("Arbaletrier", 0.16, 0.16);
      addArbaOnglet(x, 1, arB, arH);
      addArbaOnglet(x, -1, arB, arH);""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
