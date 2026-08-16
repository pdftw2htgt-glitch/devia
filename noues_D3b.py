import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_noues_D3b_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ===== T1 : declencheur modernise (facades cardinales + faitages croises) + debord de la ref =====
remplacer('''          // Penetration de toiture : aile perpendiculaire plus basse contre un gouttereau -> noues
          const coteG = o.pos.cote === "gouttereau_avant" || o.pos.cote === "gouttereau_arriere";
          if (extraMur && coteG && o.pos.faitage === "perpendiculaire" && AVEC_MURS.includes(o.type_projet) && AVEC_MURS.includes(ref.type_projet || "")) {
            const fAile = (o.hauteur || 3) + ((o.largeur || 6) / 2) * Math.tan(((o.pente || 35) * Math.PI) / 180);
            const fRef = (ref.hauteur || 3) + ((ref.largeur || 6) / 2) * Math.tan(((ref.pente || 35) * Math.PI) / 180);
            if (fAile < fRef) {
              extraMur.penetration = { hEgoutRef: ref.hauteur || 3, penteRef: ref.pente || 35 };
            }
          }''',
'''          // Penetration de toiture : aile perpendiculaire plus basse contre un GOUTTEREAU de la reference -> noues
          const refFC = ref.faitageCardinal || "";
          const oFC = o.faitageCardinal || "";
          const fcPen = o.pos.facade || "";
          const contactGoutt = (refFC === "nord_sud" && (fcPen === "est" || fcPen === "ouest"))
            || (refFC === "est_ouest" && (fcPen === "sud" || fcPen === "nord"))
            || (fcPen === "" && (o.pos.cote === "gouttereau_avant" || o.pos.cote === "gouttereau_arriere"));
          const perpFaitages = (refFC === "nord_sud" && oFC === "est_ouest")
            || (refFC === "est_ouest" && oFC === "nord_sud")
            || ((refFC === "" || oFC === "") && o.pos.faitage === "perpendiculaire");
          if (extraMur && contactGoutt && perpFaitages && AVEC_MURS.includes(o.type_projet) && AVEC_MURS.includes(ref.type_projet || "")) {
            const fAile = (o.hauteur || 3) + ((o.largeur || 6) / 2) * Math.tan(((o.pente || 35) * Math.PI) / 180);
            const fRef = (ref.hauteur || 3) + ((ref.largeur || 6) / 2) * Math.tan(((ref.pente || 35) * Math.PI) / 180);
            if (fAile < fRef) {
              extraMur.penetration = { hEgoutRef: ref.hauteur || 3, penteRef: ref.pente || 35, debordRef: ref.debord || 0 };
            }
          }''', "T1")

# ===== R1 : pied de noue etendu jusqu'au bord des debords =====
remplacer('''    const dR = (hF - hE) / Math.tan(pRad);
    const xw = s * L / 2;
    const zBrut = (hF - hE) / Math.tan(aRad);
    const zE = zBrut > lg / 2 ? lg / 2 : zBrut;
    const yPied = hF - zE * Math.tan(aRad);
    const dPied = (yPied - hE) / Math.tan(pRad);''',
'''    const dR = (hF - hE) / Math.tan(pRad);
    const xw = s * L / 2;
    const refDeb = pen.debordRef || 0;
    // La noue court jusqu'au bord du DEBORD de la reference, ou jusqu'a l'egout de l'aile (debord compris)
    const zParRef = (hF - hE + refDeb * Math.tan(pRad)) / Math.tan(aRad);
    const zParAile = lg / 2 + debord;
    const zE = zParRef > zParAile ? zParAile : zParRef;
    const yPied = hF - zE * Math.tan(aRad);
    const dPied = (yPied - hE) / Math.tan(pRad);   // negatif = au-dela du mur, au-dessus du toit de l'aile''', "R1")

# ===== R2 : empannons seulement entre le MUR et le faitage (avant le mur : chevrons de l'aile) =====
remplacer('''    const esp = (couvPen && couvPen.espChevron) ? couvPen.espChevron : 0.5;
    const plage = (dR - dPied) > 0.01 ? (dR - dPied) : 0.01;
    setPiece("Chevron");
    const nEmp = Math.max(1, Math.floor(dR / esp));
    for (let ie = 1; ie <= nEmp; ie++) {
      const dE2 = dPied + (ie / (nEmp + 1)) * plage;
      const zN = zE * (dR - dE2) / plage;''',
'''    const esp = (couvPen && couvPen.espChevron) ? couvPen.espChevron : 0.5;
    const plage = (dR - dPied) > 0.01 ? (dR - dPied) : 0.01;
    const dEmp0 = dPied > 0 ? dPied : 0;
    const plageEmp = (dR - dEmp0) > 0.01 ? (dR - dEmp0) : 0.01;
    setPiece("Chevron");
    const nEmp = Math.max(1, Math.floor(plageEmp / esp));
    for (let ie = 1; ie <= nEmp; ie++) {
      const dE2 = dEmp0 + (ie / (nEmp + 1)) * plageEmp;
      const zN = zE * (dR - dE2) / plage;''', "R2")

# ===== R3 : greffe de couverture clampee au mur =====
remplacer('''    const dec2 = 0.08;''',
'''    const dec2 = 0.08;
    const dPiedG = dPied > 0 ? dPied : 0;               // la greffe s'arrete au mur (au-dela : couverture de l'aile)
    const zEG = zE * (dR - dPiedG) / plage;
    const yPiedG = hF - zEG * Math.tan(aRad);''', "R3a")

remplacer('''      const pts = [
        xw, hF + dec2, 0,
        xw + s * dR, hF + dec2, 0,
        xw + s * dPied, yPied + dec2, sz * zE,
        xw, hF + dec2, 0,
        xw + s * dPied, yPied + dec2, sz * zE,
        xw, yPied + dec2, sz * zE,
      ];''',
'''      const pts = [
        xw, hF + dec2, 0,
        xw + s * dR, hF + dec2, 0,
        xw + s * dPiedG, yPiedG + dec2, sz * zEG,
        xw, hF + dec2, 0,
        xw + s * dPiedG, yPiedG + dec2, sz * zEG,
        xw, yPiedG + dec2, sz * zEG,
      ];''', "R3b")

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : noues traversantes (jusqu au bord des debords), empannons du mur au faitage, greffe clampee au mur.")
