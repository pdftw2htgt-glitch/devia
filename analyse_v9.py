# analyse_v9.py — refonte analyse plans, etapes 1+2
# 1) passe 1 : inventaire JSON + carte du dossier + pagesPour
# 2) passe 1B : orientation (fable, effort high)
# 3) injections geo / hauteurs / synthese + bump cache p4v9
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A_VERSION = r'''const versionPrompt = vh.toString(36) + "-p3v8";'''
R_VERSION = r'''const versionPrompt = vh.toString(36) + "-p4v9";'''

A_P1 = r'''      // PASSE 1 : inventaire des vues du dossier
      const inv = await appelAnalyse(
        "Tu inventories un dossier de permis de construire. Liste chaque page et le type de vue qu'elle contient (plan de situation, plan de masse, plan de toitures, coupes, facades, plan d'etage, notice, cartouche). Reponds en texte court, une ligne par page.",
        [...blocks, { type: "text", text: "Inventorie les vues de ce dossier." }],
        "medium");
      console.log("[DEVIA] Passe 1 (inventaire) : " + inv.slice(0, 250));'''

R_P1 = r'''      // PASSE 1 : inventaire structure des vues du dossier (JSON)
      const invBrut = await appelAnalyse(
        "Tu inventories un dossier de permis de construire. Reponds UNIQUEMENT avec un JSON valide, sans aucun texte autour, au format : {\"pages\":[{\"page\":1,\"type\":\"plan_de_masse|plan_de_situation|plan_de_toitures|coupe|facade|plan_etage|notice|cartouche|perspective|autre\",\"titre\":\"titre lu sur la page\",\"echelle\":\"1/100 ou null\",\"contenu\":\"une phrase\"}],\"nord_visible_pages\":[numeros des pages ou une fleche du nord est visible]}",
        [...blocks, { type: "text", text: "Inventorie les vues de ce dossier." }],
        "medium");
      let pagesInv = [];
      let nordPages = [];
      try {
        const mInv = invBrut.match(/\{[\s\S]*\}/);
        const objInv = mInv ? JSON.parse(mInv[0]) : null;
        if (objInv && Array.isArray(objInv.pages)) { pagesInv = objInv.pages; }
        if (objInv && Array.isArray(objInv.nord_visible_pages)) { nordPages = objInv.nord_visible_pages; }
      } catch (e) { pagesInv = []; }
      const carteDossier = pagesInv.length > 0
        ? pagesInv.map((p) => {
            const ech = p.echelle === null || p.echelle === undefined || p.echelle === "null" ? "" : ", " + p.echelle;
            return "page " + p.page + " = " + (p.titre || p.type || "?") + " (" + (p.type || "?") + ech + ")";
          }).join(" ; ")
        : invBrut;
      const pagesPour = (types) => {
        const nums = pagesInv.filter((p) => types.indexOf(p.type) >= 0).map((p) => p.page);
        return nums.length > 0 ? " PAGES A UTILISER EN PRIORITE : " + nums.join(", ") + "." : "";
      };
      const inv = carteDossier;
      console.log("[DEVIA] Passe 1 (inventaire) : " + inv.slice(0, 250));

      // PASSE 1B : orientation du batiment (source de verite pour les cardinaux)
      const orient = await appelAnalyse(
        "Tu etablis l ORIENTATION d un batiment a partir d un dossier de permis. Croise TROIS sources : 1) la fleche du nord sur le plan de masse ou de situation" + (nordPages.length > 0 ? " (fleche visible pages " + nordPages.join(", ") + ")" : "") + ", 2) les titres des facades (Facade Nord, Facade Sud-Est...), 3) la silhouette des volumes visibles sur chaque facade. Reponds UNIQUEMENT avec un JSON valide : {\"nord\":{\"page_fleche\":numero_ou_null,\"orientation_fleche\":\"haut|bas|gauche|droite|angle\",\"confiance\":\"haute|moyenne|basse\"},\"facades\":[{\"page\":numero,\"titre\":\"Facade Nord\",\"cardinal\":\"nord|sud|est|ouest\",\"volumes_visibles\":\"description courte\"}],\"coherence\":\"ok|conflit\",\"detail\":\"une phrase\"}. Si aucune fleche du nord est visible, deduis les cardinaux depuis les titres des facades seuls et mets confiance basse. N INVENTE JAMAIS : null vaut mieux que faux. CARTE DU DOSSIER : " + carteDossier + pagesPour(["plan_de_masse", "plan_de_toitures", "facade"]),
        [...blocks, { type: "text", text: "Etablis l orientation du batiment et le cardinal de chaque facade." }],
        "high", "claude-fable-5");
      console.log("[DEVIA] Passe 1B (orientation) : " + orient.slice(0, 250));'''

A_GEO = r'''un paragraphe par volume. INVENTAIRE DES VUES : " + inv,'''
R_GEO = r'''un paragraphe par volume. ORIENTATION ETABLIE (source de verite pour les cardinaux - ne la recalcule pas, appuie toi dessus et signale seulement une contradiction) : " + orient + " INVENTAIRE DES VUES : " + inv + pagesPour(["plan_de_toitures", "plan_de_masse", "plan_etage"]),'''

A_HAUT = r'''Reponds en texte structure. INVENTAIRE DES VUES : " + inv,'''
R_HAUT = r'''Reponds en texte structure. INVENTAIRE DES VUES : " + inv + pagesPour(["coupe", "notice", "cartouche", "facade"]),'''

A_SYN = r'''[{ type: "text", text: "LECTURE GEOMETRIE :\n" + geo + "\n\nLECTURE HAUTEURS ET INFOS :\n" + hauts }],'''
R_SYN = r'''[{ type: "text", text: "ORIENTATION ETABLIE :\n" + orient + "\n\nLECTURE GEOMETRIE :\n" + geo + "\n\nLECTURE HAUTEURS ET INFOS :\n" + hauts }],'''

paires = [
    ("version cache", A_VERSION, R_VERSION),
    ("bloc passe 1", A_P1, R_P1),
    ("prompt geometrie", A_GEO, R_GEO),
    ("prompt hauteurs", A_HAUT, R_HAUT),
    ("synthese", A_SYN, R_SYN),
]

erreurs = 0
for nom, ancre, rempl in paires:
    n = src.count(ancre)
    if n == 1:
        print("OK ancre : " + nom)
    else:
        erreurs = erreurs + 1
        print("ANCRE '" + nom + "' : " + str(n) + " occurrence(s) au lieu de 1")
        frag = ancre.strip().split("\n")[0][:50]
        i = src.find(frag)
        if i >= 0:
            print("--- zone reelle ---")
            print(src[max(0, i - 150):i + 400])

if erreurs > 0:
    print("ABANDON — aucune modification ecrite.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
for nom, ancre, rempl in paires:
    src = src.replace(ancre, rempl)
open(F, "w", encoding="utf-8").write(src)
print("5 modifications ecrites. Backup : " + F + ".bak_" + tag)
