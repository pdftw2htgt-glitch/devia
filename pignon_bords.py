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

# Le contour doit partir du bord du mur, pas de la premiere encoche
remp("point de depart du rampant",
"""    const haut = [];
    let dernierX = -lgb / 2;""",
"""    const haut = [[-lgb / 2, hMur(-lgb / 2)]];   // depart du rampant au nu du mur
    let dernierX = -lgb / 2;""")

# ... et se terminer au bord oppose
remp("point d arrivee du rampant",
"""    if (sommetPose === false) haut.push([0, hMur(0)]);
    const shp = new THREE.Shape();""",
"""    if (sommetPose === false) haut.push([0, hMur(0)]);
    haut.push([lgb / 2, hMur(lgb / 2)]);        // arrivee du rampant au nu du mur
    const shp = new THREE.Shape();""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
