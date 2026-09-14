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

remp("blocsPour avec budget",
"""      const blocsPour = async (types) => {
        try {
          const unPdf2 = fileList.length === 1 && fileList[0].type === "application/pdf";
          if (unPdf2 === false) return blocks;
          const nums = pagesInv.filter(p => types.indexOf(p.type) >= 0).map(p => parseInt(p.page, 10)).filter(x => isNaN(x) === false);
          if (nums.length === 0) { console.log("[DEVIA] Aucune page identifiee pour " + types.join(", ") + " : dossier complet conserve"); return blocks; }
          const imgs = await rendrePagesImages(bufs[0], nums, 2400, 0.85);
          if (imgs.length === 0) return blocks;
          console.log("[DEVIA] " + imgs.length + " page(s) en haute definition pour " + types.join(", ") + " (pages " + nums.join(", ") + ")");
          return imgs;
        } catch (eB) { console.warn("[DEVIA] Haute definition impossible, pages legeres conservees", eB); return blocks; }
      };""",
"""      const BUDGET_PASSE = 3000000;
      const poidsBloc = (b) => (b && b.source && typeof b.source.data === "string") ? b.source.data.length : 0;
      const sommeBlocs = (arr) => arr.reduce((s, b) => s + poidsBloc(b), 0);
      const blocsPour = async (types) => {
        try {
          const unPdf2 = fileList.length === 1 && fileList[0].type === "application/pdf";
          if (unPdf2 === false) return blocks;
          const rangs = pagesInv
            .filter(p => types.indexOf(p.type) >= 0)
            .map(p => ({ n: parseInt(p.page, 10), r: types.indexOf(p.type), t: (typeof p.titre === "string" && p.titre.length > 0) ? p.titre : (p.type || "vue") }))
            .filter(x => isNaN(x.n) === false);
          rangs.sort((a, b) => (a.r === b.r ? a.n - b.n : a.r - b.r));
          const nums = rangs.map(x => x.n);
          if (nums.length === 0) { console.log("[DEVIA] Aucune page identifiee pour " + types.join(", ") + " : dossier complet conserve"); return blocks; }
          let imgs = await rendrePagesImages(bufs[0], nums, 2400, 0.85);
          if (imgs.length === 0) return blocks;
          if (sommeBlocs(imgs) > BUDGET_PASSE) {
            const imgs2 = await rendrePagesImages(bufs[0], nums, 2400, 0.62);
            if (imgs2.length === imgs.length) {
              imgs = imgs2;
              console.log("[DEVIA] Lot lourd pour " + types.join(", ") + " : compression renforcee, definition inchangee (2400 px)");
            }
          }
          const gardes = [];
          const pagesGardees = [];
          const pagesEcartees = [];
          let cumul = 0;
          for (let iB = 0; iB < imgs.length; iB++) {
            if (cumul + poidsBloc(imgs[iB]) <= BUDGET_PASSE) {
              gardes.push({ type: "text", text: "PAGE " + nums[iB] + " - " + rangs[iB].t });
              gardes.push(imgs[iB]);
              pagesGardees.push(nums[iB]);
              cumul = cumul + poidsBloc(imgs[iB]);
            } else { pagesEcartees.push(nums[iB]); }
          }
          if (pagesGardees.length === 0) { console.warn("[DEVIA] Pages trop lourdes pour " + types.join(", ") + " : pages legeres conservees"); return blocks; }
          if (pagesEcartees.length > 0) console.warn("[DEVIA] Budget atteint : page(s) " + pagesEcartees.join(", ") + " ecartee(s) de " + types.join(", "));
          console.log("[DEVIA] " + pagesGardees.length + " page(s) en haute definition pour " + types.join(", ") + " (pages " + pagesGardees.join(", ") + ", " + Math.round(cumul / 1000) + " ko)");
          return gardes;
        } catch (eB) { console.warn("[DEVIA] Haute definition impossible, pages legeres conservees", eB); return blocks; }
      };""")

remp("message 413 clair",
"""        if (rep.ok === false) throw new Error("HTTP " + rep.status + " : " + brut2.slice(0, 200));""",
"""        if (rep.status === 413) throw new Error("Dossier trop lourd pour une passe d analyse - relance l analyse, le lot sera reduit");
        if (rep.ok === false) throw new Error("HTTP " + rep.status + " : " + brut2.slice(0, 200));""")

remp("version prompt",
"""const versionPrompt = vh.toString(36) + "-p6v12";""",
"""const versionPrompt = vh.toString(36) + "-p6v13";""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
