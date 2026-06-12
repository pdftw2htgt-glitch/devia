#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Fix : portee de calcul realiste par type de piece (plafond 8m)"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()

old = '''                    const sk = zoneInfo ? zoneInfo.sk : 0.45;
                    const ch = ec5DescenteCharge(params.couverture || "tuile_terre", sk);
                    const charge = {
                      portee: g.longueurUnitMax,
                      entraxe: (g.nom === "Chevron" || g.nom === "Empannon" || g.nom === "Empannon de croupe") ? 0.6
                             : (g.nom === "Panne" || g.nom === "Panne faitiere") ? 1.5
                             : (g.nom === "Sabliere" || g.nom === "Aretier") ? 1.0
                             : 1.0,
                      G: ch.G, Q: ch.Q, S: ch.S,
                      classeService: 2, typeBatiment: "courant", dureeVariable: "court",
                    };'''

new = '''                    const sk = zoneInfo ? zoneInfo.sk : 0.45;
                    const ch = ec5DescenteCharge(params.couverture || "tuile_terre", sk);
                    // --- Portee de calcul realiste selon le type de piece (plafond 8m) ---
                    // Pannes/sablieres : reposent sur les fermes -> portee = entre-axe fermes (~3.5m)
                    // Chevrons/fermes/arbaletriers : longueur reelle
                    const ENTRAXE_FERMES = 3.5; // m (cours : fermes tous les ~3.5m)
                    const PORTEE_MAX = 8;        // plafond securite
                    let porteeCalc;
                    if (g.nom === "Panne" || g.nom === "Panne faitiere" || g.nom === "Sabliere") {
                      porteeCalc = ENTRAXE_FERMES; // appuis sur chaque ferme
                    } else {
                      porteeCalc = g.longueurUnitMax; // chevrons, fermes, arbaletriers : longueur reelle
                    }
                    porteeCalc = Math.min(porteeCalc, PORTEE_MAX);
                    const charge = {
                      portee: porteeCalc,
                      entraxe: (g.nom === "Chevron" || g.nom === "Empannon" || g.nom === "Empannon de croupe") ? 0.6
                             : (g.nom === "Panne" || g.nom === "Panne faitiere") ? 1.5
                             : (g.nom === "Sabliere" || g.nom === "Aretier") ? 1.0
                             : 1.0,
                      G: ch.G, Q: ch.Q, S: ch.S,
                      classeService: 2, typeBatiment: "courant", dureeVariable: "court",
                    };'''

n = content.count(old)
if n != 1:
    print(f"[ERREUR] ancre trouvee {n} fois (attendu 1) -> abandon")
    exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fix_portee"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")
content = content.replace(old, new, 1)
open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] Portee realiste par type de piece (plafond 8m)")
print("1 MODIFICATION APPLIQUEE")
