# sens_monopente.py — DETERMINISME moteur
# 1) monopente/appentis accole : sens de pente FORCE par la geometrie
#    (cote haut toujours contre le volume de reference), l IA ne choisit plus
# 2) verificateur : volume pose en hauteur sans volume porteur dessous = NON CONFORME
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''          const rot = o.faitageCardinal === "nord_sud" ? Math.PI / 2 : (o.faitageCardinal === "est_ouest" ? 0 : ((o.pos.faitage === "perpendiculaire") ? pRef.rot + Math.PI / 2 : pRef.rot));'''
R1 = r'''          let rot = o.faitageCardinal === "nord_sud" ? Math.PI / 2 : (o.faitageCardinal === "est_ouest" ? 0 : ((o.pos.faitage === "perpendiculaire") ? pRef.rot + Math.PI / 2 : pRef.rot));
          if (o.type_projet === "monopente" || o.type_projet === "appentis") {
            const fcM = o.pos.facade || "";
            const cotM = o.pos.cote || "";
            if (fcM === "est" || cotM === "pignon_droit") { rot = -Math.PI / 2; }
            else if (fcM === "ouest" || cotM === "pignon_gauche") { rot = Math.PI / 2; }
            else if (fcM === "sud" || cotM === "gouttereau_avant") { rot = Math.PI; }
            else if (fcM === "nord" || cotM === "gouttereau_arriere") { rot = 0; }
            console.log("[DEVIA] " + o.type_projet + " accole : sens de pente FORCE, cote haut contre V" + o.pos.contre);
          }'''

A2 = r'''    vols.forEach((v, i) => {
      if (v.type === "sas" && v.pos && v.hauteur) {'''
R2 = r'''    vols.forEach((v, i) => {
      const pV = v.pose || 0;
      if (pV > 0.4 && rects[i]) {
        let porte = false;
        vols.forEach((w, k) => {
          if (k === i || rects[k] === undefined) return;
          const dv = demi(v, rects[i].q);
          const dw = demi(w, rects[k].q);
          const oxP = Math.min(rects[i].x + dv.hx, rects[k].x + dw.hx) - Math.max(rects[i].x - dv.hx, rects[k].x - dw.hx);
          const ozP = Math.min(rects[i].z + dv.hz, rects[k].z + dw.hz) - Math.max(rects[i].z - dv.hz, rects[k].z - dw.hz);
          const hautW = (w.pose || 0) + (w.hauteur || 0);
          if (oxP > 0.05 && ozP > 0.05 && hautW >= pV - 0.6) { porte = true; }
        });
        if (porte === false) { erreurs.push("V" + (i + 1) + " est pose a " + pV + " m de haut sans volume porteur sous son emprise"); }
      }
    });
    vols.forEach((v, i) => {
      if (v.type === "sas" && v.pos && v.hauteur) {'''

paires = [
    ("sens monopente force", A1, R1),
    ("verificateur volume porteur", A2, R2),
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
