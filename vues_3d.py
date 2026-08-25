import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

BLOC_VUES = '''    // ===== VUE ECLATEE / RANGEE AU SOL =====
    const vueMode = params.vue3D || "assemble";
    if (vueMode === "explose") {
      const meshesE = [];
      scene.traverse((o) => { if (o.isMesh) meshesE.push(o); });
      if (meshesE.length > 0) {
        const bbAll = new THREE.Box3();
        meshesE.forEach((m) => { bbAll.expandByObject(m); });
        const centreE = bbAll.getCenter(new THREE.Vector3());
        centreE.y = 0; // on ecarte vers le haut et les cotes, jamais sous le sol
        const K = 0.5; // intensite de l'eclatement
        meshesE.forEach((m) => {
          const bbM = new THREE.Box3().setFromObject(m);
          const cM = bbM.getCenter(new THREE.Vector3());
          const dW = cM.clone().sub(centreE).multiplyScalar(K);
          const pW = m.getWorldPosition(new THREE.Vector3());
          const cible = pW.add(dW);
          if (m.parent) m.position.copy(m.parent.worldToLocal(cible));
        });
      }
    }
    if (vueMode === "sol" && metreVue && metreVue.length > 0) {
      const aVirer = [];
      scene.traverse((o) => { if (o.isMesh) aVirer.push(o); });
      aVirer.forEach((o) => { if (o.parent) o.parent.remove(o); if (o.geometry) o.geometry.dispose(); });
      const matSol = new THREE.MeshStandardMaterial({ color: 0xc9a06a, roughness: 0.85, metalness: 0.0 });
      const parNom = {};
      metreVue.forEach((p) => {
        const nomP = p.nom || "Piece";
        if (parNom[nomP] === undefined) parNom[nomP] = [];
        parNom[nomP].push(p);
      });
      let zCur = 0;
      let xMax = 0;
      Object.keys(parNom).forEach((nomP) => {
        parNom[nomP].forEach((p) => {
          const Lp = Math.max(0.1, p.longueur || 1);
          const bM = ((p.section && p.section[0]) || 100) / 1000;
          const hM = ((p.section && p.section[1]) || 100) / 1000;
          const ep = Math.min(bM, hM);
          const larg = Math.max(bM, hM);
          const meshP = new THREE.Mesh(new THREE.BoxGeometry(Lp, ep, larg), matSol);
          meshP.position.set(Lp / 2, ep / 2 + 0.001, zCur + larg / 2);
          meshP.castShadow = true;
          scene.add(meshP);
          zCur += larg + 0.12;
          if (Lp > xMax) xMax = Lp;
        });
        zCur += 0.5; // espace entre familles de pieces
      });
      const dxS = xMax / 2;
      const dzS = zCur / 2;
      scene.traverse((o) => { if (o.isMesh) { o.position.x -= dxS; o.position.z -= dzS; } });
    }

    const H = params.hauteur || 3;
    const lg = params.largeur || 6;'''

SELECT_NORMAL = '''<option value="nuit">Nuit</option>
                  </select>
                  <select value={vue3D} onChange={e => setVue3D(e.target.value)}
                    style={{ padding: "7px 12px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                      border: "1px solid rgba(255,255,255,0.08)", background: "#181a26", color: "#d0d2dc" }}>
                    <option value="assemble">Assemblage</option>
                    <option value="explose">Vue eclatee</option>
                    <option value="sol">Range au sol</option>
                  </select>'''

SELECT_FS = '''<option value="nuit">Nuit</option>
                      </select>
                      <select value={vue3D} onChange={e => setVue3D(e.target.value)}
                        style={{ padding: "7px 12px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                          border: "1px solid rgba(255,255,255,0.14)", background: "rgba(10,12,18,0.75)", color: "#d0d2dc" }}>
                        <option value="assemble">Assemblage</option>
                        <option value="explose">Vue eclatee</option>
                        <option value="sol">Range au sol</option>
                      </select>'''

REMPL = [
    ('const [fond3D, setFond3D] = useState("noir"); // noir | blanc | soleil | pluie | nuit',
     'const [fond3D, setFond3D] = useState("noir"); // noir | blanc | soleil | pluie | nuit\n  const [vue3D, setVue3D] = useState("assemble"); // assemble | explose | sol'),
    ('size: 0.35, transparent: true, opacity: 0.8 })));\n    }',
     'size: 0.35, transparent: true, opacity: 0.8 })));\n    }\n    let metreVue = null;'),
    ('if (onMetreRef.current && metresAll.length) {',
     'metreVue = metresAll;\n      if (onMetreRef.current && metresAll.length) {'),
    ('if (onMetreRef.current && buildResultViewer.metre) {',
     'metreVue = buildResultViewer.metre;\n      if (onMetreRef.current && buildResultViewer.metre) {'),
    ('    const H = params.hauteur || 3;\n    const lg = params.largeur || 6;', BLOC_VUES),
    ('<option value="nuit">Nuit</option>\n                  </select>', SELECT_NORMAL),
    ('<option value="nuit">Nuit</option>\n                      </select>', SELECT_FS),
    ('fond3D, mode3D, sectionMode,', 'vue3D, fond3D, mode3D, sectionMode,'),
    ('params.mode3D, params.fond3D, params.sectionMode,', 'params.mode3D, params.fond3D, params.vue3D, params.sectionMode,'),
]

ok = True
for a, b in REMPL:
    n = txt.count(a)
    if n != 1:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu 1 :", a[:70].replace(chr(10), " / "))
        ok = False
if ok == False:
    raise SystemExit(1)

for a, b in REMPL:
    txt = txt.replace(a, b)

shutil.copy(CHEMIN, CHEMIN + ".backup_vues3d_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : vues Assemblage / Eclatee / Rangee au sol")
