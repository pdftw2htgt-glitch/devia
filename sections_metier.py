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

# 1) LARGEUR MINI DU CHEVRON : 60 mm laissait passer du 60x80, qui n est pas un chevron
remp("largeur mini chevron",
'  Chevron:60, Panne:75, Sabliere:75, Arbaletrier:75, "Panne faitiere":75,',
'  Chevron:80, Panne:75, Sabliere:75, Arbaletrier:75, "Panne faitiere":75,')

remp("empannons comme le chevron",
'Ferme:75, Poteau:100, Entrait:60, Aretier:75, Empannon:60, "Empannon de croupe":60,',
'Ferme:75, Poteau:100, Entrait:60, Aretier:75, Empannon:80, "Empannon de croupe":80,')

# 2) PLANCHER METIER EN SORTIE DE CALCUL (poincon et contrefiche)
remp("plancher metier de la ferme",
"""    ["mini", "conseillee"].forEach(mode => {
      const pot = result["Poteau"][mode];
      if (pot && pot.b < wSab) { pot.b = wSab; pot.h = wSab; }
    });
  }
  return result;
}""",
"""    ["mini", "conseillee"].forEach(mode => {
      const pot = result["Poteau"][mode];
      if (pot && pot.b < wSab) { pot.b = wSab; pot.h = wSab; }
    });
  }
  // PLANCHER METIER : l EC5 valide des sections que personne ne pose. Un poincon et une
  // contrefiche de ferme traditionnelle ne descendent pas sous 150 mm de cote, meme quand le
  // calcul passe a 100x100 - sinon la piece maitresse parait sous-dimensionnee au milieu
  // d arbaletriers de 140x280. Applique en SORTIE, donc valable pour tous les chemins de calcul
  // et pour tout l aval : devis, fiches techniques, 3D et export IFC disent la meme chose.
  const PLANCHER_METIER = { Poincon: 150, Contrefiche: 150 };
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
  });
  return result;
}""")

# 3) REPLIS VISUELS : un chevron se pose DEBOUT, jamais carre
remp("repli chevron 70x70",
'    const [chB, chH] = sec("Chevron", 0.07, 0.07);',
'    const [chB, chH] = sec("Chevron", 0.08, 0.10);', 2)

remp("repli chevron 70x70 (4 pans)",
'    const [chB3, chH3] = sec("Chevron", 0.07, 0.07);',
'    const [chB3, chH3] = sec("Chevron", 0.08, 0.10);')

remp("repli chevron 80x80",
'      const [chB, chH] = sec("Chevron", 0.08, 0.08);',
'      const [chB, chH] = sec("Chevron", 0.08, 0.10);', 2)

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
