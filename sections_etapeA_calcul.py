#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Sections etape A : fonction centrale de calcul des sections par type"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()

if "function calculerSectionsCharpente" in content:
    print("[WARN] fonction deja presente -> abandon"); exit(1)

fn = r'''// ============================================================
// CALCUL CENTRAL DES SECTIONS PAR TYPE DE PIECE (reutilisable 3D + tableau)
// Retourne { "Panne": {mini:{b,h,classe,tauxMax}, conseillee:{...}}, ... }
// !!! Hypotheses portee/entraxe/charge A VALIDER PROF !!!
// ============================================================
function calculerSectionsCharpente(metreAgrege, params, sk) {
  if (!metreAgrege || !metreAgrege.groupes) return {};
  const ch = ec5DescenteCharge((params && params.couverture) || "tuile_terre", sk || 0.45);
  const ENTRAXE_FERMES = 3.5;
  const PORTEE_MAX = 8;
  const result = {};

  metreAgrege.groupes.forEach((g) => {
    if (result[g.nom]) return; // un seul calcul par type (le 1er groupe du type)
    // portee realiste selon type
    let porteeCalc;
    if (g.nom === "Panne" || g.nom === "Panne faitiere" || g.nom === "Sabliere") {
      porteeCalc = ENTRAXE_FERMES;
    } else {
      porteeCalc = g.longueurUnitMax;
    }
    porteeCalc = Math.min(porteeCalc, PORTEE_MAX);
    const entraxe = (g.nom === "Chevron" || g.nom === "Empannon" || g.nom === "Empannon de croupe") ? 0.6
                  : (g.nom === "Panne" || g.nom === "Panne faitiere") ? 1.5
                  : (g.nom === "Sabliere" || g.nom === "Aretier") ? 1.0
                  : 1.0;
    const charge = {
      portee: porteeCalc, entraxe,
      G: ch.G, Q: ch.Q, S: ch.S,
      classeService: 2, typeBatiment: "courant", dureeVariable: "court",
    };
    const dim = dimensionnerPiece(g.nom, charge);
    if (dim) result[g.nom] = dim;
  });
  return result;
}

'''

anchor = "// CALCUL CENTRAL DES SECTIONS"
# Inserer juste apres la fonction dimensionnerPiece (reperer sa fin par "  return { mini, conseillee };\n}")
marqueur = "  return { mini, conseillee };\n}\n"
n = content.count(marqueur)
if n != 1:
    print(f"[ERREUR] marqueur fin dimensionnerPiece trouve {n} fois -> abandon"); exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_sectionsA"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

content = content.replace(marqueur, marqueur + "\n" + fn, 1)
open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] Fonction calculerSectionsCharpente inseree")
print("1 MODIFICATION APPLIQUEE")
