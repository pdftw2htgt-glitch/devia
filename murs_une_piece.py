import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

def bloc(nom, deb, fin, nouveau):
    # Remplace tout ce qui va de l ancre de debut (incluse) a l ancre de fin (exclue).
    global src
    nd, nf = src.count(deb), src.count(fin)
    if nd != 1 or nf != 1:
        print("ABANDON " + nom + " : ancre debut x" + str(nd) + ", ancre fin x" + str(nf))
        sys.exit(1)
    i = src.index(deb)
    j = src.index(fin)
    if j <= i:
        print("ABANDON " + nom + " : ancre de fin avant l ancre de debut")
        sys.exit(1)
    src = src[:i] + nouveau + src[j:]
    print("OK " + nom)

# ============================================================
# 1) HELPER MUR EN UNE PIECE + PIGNON DU SOL AU RAMPANT
# ============================================================
bloc("mur perce en une piece",
"  const drawPignonBeton = (xPos, lgb, Hb, htTri, ep, reservations) => {",
"  const drawMursBeton = (Lb, lgb, Hb, reservations) => {",
"""  // ===== MUR BETON D UNE SEULE PIECE =====
  // Un mur n est pas une pile de trumeaux, d alleges et d impostes : c est UNE piece percee.
  // Le decouper en boites le livrait en six a huit morceaux dans le logiciel du charpentier.
  // axe "z" : mur gouttereau (contour dans le plan XY, epaisseur selon Z)
  // axe "x" : mur de pignon (contour tourne d un quart de tour, epaisseur selon X)
  // ATTENTION : pos enregistre l ORIGINE du contour (son point 0,0), pas le centre de la
  // piece - c est ce que le placement IFC attend pour poser le profil au bon endroit.
  const drawMurPerce = (axe, posFixe, contour, trous, ep, nom) => {
    const shp = new THREE.Shape();
    shp.moveTo(contour[0][0], contour[0][1]);
    for (let i = 1; i < contour.length; i++) shp.lineTo(contour[i][0], contour[i][1]);
    shp.closePath();
    const trousOk = [];
    (trous || []).forEach((t) => {
      if (Array.isArray(t) === false || t.length < 3) return;
      const h = new THREE.Path();
      h.moveTo(t[0][0], t[0][1]);
      for (let i = 1; i < t.length; i++) h.lineTo(t[i][0], t[i][1]);
      h.closePath();
      shp.holes.push(h);
      trousOk.push(t);
    });
    const geo = new THREE.ExtrudeGeometry(shp, { depth: ep, bevelEnabled: false });
    const m = new THREE.Mesh(geo, betonMat);
    if (axe === "x") { m.rotation.y = Math.PI / 2; m.position.set(posFixe - ep / 2, 0, 0); }
    else { m.position.set(0, 0, posFixe - ep / 2); }
    m.castShadow = true;
    m.receiveShadow = true;
    scene.add(m);
    // Volume NET : aire du contour moins celle des baies (formule du lacet)
    const aire = (pts) => {
      let s = 0;
      for (let i = 0; i < pts.length; i++) {
        const a = pts[i], b = pts[(i + 1) % pts.length];
        s += a[0] * b[1] - b[0] * a[1];
      }
      return Math.abs(s) / 2;
    };
    let surf = aire(contour);
    trousOk.forEach((t) => { surf -= aire(t); });
    let xm = contour[0][0], xM = contour[0][0], ym = contour[0][1], yM = contour[0][1];
    contour.forEach((q) => {
      if (q[0] < xm) xm = q[0];
      if (q[0] > xM) xM = q[0];
      if (q[1] < ym) ym = q[1];
      if (q[1] > yM) yM = q[1];
    });
    const lgC = xM - xm, htC = yM - ym;
    metre.push({
      matiere: "beton",
      nom: nom || "Mur beton",
      section: [Math.round(ep * 1000), Math.round(htC * 1000)],
      longueur: lgC,
      volume: Math.max(0, surf) * ep,
      dimsBrutes: (axe === "x") ? [ep, htC, lgC] : [lgC, htC, ep],
      murP: { contour: contour, trous: trousOk, ep: ep, axe: axe },
      pos: (axe === "x") ? [posFixe, 0, 0] : [0, 0, posFixe],
      rot: null,
      quat: null,
    });
    console.log("[DEVIA] " + (nom || "Mur beton") + " en UNE piece : " + lgC.toFixed(2) + " x " + htC.toFixed(2) + " m, " + trousOk.length + " baie(s), " + (Math.max(0, surf) * ep).toFixed(2) + " m3 net");
  };

  // ===== MUR DE PIGNON : UNE piece, du sol jusqu au rampant =====
  // htTri a 0 (toit sans rampant de pignon, comme un 4 pans) arrete le mur a l horizontale.
  const drawPignonBeton = (xPos, lgb, Hb, htTri, ep, reservations, avecPorte) => {
    // Le macon ne laisse pas un trou ferme autour d une panne : il descend le mur sous elle.
    // Chaque panne donne donc une ENCOCHE ouverte par le haut, ou la panne vient se poser.
    const res = (reservations || [])
      .map((r) => ({
        x0: r.z - (r.b / 2 + 0.035),        // 3,5 cm de part et d autre : la reservation se voit
        x1: r.z + (r.b / 2 + 0.035),
        yb: r.y - r.h / 2 - 0.035,          // et elle descend sous la panne
        yhNet: r.y + r.h / 2,               // dessus exact : c est la sous-face des chevrons
      }))
      .filter((e) => e.x1 > -lgb / 2 + 0.02 && e.x0 < lgb / 2 - 0.02)
      .sort((a, b) => a.x0 - b.x0);
    // Le pignon monte jusqu au dessus des pannes, JAMAIS plus haut : au-dela il entrerait
    // dans les chevrons (le dessus de la panne la plus haute EST leur sous-face).
    let ySommet = Hb + htTri;
    res.forEach((e) => { if (e.yhNet > ySommet) ySommet = e.yhNet; });
    const JEU_CHEVRON = (htTri > 0.01) ? 0.004 : 0;  // au ras du bois entre deux reservations
    // Le haut du mur suit le rampant : meme PENTE que le toit (htTri sur la demi-largeur).
    // Une droite partant de zero au bord se rapprocherait du rampant en montant et viendrait
    // se coller a l arbaletrier au faitage.
    const hMur = (x) => Math.max(Hb * 0.5, ySommet - (Math.abs(x) / (lgb / 2)) * htTri - JEU_CHEVRON);
    const haut = [[-lgb / 2, hMur(-lgb / 2)]];
    let dernierX = -lgb / 2;
    let sommetPose = false;
    let nbEnc = 0;
    res.forEach((e) => {
      const a = Math.max(e.x0, -lgb / 2 + 0.02);
      const b = Math.min(e.x1, lgb / 2 - 0.02);
      if (b <= a || a < dernierX) return;               // encoches jointives : on garde la premiere
      if (a > 0 && dernierX < 0 && sommetPose === false) { haut.push([0, hMur(0)]); sommetPose = true; }
      if (a < 0 && b > 0) sommetPose = true;            // l encoche emporte le faitage
      const fond = Math.max(Hb * 0.5, Math.min(e.yb, Math.min(hMur(a), hMur(b)) - 0.01));
      haut.push([a, hMur(a)]);
      haut.push([a, fond]);
      haut.push([b, fond]);
      haut.push([b, hMur(b)]);
      dernierX = b;
      nbEnc += 1;
    });
    if (sommetPose === false) haut.push([0, hMur(0)]);
    haut.push([lgb / 2, hMur(lgb / 2)]);
    // Contour complet : la base au sol, puis le haut parcouru de droite a gauche
    const cont = [[-lgb / 2, 0], [lgb / 2, 0]];
    for (let i = haut.length - 1; i >= 0; i--) {
      const px = haut[i][0], py = haut[i][1];
      const prec = cont[cont.length - 1];
      if (Math.abs(px - prec[0]) > 0.0002 || Math.abs(py - prec[1]) > 0.0002) cont.push([px, py]);
    }
    // Porte du pignon avant : un VRAI percement dans la piece, avec un seuil de 5 cm
    // (un trou qui touche le bord bas ne serait plus un trou mais une echancrure).
    const trous = [];
    const phP = Math.min(2.1, Hb - 0.2);
    if (avecPorte === true && lgb > 1.6 && phP > 0.5) {
      const pw = 0.9;
      trous.push([[-pw / 2, 0.05], [pw / 2, 0.05], [pw / 2, phP], [-pw / 2, phP]]);
    }
    console.log("[DEVIA] Pignon : " + nbEnc + " encoche(s) de panne, sommet a " + ySommet.toFixed(2) + " m");
    drawMurPerce("x", xPos, cont, trous, ep, "Mur pignon beton");
  };

""")

# ============================================================
# 2) GOUTTEREAUX ET PIGNONS : UN APPEL PAR FACE
# ============================================================
bloc("gouttereaux et pignons en une piece",
"    // --- Bande de mur gouttereau (a z fixe, de yBase a yBase+hBande) avec ouvertures [{cx,w,y0,y1}] ---",
"    // --- PLANCHERS INTERMEDIAIRES (un par etage) ---",
"""    // --- GOUTTEREAUX : un mur = UNE piece, les baies de TOUS les niveaux en percements ---
    const baiesAv = [];
    const baiesAr = [];
    for (let k = 0; k < nbNiveaux; k++) {
      const yBase = k * hEtage;
      const y0F = yBase + 1.0, y1F = yBase + Math.min(2.0, hEtage - 0.3);
      baiesAv.push({ cx: -Lb / 4, w: 1.2, y0: y0F, y1: y1F });
      baiesAv.push({ cx: Lb / 4, w: 1.2, y0: y0F, y1: y1F });
      baiesAr.push({ cx: 0, w: 1.2, y0: y0F, y1: y1F });
    }
    if (pfB) {
      // Porte-fenetre de balcon : elle remplace les fenetres qu elle recouvre
      const pf = { cx: pfB.cx || 0, w: pfB.w || 1.4, y0: pfB.yPlancher + 0.05, y1: pfB.yPlancher + 2.1 };
      const gardees = baiesAv.filter((f) => Math.abs(f.cx - pf.cx) > (f.w + pf.w) / 2 + 0.2 || f.y1 < pf.y0 || f.y0 > pf.y1);
      baiesAv.length = 0;
      gardees.forEach((f) => baiesAv.push(f));
      baiesAv.push(pf);
    }
    const rectMur = [[-Lb / 2, 0], [Lb / 2, 0], [Lb / 2, Hb], [-Lb / 2, Hb]];
    const baiesEnTrous = (baies) => baies
      .filter((f) => f.cx - f.w / 2 > -Lb / 2 + 0.3 && f.cx + f.w / 2 < Lb / 2 - 0.3
        && f.y1 - f.y0 > 0.1 && f.y1 < Hb - 0.05 && f.y0 > 0.04)
      .map((f) => [[f.cx - f.w / 2, f.y0], [f.cx + f.w / 2, f.y0], [f.cx + f.w / 2, f.y1], [f.cx - f.w / 2, f.y1]]);
    if ((sansFace === "gouttereau_avant") === false) drawMurPerce("z", lgb / 2, rectMur, baiesEnTrous(baiesAv), ep, "Mur beton");
    if ((sansFace === "gouttereau_arriere") === false) drawMurPerce("z", -lgb / 2, rectMur, baiesEnTrous(baiesAr), ep, "Mur beton");

    // --- PIGNONS : UNE piece chacun, du sol au rampant, porte percee au pignon avant ---
    const modePignon = (params && params.pignon) || "plein";
    if (modePignon === "aucun") {
      console.log("[DEVIA] Pignons : aucun mur, la ferme reste apparente");
    } else {
      // Un rampant de pignon ne se justifie que sur un toit A DEUX PANS, qui declare ou
      // passent ses pannes. Un toit 4 pans n a pas de pignon du tout : ses quatre cotes
      // descendent en croupe et les murs s arretent a l horizontale.
      const aDesPannes = Array.isArray(reservations) && reservations.length > 0;
      const htTriangle = (lgb / 2) * Math.tan((pente * Math.PI) / 180);
      const triActif = (modePignon === "plein" && aDesPannes && htTriangle > 0.05);
      if (aDesPannes === false) console.log("[DEVIA] Pas de rampant de pignon sur ce toit : murs arretes a l horizontale");
      else if (triActif) console.log("[DEVIA] Pignons maconnes jusqu aux rampants (triangle " + htTriangle.toFixed(2) + " m)");
      else console.log("[DEVIA] Pignons arretes a la sabliere");
      if ((sansFace === "pignon_droit") === false) {
        drawPignonBeton(Lb / 2, lgb, Hb, triActif ? htTriangle : 0, ep, triActif ? reservations : [], true);
      }
      if ((sansFace === "pignon_gauche") === false) {
        drawPignonBeton(-Lb / 2, lgb, Hb, triActif ? htTriangle : 0, ep, triActif ? reservations : [], false);
      }
    }

""")

# ============================================================
# 3) EXPORT IFC : PROFIL AVEC BAIES PERCEES, POUR MURS ET PIGNONS
# ============================================================
bloc("export IFC des murs perces",
"    // --- Pignon maconne : profil triangulaire reel (pas une boite approchee) ---",
"    // --- Dimensions Three.js d'origine ---",
"""    // --- Element maconne plan : UNE piece, contour reel et baies percees ---
    // murP = { contour, trous, ep, axe } pour les murs et les pignons.
    // tri = ancien format (triangle de pignon seul), garde en repli pour un metre deja en base.
    const planP = p.murP
      ? p.murP
      : ((p.tri && p.tri.b > 0.05 && p.tri.h > 0.05 && p.tri.ep > 0.01)
          ? {
              contour: (Array.isArray(p.tri.contour) && p.tri.contour.length >= 3)
                ? p.tri.contour
                : [[-p.tri.b / 2, 0], [p.tri.b / 2, 0], [0, p.tri.h]],
              trous: [], ep: p.tri.ep, axe: "x",
            }
          : null);
    if (planP && Array.isArray(planP.contour) && planP.contour.length >= 3 && planP.ep > 0.01) {
      const mRT = new THREE.Matrix4();
      if (p.quat) mRT.makeRotationFromQuaternion(new THREE.Quaternion(p.quat[0], p.quat[1], p.quat[2], p.quat[3]));
      else if (p.rot) mRT.makeRotationFromEuler(new THREE.Euler(p.rot[0] || 0, p.rot[1] || 0, p.rot[2] || 0, "XYZ"));
      const eT = mRT.elements;
      const axXl = [eT[0], eT[1], eT[2]];      // X local
      const axZl = [eT[8], eT[9], eT[10]];     // Z local
      // L epaisseur part selon la normale du mur : X local pour un pignon, Z local pour un
      // gouttereau. Le profil garde ainsi le meme repere que la forme dessinee a l ecran.
      const axNormale = (planP.axe === "z") ? axZl : axXl;
      const axProfX = (planP.axe === "z") ? axXl : [-axZl[0], -axZl[1], -axZl[2]];
      const dirT = (v) => {
        const n = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) || 1;
        return "(" + num(v[0] / n, 6) + "," + num(v[1] / n, 6) + "," + num(v[2] / n, 6) + ")";
      };
      const vIfcT = (v) => [v[0], -v[2], v[1]];
      const courbe = (pts) => {
        const idsQ = pts.map((q) => {
          const idq = nextId();
          E(idq, "IFCCARTESIANPOINT((" + num(q[0]) + "," + num(q[1]) + "));");
          return idq;
        });
        const idp = nextId();
        E(idp, "IFCPOLYLINE((#" + idsQ.join(",#") + ",#" + idsQ[0] + "));");
        return idp;
      };
      const polyExt = courbe(planP.contour);
      const trousP = Array.isArray(planP.trous) ? planP.trous.filter((t) => Array.isArray(t) && t.length >= 3) : [];
      const profT = nextId();
      if (trousP.length > 0) {
        const idsIn = trousP.map((t) => courbe(t));
        E(profT, "IFCARBITRARYPROFILEDEFWITHVOIDS(.AREA.,$,#" + polyExt + ",(#" + idsIn.join(",#") + "));");
      } else {
        E(profT, "IFCARBITRARYCLOSEDPROFILEDEF(.AREA.,$,#" + polyExt + ");");
      }
      const posT = nextId(); E(posT, "IFCCARTESIANPOINT((" + num(p.pos[0]) + "," + num(-p.pos[2]) + "," + num(p.pos[1]) + "));");
      const dzT = nextId(); E(dzT, "IFCDIRECTION(" + dirT(vIfcT(axNormale)) + ");");
      const dxT = nextId(); E(dxT, "IFCDIRECTION(" + dirT(vIfcT(axProfX)) + ");");
      const axT = nextId(); E(axT, "IFCAXIS2PLACEMENT3D(#" + posT + ",#" + dzT + ",#" + dxT + ");");
      const plcT = nextId(); E(plcT, "IFCLOCALPLACEMENT(#" + storeyPlc + ",#" + axT + ");");
      const exPtT = nextId(); E(exPtT, "IFCCARTESIANPOINT((0.,0.," + num(-planP.ep / 2) + "));");
      const exAxT = nextId(); E(exAxT, "IFCAXIS2PLACEMENT3D(#" + exPtT + ",$,$);");
      const exDirT = nextId(); E(exDirT, "IFCDIRECTION((0.,0.,1.));");
      const solT = nextId(); E(solT, "IFCEXTRUDEDAREASOLID(#" + profT + ",#" + exAxT + ",#" + exDirT + "," + num(planP.ep) + ");");
      const repT = nextId(); E(repT, "IFCSHAPEREPRESENTATION(#" + bodyCtx + ",'Body','SweptSolid',(#" + solT + "));");
      const pdT = nextId(); E(pdT, "IFCPRODUCTDEFINITIONSHAPE($,$,(#" + repT + "));");
      const clsM = classeDe(p);
      const murT = nextId();
      E(murT, clsM[0] + "('" + guid() + "',#" + owner + ",'" + txt(p.nom || "Mur") + "',$,$,#" + plcT + ",#" + pdT + ",'" + (iP + 1) + "'," + clsM[1] + ");");
      memberIds.push(murT);
      idsBeton.push(murT);
      console.log("[DEVIA] IFC : " + (p.nom || "Mur") + " en une piece, " + planP.contour.length + " points et " + trousP.length + " baie(s) percee(s)");
      return;
    }
""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
