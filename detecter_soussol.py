import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

if src.count("const ajouterVolume = (modele) => {") != 1:
    print("ABANDON : lance d'abord ajouter_volume.py, ce script s'appuie dessus")
    sys.exit(1)

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

# 1) La variable survit au bloc d analyse (elle sert aussi apres, pour le controle)
remp("declaration pagesNiveauBas",
"""      let j = null;
      const appelAnalyse = async (sysTxt, contenu, effortNiveau, modele) => {""",
"""      let j = null;
      let pagesNiveauBas = [];
      const appelAnalyse = async (sysTxt, contenu, effortNiveau, modele) => {""")

# 2) Le logiciel repere lui-meme les pages de niveau bas dans l inventaire
remp("detection niveau bas",
r"""      const typesPresents = pagesInv.map((p) => p.type).filter((t) => typeof t === "string");""",
r"""      const RX_BAS = /(r\s*[-\u2013]\s*1|sous[\s-]?sol|soussol|niveau\s*[-\u2013]\s*1|\bcave\b|\bcaves\b|semi[\s-]?enterre|infrastructure)/i;
      pagesNiveauBas = pagesInv.filter((p) => RX_BAS.test(String(p.titre || "") + " " + String(p.contenu || ""))).map((p) => p.page);
      const indiceBas = pagesNiveauBas.length > 0
        ? " NIVEAU BAS CONFIRME PAR LE LOGICIEL : le dossier comporte un plan de niveau BAS en page(s) " + pagesNiveauBas.join(", ") + " (R-1, sous-sol, cave ou niveau semi-enterre). Ce niveau EXISTE, ce n est pas a discuter : donne son emprise lue sur ce plan et sa hauteur sous plafond lue sur la coupe, et dis explicitement s il est enterre, semi-enterre ou de plain-pied."
        : "";
      if (pagesNiveauBas.length > 0) console.log("[DEVIA] Niveau bas repere par le logiciel : page(s) " + pagesNiveauBas.join(", "));
      const typesPresents = pagesInv.map((p) => p.type).filter((t) => typeof t === "string");""")

# 3) La passe geometrie lit desormais les NIVEAUX, pas seulement les toitures
remp("passe 2A niveaux",
"""fais la liste des volumes batis : un faitage dessine = un volume, une toiture plate de liaison = un volume aussi.""",
"""fais la liste des volumes batis : un faitage dessine = un volume, une toiture plate de liaison = un volume aussi. LISTE AUSSI LES NIVEAUX : a partir des plans de niveaux et des coupes, donne pour CHAQUE niveau du batiment (R-1 ou sous-sol, rez-de-chaussee, etage, mezzanine, combles) son emprise cotee et sa hauteur sous plafond, et dis lequel est ENTERRE ou SEMI-ENTERRE - une coupe ou le terrain naturel remonte au-dessus du plancher bas le prouve. Un niveau enterre ne porte aucun faitage : il ne se voit pas sur un plan de toitures, il se lit sur son plan de niveau et sur les coupes. Ne l omets jamais sous pretexte qu il n a pas de charpente.""")

remp("passe 2A indice",
"""+ pagesPour(["plan_de_toitures", "plan_de_masse", "plan_etage", "coupe"]) + vuesAbsentes(["plan_de_toitures", "plan_de_masse"]),""",
"""+ pagesPour(["plan_de_toitures", "plan_de_masse", "plan_etage", "coupe"]) + vuesAbsentes(["plan_de_toitures", "plan_de_masse"]) + indiceBas,""")

remp("passe 2B indice",
"""+ pagesPour(["coupe", "notice", "cartouche", "facade", "perspective", "autre"]) + vuesAbsentes(["notice", "cartouche"]),""",
"""+ pagesPour(["coupe", "notice", "cartouche", "facade", "perspective", "autre"]) + vuesAbsentes(["notice", "cartouche"]) + indiceBas,""")

remp("synthese indice",
"""        sysAnalyse + " SYNTHESE FINALE : construis le JSON UNIQUEMENT a partir des deux lectures fournies (geometrie, puis hauteurs et infos).""",
"""        sysAnalyse + indiceBas + " SYNTHESE FINALE : construis le JSON UNIQUEMENT a partir des deux lectures fournies (geometrie, puis hauteurs et infos).""")

# 4) Controle final : un plan R-1 au dossier sans volume enterre monte, c est dit
remp("controle niveau bas",
"""        const notesH = completerHauteurs(structs);""",
"""        const aEnterre = structs.some(s => typeof s.pose === "number" && s.pose < -0.05);
        const manqueBas = pagesNiveauBas.length > 0 && aEnterre === false;
        setAnalyseManqueBas(manqueBas);
        if (manqueBas) console.warn("[DEVIA] Plan de niveau bas page(s) " + pagesNiveauBas.join(", ") + " mais aucun volume enterre monte");
        const notesH = completerHauteurs(structs);""")

# 5) Etat React
remp("etat analyseManqueBas",
"""  const [analyseHauteursDeduites, setAnalyseHauteursDeduites] = useState([]);""",
"""  const [analyseHauteursDeduites, setAnalyseHauteursDeduites] = useState([]);
  const [analyseManqueBas, setAnalyseManqueBas] = useState(false);""")

# 6) Bandeau avec ajout en un clic
remp("bandeau niveau bas",
"""                    {analyseHauteursDeduites.length > 0 ? (""",
"""                    {analyseManqueBas ? (
                      <div style={{ marginTop: 8, padding: "8px 10px", borderRadius: 8, background: "rgba(240,192,64,0.07)", border: "1px solid rgba(240,192,64,0.35)" }}>
                        <div style={{ color: "#f0c040", fontSize: 11.5, fontWeight: 700 }}>NIVEAU BAS NON MONTE</div>
                        <div style={{ marginTop: 4, color: cl("#b8bccc", "#565a6c"), fontSize: 11, lineHeight: 1.5 }}>Le dossier contient un plan de niveau bas (R-1, sous-sol ou cave) mais aucun volume enterre n a ete monte. Ajoute-le, puis regle son emprise et sa hauteur sur le plan.</div>
                        <button type="button" onClick={() => { ajouterVolume("enterre"); setEditeurOuvert(true); }} style={{ marginTop: 6, padding: "6px 14px", borderRadius: 8, cursor: "pointer", background: "rgba(240,192,64,0.12)", border: "1px solid rgba(240,192,64,0.5)", color: "#f0c040", fontSize: 11.5, fontWeight: 700, display: "block" }}>Ajouter le niveau enterre</button>
                      </div>
                    ) : null}
                    {analyseHauteursDeduites.length > 0 ? (""")

# 7) Bump de version
remp("version prompt",
'const versionPrompt = vh.toString(36) + "-p6v16";',
'const versionPrompt = vh.toString(36) + "-p6v17";')

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
