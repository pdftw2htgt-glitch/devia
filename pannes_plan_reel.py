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

remp("plan reel des chevrons",
"""    const [sbB, sbH] = sec("Sabliere", 0.14, 0.14);
    const [arBr, arHr] = sec("Arbaletrier", 0.16, 0.16);
    const cosR = Math.cos(ang), tanR = Math.tan(ang);
    const yPlanRampant = Ht + (arHr / 2) / cosR;              // plan des chevrons a l aplomb du mur
    const ySabl = yPlanRampant + (sbB / 2) * tanR - sbH / 2;  // coin amont de la sabliere sur ce plan
    addBox(L + 0.3, sbH, sbB, 0, ySabl, lg/2, woodMat);
    addBox(L + 0.3, sbH, sbB, 0, ySabl, -lg/2, woodMat);""",
"""    const [sbB, sbH] = sec("Sabliere", 0.14, 0.14);
    const [arBr, arHr] = sec("Arbaletrier", 0.16, 0.16);
    const [pnBr, pnHr] = sec("Panne", 0.12, 0.12);
    const cosR = Math.cos(ang), tanR = Math.tan(ang);
    // Le plan porteur n est PAS l extrados des arbaletriers : les chevrons passent par-dessus les
    // pannes (voir dPerpChevron plus bas). Sabliere et faitiere doivent atteindre CE plan, sinon
    // les chevrons flottent au-dessus d elles.
    const dPerpSousChevron = arHr / 2 + (pnHr + 0.03) * cosR;
    const yPlanRampant = Ht + dPerpSousChevron / cosR;        // sous-face des chevrons a l aplomb du mur
    const ySabl = yPlanRampant + (sbB / 2) * tanR - sbH / 2;  // coin amont de la sabliere sur ce plan
    addBox(L + 0.3, sbH, sbB, 0, ySabl, lg/2, woodMat);
    addBox(L + 0.3, sbH, sbB, 0, ySabl, -lg/2, woodMat);""")

remp("faitiere sur le meme plan",
"""    const yFaitPanne = yFait + (arHr / 2) / cosR - pfH / 2;""",
"""    const yFaitPanne = yFait + dPerpSousChevron / cosR - pfH / 2;""")

remp("trace lisible",
"""    console.log("[DEVIA] Pannes : sabliere a " + ySabl.toFixed(3) + " m, faitiere a " + yFaitPanne.toFixed(3) + " m (dessus dans le plan du rampant)");""",
"""    console.log("[DEVIA] Pannes : dessus sabliere " + (ySabl + sbH / 2).toFixed(3) + " m, dessus faitiere " + (yFaitPanne + pfH / 2).toFixed(3) + " m, sous-face chevrons au mur " + yPlanRampant.toFixed(3) + " m");""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
