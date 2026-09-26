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

remp("generation devis avec repli",
"""  const callDeviaIA = async (systemPrompt, userContent, modele) => {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: modele || "claude-sonnet-5",
        max_tokens: 20000,
        thinking: { type: "adaptive" },
        output_config: { effort: "medium" },
        system: systemPrompt,
        messages: [{ role: "user", content: userContent }],
      }),
    });
    if (!response.ok) {""",
"""  const callDeviaIA = async (systemPrompt, userContent, modele) => {
    // L hebergeur coupe une fonction au-dela de son temps autorise : si la generation depasse,
    // on relance aussitot en mode rapide plutot que de rendre la main a l utilisateur.
    const corpsDevis = (rapide) => {
      const obj = {
        model: modele || "claude-sonnet-5",
        max_tokens: rapide ? 12000 : 20000,
        output_config: { effort: rapide ? "low" : "medium" },
        system: systemPrompt,
        messages: [{ role: "user", content: userContent }],
      };
      if (rapide === false) obj.thinking = { type: "adaptive" };
      return JSON.stringify(obj);
    };
    const tDevis = Date.now();
    let response = null;
    let rapideD = false;
    for (let essaiD = 1; essaiD <= 3; essaiD++) {
      try {
        response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: corpsDevis(rapideD),
        });
      } catch (eNetD) {
        const secN = Math.round((Date.now() - tDevis) / 1000);
        console.warn("[DEVIA] Devis : connexion perdue apres " + secN + " s (essai " + essaiD + " sur 3)", eNetD);
        if (essaiD === 3) throw new Error("Connexion perdue pendant la generation du devis (" + secN + " s) - relance la generation");
        rapideD = true;
        await new Promise(r => setTimeout(r, 2000));
        continue;
      }
      if ((response.status === 504 || response.status === 502) && essaiD < 3) {
        console.warn("[DEVIA] Devis : coupe par l hebergeur apres " + Math.round((Date.now() - tDevis) / 1000) + " s - nouvelle tentative en mode rapide");
        rapideD = true;
        continue;
      }
      break;
    }
    console.log("[DEVIA] Devis : reponse en " + Math.round((Date.now() - tDevis) / 1000) + " s" + (rapideD ? " (mode rapide)" : ""));
    if (response.status === 504 || response.status === 502) {
      throw new Error("La generation a depasse le temps autorise par l hebergeur, meme en mode rapide. Relance la generation.");
    }
    if (!response.ok) {""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
