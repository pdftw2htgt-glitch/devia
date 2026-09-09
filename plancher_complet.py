# plancher_complet.py — ETAPE 1 du chantier sous-sol
# Le plancher sur solivage chiffre desormais ce qu on pose reellement :
# les SABOTS metalliques (2 par solive) et le PANNEAU DE PLANCHER au-dessus.
# Sert au plancher au-dessus d un sous-sol comme a tout plancher d etage.
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''    // ===== SOLIVES (sens lg, ENTRE les murailleres, dessus affleurant) =====
    setPiece("Solive");
    const lgSolive = lg - 2 * ppB;                   // s'arretent contre les murailleres
    const nbSolives = Math.max(2, Math.round(L / 0.5) + 1);
    for (let i = 0; i < nbSolives; i++) {
      const x = -L/2 + soB/2 + (i / (nbSolives - 1)) * (L - soB);
      addBox(soB, soH, lgSolive, x, ySolive, 0, woodMat);
    }
  };'''

R1 = r'''    // ===== SOLIVES (sens lg, ENTRE les murailleres, dessus affleurant) =====
    setPiece("Solive");
    const lgSolive = lg - 2 * ppB;                   // s'arretent contre les murailleres
    const nbSolives = Math.max(2, Math.round(L / 0.5) + 1);
    for (let i = 0; i < nbSolives; i++) {
      const x = -L/2 + soB/2 + (i / (nbSolives - 1)) * (L - soB);
      addBox(soB, soH, lgSolive, x, ySolive, 0, woodMat);
    }

    // ===== SABOTS METALLIQUES : 2 par solive, aux appuis sur les murailleres =====
    setPiece("Sabot");
    const sabotMat = new THREE.MeshStandardMaterial({ color: 0x9aa0ab, roughness: 0.55, metalness: 0.75 });
    for (let i = 0; i < nbSolives; i++) {
      const x = -L/2 + soB/2 + (i / (nbSolives - 1)) * (L - soB);
      for (const sz of [-1, 1]) {
        const zS = sz * (lgSolive / 2 - 0.03);
        addBox(soB + 0.008, soH * 0.75, 0.06, x, ySolive - soH * 0.1, zS, sabotMat);
      }
    }

    // ===== PANNEAU DE PLANCHER (pose sur les solives, chiffre au m2) =====
    setPiece("Panneau plancher");
    addBox(L, 0.022, lg, 0, hPlancher + 0.011, 0, woodMat);
  };'''

A2 = r'''"Lisse MOB":0, "Montant MOB":0, "Entretoise MOB":0, "Panneau OSB":0,'''
R2 = r'''"Lisse MOB":0, "Montant MOB":0, "Entretoise MOB":0, "Panneau OSB":0, Sabot:0,'''

paires = [
    ("plancher : sabots + panneau", A1, R1),
    ("sabot non structurel", A2, R2),
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

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
for nom, ancre, rempl in paires:
    src = src.replace(ancre, rempl)
open(F, "w", encoding="utf-8").write(src)
print("2 modifications ecrites. Backup : " + F + ".bak_" + tag)
