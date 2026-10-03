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

remp("terrain perce sur la fouille",
"""    const listeSol = Array.isArray(params.ouvrages) ? params.ouvrages : [];
    const aDuEnterre = listeSol.some(o => o && typeof o.pose === "number" && o.pose < -0.05) || (typeof params.pose === "number" && params.pose < -0.05);
    if (aDuEnterre) console.log("[DEVIA] Niveau enterre detecte : terrain rendu translucide");
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(120, 120),
      new THREE.MeshStandardMaterial({ color: 0x1a1f2e, roughness: 0.95, metalness: 0.0, transparent: aDuEnterre, opacity: aDuEnterre ? 0.25 : 1, depthWrite: (aDuEnterre === false) })
    );
    ground.rotation.x = -Math.PI/2;
    ground.receiveShadow = true;
    scene.add(ground);""",
"""    const listeSol = Array.isArray(params.ouvrages) ? params.ouvrages : [];
    // On ne se fie plus seulement aux parametres : on regarde ce qui a REELLEMENT ete dessine
    // sous le niveau zero. Un volume enterre arrive par des chemins differents (analyse de plan,
    // decomposition manuelle, rechargement d un projet) et la pose ne suit pas toujours.
    const SEUIL_FOUILLE = -0.5;
    const bbSous = new THREE.Box3();
    let aDuVolumeSous = false;
    scene.traverse((oS) => {
      if (oS.isMesh === true && oS.geometry) {
        const bbS = new THREE.Box3().setFromObject(oS);
        if (bbS.min.y < SEUIL_FOUILLE) { bbSous.union(bbS); aDuVolumeSous = true; }
      }
    });
    const aDuEnterre = aDuVolumeSous || listeSol.some(o => o && typeof o.pose === "number" && o.pose < -0.05) || (typeof params.pose === "number" && params.pose < -0.05);
    const profEnterre = aDuVolumeSous ? bbSous.min.y : 0;
    if (aDuVolumeSous) console.log("[DEVIA] Niveau enterre : fond de fouille a " + profEnterre.toFixed(2) + " m, terrain perce et translucide");
    if (aDuEnterre && aDuVolumeSous === false) console.log("[DEVIA] ATTENTION : pose negative annoncee mais rien n a ete dessine sous le sol");
    let geoSol = new THREE.PlaneGeometry(120, 120);
    if (aDuVolumeSous) {
      // Le sol est perce a l aplomb du volume enterre : le sous-sol passe DESSOUS la surface
      // au lieu de la traverser. ShapeGeometry vit dans le plan XY et subit rotation.x = -PI/2 :
      // un point (x, y) de la forme arrive en (x, 0, -y) dans le monde, d ou les -z ci-dessous.
      const JEU_F = 0.03;
      const x0 = bbSous.min.x - JEU_F, x1 = bbSous.max.x + JEU_F;
      const z0 = bbSous.min.z - JEU_F, z1 = bbSous.max.z + JEU_F;
      const forme = new THREE.Shape([
        new THREE.Vector2(-60, -60), new THREE.Vector2(60, -60),
        new THREE.Vector2(60, 60), new THREE.Vector2(-60, 60),
      ]);
      forme.holes.push(new THREE.Path([
        new THREE.Vector2(x0, -z1), new THREE.Vector2(x1, -z1),
        new THREE.Vector2(x1, -z0), new THREE.Vector2(x0, -z0),
      ]));
      geoSol = new THREE.ShapeGeometry(forme);
      console.log("[DEVIA] Fouille ouverte dans le terrain : " + (x1 - x0).toFixed(2) + " x " + (z1 - z0).toFixed(2) + " m");
    }
    const ground = new THREE.Mesh(
      geoSol,
      new THREE.MeshStandardMaterial({ color: 0x1a1f2e, roughness: 0.95, metalness: 0.0, side: THREE.DoubleSide, transparent: aDuEnterre, opacity: aDuEnterre ? 0.22 : 1, depthWrite: (aDuEnterre === false) })
    );
    ground.rotation.x = -Math.PI/2;
    ground.receiveShadow = true;
    scene.add(ground);
    if (aDuVolumeSous) {
      // Arete de fouille : sans ce trait, un terrain translucide ne laisse pas lire ou il s arrete.
      const yA = 0.004;
      const cF = [
        [bbSous.min.x, bbSous.min.z], [bbSous.max.x, bbSous.min.z],
        [bbSous.max.x, bbSous.max.z], [bbSous.min.x, bbSous.max.z],
      ];
      const ptsF = [];
      for (let iF = 0; iF < 4; iF++) {
        const a = cF[iF], b = cF[(iF + 1) % 4];
        ptsF.push(new THREE.Vector3(a[0], yA, a[1]), new THREE.Vector3(b[0], yA, b[1]));
      }
      scene.add(new THREE.LineSegments(
        new THREE.BufferGeometry().setFromPoints(ptsF),
        new THREE.LineBasicMaterial({ color: 0x8aa0c0, transparent: true, opacity: 0.6 })
      ));
      // Le fond de fouille ne recoit aucune lumiere du ciel : sans cet appoint, descendre
      // la camera sous le terrain ne montre qu un volume noir.
      const lumSous = new THREE.DirectionalLight(0xdce6f5, 0.35);
      lumSous.position.set(6, profEnterre - 8, 6);
      scene.add(lumSous);
    }""")

remp("camera sous le terrain",
"""    controls.maxPolarAngle = aDuEnterre ? Math.PI * 0.93 : Math.PI / 2.1;""",
"""    controls.maxPolarAngle = aDuEnterre ? Math.PI - 0.06 : Math.PI / 2.1;""")

remp("cible camera avec sous-sol",
"""    if (savedCam) {
      controls.target.copy(savedCam.target);
    } else {
      controls.target.set(0, yCentre, 0);
    }""",
"""    if (savedCam) {
      controls.target.copy(savedCam.target);
    } else {
      // Avec une fouille, le centre d orbite descend d autant : sinon le sous-sol sort du champ
      // par le bas des qu on tourne autour du batiment.
      controls.target.set(0, yCentre + profEnterre / 2, 0);
    }""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
