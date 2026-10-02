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

remp("pignon reserve aux toits a deux pans",
"""      const htTriangle = (lgb / 2) * Math.tan((pente * Math.PI) / 180);
      if (modePignon === "plein" && htTriangle > 0.05) {""",
"""      // Un triangle de pignon ne se justifie que sur un toit A DEUX PANS, qui a declare ou
      // passent ses pannes. Un toit 4 pans n a pas de pignon du tout : ses quatre cotes
      // descendent en croupe et les murs s arretent a l horizontale.
      const aDesPannes = Array.isArray(reservations) && reservations.length > 0;
      const htTriangle = (lgb / 2) * Math.tan((pente * Math.PI) / 180);
      if (aDesPannes === false) console.log("[DEVIA] Pas de pignon maconne : ce toit n a pas de rampant de pignon");
      if (modePignon === "plein" && aDesPannes && htTriangle > 0.05) {""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
