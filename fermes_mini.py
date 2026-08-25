import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

FONCTION = '''// REGLE METIER (Mathis 25/08) : le MOINS de fermes possible tant que la panne
// tient le calcul EC5 sur la portee entre fermes. Une panne est d'une seule
// piece jusqu'a 13 m (reference stock fournisseur). Repli : 3,5 m historique.
function entraxeFermesOptimal(L, couverture, sk, pente, dS, solaire, altitude) {
  try {
    const ch = ec5DescenteCharge(couverture || "tuile_terre", sk || 0.45, pente || 35, dS || 0, solaire ? true : false);
    for (let nInt = 1; nInt <= 10; nInt++) {
      const entraxe = L / nInt;
      if (entraxe > 13) continue;
      const dim = dimensionnerPiece("Panne", {
        portee: entraxe, entraxe: 1.5,
        G: ch.G, Q: ch.Q, S: ch.S,
        classeService: 2, typeBatiment: "courant", dureeVariable: "court",
        altitude: altitude || 0, console: false,
      });
      if (dim) return entraxe;
    }
  } catch (e) { console.warn("[DEVIA] entraxeFermesOptimal:", e); }
  return 3.5;
}

function calculerSectionsCharpente(metreAgrege, params, sk) {'''

REMPL = [
    # 1. Nouvelle fonction juste avant le calcul des sections
    ("function calculerSectionsCharpente(metreAgrege, params, sk) {", FONCTION),
    # 2. Entraxe dynamique dans le calcul EC5 (portee pannes + charges fermes)
    ("  const ENTRAXE_FERMES = 3.5;\n  const PORTEE_MAX = 8;",
     '  const ENTRAXE_FERMES = entraxeFermesOptimal(((params && params.longueur) || 8), (params && params.couverture), sk, (params && params.pente), (params && params.dS), (params && params.solaire), (params && Number(params.altitude)) || 0);\n  const PORTEE_MAX = 8;'),
    # 3. La portee des pannes ne doit plus etre plafonnee a 8 m (elle est validee par la recherche)
    ("    porteeCalc = Math.min(porteeCalc, PORTEE_MAX);",
     '    const clampable = (g.nom === "Panne" || g.nom === "Panne faitiere" || g.nom === "Sabliere") === false;\n    if (clampable) { porteeCalc = Math.min(porteeCalc, PORTEE_MAX); }'),
    # 4. Geometrie traditionnelle : nombre de fermes = l'optimal
    ("    const nbFermes = Math.max(2, Math.ceil(L / 3.5));",
     "    const entraxeFOpt = entraxeFermesOptimal(L, params && params.couverture, params && params.sk, params && params.pente, params && params.dS, params && params.solaire, (params && Number(params.altitude)) || 0);\n    const nbFermes = Math.max(1, Math.round(L / entraxeFOpt));"),
]

ok = True
for a, b in REMPL:
    n = txt.count(a)
    if n != 1:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu 1 :", a[:70].replace(chr(10), " / "))
        ok = False
if ok == False:
    raise SystemExit(1)

for a, b in REMPL:
    txt = txt.replace(a, b)

shutil.copy(CHEMIN, CHEMIN + ".backup_fermes_mini_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : minimum de fermes qui tient le calcul (traditionnelle)")
