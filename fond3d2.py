import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

BLOC_AMBIANCE = '''sun.shadow.bias = -0.0005;
    scene.add(sun);

    // ===== FOND / AMBIANCE 3D =====
    const AMBIANCES = {
      noir:  { ciel: 0x000000, ambI: 0.45, sunI: 1.2,  sunC: 0xfff8e7 },
      blanc: { ciel: 0xf2f4f8, ambI: 0.6,  sunI: 1.1,  sunC: 0xffffff },
      soleil: { ciel: 0x8ec8ee, ambI: 0.6, sunI: 1.65, sunC: 0xfff2c8 },
      pluie: { ciel: 0x77828e, ambI: 0.55, sunI: 0.4,  sunC: 0xdde5ee, pluie: true },
      nuit:  { ciel: 0x070d1e, ambI: 0.16, sunI: 0.3,  sunC: 0xb8ccff, etoiles: true },
    };
    const amb3D = AMBIANCES[params.fond3D] || AMBIANCES.noir;
    scene.background = new THREE.Color(amb3D.ciel);
    lumAmb.intensity = amb3D.ambI;
    sun.intensity = amb3D.sunI;
    sun.color.set(amb3D.sunC);
    let pluiePts = null;
    if (amb3D.pluie) {
      const nG = 1400;
      const posG = new Float32Array(nG * 3);
      for (let iG = 0; iG < nG; iG++) {
        posG[iG * 3] = (Math.random() - 0.5) * 50;
        posG[iG * 3 + 1] = Math.random() * 30;
        posG[iG * 3 + 2] = (Math.random() - 0.5) * 50;
      }
      const geoP = new THREE.BufferGeometry();
      geoP.setAttribute("position", new THREE.BufferAttribute(posG, 3));
      pluiePts = new THREE.Points(geoP, new THREE.PointsMaterial({ color: 0xaec6dd, size: 0.09, transparent: true, opacity: 0.55 }));
      scene.add(pluiePts);
    }
    if (amb3D.etoiles) {
      const nE = 450;
      const posE = new Float32Array(nE * 3);
      for (let iE = 0; iE < nE; iE++) {
        const th = Math.random() * Math.PI * 2;
        const ph = Math.random() * Math.PI * 0.48;
        posE[iE * 3] = 90 * Math.sin(ph) * Math.cos(th);
        posE[iE * 3 + 1] = 90 * Math.cos(ph) + 2;
        posE[iE * 3 + 2] = 90 * Math.sin(ph) * Math.sin(th);
      }
      const geoE = new THREE.BufferGeometry();
      geoE.setAttribute("position", new THREE.BufferAttribute(posE, 3));
      scene.add(new THREE.Points(geoE, new THREE.PointsMaterial({ color: 0xdfe8ff, size: 0.35, transparent: true, opacity: 0.8 })));
    }'''

BLOC_PLUIE_ANIM = '''      if (pluiePts) {
        const arrP = pluiePts.geometry.attributes.position;
        for (let iG = 0; iG < arrP.count; iG++) {
          let yP = arrP.getY(iG) - 0.35;
          if (yP < 0) yP = 30;
          arrP.setY(iG, yP);
        }
        arrP.needsUpdate = true;
      }
      renderer.render(scene, camera);'''

SELECT_UI = '''
                  <select value={fond3D} onChange={e => setFond3D(e.target.value)}
                    style={{ padding: "7px 12px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                      border: "1px solid rgba(255,255,255,0.08)", background: "#181a26", color: "#d0d2dc" }}>
                    <option value="noir">Fond noir</option>
                    <option value="blanc">Fond blanc</option>
                    <option value="soleil">Ensoleille</option>
                    <option value="pluie">Pluie</option>
                    <option value="nuit">Nuit</option>
                  </select>'''

REMPL = [
    ('const [mode3D, setMode3D] = useState("technique"); // "technique" | "realiste"',
     'const [mode3D, setMode3D] = useState("technique"); // "technique" | "realiste"\n  const [fond3D, setFond3D] = useState("noir"); // noir | blanc | soleil | pluie | nuit'),
    ('scene.add(new THREE.AmbientLight(0xffffff, 0.45));',
     'const lumAmb = new THREE.AmbientLight(0xffffff, 0.45);\n    scene.add(lumAmb);'),
    ('sun.shadow.bias = -0.0005;\n    scene.add(sun);', BLOC_AMBIANCE),
    ('      renderer.render(scene, camera);', BLOC_PLUIE_ANIM),
    ('mode3D, sectionMode, sk: zoneInfo ? zoneInfo.sk : 0.45, dS: zoneInfo ? zoneInfo.dS : 0 }}',
     'fond3D, mode3D, sectionMode, sk: zoneInfo ? zoneInfo.sk : 0.45, dS: zoneInfo ? zoneInfo.dS : 0 }}'),
    ('params.mode3D, params.sectionMode,',
     'params.mode3D, params.fond3D, params.sectionMode,'),
]

M_UI = '{ id: "technique", label: "Vue technique" }, { id: "realiste", label: "Vue realiste" }'
FIN_MAP = "))}"

ok = True
for a, b in REMPL:
    n = txt.count(a)
    if n != 1:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu 1 :", a[:70].replace(chr(10), " / "))
        ok = False
if txt.count(M_UI) != 1:
    print("ABANDON : rangee Vue technique/realiste en", txt.count(M_UI), "exemplaire(s)")
    ok = False
if ok == False:
    raise SystemExit(1)

for a, b in REMPL:
    txt = txt.replace(a, b)

iUI = txt.find(M_UI)
jFin = txt.find(FIN_MAP, iUI)
if jFin < 0:
    print("ABANDON : fin de rangee introuvable apres la rangee de boutons")
    raise SystemExit(1)
jFin = jFin + len(FIN_MAP)
txt = txt[:jFin] + SELECT_UI + txt[jFin:]

shutil.copy(CHEMIN, CHEMIN + ".backup_fond3d_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : fond 3D noir / blanc / ensoleille / pluie / nuit")
