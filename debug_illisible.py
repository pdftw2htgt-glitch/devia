# L'erreur "analyse illisible" montre le debut de la reponse du modele
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()
OLD1 = '''throw new Error("analyse illisible");'''
NEW1 = '''throw new Error("analyse illisible - stop_reason " + ((data && data.stop_reason) || "aucun") + " - debut de reponse : " + (txt ? txt.slice(0, 180) : "reponse vide"));'''
n = c.count(OLD1)
if n != 1:
    print("ERREUR ancre : " + str(n) + " occurrence(s) - abandon")
    sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_debug_illisible")
c = c.replace(OLD1, NEW1)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : erreur analyse detaillee")
