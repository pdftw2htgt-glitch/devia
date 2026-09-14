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

# 1) Helper : liste des types de vues reellement presents + message des vues absentes
remp("helper vuesAbsentes",
"""      const inv = carteDossier;
      console.log("[DEVIA] Passe 1 (inventaire) : " + inv.slice(0, 250));""",
"""      const inv = carteDossier;
      const typesPresents = pagesInv.map((p) => p.type).filter((t) => typeof t === "string");
      const vuesAbsentes = (types) => {
        const manque = types.filter((t) => typesPresents.indexOf(t) < 0);
        if (manque.length === 0) return "";
        return " VUES ABSENTES DE CE DOSSIER : " + manque.join(", ") + ". Elles n existent pas ici : ne les reclame pas, ne dis pas qu elles manquent, et ne refuse pas de conclure. Travaille avec les pages transmises et cite la page de chaque chiffre.";
      };
      console.log("[DEVIA] Passe 1 (inventaire) : " + inv.slice(0, 250));
      console.log("[DEVIA] Types de vues presents : " + typesPresents.join(", "));""")

# 2) Chaque passe recoit les vues qui portent l information
remp("listes de pages par passe",
"""      const blocsOrientation = await blocsPour(["plan_de_masse", "plan_de_toitures", "facade"]);
      const blocsGeo = await blocsPour(["plan_de_toitures", "plan_de_masse", "plan_etage"]);
      const blocsHauteurs = await blocsPour(["coupe", "notice", "cartouche", "facade"]);""",
"""      const blocsOrientation = await blocsPour(["plan_de_masse", "plan_de_situation", "plan_de_toitures", "facade"]);
      const blocsGeo = await blocsPour(["plan_de_toitures", "plan_de_masse", "plan_etage", "coupe"]);
      const blocsHauteurs = await blocsPour(["coupe", "notice", "cartouche", "facade", "perspective", "autre"]);""")

# 3) Passe 1B : dire ce qui manque
remp("passe 1B vues absentes",
"""+ pagesPour(["plan_de_masse", "plan_de_toitures", "facade"]),""",
"""+ pagesPour(["plan_de_masse", "plan_de_situation", "plan_de_toitures", "facade"]) + vuesAbsentes(["plan_de_masse", "plan_de_toitures"]),""")

# 4) Passe 2A : repli explicite quand ni plan de masse ni plan de toitures
remp("passe 2A repli",
"""Tu lis la GEOMETRIE d'un dossier de permis de construire. En te concentrant sur le plan de toitures et le plan de masse, fais la liste""",
"""Tu lis la GEOMETRIE d'un dossier de construction. En te concentrant sur le plan de toitures et le plan de masse QUAND ILS EXISTENT, et sinon sur les plans d etage et les COUPES transmis (une coupe donne l emprise, les niveaux et les decrochements), fais la liste""")

remp("passe 2A vues absentes",
"""+ pagesPour(["plan_de_toitures", "plan_de_masse", "plan_etage"]),""",
"""+ pagesPour(["plan_de_toitures", "plan_de_masse", "plan_etage", "coupe"]) + vuesAbsentes(["plan_de_toitures", "plan_de_masse"]),""")

# 5) Passe 2B : coupes et facades d abord, notice et cartouche si presents
remp("passe 2B repli",
"""En te concentrant sur les COUPES, la NOTICE et le CARTOUCHE, donne""",
"""En te concentrant sur les COUPES et les FACADES transmises, puis sur la notice et le cartouche QUAND ILS EXISTENT, donne""")

remp("passe 2B vues absentes",
"""+ pagesPour(["coupe", "notice", "cartouche", "facade"]),""",
"""+ pagesPour(["coupe", "notice", "cartouche", "facade", "perspective", "autre"]) + vuesAbsentes(["notice", "cartouche"]),""")

# 6) Bump de version : les reponses en cache datent des anciens prompts
remp("version prompt",
"""const versionPrompt = vh.toString(36) + "-p6v11";""",
"""const versionPrompt = vh.toString(36) + "-p6v12";""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
