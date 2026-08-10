# Analyse en 3 passes : inventaire des vues -> lecture geometrie (effort high)
# -> lecture hauteurs/infos -> synthese JSON depuis les lectures uniquement.
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

START = '''      if (jCache === null) {'''
END = '''      j = JSON.parse(m[0]);'''
if c.count(START) != 1 or c.count(END) != 1:
    print("ERREUR bornes : start=" + str(c.count(START)) + " end=" + str(c.count(END)) + " (attendu 1/1) - abandon")
    sys.exit(1)
i1 = c.find(START)
i2 = c.find(END)
if i2 < i1:
    print("ERREUR ordre des bornes - abandon")
    sys.exit(1)
segment = c[i1:i2 + len(END)]
if ("sysAnalyse" in segment) == False or ("analyse illisible" in segment) == False:
    print("ERREUR contenu du segment inattendu - abandon")
    sys.exit(1)

NEW_BLOCK = '''      const appelAnalyse = async (sysTxt, contenu, effortNiveau) => {
        const rep = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            model: "claude-sonnet-5",
            max_tokens: 12000,
            thinking: { type: "adaptive" },
            output_config: { effort: effortNiveau },
            system: sysTxt,
            messages: [{ role: "user", content: contenu }],
          }),
        });
        const brut2 = await rep.text();
        if (rep.ok === false) throw new Error("HTTP " + rep.status + " : " + brut2.slice(0, 200));
        let dat = null;
        try { dat = JSON.parse(brut2); } catch (pe) { throw new Error("Reponse serveur illisible : " + brut2.slice(0, 200)); }
        if (dat && dat.error) throw new Error("API analyse : " + (dat.error.message || JSON.stringify(dat.error)));
        if (dat && dat.stop_reason === "max_tokens") console.warn("[DEVIA] Analyse : reponse tronquee (max_tokens)");
        const tb2 = (dat.content && Array.isArray(dat.content)) ? dat.content.find(b => b && b.type === "text" && b.text) : null;
        return (tb2 && tb2.text) ? tb2.text.replace(/\\x60\\x60\\x60json|\\x60\\x60\\x60/g, "").trim() : "";
      };
      if (jCache === null) {
      // PASSE 1 : inventaire des vues du dossier
      const inv = await appelAnalyse(
        "Tu inventories un dossier de permis de construire. Liste chaque page et le type de vue qu'elle contient (plan de situation, plan de masse, plan de toitures, coupes, facades, plan d'etage, notice, cartouche). Reponds en texte court, une ligne par page.",
        [...blocks, { type: "text", text: "Inventorie les vues de ce dossier." }],
        "medium");
      console.log("[DEVIA] Passe 1 (inventaire) : " + inv.slice(0, 250));
      // PASSE 2A : geometrie des volumes (plan de toitures + plan de masse), effort maximal
      const geo = await appelAnalyse(
        "Tu lis la GEOMETRIE d'un dossier de permis de construire. En te concentrant sur le plan de toitures et le plan de masse, fais la liste des volumes batis : un faitage dessine = un volume, une toiture plate de liaison = un volume aussi. Pour CHAQUE volume : ses cotes d'emprise ECRITES sur le plan (jamais estimees, jamais arrondies), le sens de son faitage par rapport a celui du volume principal (parallele ou perpendiculaire), contre quel volume il s'accole, sur quel cote (pignon = petit cote, gouttereau = long cote), et le decalage cote quand il existe. Cite la page d'ou vient chaque chiffre. Reponds en texte structure, un paragraphe par volume. INVENTAIRE DES VUES : " + inv,
        [...blocks, { type: "text", text: "Lis la geometrie des volumes." }],
        "high");
      console.log("[DEVIA] Passe 2A (geometrie) : " + geo.slice(0, 300));
      // PASSE 2B : hauteurs et infos generales (coupes + notice + cartouche)
      const hauts = await appelAnalyse(
        "Tu lis un dossier de permis de construire. En te concentrant sur les COUPES, la NOTICE et le CARTOUCHE, donne : la hauteur de chaque volume (egout et faitage, en precisant de quel volume il s'agit - un corps a etage est plus haut qu'un corps en rez-de-chaussee), la pente de toiture telle qu'ecrite avec son unite, la couverture, la commune du chantier, les combles, et ce que la notice dit de la composition des volumes. Cite la page de chaque info. Reponds en texte structure. INVENTAIRE DES VUES : " + inv,
        [...blocks, { type: "text", text: "Lis les hauteurs et les infos generales." }],
        "medium");
      console.log("[DEVIA] Passe 2B (hauteurs) : " + hauts.slice(0, 300));
      // PASSE 3 : synthese -> JSON final, uniquement depuis les lectures
      const syn = await appelAnalyse(
        sysAnalyse + " SYNTHESE FINALE : construis le JSON UNIQUEMENT a partir des deux lectures fournies (geometrie, puis hauteurs et infos). Ne reinvente aucun chiffre : si une valeur manque dans les lectures, mets null.",
        [{ type: "text", text: "LECTURE GEOMETRIE :\\n" + geo + "\\n\\nLECTURE HAUTEURS ET INFOS :\\n" + hauts }],
        "medium");
      const m = syn.match(/\\{[\\s\\S]*\\}/);
      if (m === null) throw new Error("synthese illisible - debut : " + (syn ? syn.slice(0, 180) : "reponse vide"));
      j = JSON.parse(m[0]);'''

c = c.replace(segment, NEW_BLOCK)

OLD2 = '''      const versionPrompt = vh.toString(36);'''
NEW2 = '''      const versionPrompt = vh.toString(36) + "-p3v1";'''
if c.count(OLD2) != 1:
    print("ERREUR ancre version cache : " + str(c.count(OLD2)) + " occurrence(s) - abandon")
    sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_analyse_3passes")
c = c.replace(OLD2, NEW2)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : analyse en 3 passes en place (inventaire, geometrie high, hauteurs, synthese)")
