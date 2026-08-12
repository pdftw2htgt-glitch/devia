# Position fixe : le type 3D vient de l'analyse cachee, plus jamais de la generation
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()
OLD1 = '''        type_projet: s.type === "sas" ? "sas_liaison" : ((devisParOuvrage[i] && devisParOuvrage[i].projet && devisParOuvrage[i].projet.type_projet) || TYPE_TO_PROJET[s.type] || "charpente_trad"),'''
NEW1 = '''        type_projet: TYPE_TO_PROJET[s.type] || ((devisParOuvrage[i] && devisParOuvrage[i].projet && devisParOuvrage[i].projet.type_projet) || "charpente_trad"),'''
n = c.count(OLD1)
if n != 1:
    print("ERREUR ancre : " + str(n) + " occurrence(s) - abandon")
    sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_position_fixe")
c = c.replace(OLD1, NEW1)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : geometrie pilotee par l'analyse cachee uniquement")
