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

# 1) Deux lots d images distincts : les plans pour les volumes, les coupes pour les niveaux
remp("lots separes",
"""      const blocsGeo = await blocsPour(["plan_de_toitures", "plan_de_masse", "plan_etage", "coupe"]);""",
"""      const blocsGeo = await blocsPour(["plan_de_toitures", "plan_de_masse", "plan_etage"]);
      const blocsNiveaux = await blocsPour(["coupe", "plan_etage"]);""")

# 2) La passe 2A redevient une seule tache : les volumes vus en plan
remp("2A allegee",
""" LISTE AUSSI LES NIVEAUX : a partir des plans de niveaux et des coupes, donne pour CHAQUE niveau du batiment (R-1 ou sous-sol, rez-de-chaussee, etage, mezzanine, combles) son emprise cotee et sa hauteur sous plafond, et dis lequel est ENTERRE ou SEMI-ENTERRE - une coupe ou le terrain naturel remonte au-dessus du plancher bas le prouve. Un niveau enterre ne porte aucun faitage : il ne se voit pas sur un plan de toitures, il se lit sur son plan de niveau et sur les coupes. Ne l omets jamais sous pretexte qu il n a pas de charpente.""",
"""""")

remp("2A pages sans coupes",
"""+ pagesPour(["plan_de_toitures", "plan_de_masse", "plan_etage", "coupe"]) + vuesAbsentes(["plan_de_toitures", "plan_de_masse"]) + indiceBas,""",
"""+ pagesPour(["plan_de_toitures", "plan_de_masse", "plan_etage"]) + vuesAbsentes(["plan_de_toitures", "plan_de_masse"]),""")

# 3) Nouvelle passe courte : les niveaux et les decrochements, lus sur les coupes
remp("passe niveaux",
"""      console.log("[DEVIA] Passe 2A (geometrie) : " + geo.slice(0, 300));""",
"""      console.log("[DEVIA] Passe 2A (geometrie) : " + geo.slice(0, 300));
      // PASSE 2A-2 : les NIVEAUX du batiment, lus sur les coupes (passe courte et ciblee)
      const niveaux = await appelAnalyse(
        "Tu lis les NIVEAUX d un batiment sur ses COUPES et ses plans de niveaux. Donne, pour CHAQUE niveau (sous-sol ou R-1, rez-de-chaussee, etage, mezzanine, combles) : son nom tel qu il est ecrit, son emprise si elle est cotee, sa hauteur sous plafond, et s il est ENTERRE, SEMI-ENTERRE ou hors sol - une coupe ou le terrain naturel remonte au-dessus du plancher bas prouve l enterrement. Un niveau enterre ne porte aucun faitage et ne se voit pas sur un plan de toitures : il se lit ici, et il compte comme un volume a part entiere. Donne ensuite les DECROCHEMENTS DE TOITURE visibles en coupe : deux pans paralleles decales en hauteur, une bande verticale vitree entre deux pans, un corps plus haut que son voisin - precise de combien et dans quel sens. Reponds en texte structure, un paragraphe par niveau, en citant la page de chaque chiffre. INVENTAIRE DES VUES : " + inv + pagesPour(["coupe", "plan_etage"]) + indiceBas,
        [...blocsNiveaux, { type: "text", text: "Lis les niveaux du batiment et les decrochements de toiture." }],
        "medium");
      console.log("[DEVIA] Passe 2A-2 (niveaux) : " + niveaux.slice(0, 300));""")

# 4) La synthese recoit la lecture des niveaux
remp("synthese avec niveaux",
r"""        [{ type: "text", text: "ORIENTATION ETABLIE :\n" + orient + "\n\nLECTURE GEOMETRIE :\n" + geo + "\n\nLECTURE HAUTEURS ET INFOS :\n" + hauts }],""",
r"""        [{ type: "text", text: "ORIENTATION ETABLIE :\n" + orient + "\n\nLECTURE GEOMETRIE :\n" + geo + "\n\nLECTURE DES NIVEAUX :\n" + niveaux + "\n\nLECTURE HAUTEURS ET INFOS :\n" + hauts }],""")

remp("synthese trois lectures",
"""SYNTHESE FINALE : construis le JSON UNIQUEMENT a partir des deux lectures fournies (geometrie, puis hauteurs et infos).""",
"""SYNTHESE FINALE : construis le JSON UNIQUEMENT a partir des lectures fournies (geometrie, niveaux, puis hauteurs et infos). Tout niveau declare ENTERRE ou SEMI-ENTERRE dans la lecture des niveaux DOIT ressortir comme un volume de type etage avec pose_hauteur_m negatif.""")

# 5) Les passes sont nommees dans le bon ordre
remp("noms des passes",
"""const NOMS_PASSES = ["1 inventaire", "1B orientation", "2A geometrie", "2B hauteurs", "3 synthese", "4 confrontation"];""",
"""const NOMS_PASSES = ["1 inventaire", "1B orientation", "2A geometrie", "2A-2 niveaux", "2B hauteurs", "3 synthese", "4 confrontation"];""")

# 6) Bump de version
remp("version prompt",
'const versionPrompt = vh.toString(36) + "-p6v17";',
'const versionPrompt = vh.toString(36) + "-p7v18";')

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
