import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

ANIM_PLUIE = '''      if (pluiePts) {
        if (pluieToitMats === null) {
          pluieToitMats = [];
          const dejaVu = new Set();
          scene.traverse((o) => {
            if (o.isMesh && o.material && o.material.userData && o.material.userData.estCouverture === true) {
              if (dejaVu.has(o.material.uuid) === false) {
                dejaVu.add(o.material.uuid);
                pluieToitMats.push({ mat: o.material, base: o.material.color.clone() });
              }
            }
          });
          t0Pluie = performance.now();
        }
        const tHum = Math.max(0, Math.min(1, (performance.now() - t0Pluie - 10000) / 4000));
        pluieToitMats.forEach((eT) => { eT.mat.color.copy(eT.base).multiplyScalar(1 - 0.45 * tHum); });
        const arrP = pluiePts.geometry.attributes.position;'''

REMPL = [
    # 1. Variables du chrono pluie
    ("let pluiePts = null;",
     "let pluiePts = null;\n    let pluieToitMats = null;\n    let t0Pluie = 0;"),
    # 2. Boucle d'animation : assombrissement apres 10 s
    ("      if (pluiePts) {\n        const arrP = pluiePts.geometry.attributes.position;", ANIM_PLUIE),
    # 3. Marquage du materiau couverture (vue technique)
    ('''      return new THREE.MeshStandardMaterial({
        color: couv.couleur, roughness: 0.8, metalness: 0.0, transparent: true, opacity: 0.4, side: THREE.DoubleSide
      });''',
     '''      const mTech = new THREE.MeshStandardMaterial({
        color: couv.couleur, roughness: 0.8, metalness: 0.0, transparent: true, opacity: 0.4, side: THREE.DoubleSide
      });
      mTech.userData.estCouverture = true;
      return mTech;'''),
    # 4. Marquage du materiau couverture (vue realiste)
    ("const mat = new THREE.MeshStandardMaterial({ map: ptex, roughness: 0.75, metalness: 0.05, side: THREE.DoubleSide });",
     "const mat = new THREE.MeshStandardMaterial({ map: ptex, roughness: 0.75, metalness: 0.05, side: THREE.DoubleSide });\n    mat.userData.estCouverture = true;"),
    # 5. Marquage du materiau couverture generique
    ("const roofMat = new THREE.MeshStandardMaterial({ color: roofColor, roughness: 0.75, metalness: 0.05, side: THREE.DoubleSide });",
     "const roofMat = new THREE.MeshStandardMaterial({ color: roofColor, roughness: 0.75, metalness: 0.05, side: THREE.DoubleSide });\n  roofMat.userData.estCouverture = true;"),
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

shutil.copy(CHEMIN, CHEMIN + ".backup_pluie_toit_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : la pluie mouille la toiture apres 10 s")
