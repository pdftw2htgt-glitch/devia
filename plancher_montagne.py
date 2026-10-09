import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

def remp(nom, ancre, nouveau, attendu=1):
    global src
    n = src.count(ancre)
    if n != attendu:
        print("ABANDON " + nom + " : ancre trouvee " + str(n) + " fois au lieu de " + str(attendu))
        cle = ancre.strip().split("\n")[0][:45]
        for i, l in enumerate(src.split("\n")):
            if cle in l:
                print("  ligne " + str(i + 1) + " : " + l.strip()[:200])
        sys.exit(1)
    src = src.replace(ancre, nouveau)
    print("OK " + nom + " (" + str(n) + " fois)")

remp("plancher metier etendu a la table chantier",
"""  const PLANCHER_METIER = { Poincon: 150, Contrefiche: 150 };
  Object.keys(PLANCHER_METIER).forEach((nomP) => {
    const miniP = PLANCHER_METIER[nomP];
    const rP = result[nomP];
    if (rP === undefined || rP === null) return;
    let releve = false;
    ["mini", "conseillee"].forEach((mode) => {
      const s = rP[mode];
      if (s === undefined || s === null) return;
      if (s.b < miniP) { s.b = miniP; releve = true; }
      if (s.h < miniP) { s.h = miniP; releve = true; }
    });
    if (releve) console.log("[DEVIA] EC5 : " + nomP + " releve au plancher metier de " + miniP + " mm");
  });""",
"""  // La table de reference est celle des chantiers de Mathis (ex-table montagne) : elle devient
  // le MINIMUM partout, le calcul pouvant toujours aller au-dessus mais jamais en dessous.
  const PLANCHER_METIER = {
    Chevron: [80, 100], Empannon: [80, 100], "Empannon de croupe": [80, 100],
    Panne: [120, 240], "Panne faitiere": [120, 240], Sabliere: [120, 240],
    Muraillere: [120, 240], Aretier: [120, 240],
    Arbaletrier: [160, 160], Entrait: [160, 160], Contrefiche: [160, 160],
    Poincon: [180, 180], Poteau: [150, 150],
  };
  Object.keys(PLANCHER_METIER).forEach((nomP) => {
    const bMin = PLANCHER_METIER[nomP][0];
    const hMin = PLANCHER_METIER[nomP][1];
    const rP = result[nomP];
    if (rP === undefined || rP === null) return;
    let releve = false;
    ["mini", "conseillee"].forEach((mode) => {
      const s = rP[mode];
      if (s === undefined || s === null) return;
      if (s.b < bMin) { s.b = bMin; releve = true; }
      if (s.h < hMin) { s.h = hMin; releve = true; }
    });
    if (releve) console.log("[DEVIA] EC5 : " + nomP + " releve au plancher metier " + bMin + "x" + hMin);
  });""")

# Replis visuels alignes sur la meme table (cas ou l EC5 ne rend rien pour la piece)
remp("repli panne trad",
'    const [pnB, pnH] = sec("Panne", 0.12, 0.12);',
'    const [pnB, pnH] = sec("Panne", 0.12, 0.24);', 3)

remp("repli panne faitiere trad",
'    const [pfB0, pfH0] = sec("Panne faitiere", 0.14, 0.14);',
'    const [pfB0, pfH0] = sec("Panne faitiere", 0.12, 0.24);')

remp("repli panne faitiere ferme",
'    const [pfB, pfH] = sec("Panne faitiere", 0.14, 0.14);',
'    const [pfB, pfH] = sec("Panne faitiere", 0.12, 0.24);')

remp("repli sabliere trad",
'    const [sbB0, sbH0] = sec("Sabliere", 0.14, 0.14);',
'    const [sbB0, sbH0] = sec("Sabliere", 0.12, 0.24);')

remp("repli sabliere ferme",
'    const [sbB, sbH] = sec("Sabliere", 0.14, 0.14);',
'    const [sbB, sbH] = sec("Sabliere", 0.12, 0.24);')

remp("repli poincon",
'      const [poB, poH] = sec("Poincon", 0.15, 0.15);',
'      const [poB, poH] = sec("Poincon", 0.18, 0.18);', 2)

remp("repli contrefiche",
'      const cfSec = sec("Contrefiche", 0.13, 0.13)[0];',
'      const cfSec = sec("Contrefiche", 0.16, 0.16)[0];', 2)

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
