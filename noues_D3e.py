import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_noues_D3e_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ===== E1 : UV sur la greffe -> motif des tuiles =====
remplacer('''      g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pts), 3));
      g.computeVertexNormals();
      scene.add(new THREE.Mesh(g, matPen));''',
'''      g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pts), 3));
      const uC = dR > 0.01 ? dPiedG / dR : 0;
      g.setAttribute("uv", new THREE.BufferAttribute(new Float32Array([0, 1, 1, 1, uC, 0, 0, 1, uC, 0, 0, 0]), 2));
      g.computeVertexNormals();
      scene.add(new THREE.Mesh(g, matPen));''', "E1")

# ===== E2 : la pre-passe stocke aussi la geometrie de la noue (pour l'encoche du pan) =====
remplacer('''        const liste2 = decoupesParOuvrage.get(refP) || [];
        liste2.push({ face: face2, a: a2, b: b2 });''',
'''        const tanP2 = Math.tan(((refP.pente || 35) * Math.PI) / 180);
        const tanA2 = Math.tan(((oP.pente || 35) * Math.PI) / 180);
        const hE2 = refP.hauteur || 3;
        if (fA2 <= hE2 + 0.05) return;
        const refDeb2 = refP.debord || 0;
        const dR3 = (fA2 - hE2) / tanP2;
        const zPR = (fA2 - hE2 + refDeb2 * tanP2) / tanA2;
        const zPA = (oP.largeur || 6) / 2 + (oP.debord || 0);
        const zN3 = zPR > zPA ? zPA : zPR;
        const yP3 = fA2 - zN3 * tanA2;
        const dP3 = (yP3 - hE2) / tanP2;
        const liste2 = decoupesParOuvrage.get(refP) || [];
        liste2.push({ face: face2, a: a2, b: b2, xApex: (a2 + b2) / 2, dApex: dR3, zNoue: zN3, dPied: dP3 });''', "E2")

# ===== E3 : pans du toit en geometrie sur mesure, avec encoche le long des noues =====
remplacer('''    const tradRoofMat = makeRoofMaterial(couv, L + debLX, plCouv);
    const rg = new THREE.PlaneGeometry(L + rivG + rivD + debLX, plCouv);
    // centre du pan : centre rampant + dPerp perpendiculaire + ext/2 vers le haut + extBas/2 vers le bas
    const yR = Ht + hf/2 + dPerpCouv * cosA + (ext/2) * sinA - (extBas/2) * sinA;
    const zR = lg/4 + dPerpCouv * sinA - (ext/2) * cosA + (extBas/2) * cosA;
    const r1 = new THREE.Mesh(rg, tradRoofMat);
    r1.position.set(debCX + (rivD - rivG) / 2, yR, zR);
    r1.rotation.x = ang - Math.PI/2;
    scene.add(r1);
    const r2 = new THREE.Mesh(rg, tradRoofMat);
    r2.position.set(debCX + (rivD - rivG) / 2, yR, -zR);
    r2.rotation.x = -(ang - Math.PI/2);
    scene.add(r2);''',
'''    const panW = L + rivG + rivD + debLX;
    const panH = plCouv;
    const tradRoofMat = makeRoofMaterial(couv, panW, panH);
    const cXpan = debCX + (rivD - rivG) / 2;
    // centre du pan : centre rampant + dPerp perpendiculaire + ext/2 vers le haut + extBas/2 vers le bas
    const yR = Ht + hf/2 + dPerpCouv * cosA + (ext/2) * sinA - (extBas/2) * sinA;
    const zR = lg/4 + dPerpCouv * sinA - (ext/2) * cosA + (extBas/2) * cosA;
    // Pan sur mesure : encoche triangulaire le long des noues au droit d'une aile en penetration
    const construirePan = (signZ) => {
      const faceP = signZ === 1 ? "gouttereau_avant" : "gouttereau_arriere";
      const notches = [];
      const decsP = (opts && opts.decoupesDebord) || null;
      if (decsP) { for (const dd of decsP) { if (dd.face === faceP && typeof dd.xApex === "number") notches.push(dd); } }
      const yDeZ = (zz) => panH/2 - ext - zz / cosA;   // z local du batiment (0 = faitage) -> y dans le plan du pan
      const tris = [];
      const rect = (xa, xb) => { if (xb - xa > 0.001) { tris.push([xa, -panH/2, xb, -panH/2, xb, panH/2], [xa, -panH/2, xb, panH/2, xa, panH/2]); } };
      if (notches.length === 0) { rect(-panW/2, panW/2); }
      else {
        notches.sort((u, v) => u.xApex - v.xApex);
        let curseur = -panW/2;
        for (const nt of notches) {
          const xA = nt.xApex - cXpan;
          let xF1 = nt.xApex - nt.zNoue - cXpan;
          let xF2 = nt.xApex + nt.zNoue - cXpan;
          if (xF1 < -panW/2) xF1 = -panW/2;
          if (xF2 > panW/2) xF2 = panW/2;
          let yA = yDeZ(lg/2 - nt.dApex);
          let yF = yDeZ(lg/2 - nt.dPied);
          if (yF < -panH/2) yF = -panH/2;
          if (yA > panH/2) yA = panH/2;
          rect(curseur, xF1);
          // encoche : deux trapezes de part et d'autre de l'apex
          tris.push([xF1, panH/2, xA, yA, xA, panH/2]);
          tris.push([xF1, panH/2, xF1, yF, xA, yA]);
          tris.push([xA, panH/2, xF2, yF, xF2, panH/2]);
          tris.push([xA, panH/2, xA, yA, xF2, yF]);
          // sous les pieds de noue, le pan continue jusqu'a l'egout
          if (yF > -panH/2 + 0.01) {
            tris.push([xF1, -panH/2, xF2, -panH/2, xF2, yF]);
            tris.push([xF1, -panH/2, xF2, yF, xF1, yF]);
          }
          curseur = xF2;
        }
        rect(curseur, panW/2);
      }
      const pos = [], uv = [];
      for (const t of tris) {
        for (let k = 0; k < 3; k++) {
          const px2 = t[k*2], py2 = t[k*2 + 1];
          pos.push(px2, py2, 0);
          uv.push((px2 + panW/2) / panW, (py2 + panH/2) / panH);
        }
      }
      const g2 = new THREE.BufferGeometry();
      g2.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pos), 3));
      g2.setAttribute("uv", new THREE.BufferAttribute(new Float32Array(uv), 2));
      g2.computeVertexNormals();
      const mP = new THREE.Mesh(g2, tradRoofMat);
      mP.position.set(cXpan, yR, signZ * zR);
      mP.rotation.x = signZ * (ang - Math.PI/2);
      scene.add(mP);
    };
    construirePan(1);
    construirePan(-1);''', "E3")

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : tuiles sur la greffe (UV) + encoche des tuiles le long des noues sur le pan principal.")
