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

# 1) MONOPENTE : les sablieres s arretent sous les chevrons au lieu d etre traversees
remp("sablieres monopente",
"""    // Dalle interieure
    drawDalleBeton(L, lg, 0);

    setPiece("Sabliere");
    // ===== SABLIERES (basse avant + haute arriere) =====
    const [sbB, sbH] = sec("Sabliere", 0.16, 0.16);
    addBox(L + 0.3, sbH, sbB, 0, Hbas, -lg/2, woodMat);
    addBox(L + 0.3, sbH, sbB, 0, Hhaut, lg/2, woodMat);""",
"""    // Dalle interieure
    drawDalleBeton(L, lg, 0);

    setPiece("Sabliere");
    // ===== SABLIERES (basse avant + haute arriere) =====
    // Les chevrons sont poses a +0.07 de la ligne de rampant, hauteur 0.08 : leur SOUS-FACE
    // est donc a +0.03. Sablieres et pannes etaient centrees SUR la ligne, donc traversees
    // par les chevrons sur la moitie de leur hauteur. Elles s arretent maintenant a ce plan.
    const SOUS_CHEVRON_MP = 0.03;
    const [sbB, sbH] = sec("Sabliere", 0.16, 0.16);
    addBox(L + 0.3, sbH, sbB, 0, Hbas + SOUS_CHEVRON_MP - sbH / 2, -lg/2, woodMat);
    addBox(L + 0.3, sbH, sbB, 0, Hhaut + SOUS_CHEVRON_MP - sbH / 2, lg/2, woodMat);""")

# 2) MONOPENTE : les pannes intermediaires suivent la meme regle
remp("pannes monopente",
"""      const [pnB, pnH] = sec("Panne", 0.14, 0.14);
      addBox(L + 0.3, pnH, pnB, 0, y, z, woodMat);
      pannePositions.push({ y, z, t });""",
"""      const [pnB, pnH] = sec("Panne", 0.14, 0.14);
      const yPanneMP = y + (pnB / 2) * Math.tan(ang) + SOUS_CHEVRON_MP - pnH / 2;
      addBox(L + 0.3, pnH, pnB, 0, yPanneMP, z, woodMat);
      pannePositions.push({ y, z, t });""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
