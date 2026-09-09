# charges_plancher.py — UN PLANCHER N EST PAS UNE TOITURE
# Les pieces d un plancher (solives, poutre porteuse, murailleres) etaient
# calculees avec les charges de toiture, neige comprise. Elles recoivent
# desormais leurs vraies charges :
#   G = 60 kg/m2 (panneau, parquet, isolant) + poids du solivage
#   Q = 150 kg/m2 exploitation habitation (categorie A)
#   S = 0 (aucune neige a l interieur)
#   Fleche admissible : L/300 instantanee, L/250 finale
#   Duree de charge : moyen terme (et non court terme comme la neige)
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''const EC5_G_TO_KN = 0.0098;       // kg/m2 -> kN/m2'''
R1 = r'''const EC5_G_TO_KN = 0.0098;       // kg/m2 -> kN/m2
// --- CHARGES DE PLANCHER (decisions Mathis, a valider prof) ---
const EC5_PLANCHER_REV = 60 * 0.0098;   // 60 kg/m2 : panneau 22, parquet, isolant, plafond
const EC5_PLANCHER_Q = 150 * 0.0098;    // 150 kg/m2 : exploitation habitation, categorie A'''

A2 = r'''const EC5_FLECHE_ADM = { courant:{winst:300,wnetfin:200}, agricole:{winst:200,wnetfin:150} };'''
R2 = r'''const EC5_FLECHE_ADM = { courant:{winst:300,wnetfin:200}, agricole:{winst:200,wnetfin:150}, plancher:{winst:300,wnetfin:250} };'''

A3 = r'''    const charge = {
      portee: porteeCalc, entraxe,
      G: ch.G, Q: ch.Q, S: ch.S,
      classeService: 2,
      typeBatiment: ((params && params.type_projet) === "hangar") ? "agricole" : "courant",
      dureeVariable: "court",'''
R3 = r'''    // PLANCHER : un solivage d etage porte des meubles et des gens, pas de la neige
    const typeOuvrage = (params && (params.type_projet || params.type)) || "";
    const piecesPlancher = ["Solive", "Poutre porteuse", "Muraillere"];
    const estPlancher = typeOuvrage === "etage" && piecesPlancher.indexOf(g.nom) >= 0;
    const charge = {
      portee: porteeCalc, entraxe,
      G: estPlancher ? (EC5_PLANCHER_REV + EC5_POIDS_CHARPENTE) : ch.G,
      Q: estPlancher ? EC5_PLANCHER_Q : ch.Q,
      S: estPlancher ? 0 : ch.S,
      classeService: 2,
      typeBatiment: estPlancher ? "plancher" : (((params && params.type_projet) === "hangar") ? "agricole" : "courant"),
      dureeVariable: estPlancher ? "moyen" : "court",'''

paires = [
    ("constantes de charge plancher", A1, R1),
    ("fleche admissible plancher", A2, R2),
    ("charges appliquees aux pieces de plancher", A3, R3),
]

erreurs = 0
for nom, ancre, rempl in paires:
    n = src.count(ancre)
    if n == 1:
        print("OK ancre : " + nom)
    else:
        erreurs = erreurs + 1
        print("ANCRE '" + nom + "' : " + str(n) + " occurrence(s) au lieu de 1")

if erreurs > 0:
    print("ABANDON — aucune modification ecrite.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
for nom, ancre, rempl in paires:
    src = src.replace(ancre, rempl)
open(F, "w", encoding="utf-8").write(src)
print("3 modifications ecrites. Backup : " + F + ".bak_" + tag)
