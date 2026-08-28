# sas_hauteur.py — regle de coherence des hauteurs dans le prompt de synthese :
# le toit plat d un sas passe SOUS les egouts de ses voisins
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''pour un sas, hauteur_murs = hauteur du toit plat lue sur les coupes.'''
R1 = r'''pour un sas, hauteur_murs = hauteur du toit plat lue sur les coupes. CONTROLE SAS : cette hauteur est FORCEMENT inferieure a la hauteur des murs des deux volumes relies (le toit plat passe sous leurs egouts) ; si ta lecture donne plus, tu as pris une cote de faitage ou d acrotere - reprends la coupe et donne la sous-face reelle du toit plat. Meme logique pour un garage ou une annexe : sa hauteur de murs est en general inferieure a celle du corps d habitation - verifie chaque hauteur sur SA coupe avant de repondre.'''

n = src.count(A1)
if n == 1:
    print("OK ancre : controle sas")
else:
    print("ANCRE : " + str(n) + " occurrence(s) au lieu de 1 — ABANDON, rien ecrit.")
    i = src.find(A1[:40])
    if i >= 0:
        print("--- zone reelle ---")
        print(src[max(0, i - 150):i + 400])
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
src = src.replace(A1, R1)
open(F, "w", encoding="utf-8").write(src)
print("1 modification ecrite. Backup : " + F + ".bak_" + tag)
