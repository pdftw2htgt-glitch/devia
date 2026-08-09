# Chantier split : un batiment a plusieurs faitages = un volume par faitage
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()
OLD1 = '''Ne cree un element que pour les volumes qui portent une charpente ou une structure bois a chiffrer : ignore les terrasses dallees et les piscines. '''
NEW1 = '''REGLE MULTI-FAITAGES (tres important) : un batiment d'habitation en L, en T ou compose de plusieurs corps = un volume PAR faitage visible sur le plan de toitures. Chaque corps a ses propres cotes (plan de masse ou de toitures) et sa propre hauteur_murs lue sur SA coupe - un corps a etage est plus haut qu'un corps en rez-de-chaussee. Ne fusionne jamais deux corps de faitages differents en un seul rectangle. Ne cree un element que pour les volumes qui portent une charpente ou une structure bois a chiffrer : ignore les terrasses dallees et les piscines. '''
n = c.count(OLD1)
if n != 1:
    print("ERREUR ancre : " + str(n) + " occurrence(s) - abandon (si 0 : le script est peut-etre deja passe)")
    sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_split_habitat")
c = c.replace(OLD1, NEW1)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : regle multi-faitages en place")
