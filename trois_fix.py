# trois_fix.py — analyse plans, 3 corrections
# 1) budget de reponse des passes : 20000 -> 32000 (plus de passe geometrie tronquee)
# 2) decomposition normalisee : le premier volume est TOUJOURS pose libre,
#    plus jamais de volume accroche a lui-meme
# 3) la description auto "D apres le plan" ne declenche plus l extraction
#    d adresse (fini la localisation Rousies qui ecrase Talloires)
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''            model: modele || "claude-sonnet-5",
            max_tokens: 20000,'''
R1 = r'''            model: modele || "claude-sonnet-5",
            max_tokens: 32000,'''

A2 = r'''      const decomp = gardes.map(o => {
        if (o.contre && nouvNum[o.contre] === undefined) {
          console.warn("[DEVIA] Decomposition : accroche contre V" + o.contre + " perdue, rattachee au volume principal");
          return { ...o, contre: 1 };
        }
        if (o.contre) { return { ...o, contre: nouvNum[o.contre] }; }
        return o;
      });'''
R2 = r'''      const decomp = gardes.map((o, idx) => {
        let oc = null;
        if (o.contre) {
          if (nouvNum[o.contre] === undefined) {
            console.warn("[DEVIA] Decomposition : accroche contre V" + o.contre + " perdue, rattachee au volume principal");
            oc = 1;
          } else {
            oc = nouvNum[o.contre];
          }
        }
        if (idx === 0 && oc) {
          console.warn("[DEVIA] Decomposition : le volume principal etait accroche, il est repose libre");
          return { ...o, contre: null, cote: null, facade: null, alignement: null, decalage_m: null, faitage: null };
        }
        if (idx > 0 && oc === idx + 1) {
          console.warn("[DEVIA] Decomposition : V" + (idx + 1) + " accroche a lui-meme, rattache au volume principal");
          oc = 1;
        }
        if (oc) { return { ...o, contre: oc }; }
        return o;
      });'''

A3 = r'''    console.log("[DEVIA] Debounce demarre, attente 1s avant extraction...");'''
R3 = r'''    if (prompt && prompt.indexOf("D'apres le plan") === 0) {
      console.log("[DEVIA] Description issue du plan : extraction adresse ignoree (commune lue sur le cartouche)");
      return;
    }
    console.log("[DEVIA] Debounce demarre, attente 1s avant extraction...");'''

paires = [
    ("budget max_tokens analyse", A1, R1),
    ("decomposition normalisee", A2, R2),
    ("extraction adresse ignoree sur description auto", A3, R3),
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
print("3 modifications ecrites. Backup : " + F + ".bak_" + tag)
