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

# 1) 4 PANS : sablieres et faitage sous les chevrons
remp("sablieres et faitage 4 pans",
"""setPiece("Sabliere");
    // ===== SABLIERES DE CHAINAGE (haut des 4 murs) =====
    const [sbB, sbH] = sec("Sabliere", 0.16, 0.16);
    addBox(L + 0.2, sbH, sbB, 0, Ht, lg/2, woodMat);
    addBox(L + 0.2, sbH, sbB, 0, Ht, -lg/2, woodMat);
    addBox(sbB, sbH, lg, -L/2, Ht, 0, woodMat);
    addBox(sbB, sbH, lg, L/2, Ht, 0, woodMat);

setPiece("Faitage");
    // ===== FAITAGE (central) =====
    const [ftB, ftH] = sec("Faitage", 0.15, 0.15);
    addBox(Lfait, ftH, ftB, 0, yFait, 0, woodMat);""",
"""setPiece("Sabliere");
    // ===== SABLIERES DE CHAINAGE (haut des 4 murs) =====
    // Les chevrons sont tendus SUR la ligne de rampant (de l egout au faitage), donc leur
    // sous-face est a -chH/2 perpendiculairement. Sablieres, pannes et faitage etaient eux
    // aussi centres sur cette ligne : les chevrons les traversaient de part en part.
    const cosQ = Math.cos(angLong), tanQ = Math.tan(angLong);
    const SOUS_CHEV_Q = (secChevron / 2) / cosQ;   // retrait vertical sous la ligne de rampant
    const [sbB, sbH] = sec("Sabliere", 0.16, 0.16);
    const ySablQ = Ht - SOUS_CHEV_Q + (sbB / 2) * tanQ - sbH / 2;
    addBox(L + 0.2, sbH, sbB, 0, ySablQ, lg/2, woodMat);
    addBox(L + 0.2, sbH, sbB, 0, ySablQ, -lg/2, woodMat);
    addBox(sbB, sbH, lg, -L/2, ySablQ, 0, woodMat);
    addBox(sbB, sbH, lg, L/2, ySablQ, 0, woodMat);

setPiece("Faitage");
    // ===== FAITAGE (central) : il porte les abouts hauts des chevrons =====
    const [ftB, ftH] = sec("Faitage", 0.15, 0.15);
    addBox(Lfait, ftH, ftB, 0, yFait - SOUS_CHEV_Q - ftH / 2, 0, woodMat);""")

# 2) 4 PANS : pannes sous les chevrons
remp("pannes 4 pans",
"""      const [pnB, pnH] = sec("Panne", 0.12, 0.12);
      addBox(lenPanne, pnH, pnB, 0, yPanne, zPanne, woodMat);
      addBox(lenPanne, pnH, pnB, 0, yPanne, -zPanne, woodMat);""",
"""      const [pnB, pnH] = sec("Panne", 0.12, 0.12);
      const yPanneQ = yPanne - SOUS_CHEV_Q + (pnB / 2) * tanQ - pnH / 2;
      addBox(lenPanne, pnH, pnB, 0, yPanneQ, zPanne, woodMat);
      addBox(lenPanne, pnH, pnB, 0, yPanneQ, -zPanne, woodMat);""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
