# decomp_fiable.py — decomposition fiable
# 1) code : plus de volume jete en silence - numeros recales, volume ecarte signale,
#    accroche perdue rattachee au volume principal au lieu de pointer dans le vide
# 2) prompt : dimensions obligatoires pour chaque volume + verification des references
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''      const decomp = Array.isArray(j.ouvrages)
        ? j.ouvrages.filter(o => o && TYPES_DECOMP.includes(o.type) && o.longueur > 0 && o.largeur > 0)
        : [];'''
R1 = r'''      const bruts = Array.isArray(j.ouvrages) ? j.ouvrages : [];
      const gardes = [];
      const nouvNum = {};
      bruts.forEach((o, idx) => {
        if (o && TYPES_DECOMP.includes(o.type) && o.longueur > 0 && o.largeur > 0) {
          gardes.push(o);
          nouvNum[idx + 1] = gardes.length;
        } else if (o) {
          console.warn("[DEVIA] Decomposition : volume " + (idx + 1) + " ecarte (type inconnu ou dimensions manquantes) : type=" + o.type + " longueur=" + o.longueur + " largeur=" + o.largeur);
        }
      });
      const decomp = gardes.map(o => {
        if (o.contre && nouvNum[o.contre] === undefined) {
          console.warn("[DEVIA] Decomposition : accroche contre V" + o.contre + " perdue, rattachee au volume principal");
          return { ...o, contre: 1 };
        }
        if (o.contre) { return { ...o, contre: nouvNum[o.contre] }; }
        return o;
      });'''

A2 = r'''Le PREMIER element du tableau = le volume principal (le plus grand ou le plus haut).'''
R2 = r'''Le PREMIER element du tableau = le volume principal (le plus grand ou le plus haut). DIMENSIONS OBLIGATOIRES : CHAQUE element du tableau DOIT avoir longueur et largeur en metres, lues ou deduites des plans cotes, jamais null ni zero - un volume sans dimensions serait ecarte du montage ; pour un sas, longueur et largeur se mesurent entre les deux volumes relies. REFERENCES : les numeros contre pointent vers des elements de TON tableau (1 = premier element) ; avant de repondre, verifie que chaque contre pointe vers un element qui existe.'''

paires = [
    ("filtre decomposition", A1, R1),
    ("prompt dimensions obligatoires", A2, R2),
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

for nv in ("const bruts", "const gardes", "const nouvNum"):
    if src.count(nv) > 0:
        print("ABANDON — nom deja pris : " + nv)
        sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
for nom, ancre, rempl in paires:
    src = src.replace(ancre, rempl)
open(F, "w", encoding="utf-8").write(src)
print("2 modifications ecrites. Backup : " + F + ".bak_" + tag)
