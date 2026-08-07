# Analyse : interdiction d'estimer - recopier les cotes ECRITES du plan
import shutil, datetime, sys

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"

with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''        "Mets null quand l'info n'est pas lisible sur le document. Les dimensions en metres.";'''
NEW1 = '''        "REGLE COTES (tres important) : recopie les cotes ECRITES sur le plan (plan de masse, plan de toitures, coupes) - ne mesure jamais a l'oeil, n'estime jamais, n'arrondis jamais. Cherche la cote ecrite la plus proche de chaque volume avant de conclure. Si une dimension n'est vraiment pas cotee, mets null plutot que d'inventer. Deux analyses du meme plan doivent donner exactement les memes chiffres. " +
        "Mets null quand l'info n'est pas lisible sur le document. Les dimensions en metres.";'''

n = c.count(OLD1)
if n != 1:
    print("ERREUR ancre (fin consignes analyse) : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
    sys.exit(1)

shutil.copy2(F, F + ".backup_" + stamp + "_cotes_exactes")
c = c.replace(OLD1, NEW1)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : analyse contrainte aux cotes ecrites du plan")
