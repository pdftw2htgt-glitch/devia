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

remp("haut du mur parallele au rampant",
"""    const JEU_CHEVRON = 0.01;   // 1 cm de jeu pour que le beton ne frotte pas le bois
    const hMur = (x) => Math.max(0.02, hSommet * (1 - Math.abs(x) / (lgb / 2)) - JEU_CHEVRON);""",
"""    const JEU_CHEVRON = 0.01;   // 1 cm de jeu pour que le beton ne frotte pas le bois
    // Le haut du mur suit le rampant : meme PENTE que le toit (htTri sur la demi-largeur),
    // abaissee du jeu. Une droite partant de zero au bord se rapprocherait du rampant en
    // montant et viendrait se coller a l arbaletrier au faitage.
    const hMur = (x) => Math.max(0.02, hSommet - (Math.abs(x) / (lgb / 2)) * htTri - JEU_CHEVRON);""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
