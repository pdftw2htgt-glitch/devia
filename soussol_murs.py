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

remp("murs et dalle du niveau enterre",
"""    } else {
      console.log("[DEVIA] Plancher sur murs porteurs : aucun poteau bois chiffre");
    }""",
"""    } else {
      console.log("[DEVIA] Plancher sur murs porteurs : aucun poteau bois chiffre");
      // NIVEAU ENTERRE : jusqu ici le plancher flottait au-dessus du vide. On dessine le volume
      // maconne qui le porte - 4 murs peripheriques + dalle basse - uniquement quand le volume
      // est reellement enterre (pose negative). Sur des murs existants hors sol, ces murs
      // appartiennent au batiment en place et n ont pas a etre representes ni chiffres.
      const poseEtage = (params && typeof params.pose === "number") ? params.pose : 0;
      if (poseEtage < -0.05) {
        const epSS = 0.2;
        addBox(L, hPot, epSS, 0, hPot / 2, lg / 2 - epSS / 2, betonMat);
        addBox(L, hPot, epSS, 0, hPot / 2, -lg / 2 + epSS / 2, betonMat);
        addBox(epSS, hPot, lg - 2 * epSS, L / 2 - epSS / 2, hPot / 2, 0, betonMat);
        addBox(epSS, hPot, lg - 2 * epSS, -L / 2 + epSS / 2, hPot / 2, 0, betonMat);
        drawDalleBeton(L, lg, 0);
        console.log("[DEVIA] Niveau enterre : 4 murs beton de " + hPot.toFixed(2) + " m et dalle basse (hors chiffrage bois)");
      }
    }""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
