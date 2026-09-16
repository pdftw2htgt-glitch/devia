import shutil, datetime, sys, json

# ---------- 1) vercel.json : la duree est declaree la ou Vercel la lit vraiment ----------
V = "vercel.json"
shutil.copy(V, V + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
vj = json.load(open(V, encoding="utf-8"))
vj["functions"] = {"api/chat.js": {"maxDuration": 60}}
json.dump(vj, open(V, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("OK vercel.json : maxDuration 60 s sur api/chat.js")

# ---------- 2) devia.jsx ----------
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

remp("repli lecture rapide",
"""        const corpsTxt = JSON.stringify({
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
        console.log("[DEVIA] " + etiquette + " : reponse recue en " + Math.round((Date.now() - tDebut) / 1000) + " s");""",
"""        const corpsPour = (rapide) => {
          const obj = {
            model: modele || "claude-sonnet-5",
            max_tokens: rapide ? 12000 : 32000,
            output_config: { effort: rapide ? "low" : effortNiveau },
            system: sysTxt,
            messages: [{ role: "user", content: contenu }],
          };
          if (rapide === false) obj.thinking = { type: "adaptive" };
          return JSON.stringify(obj);
        };
        const tDebut = Date.now();
        let rep = null;
        let brut2 = "";
        let rapide = false;
        for (let essai = 1; essai <= 3; essai++) {
          const corpsTxt = corpsPour(rapide);
          if (essai === 1) console.log("[DEVIA] " + etiquette + " : envoi de " + Math.round(corpsTxt.length / 1000) + " ko");
          try {
            rep = await fetch("/api/chat", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: corpsTxt,
            });
            brut2 = await rep.text();
          } catch (eRes) {
            const secE = Math.round((Date.now() - tDebut) / 1000);
            console.warn("[DEVIA] " + etiquette + " : connexion perdue apres " + secE + " s (essai " + essai + " sur 3)", eRes);
            if (essai === 3) throw new Error(etiquette + " : connexion perdue apres " + secE + " s");
            rapide = true;
            await new Promise(r => setTimeout(r, 2000));
            continue;
          }
          const secR = Math.round((Date.now() - tDebut) / 1000);
          if ((rep.status === 504 || rep.status === 502) && essai < 3) {
            console.warn("[DEVIA] " + etiquette + " : coupee par l hebergeur apres " + secR + " s - nouvelle tentative en lecture rapide");
            rapide = true;
            continue;
          }
          console.log("[DEVIA] " + etiquette + " : reponse recue en " + secR + " s" + (rapide ? " (lecture rapide)" : ""));
          break;
        }""")

# 3) La passe geometrie ne part plus en effort maximal : c est elle qui depassait
remp("2A en effort moyen",
"""        [...blocsGeo, { type: "text", text: "Lis la geometrie des volumes." }],
        "high", "claude-fable-5");""",
"""        [...blocsGeo, { type: "text", text: "Lis la geometrie des volumes." }],
        "medium", "claude-fable-5");""")

# 4) Bump de version
remp("version prompt",
'const versionPrompt = vh.toString(36) + "-p7v18";',
'const versionPrompt = vh.toString(36) + "-p7v19";')

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
