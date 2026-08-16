import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_noues_D3c_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ===== C1 : noue POSEE A PLAT sur le pan de la reference =====
remplacer('''    setPiece("Noue");
    for (const sz of [-1, 1]) {
      addBeam(xw + s * dPied, yPied, sz * zE, xw + s * dR, hF, 0, 0.12, woodMat);
    }''',
'''    setPiece("Noue");
    // Noue posee A PLAT sur le pan de la reference : relevee d'une demi-epaisseur suivant la normale du pan
    const nxN = -s * Math.sin(pRad), nyN = Math.cos(pRad);
    const relN = 0.06;
    for (const sz of [-1, 1]) {
      addBeam(xw + s * dPied + nxN * relN, yPied + nyN * relN, sz * zE, xw + s * dR + nxN * relN, hF + nyN * relN, 0, 0.12, woodMat);
    }''', "C1")

# ===== C2 : la faitiere de l'aile RENTRE dans le pan de la reference =====
remplacer('''    addBox(dR, 0.24, 0.12, xw + s * dR / 2, hF - 0.12, 0, woodMat);''',
'''    addBox(dR + 0.25, 0.24, 0.12, xw + s * (dR + 0.25) / 2, hF - 0.12, 0, woodMat);''', "C2")

# ===== C3 : pre-passe qui calcule la decoupe du debord de la reference au droit de chaque aile =====
remplacer('''      const AVEC_MURS = ["charpente_trad", "monopente", "4_pans"];
      const idxPorteur = params.ouvrages.findIndex(o => AVEC_MURS.includes(o.type_projet));''',
'''      const AVEC_MURS = ["charpente_trad", "monopente", "4_pans"];
      const idxPorteur = params.ouvrages.findIndex(o => AVEC_MURS.includes(o.type_projet));
      // ===== PRE-PASSE NOUES : decoupe du DEBORD de la reference au droit de chaque aile en penetration =====
      const decoupesParOuvrage = new Map();
      params.ouvrages.forEach((oP) => {
        if (oP.pos === undefined || oP.pos === null) return;
        const refP = params.ouvrages[(oP.pos.contre || 1) - 1];
        if (refP === undefined || refP === oP) return;
        const refFC2 = refP.faitageCardinal || "";
        const oFC2 = oP.faitageCardinal || "";
        const fc2 = oP.pos.facade || "";
        const goutt2 = (refFC2 === "nord_sud" && (fc2 === "est" || fc2 === "ouest")) || (refFC2 === "est_ouest" && (fc2 === "sud" || fc2 === "nord"));
        const perp2 = (refFC2 === "nord_sud" && oFC2 === "est_ouest") || (refFC2 === "est_ouest" && oFC2 === "nord_sud");
        if (goutt2 === false || perp2 === false) return;
        if (AVEC_MURS.includes(oP.type_projet) === false || AVEC_MURS.includes(refP.type_projet || "") === false) return;
        const fA2 = (oP.hauteur || 3) + ((oP.largeur || 6) / 2) * Math.tan(((oP.pente || 35) * Math.PI) / 180);
        const fR2 = (refP.hauteur || 3) + ((refP.largeur || 6) / 2) * Math.tan(((refP.pente || 35) * Math.PI) / 180);
        if (fA2 >= fR2) return;
        // Etendues le long du mur de contact (les faitages sont croises : aile = largeur, ref = longueur)
        const aH2 = (oP.largeur || 6) / 2;
        const rH2 = (refP.longueur || 8) / 2;
        const al2 = oP.pos.alignement || "";
        let cAxe = oP.pos.decalage || 0;
        if (fc2 === "est" || fc2 === "ouest") {
          if (al2 === "sud") cAxe = rH2 - aH2;
          else if (al2 === "nord") cAxe = -(rH2 - aH2);
        } else {
          if (al2 === "est") cAxe = rH2 - aH2;
          else if (al2 === "ouest") cAxe = -(rH2 - aH2);
        }
        let m0 = cAxe - aH2, m1 = cAxe + aH2;
        if (m0 < -rH2) m0 = -rH2;
        if (m1 > rH2) m1 = rH2;
        // Axe monde -> X local de la reference (nord_sud : x local = -z monde)
        const qR2 = refFC2 === "nord_sud" ? 1 : 0;
        const a2 = qR2 === 1 ? -m1 : m0;
        const b2 = qR2 === 1 ? -m0 : m1;
        const face2 = qR2 === 1 ? (fc2 === "est" ? "gouttereau_avant" : "gouttereau_arriere") : (fc2 === "sud" ? "gouttereau_avant" : "gouttereau_arriere");
        const liste2 = decoupesParOuvrage.get(refP) || [];
        liste2.push({ face: face2, a: a2, b: b2 });
        decoupesParOuvrage.set(refP, liste2);
        console.log("[DEVIA] Decoupe debord : " + face2 + " de x=" + a2.toFixed(2) + " a x=" + b2.toFixed(2) + " (penetration aile)");
      });''', "C3")

# ===== C4 : la decoupe est transmise au build de la reference =====
remplacer('''        const res = buildScene3D(grp, oParams, {
          couverture: oParams.couverture, mode: params.mode3D,
          sections: secs, sectionMode: params.sectionMode || "conseillee",
          ...(extraOpts || {}),
        });''',
'''        const res = buildScene3D(grp, oParams, {
          couverture: oParams.couverture, mode: params.mode3D,
          sections: secs, sectionMode: params.sectionMode || "conseillee",
          decoupesDebord: decoupesParOuvrage.get(o) || null,
          ...(extraOpts || {}),
        });''', "C4")

# ===== C5 : chevrons du ref sans depasse sur le segment decoupe =====
remplacer('''      const zE = lg/2 + debord;                     // egout (aplomb du mur + depasse)''',
'''      let debZ = debord;
      const decsCh = (opts && opts.decoupesDebord) || null;
      if (decsCh) {
        const faceCh = signZ === 1 ? "gouttereau_avant" : "gouttereau_arriere";
        for (const dd of decsCh) { if (dd.face === faceCh && x >= dd.a && x <= dd.b) debZ = 0; }
      }
      const zE = lg/2 + debZ;                       // egout (aplomb du mur + depasse, coupe au droit d'une aile)''', "C5")

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : noue posee sur le pan, faitiere qui rentre dedans, debord du principal coupe au droit de l aile.")
