#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Brique 3c : affichage sections mini/conseillee dans le panneau"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()
modifs = 0
def apply(old, new, label):
    global content, modifs
    n = content.count(old)
    if n == 1:
        content = content.replace(old, new, 1); print(f"[OK] {label}"); modifs += 1
    elif n == 0: print(f"[WARN] {label} : NON trouve")
    else: print(f"[WARN] {label} : {n}x ambigu -> ignore")

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_brique3c"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) PanneauTechnique accepte zoneInfo
apply(
    "function PanneauTechnique({ data, params }) {",
    "function PanneauTechnique({ data, params, zoneInfo }) {",
    "PanneauTechnique : prop zoneInfo"
)

# 2) Passer zoneInfo au composant
apply(
    "<PanneauTechnique data={metreData} params={view3DParams} />",
    "<PanneauTechnique data={metreData} params={view3DParams} zoneInfo={zoneInfo} />",
    "zoneInfo passe au panneau"
)

# 3) Dans le tableau de metre, calculer + afficher la section dimensionnee.
#    On ajoute 1 colonne "Section EC5 (mini / conseillee)" au tableau existant.
#    On cible l'en-tete du tableau (derniere colonne Poids) pour ajouter la colonne.
apply(
    '''                <th style={{ ...th, textAlign: "right" }}>Poids (kg)</th>
              </tr>
            </thead>''',
    '''                <th style={{ ...th, textAlign: "right" }}>Poids (kg)</th>
                <th style={{ ...th, textAlign: "right" }}>Section EC5 (mini / conseillee)</th>
              </tr>
            </thead>''',
    "En-tete colonne Section EC5"
)

# 4) Ajouter la cellule calculee dans chaque ligne (apres la cellule Poids)
apply(
    '''                  <td style={{ ...td, textAlign: "right", color: "#f0c040" }}>{fmt(g.poids, 0)}</td>
                </tr>
              ))}''',
    '''                  <td style={{ ...td, textAlign: "right", color: "#f0c040" }}>{fmt(g.poids, 0)}</td>
                  <td style={{ ...td, textAlign: "right", fontSize: 12 }}>{(() => {
                    const sk = zoneInfo ? zoneInfo.sk : 0.45;
                    const ch = ec5DescenteCharge(params.couverture || "tuile_terre", sk);
                    const charge = {
                      portee: g.longueurUnitMax,
                      entraxe: (g.nom === "Chevron" || g.nom === "Empannon" || g.nom === "Empannon de croupe") ? 0.6
                             : (g.nom === "Panne" || g.nom === "Panne faitiere") ? 1.5
                             : (g.nom === "Sabliere" || g.nom === "Aretier") ? 1.0
                             : 1.0,
                      G: ch.G, Q: ch.Q, S: ch.S,
                      classeService: 2, typeBatiment: "courant", dureeVariable: "court",
                    };
                    const dim = dimensionnerPiece(g.nom, charge);
                    if (!dim) return <span style={{ color: "#545870" }}>-</span>;
                    return (
                      <span>
                        <span style={{ color: "#e8eaf2" }}>{dim.mini.b}x{dim.mini.h} {dim.mini.classe}</span>
                        <span style={{ color: "#545870" }}> / </span>
                        <span style={{ color: "#f0c040" }}>{dim.conseillee.b}x{dim.conseillee.h} {dim.conseillee.classe}</span>
                      </span>
                    );
                  })()}</td>
                </tr>
              ))}''',
    "Cellule section EC5 calculee"
)

# 5) Note A VALIDER sous le tableau
apply(
    '''          Essence : {data.essence || params.essence || "sapin"} - sections indicatives, a valider (DTU / Eurocode 5).''',
    '''          Essence : {data.essence || params.essence || "sapin"} - sections indicatives, a valider (DTU / Eurocode 5).<br/>
          Dimensionnement EC5 (flexion) : portee = longueur piece, entraxe et descente de charge selon hypotheses - <b>valeurs a valider par un professionnel</b>.''',
    "Note A VALIDER mise a jour"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
