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

# 1) La reservation est franchement plus large que la panne : on doit la voir
remp("jeu de reservation",
"""        x0: r.z - (r.b / 2 + 0.01),
        x1: r.z + (r.b / 2 + 0.01),
        yb: (r.y - r.h / 2 - 0.01) - Hb,   // sous-face de la panne, jeu compris
        yh: (r.y + r.h / 2 + 0.01) - Hb,   // dessus de la panne, jeu compris""",
"""        x0: r.z - (r.b / 2 + 0.035),        // 3,5 cm de part et d autre : la reservation se voit
        x1: r.z + (r.b / 2 + 0.035),
        yb: (r.y - r.h / 2 - 0.035) - Hb,   // et elle descend sous la panne
        yh: (r.y + r.h / 2 + 0.035) - Hb,""")

# 2) Entre les reservations, le beton monte au ras du bois
remp("mur au ras du bois",
"""    const JEU_CHEVRON = 0.01;   // 1 cm de jeu pour que le beton ne frotte pas le bois""",
"""    const JEU_CHEVRON = 0.004;  // le mur monte au ras du bois entre deux reservations""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
