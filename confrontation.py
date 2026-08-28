# confrontation.py — ETAPE 3 : passe 4 de confrontation aux facades
# Apres la synthese, l IA compare le montage aux facades du dossier
# (volumes visibles, ordre gauche-droite, hauteurs relatives) et corrige
# champ par champ en citant sa preuve. Le verificateur garde le dernier mot.
# + bump version cache p4v9 -> p5v10 (nouvelle passe)
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''      j = JSON.parse(m[0]);
      if (uCache) {'''
R1 = r'''      j = JSON.parse(m[0]);
      // PASSE 4 : confrontation du montage avec les facades du dossier
      if (Array.isArray(j.ouvrages) && j.ouvrages.length >= 2) {
        try {
          const conf = await appelAnalyse(
            "Tu confrontes un montage de volumes a des dessins de FACADES. MONTAGE DEDUIT DU DOSSIER (volumes numerotes a partir de 1) : " + JSON.stringify(j.ouvrages.map((o, ci) => ({ volume: ci + 1, type: o.type, longueur: o.longueur, largeur: o.largeur, hauteur_murs: o.hauteur_murs, contre: o.contre, cote: o.cote, facade: o.facade, alignement: o.alignement, decalage_m: o.decalage_m, faitage: o.faitage, desc: o.desc }))) + ". ORIENTATION ETABLIE : " + orient + " REGLE DE LECTURE : face a une facade nord, l est est a gauche ; face a une facade sud, l est est a droite ; face a une facade est, le nord est a droite ; face a une facade ouest, le nord est a gauche. TRAVAIL : pour CHAQUE facade nommee du dossier, compte les volumes visibles, leur ordre gauche-droite et leurs hauteurs relatives, puis verifie que le montage les reproduit (bon cote, bon alignement, bonnes hauteurs relatives). Reponds UNIQUEMENT avec un JSON valide : {\"verdict\":\"ok|corrections\",\"corrections\":[{\"volume\":numero,\"champ\":\"cote|facade|alignement|decalage_m|faitage|hauteur_murs\",\"valeur\":\"nouvelle valeur\",\"preuve\":\"facade et page qui le montrent\"}],\"resume\":\"une phrase\"}. Ne corrige que ce que les facades PROUVENT ; en cas de doute, ne corrige pas." + pagesPour(["facade"]),
            [...blocks, { type: "text", text: "Confronte ce montage aux facades du dossier." }],
            "high", "claude-fable-5");
          console.log("[DEVIA] Passe 4 (confrontation facades) : " + conf.slice(0, 250));
          const mc = conf.match(/\{[\s\S]*\}/);
          const jc = mc ? JSON.parse(mc[0]) : null;
          if (jc && jc.verdict === "corrections" && Array.isArray(jc.corrections)) {
            jc.corrections.forEach((c) => {
              const cible = j.ouvrages[(c.volume || 0) - 1];
              const champsOk = ["cote", "facade", "alignement", "decalage_m", "faitage", "hauteur_murs"];
              if (cible && champsOk.includes(c.champ)) {
                const numerique = c.champ === "decalage_m" || c.champ === "hauteur_murs";
                const vNum = numerique ? parseFloat(c.valeur) : c.valeur;
                const vOk = numerique ? isNaN(vNum) === false : true;
                if (vOk) {
                  console.log("[DEVIA] Confrontation : V" + c.volume + " " + c.champ + " -> " + c.valeur + " (" + (c.preuve || "sans preuve") + ")");
                  cible[c.champ] = vNum;
                }
              }
            });
          }
        } catch (eConf) { console.warn("[DEVIA] Passe 4 (confrontation) ignoree :", eConf); }
      }
      if (uCache) {'''

A2 = r'''const versionPrompt = vh.toString(36) + "-p4v9";'''
R2 = r'''const versionPrompt = vh.toString(36) + "-p5v10";'''

paires = [
    ("passe 4 confrontation", A1, R1),
    ("bump version cache", A2, R2),
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
print("2 modifications ecrites. Backup : " + F + ".bak_" + tag)
