import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

def remp(nom, ancre, nouveau, attendu=1):
    global src
    n = src.count(ancre)
    if n != attendu:
        print("ABANDON " + nom + " : ancre trouvee " + str(n) + " fois au lieu de " + str(attendu))
        cle = ancre.strip().split("\n")[0][:45]
        for i, l in enumerate(src.split("\n")):
            if cle in l:
                print("  ligne " + str(i + 1) + " : " + l.strip()[:200])
        sys.exit(1)
    src = src.replace(ancre, nouveau)
    print("OK " + nom + " (" + str(n) + " fois)")

# 1) MARQUAGE DES PIECES BOIS, en un seul point de passage
remp("marquage des bois",
"""  return { yCentre, metre, densiteBois, essence };
}""",
"""  // Marque les pieces en BOIS. Un seul point de passage : tout ce qui porte le materiau bois
  // est marque ici, le viewer n a plus qu a lire ce drapeau pour tracer les aretes.
  scene.traverse((oM) => { if (oM.isMesh === true && oM.material === woodMat) oM.userData.boisDevia = true; });

  return { yCentre, metre, densiteBois, essence };
}""")

# 2) VUE RANGEE AU SOL : les pieces debitees meritent aussi leurs aretes
remp("marquage des bois ranges au sol",
"""          meshP.position.set(Lp / 2, ep / 2 + 0.001, zCur + larg / 2);
          meshP.castShadow = true;""",
"""          meshP.position.set(Lp / 2, ep / 2 + 0.001, zCur + larg / 2);
          meshP.castShadow = true;
          meshP.userData.boisDevia = true;""")

# 3) ARETES : une seule geometrie pour toute la charpente
remp("aretes des bois",
"""    const listeSol = Array.isArray(params.ouvrages) ? params.ouvrages : [];""",
"""    // ===== ARETES DES BOIS =====
    // Deux pieces de meme teinte qui se touchent se fondent l une dans l autre : la charpente
    // parait molle et les sections paraissent plus maigres qu elles ne sont. Une arete sur
    // chaque piece lui rend son volume. Toutes les aretes sont empilees dans UNE geometrie
    // (coordonnees monde), donc un seul objet a dessiner : aucun cout d affichage notable.
    const ptsAretes = [];
    scene.updateMatrixWorld(true);
    scene.traverse((oA) => {
      if (oA.isMesh === true && oA.userData && oA.userData.boisDevia === true && oA.geometry) {
        const egA = new THREE.EdgesGeometry(oA.geometry, 25);
        const paA = egA.attributes.position;
        const vA = new THREE.Vector3();
        for (let iA = 0; iA < paA.count; iA++) {
          vA.set(paA.getX(iA), paA.getY(iA), paA.getZ(iA)).applyMatrix4(oA.matrixWorld);
          ptsAretes.push(vA.x, vA.y, vA.z);
        }
        egA.dispose();
      }
    });
    if (ptsAretes.length > 0) {
      const gAr = new THREE.BufferGeometry();
      gAr.setAttribute("position", new THREE.BufferAttribute(new Float32Array(ptsAretes), 3));
      const arSombre = (params.mode3D === "realiste");
      scene.add(new THREE.LineSegments(gAr, new THREE.LineBasicMaterial({
        color: arSombre ? 0x4a3118 : 0x2e2114,
        transparent: true,
        opacity: arSombre ? 0.45 : 0.6,
      })));
      console.log("[DEVIA] Aretes des bois : " + Math.round(ptsAretes.length / 6) + " segments en un seul objet");
    }

    const listeSol = Array.isArray(params.ouvrages) ? params.ouvrages : [];""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
