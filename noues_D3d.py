import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_noues_D3d_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ===== D1 : la greffe prend le MEME decalage perpendiculaire que le pan de l'aile =====
remplacer('''    const dec2 = 0.08;
    const dPiedG = dPied > 0 ? dPied : 0;               // la greffe s'arrete au mur (au-dela : couverture de l'aile)
    const zEG = zE * (dR - dPiedG) / plage;
    const yPiedG = hF - zEG * Math.tan(aRad);''',
'''    // Greffe COPLANAIRE a la couverture de l'aile : meme decalage perpendiculaire que le pan trad
    const [arB3, arH3] = sec("Arbaletrier", 0.16, 0.16);
    const [pnB3, pnH3] = sec("Panne", 0.12, 0.12);
    const [chB3, chH3] = sec("Chevron", 0.07, 0.07);
    const cosA3 = Math.cos(aRad), sinA3 = Math.sin(aRad);
    const dPerp3 = arH3/2 + (pnH3 + 0.03) * cosA3 + chH3 + 0.01;
    const hcr3 = dPerp3 / cosA3;                        // remontee au faitage : ferme le joint central
    const dPiedG = dPied > 0 ? dPied : 0;               // la greffe demarre au mur (avant : couverture de l'aile)
    const zEG = zE * (dR - dPiedG) / plage;
    const yPiedG = hF - zEG * Math.tan(aRad);''', "D1")

# ===== D2 : sommets de la greffe releves dans le plan de la couverture =====
remplacer('''      const pts = [
        xw, hF + dec2, 0,
        xw + s * dR, hF + dec2, 0,
        xw + s * dPiedG, yPiedG + dec2, sz * zEG,
        xw, hF + dec2, 0,
        xw + s * dPiedG, yPiedG + dec2, sz * zEG,
        xw, yPiedG + dec2, sz * zEG,
      ];''',
'''      const pts = [
        xw, hF + hcr3, 0,
        xw + s * dR, hF + hcr3, 0,
        xw + s * dPiedG, yPiedG + dPerp3 * cosA3, sz * (zEG + dPerp3 * sinA3),
        xw, hF + hcr3, 0,
        xw + s * dPiedG, yPiedG + dPerp3 * cosA3, sz * (zEG + dPerp3 * sinA3),
        xw, yPiedG + dPerp3 * cosA3, sz * (zEG + dPerp3 * sinA3),
      ];''', "D2")

# ===== D3 : le pan de l'aile s'arrete PILE au mur de contact (plus de levre de 30 cm) =====
remplacer('''    const debCX = (debD - debG) / 2;                      // recentrage X des pieces filantes''',
'''    const debCX = (debD - debG) / 2;                      // recentrage X des pieces filantes
    const rivG = smf === "pignon_gauche" ? 0 : 0.3;       // petit debord de rive de base, sauf cote contact
    const rivD = smf === "pignon_droit" ? 0 : 0.3;''', "D3")

remplacer('''    const rg = new THREE.PlaneGeometry(L + 0.6 + debLX, plCouv);''',
'''    const rg = new THREE.PlaneGeometry(L + rivG + rivD + debLX, plCouv);''', "D4")

remplacer('''    r1.position.set(debCX, yR, zR);''',
'''    r1.position.set(debCX + (rivD - rivG) / 2, yR, zR);''', "D5")

remplacer('''    r2.position.set(debCX, yR, -zR);''',
'''    r2.position.set(debCX + (rivD - rivG) / 2, yR, -zR);''', "D6")

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : greffe coplanaire au pan de l aile, pan arrete au mur -> toiture continue jusqu a la noue.")
