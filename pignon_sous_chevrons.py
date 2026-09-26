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

remp("hauteur nette des pannes",
"""        yb: (r.y - r.h / 2 - 0.01) - Hb,   // sous-face de la panne, jeu compris
        yh: (r.y + r.h / 2 + 0.01) - Hb,   // dessus de la panne""",
"""        yb: (r.y - r.h / 2 - 0.01) - Hb,   // sous-face de la panne, jeu compris
        yh: (r.y + r.h / 2 + 0.01) - Hb,   // dessus de la panne, jeu compris
        yhNet: (r.y + r.h / 2) - Hb,       // dessus exact : c est le plan des chevrons""")

remp("sommet cale sous les chevrons",
"""    // Le pignon monte au moins au-dessus de la panne la plus haute, sinon rien a encocher
    let hSommet = htTri;
    res.forEach((e) => { if (e.yh + 0.03 > hSommet) hSommet = e.yh + 0.03; });
    const hMur = (x) => hSommet * (1 - Math.abs(x) / (lgb / 2));""",
"""    // Le pignon monte jusqu au dessus des pannes, JAMAIS plus haut : au-dela il entrerait
    // dans les chevrons (le dessus de la panne la plus haute EST le plan de sous-face des chevrons).
    let hSommet = htTri;
    res.forEach((e) => { if (e.yhNet > hSommet) hSommet = e.yhNet; });
    const JEU_CHEVRON = 0.01;   // 1 cm de jeu pour que le beton ne frotte pas le bois
    const hMur = (x) => Math.max(0.02, hSommet * (1 - Math.abs(x) / (lgb / 2)) - JEU_CHEVRON);""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
