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

remp("deux boutons de pignon",
"""                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
                  {[
                    { val: "plein", label: "Maconne jusque sous les pannes" },
                    { val: "egout", label: "Maconne jusqu a la sabliere" },
                    { val: "aucun", label: "Sans mur : ferme apparente" }
                  ].map(opt => (""",
"""                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                  {[
                    { val: "plein", label: "Mur pignon beton" },
                    { val: "egout", label: "Mur pignon avec ferme apparente" }
                  ].map(opt => (""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
