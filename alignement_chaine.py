# Lecture des positions : regle d'alignement des chaines + auto-verification
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()
OLD1 = '''Si deux volumes sont relies par une liaison (sas), chaine les accolements : la liaison contre le volume principal, le volume suivant contre la liaison. '''
NEW1 = '''Si deux volumes sont relies par une liaison (sas), chaine les accolements : la liaison contre le volume principal, le volume suivant contre la liaison. REGLE D'ALIGNEMENT : quand trois volumes s'enchainent en ligne sur le plan de masse (principal, liaison, second volume), le second volume s'accole a la liaison sur le cote OPPOSE a celui ou la liaison touche le principal - la chaine continue dans la meme direction (ex : liaison contre V1 pignon_gauche, donc V3 contre V2 pignon_gauche aussi). Un gouttereau ne se choisit que si le plan de masse montre clairement le volume sur le long cote. Pour choisir un cote, compare les positions des emprises sur le plan de masse. VERIFICATION FINALE : reconstruis mentalement la disposition a partir de tes contre, cote et decalage, compare-la au plan de masse, et corrige avant de repondre si ca ne correspond pas. '''
n = c.count(OLD1)
if n != 1:
    print("ERREUR ancre : " + str(n) + " occurrence(s) - abandon")
    sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_alignement_chaine")
c = c.replace(OLD1, NEW1)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : regle d'alignement + auto-verification des positions")
