import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

def remp(nom, ancre, nouveau, attendu=1):
    global src
    n = src.count(ancre)
    if n != attendu:
        print("ABANDON " + nom + " : ancre trouvee " + str(n) + " fois au lieu de " + str(attendu))
        cle = ancre.strip().split("\n")[0][:45]
        for i, l in enumerate(src.split("\n")):
            if cle in l:
                print("  ligne " + str(i + 1) + " : " + l.strip()[:200])
        sys.exit(1)
    src = src.replace(ancre, nouveau)
    print("OK " + nom + " (" + str(n) + " fois)")

# 1) La gamme sautait de 80x100 a 63x150 : on comble avec les deux sections de scierie
#    qui manquaient, sinon aucun chevron de chalet n est representable.
remp("gamme chevrons de chalet",
"  [60,80],[80,80],[60,100],[80,100],[63,150],[75,150],",
"  [60,80],[80,80],[60,100],[80,100],[100,120],[100,140],[63,150],[75,150],")

# 2) Largeur mini du chevron a 100 : le calcul part directement sur la bonne famille
remp("largeur mini chevron a 100",
'  Chevron:80, Panne:75, Sabliere:75, Arbaletrier:75, "Panne faitiere":75,',
'  Chevron:100, Panne:75, Sabliere:75, Arbaletrier:75, "Panne faitiere":75,')

remp("largeur mini empannons a 100",
'Ferme:75, Poteau:100, Entrait:60, Aretier:75, Empannon:80, "Empannon de croupe":80,',
'Ferme:75, Poteau:100, Entrait:60, Aretier:75, Empannon:100, "Empannon de croupe":100,')

# 3) La table de planchers remonte EN TETE DE FICHIER, a cote des autres tables metier :
#    c est un reglage de charpentier, il doit se changer sans aller fouiller dans le calcul.
remp("table des planchers en tete de fichier",
"""const EC5_LARGEUR_MINI = {""",
"""// ============================================================
// PLANCHER METIER - LA TABLE A AJUSTER POUR L ALLURE DE LA CHARPENTE
// ============================================================
// L EC5 valide des sections que personne ne pose (il sortait des chevrons de 60x80).
// Cette table est le MINIMUM impose a chaque piece : le calcul peut toujours aller
// AU-DESSUS si la portee l exige, jamais en dessous. Format [largeur, hauteur] en mm.
// Pour changer l allure d une piece dans la 3D, c est ICI et nulle part ailleurs :
// le devis, les fiches techniques, la 3D et l export IFC suivent tous automatiquement.
// Rester sur des sections de scierie (voir EC5_SECTIONS plus haut), sinon le devis
// annonce un bois qui ne se commande pas.
const PLANCHER_METIER = {
  Chevron: [100, 140], Empannon: [100, 140], "Empannon de croupe": [100, 140],
  Panne: [120, 240], "Panne faitiere": [120, 240], Sabliere: [120, 240],
  Muraillere: [120, 240], Aretier: [120, 240],
  Arbaletrier: [160, 160], Entrait: [160, 160], Contrefiche: [160, 160],
  Poincon: [180, 180], Poteau: [150, 150],
};
const EC5_LARGEUR_MINI = {""")

# 4) Le calcul lit desormais la table globale au lieu de la redefinir
remp("lecture de la table globale",
"""  // La table de reference est celle des chantiers de Mathis (ex-table montagne) : elle devient
  // le MINIMUM partout, le calcul pouvant toujours aller au-dessus mais jamais en dessous.
  const PLANCHER_METIER = {
    Chevron: [80, 100], Empannon: [80, 100], "Empannon de croupe": [80, 100],
    Panne: [120, 240], "Panne faitiere": [120, 240], Sabliere: [120, 240],
    Muraillere: [120, 240], Aretier: [120, 240],
    Arbaletrier: [160, 160], Entrait: [160, 160], Contrefiche: [160, 160],
    Poincon: [180, 180], Poteau: [150, 150],
  };
  Object.keys(PLANCHER_METIER).forEach((nomP) => {""",
"""  // Plancher metier : voir la table PLANCHER_METIER en tete de fichier.
  Object.keys(PLANCHER_METIER).forEach((nomP) => {""")

# 5) Replis visuels du chevron alignes sur le plancher.
#    ATTENTION : l ancre est donnee SANS indentation - une chaine indentee de 4 espaces est
#    contenue dans la meme ligne indentee de 6, et le comptage devient faux.
remp("repli chevron 80x100",
'const [chB, chH] = sec("Chevron", 0.08, 0.10);',
'const [chB, chH] = sec("Chevron", 0.10, 0.14);', 4)

remp("repli chevron 80x100 (4 pans)",
'const [chB3, chH3] = sec("Chevron", 0.08, 0.10);',
'const [chB3, chH3] = sec("Chevron", 0.10, 0.14);')

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
