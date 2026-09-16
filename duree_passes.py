import shutil, datetime, sys, os

# ---------- 1) api/chat.js : autoriser une execution longue ----------
A = "api/chat.js"
sa = open(A, encoding="utf-8").read()
shutil.copy(A, A + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
if sa.count("maxDuration") > 0:
    print("OK api/chat.js : maxDuration deja present")
else:
    anc = "export default async function handler(req, res) {"
    if sa.count(anc) != 1:
        print("ABANDON api/chat.js : ancre trouvee " + str(sa.count(anc)) + " fois")
        sys.exit(1)
    sa = sa.replace(anc, "export const config = { maxDuration: 60 };\n\n" + anc)
    open(A, "w", encoding="utf-8").write(sa)
    print("OK api/chat.js : maxDuration 60 s")

# ---------- 2) devia.jsx : chrono, nom de passe, reprise sur coupure ----------
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

remp("appelAnalyse instrumente",
"""      const appelAnalyse = async (sysTxt, contenu, effortNiveau, modele) => {
        const rep = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            model: modele || "claude-sonnet-5",
            max_tokens: 32000,
            thinking: { type: "adaptive" },
            output_config: { effort: effortNiveau },
            system: sysTxt,
            messages: [{ role: "user", content: contenu }],
          }),
        });
        const brut2 = await rep.text();""",
"""      let compteurPasse = 0;
      const NOMS_PASSES = ["1 inventaire", "1B orientation", "2A geometrie", "2B hauteurs", "3 synthese", "4 confrontation"];
      const appelAnalyse = async (sysTxt, contenu, effortNiveau, modele) => {
        compteurPasse += 1;
        const etiquette = "Passe " + (NOMS_PASSES[compteurPasse - 1] || String(compteurPasse));
        const corpsTxt = JSON.stringify({
          model: modele || "claude-sonnet-5",
          max_tokens: 32000,
          thinking: { type: "adaptive" },
          output_config: { effort: effortNiveau },
          system: sysTxt,
          messages: [{ role: "user", content: contenu }],
        });
        console.log("[DEVIA] " + etiquette + " : envoi de " + Math.round(corpsTxt.length / 1000) + " ko");
        const tDebut = Date.now();
        let rep = null;
        let brut2 = "";
        for (let essai = 1; essai <= 2; essai++) {
          try {
            rep = await fetch("/api/chat", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: corpsTxt,
            });
            brut2 = await rep.text();
            break;
          } catch (eRes) {
            const secP = Math.round((Date.now() - tDebut) / 1000);
            console.warn("[DEVIA] " + etiquette + " : connexion perdue apres " + secP + " s (essai " + essai + " sur 2)", eRes);
            if (essai === 2) throw new Error(etiquette + " : connexion perdue apres " + secP + " s - la passe a probablement depasse le temps autorise par l hebergeur");
            await new Promise(r => setTimeout(r, 2500));
          }
        }
        console.log("[DEVIA] " + etiquette + " : reponse recue en " + Math.round((Date.now() - tDebut) / 1000) + " s");""")

remp("erreurs nommees",
"""        if (rep.status === 413) throw new Error("Dossier trop lourd pour une passe d analyse - relance l analyse, le lot sera reduit");
        if (rep.ok === false) throw new Error("HTTP " + rep.status + " : " + brut2.slice(0, 200));""",
"""        if (rep.status === 413) throw new Error(etiquette + " : dossier trop lourd - relance l analyse, le lot sera reduit");
        if (rep.status === 504 || rep.status === 502) throw new Error(etiquette + " : l hebergeur a coupe la passe (trop longue) - relance l analyse");
        if (rep.ok === false) throw new Error(etiquette + " - HTTP " + rep.status + " : " + brut2.slice(0, 200));""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
