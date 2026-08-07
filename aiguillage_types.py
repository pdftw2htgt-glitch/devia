# Decomposition : regles d'aiguillage des types (construction reelle, pas usage)
import shutil, datetime, sys

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"

with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''Si le batiment est un simple rectangle, mets ouvrages a null et remplis seulement les champs simples. " +'''
NEW1 = '''AIGUILLAGE DES TYPES (tres important) : choisis le type d'apres la CONSTRUCTION reelle, pas d'apres l'usage. Un garage FERME (murs, portes) couvert en 2 pans = type traditionnelle, desc precisant garage ferme - le type carport est reserve aux abris OUVERTS sur poteaux, sans murs. Un volume d'habitation secondaire en 2 pans = type traditionnelle aussi. Un sas ou une liaison a TOIT PLAT = type etage (solivage bois porteur), desc precisant toit plat. Un seul pan incline adosse a un mur = type appentis. Recopie pour CHAQUE volume sa pente et sa couverture telles que donnees par le plan (elles peuvent differer d'un volume a l'autre). Si le batiment est un simple rectangle, mets ouvrages a null et remplis seulement les champs simples. " +'''

n = c.count(OLD1)
if n != 1:
    print("ERREUR ancre (regle decomposition) : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
    sys.exit(1)

shutil.copy2(F, F + ".backup_" + stamp + "_aiguillage_types")
c = c.replace(OLD1, NEW1)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : aiguillage des types par construction reelle (garage ferme = traditionnelle, toit plat = etage)")
