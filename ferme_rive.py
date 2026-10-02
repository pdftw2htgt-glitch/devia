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

# 1) Un pignon maconne remplace la ferme de rive : on ne la dessine pas dans le mur
remp("fermes de rive",
"""    const fermeXs = [];""",
"""    // Un mur pignon maconne porte lui-meme les pannes dans ses reservations : il n y a donc
    // PAS de ferme en rive. En dessiner une la noierait dans le beton (arbaletriers visibles
    // dans la maconnerie) et la ferait payer pour rien.
    const smfF = (opts && opts.sansMurFace) || "";
    const pignonPorteur = (params.murs === "ossature_bois") === false && ((params.pignon || "plein") === "aucun") === false;
    const sansFermeGauche = pignonPorteur && (smfF === "pignon_gauche") === false;
    const sansFermeDroite = pignonPorteur && (smfF === "pignon_droit") === false;
    if (sansFermeGauche || sansFermeDroite) console.log("[DEVIA] Ferme de rive supprimee : le pignon maconne porte les pannes");
    const fermeXs = [];
    const fermesDessinees = [];""")

# 2) La boucle saute la ferme quand le pignon la remplace
remp("saut de la ferme de rive",
"""    for (let i = 0; i <= nbFermes; i++) {
      const x = -L/2 + (i / nbFermes) * L;
      fermeXs.push(x);

      // ENTRAIT (poutre horizontale basse, sur toute la largeur)""",
"""    for (let i = 0; i <= nbFermes; i++) {
      const x = -L/2 + (i / nbFermes) * L;
      fermeXs.push(x);
      if (i === 0 && sansFermeGauche) continue;
      if (i === nbFermes && sansFermeDroite) continue;
      fermesDessinees.push(x);

      // ENTRAIT (poutre horizontale basse, sur toute la largeur)""")

# 3) Pas de ferme, pas d echantignole : la panne repose dans sa reservation
remp("echantignoles sur fermes reelles",
"""    pannesInfo.forEach(({ zRef, yRef }) => {
      fermeXs.forEach((fx) => {
        addEchantignole(fx, zRef, yRef, 1);
        addEchantignole(fx, zRef, yRef, -1);
      });
    });""",
"""    pannesInfo.forEach(({ zRef, yRef }) => {
      fermesDessinees.forEach((fx) => {
        addEchantignole(fx, zRef, yRef, 1);
        addEchantignole(fx, zRef, yRef, -1);
      });
    });""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
