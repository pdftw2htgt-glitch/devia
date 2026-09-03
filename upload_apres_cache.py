# upload_apres_cache.py — le PDF n est televerse sur Supabase QUE si une vraie
# analyse est necessaire. Un dossier deja en cache ou verrouille par tes
# corrections ne consomme plus rien : ni stockage, ni transfert, ni IA.
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''      const blocks = await buildFileBlocks(fileList);
      if (blocks.length === 0) { setAnalyseFichier(""); return; }'''
R1 = r'''      let blocks = [];'''

A2 = r'''      if (jCache === null) {
      // PASSE 1 : inventaire structure des vues du dossier (JSON)'''
R2 = r'''      if (jCache === null) {
      // Televersement UNIQUEMENT ici : le dossier n est ni en cache ni verrouille
      blocks = await buildFileBlocks(fileList);
      if (blocks.length === 0) { setAnalyseFichier(""); return; }
      // PASSE 1 : inventaire structure des vues du dossier (JSON)'''

paires = [
    ("blocs differes", A1, R1),
    ("upload dans le bloc analyse", A2, R2),
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
print("2 modifications ecrites. Backup : " + F + ".bak_" + tag)
