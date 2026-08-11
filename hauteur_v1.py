# Synthese : hauteur du volume principal OBLIGATOIRE (egout, converti du faitage si besoin)
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''sysAnalyse + " SYNTHESE FINALE : construis le JSON UNIQUEMENT a partir des deux lectures fournies (geometrie, puis hauteurs et infos). Ne reinvente aucun chiffre : si une valeur manque dans les lectures, mets null.",'''
NEW1 = '''sysAnalyse + " SYNTHESE FINALE : construis le JSON UNIQUEMENT a partir des deux lectures fournies (geometrie, puis hauteurs et infos). Ne reinvente aucun chiffre : si une valeur manque dans les lectures, mets null. EXCEPTION OBLIGATOIRE : hauteur_murs du PREMIER volume (le principal) ne doit JAMAIS etre null - prends son egout dans la lecture hauteurs ; si la lecture ne donne que son faitage, convertis : egout = faitage moins (largeur divisee par 2) multipliee par tangente de la pente. Fais de meme pour chaque volume dont l'egout figure dans les lectures.",'''

OLD2 = '''const versionPrompt = vh.toString(36) + "-p3v4";'''
NEW2 = '''const versionPrompt = vh.toString(36) + "-p3v5";'''

anchors = [("synthese hauteur obligatoire", OLD1, NEW1), ("cache v5", OLD2, NEW2)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_hauteur_v1")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : hauteur du volume principal obligatoire en synthese (cache v5)")
