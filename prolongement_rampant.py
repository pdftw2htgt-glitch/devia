# prolongement_rampant.py — PROLONGEMENT DE RAMPANT (regle moteur, deterministe)
# Une monopente ou un appentis accole a un batiment, de MEME PENTE (a 2 degres
# pres), est traite comme un prolongement du pan : sa pente est alignee sur
# celle du porteur et la hauteur de son mur bas est recalculee pour que le HAUT
# de son rampant arrive exactement a l egout du batiment. La couverture continue
# sans rupture. Applique au viewer, a la capture PDF ET au metre du devis, pour
# qu ils ne divergent jamais.
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''function assemblerOuvrages(listeOuvrages, construireOuvrage) {
      const gap = 2.0;'''
R1 = r'''function ajusterProlongements(liste) {
  if (Array.isArray(liste) === false) return;
  liste.forEach((o) => {
    if (o === undefined || o === null) return;
    const t = o.type_projet || o.type || "";
    if (t !== "monopente" && t !== "appentis") return;
    if (o.pos === undefined || o.pos === null) return;
    const ref = liste[(o.pos.contre || 1) - 1];
    if (ref === undefined || ref === null || ref === o) return;
    const pO = Number(o.pente) || 0;
    const pR = Number(ref.pente) || 0;
    if (pO <= 0 || pR <= 0) return;
    if (Math.abs(pO - pR) > 2) return;           // pentes differentes : batiment independant
    const hRef = Number(ref.hauteur) || 0;
    const lgO = Number(o.largeur) || 0;
    if (hRef <= 0 || lgO <= 0) return;
    const hBas = Math.round((hRef - lgO * Math.tan((pR * Math.PI) / 180)) * 100) / 100;
    if (hBas < 0.5) {
      console.warn("[DEVIA] Prolongement de rampant impossible : le mur bas tomberait a " + hBas.toFixed(2) + " m, hauteurs conservees");
      return;
    }
    o.pente = pR;
    o.hauteur = hBas;
    console.log("[DEVIA] Prolongement de rampant : " + t + " calee sur l egout du porteur (mur bas " + hBas.toFixed(2) + " m, pente " + pR + " degres)");
  });
}

function assemblerOuvrages(listeOuvrages, construireOuvrage) {
      const gap = 2.0;
      ajusterProlongements(listeOuvrages);'''

A2 = r'''        const fp = {
          type: s.type, couverture: s.couverture, essence: s.essence, finition: s.finition,'''
R2 = r'''        ajusterProlongements(structures);
        const fp = {
          type: s.type, couverture: s.couverture, essence: s.essence, finition: s.finition,'''

paires = [
    ("regle prolongement + appel viewer", A1, R1),
    ("appel avant le metre du devis", A2, R2),
]

erreurs = 0
for nom, ancre, rempl in paires:
    n = src.count(ancre)
    if n == 1:
        print("OK ancre : " + nom)
    else:
        erreurs = erreurs + 1
        print("ANCRE '" + nom + "' : " + str(n) + " occurrence(s) au lieu de 1")

if erreurs > 0:
    print("ABANDON — aucune modification ecrite.")
    sys.exit(1)

if src.count("function ajusterProlongements") > 0:
    print("ABANDON — la fonction existe deja (script deja passe).")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
for nom, ancre, rempl in paires:
    src = src.replace(ancre, rempl)
open(F, "w", encoding="utf-8").write(src)
print("2 modifications ecrites. Backup : " + F + ".bak_" + tag)
