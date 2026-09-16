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

remp("camera sous le terrain",
"""    controls.minPolarAngle = 0.1;           // empeche de passer en dessous
    controls.maxPolarAngle = Math.PI / 2.1; // empeche de passer sous le sol""",
"""    controls.minPolarAngle = 0.1;           // empeche de passer en dessous
    // Avec un niveau enterre, la camera doit pouvoir descendre sous le terrain
    controls.maxPolarAngle = aDuEnterre ? Math.PI * 0.93 : Math.PI / 2.1;
    if (aDuEnterre) console.log("[DEVIA] Camera libre sous le terrain (niveau enterre present)");""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
