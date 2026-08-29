# prompts_v11.py — durcissements IA regroupes (UN SEUL test payant)
# terrasse basse = hauteur du platelage / terrasse couverte = carport /
# pose_hauteur_m dans le JSON / interdiction du double comptage / piege NGF / bump v11
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''"debord_toiture_cm":num_ou_null,'''
R1 = r'''"debord_toiture_cm":num_ou_null,"pose_hauteur_m":num_ou_null,'''

A2 = r'''Un seul pan incline adosse a un mur = type appentis.'''
R2 = r'''Un seul pan incline adosse a un mur = type appentis. TERRASSE : une terrasse bois BASSE = type terrasse, avec hauteur_murs = hauteur du PLATELAGE au-dessus du sol (0.3 si plain-pied) - JAMAIS une hauteur de mur ; une terrasse COUVERTE (toit sur poteaux) = type carport. POSE EN HAUTEUR : pose_hauteur_m = altitude de POSE du volume au-dessus du sol (0 ou null = pose au sol) ; un volume pose SUR un autre (appentis sur terrasse, etage sur rez-de-chaussee) a pose_hauteur_m = hauteur du volume porteur ; deux volumes ne peuvent occuper la meme emprise QUE si leurs poses different.'''

A3 = r'''Ne fusionne jamais deux corps de faitages differents en un seul rectangle.'''
R3 = r'''Ne fusionne jamais deux corps de faitages differents en un seul rectangle. INTERDICTION DU DOUBLE COMPTAGE : ne cree JAMAIS un volume pour l emprise TOTALE du batiment EN PLUS de ses sous-volumes - les volumes se PARTAGENT l emprise, chaque metre carre n appartient qu a UN SEUL volume (un batiment de 7.3 en deux corps = un volume de 3.8 plus un volume de 3.5, PAS un volume de 7.3 plus un de 3.5).'''

A4 = r'''Cite la page de chaque info. Reponds en texte structure. INVENTAIRE DES VUES'''
R4 = r'''ATTENTION COTES NGF : une cote NGF (ex 1335.09) est une ALTITUDE ABSOLUE en metres au-dessus du niveau de la mer, PAS une hauteur - une hauteur se calcule par DIFFERENCE entre deux cotes NGF (ex egout moins terrain fini) ; ne recopie JAMAIS une cote NGF comme hauteur. Cite la page de chaque info. Reponds en texte structure. INVENTAIRE DES VUES'''

A5 = r'''const versionPrompt = vh.toString(36) + "-p5v10";'''
R5 = r'''const versionPrompt = vh.toString(36) + "-p6v11";'''

paires = [
    ("schema json pose", A1, R1),
    ("regle terrasse + pose", A2, R2),
    ("double comptage", A3, R3),
    ("piege NGF passe 2B", A4, R4),
    ("bump version v11", A5, R5),
]

erreurs = 0
for nom, ancre, rempl in paires:
    n = src.count(ancre)
    if n == 1:
        print("OK ancre : " + nom)
    else:
        erreurs = erreurs + 1
        print("ANCRE '" + nom + "' : " + str(n) + " occurrence(s) au lieu de 1")
        frag = ancre.strip().split("\n")[0][:50]
        i = src.find(frag)
        if i >= 0:
            print("--- zone reelle ---")
            print(src[max(0, i - 150):i + 400])

if erreurs > 0:
    print("ABANDON — aucune modification ecrite.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
for nom, ancre, rempl in paires:
    src = src.replace(ancre, rempl)
open(F, "w", encoding="utf-8").write(src)
print("5 modifications ecrites. Backup : " + F + ".bak_" + tag)
