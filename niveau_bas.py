import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

def remp(nom, ancre, nouveau):
    global src
    n = src.count(ancre)
    if n != 1:
        print("ABANDON " + nom + " : ancre trouvee " + str(n) + " fois")
        cle = ancre.strip().split("\n")[0][:45]
        for i, l in enumerate(src.split("\n")):
            if cle in l:
                print("  ligne " + str(i + 1) + " : " + l.strip()[:200])
        sys.exit(1)
    src = src.replace(ancre, nouveau)
    print("OK " + nom)

# 1) Lever l interdiction qui faisait ignorer le niveau enterre
remp("exception niveau enterre",
"""Ne cree un element que pour les volumes qui portent une charpente ou une structure bois a chiffrer : ignore les terrasses dallees et les piscines.""",
"""Ne cree un element que pour les volumes qui portent une charpente ou une structure bois a chiffrer : ignore les terrasses dallees et les piscines - SAUF un niveau enterre, qui fait exception (voir NIVEAU ENTERRE plus bas). NIVEAU ENTERRE (tres important) : si le dossier comporte un plan de niveau R-1, un sous-sol, un garage en dessous ou un niveau semi-enterre - une coupe ou le terrain naturel passe au-dessus du plancher bas suffit a le prouver - cree UN VOLUME DE PLUS pour ce niveau : type etage, longueur et largeur = son emprise lue sur le plan R-1, hauteur_murs = sa hauteur sous plafond, et pose_hauteur_m = MOINS cette hauteur (2.60 m sous plafond donne pose_hauteur_m = -2.6). Ce volume se place sous celui du rez-de-chaussee, qui lui reste a pose_hauteur_m null : les deux partagent la meme emprise, c est normal et ce n est PAS un double comptage. Ce volume compte meme si ses murs sont en maconnerie, parce que son plancher haut porte le rez-de-chaussee et se chiffre en bois. Un plan de niveau nomme R-1, sous-sol, garage ou cave dans l inventaire des vues est la preuve suffisante : ne l ignore jamais.""")

# 2) Un niveau enterre est maconne : ses appuis sont des murs, pas des poteaux bois
remp("appuis murs pour niveau enterre",
"""            pose: (typeof o.pose_hauteur_m === "number" && Math.abs(o.pose_hauteur_m) > 0.01) ? o.pose_hauteur_m : undefined,""",
"""            pose: (typeof o.pose_hauteur_m === "number" && Math.abs(o.pose_hauteur_m) > 0.01) ? o.pose_hauteur_m : undefined,
            appuis: (typeof o.pose_hauteur_m === "number" && o.pose_hauteur_m < -0.05) ? "murs" : undefined,""")

# 3) La synthese doit reporter le niveau enterre
remp("synthese niveau enterre",
"""SYNTHESE FINALE : construis le JSON UNIQUEMENT a partir des deux lectures fournies (geometrie, puis hauteurs et infos).""",
"""SYNTHESE FINALE : construis le JSON UNIQUEMENT a partir des deux lectures fournies (geometrie, puis hauteurs et infos). Si les lectures mentionnent un niveau R-1, un sous-sol, une cave ou un garage enterre, il DOIT ressortir comme un volume de type etage avec un pose_hauteur_m negatif : ne le laisse jamais de cote.""")

# 4) Bump de version
remp("version prompt",
'const versionPrompt = vh.toString(36) + "-p6v15";',
'const versionPrompt = vh.toString(36) + "-p6v16";')

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
