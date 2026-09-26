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

remp("sabliere et faitiere porteuses",
"""setPiece("Sabliere");
    // ===== SABLIERES (poutres basses sur les murs longs) =====
    const [sbB, sbH] = sec("Sabliere", 0.14, 0.14);
    addBox(L + 0.3, sbH, sbB, 0, Ht, lg/2, woodMat);
    addBox(L + 0.3, sbH, sbB, 0, Ht, -lg/2, woodMat);

setPiece("Panne faitiere");
    // ===== PANNE FAITIERE =====
    const [pfB, pfH] = sec("Panne faitiere", 0.14, 0.14);
    addBox(L + 0.4 + debLX, pfH, pfB, debCX, yFait, 0, woodMat);""",
"""setPiece("Sabliere");
    // ===== SABLIERES = PANNES BASSES =====
    // Elles etaient centrees sur l axe des arbaletriers, donc noyees dedans et ne portaient rien.
    // Regle unique pour les trois niveaux de pannes : le DESSUS est dans le plan du rampant
    // (sous-face des chevrons), l extrados des arbaletriers etant a arH/2 perpendiculaire de leur axe.
    const [sbB, sbH] = sec("Sabliere", 0.14, 0.14);
    const [arBr, arHr] = sec("Arbaletrier", 0.16, 0.16);
    const cosR = Math.cos(ang), tanR = Math.tan(ang);
    const yPlanRampant = Ht + (arHr / 2) / cosR;              // plan des chevrons a l aplomb du mur
    const ySabl = yPlanRampant + (sbB / 2) * tanR - sbH / 2;  // coin amont de la sabliere sur ce plan
    addBox(L + 0.3, sbH, sbB, 0, ySabl, lg/2, woodMat);
    addBox(L + 0.3, sbH, sbB, 0, ySabl, -lg/2, woodMat);

setPiece("Panne faitiere");
    // ===== PANNE FAITIERE : posee sur les poincons, son dessus a l arete du toit =====
    const [pfB, pfH] = sec("Panne faitiere", 0.14, 0.14);
    const yFaitPanne = yFait + (arHr / 2) / cosR - pfH / 2;
    addBox(L + 0.4 + debLX, pfH, pfB, debCX, yFaitPanne, 0, woodMat);
    console.log("[DEVIA] Pannes : sabliere a " + ySabl.toFixed(3) + " m, faitiere a " + yFaitPanne.toFixed(3) + " m (dessus dans le plan du rampant)");""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
