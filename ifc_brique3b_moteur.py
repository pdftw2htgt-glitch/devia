#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Brique 3b : insere le moteur de dimensionnement (sans affichage)"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()

if "function dimensionnerPiece" in content:
    print("[WARN] moteur deja present -> abandon")
    exit(1)

moteur = r'''// ============================================================
// MOTEUR DE DIMENSIONNEMENT EC5 (cours TCB Gojon)
// !!! Valeurs de descente de charge A VALIDER PAR LE PROF !!!
// ============================================================
const EC5_BOIS = { C18:{fmk:18,E:9000}, C24:{fmk:24,E:11000}, C30:{fmk:30,E:12000} };
const EC5_GAMMA_M = 1.3; // bois massif
const EC5_KMOD = {
  1:{permanent:0.6,long:0.7,moyen:0.8,court:0.9,instant:1.1},
  2:{permanent:0.6,long:0.7,moyen:0.8,court:0.9,instant:0.9},
  3:{permanent:0.5,long:0.55,moyen:0.65,court:0.7,instant:0.9},
};
const EC5_KDEF = {1:0.6,2:0.8,3:2.0};
const EC5_FLECHE_ADM = { courant:{winst:300,wnetfin:200}, agricole:{winst:200,wnetfin:150} };

// Sections standard FR (b x h mm)
const EC5_SECTIONS = [
  [38,100],[38,120],[38,150],[38,175],[38,200],[38,225],
  [50,150],[50,175],[50,200],[50,225],[50,250],
  [63,150],[63,175],[63,200],[63,225],[63,250],
  [75,175],[75,200],[75,225],[75,250],[75,300],
  [100,200],[100,225],[100,250],[100,300],
  [150,300],[150,350],[150,400],
];
const EC5_LARGEUR_MINI = {
  Chevron:60, Panne:75, Sabliere:75, Arbaletrier:75, "Panne faitiere":75,
  Ferme:75, Poteau:100, Entrait:60, Aretier:75, Empannon:60, "Empannon de croupe":60,
  Liteau:0, Echantignole:0, Defaut:60,
};
const EC5_RATIO_MAX = 3;

// Poids couvertures (kg/m2) -> recuperes du registre COUVERTURES
const EC5_COUV_POIDS = {
  tuile_terre:45, tuile_beton:48, ardoise:30, bac_acier:10, zinc:12, shingle:12, fibrociment:18,
};
// --- CONSTANTES DESCENTE DE CHARGE (A VALIDER PROF) ---
const EC5_POIDS_CHARPENTE = 0.15; // kN/m2 (A VALIDER)
const EC5_MU_NEIGE = 0.8;         // coef forme toiture (A VALIDER, depend pente)
const EC5_Q_TOITURE = 0.0;        // kN/m2 exploitation toiture (A VALIDER)
const EC5_G_TO_KN = 0.0098;       // kg/m2 -> kN/m2

function ec5DescenteCharge(couverture, sk) {
  const poidsCouv = (EC5_COUV_POIDS[couverture] || 45) * EC5_G_TO_KN;
  const G = poidsCouv + EC5_POIDS_CHARPENTE;
  const S = (sk || 0.45) * EC5_MU_NEIGE;
  const Q = EC5_Q_TOITURE;
  return { G, Q, S };
}

function ec5VerifierFlexion(o) {
  const mat = EC5_BOIS[o.classe];
  const L = o.portee * 1000;
  const IGz = (o.b * Math.pow(o.h, 3)) / 12;
  let qELU = 1.35*o.G + 1.5*o.Q; if (o.S>0) qELU += 0.5*o.S;
  const Mfz = (qELU*o.entraxe*L*L)/8;
  const sigmaMax = Mfz/(IGz/(0.5*o.h));
  const kmod = EC5_KMOD[o.classeService][o.dureeVariable] || EC5_KMOD[o.classeService].moyen;
  const Fmd = mat.fmk*kmod/EC5_GAMMA_M;
  const tauxELU = (sigmaMax/Fmd)*100;
  const qInst = Math.max(o.Q, o.S||0);
  const Winst = (5*qInst*o.entraxe*Math.pow(L,4))/(384*mat.E*IGz);
  const tauxWinst = (Winst/(L/EC5_FLECHE_ADM[o.typeBatiment].winst))*100;
  const kdef = EC5_KDEF[o.classeService];
  const qNetFin = o.G*(1+1*kdef) + o.Q*(1+0.3*kdef);
  const WnetFin = (5*qNetFin*o.entraxe*Math.pow(L,4))/(384*mat.E*IGz);
  const tauxWnetFin = (WnetFin/(L/EC5_FLECHE_ADM[o.typeBatiment].wnetfin))*100;
  return { tauxELU, tauxWinst, tauxWnetFin, tauxMax: Math.max(tauxELU,tauxWinst,tauxWnetFin) };
}

// Dimensionne UNE piece -> { mini, conseillee } ou null
function dimensionnerPiece(typePiece, charge) {
  const wMini = EC5_LARGEUR_MINI[typePiece] != null ? EC5_LARGEUR_MINI[typePiece] : EC5_LARGEUR_MINI.Defaut;
  if (wMini === 0) return null; // pieces non structurelles (liteau, echantignole)
  const ordreClasse = { C18:0, C24:1, C30:2 };
  const candidats = [];
  for (const classe of ["C18","C24","C30"]) {
    for (const [b,h] of EC5_SECTIONS) {
      if (b < wMini) continue;
      if (h/b > EC5_RATIO_MAX) continue;
      const r = ec5VerifierFlexion({ ...charge, b, h, classe });
      if (r.tauxMax <= 100) candidats.push({ b,h,classe,...r, aire:b*h });
    }
  }
  if (!candidats.length) return null;
  const mini = [...candidats].sort((a,b)=> a.aire-b.aire || ordreClasse[a.classe]-ordreClasse[b.classe])[0];
  const conseillee = [...candidats].sort((a,b)=> Math.abs(a.tauxMax-70)-Math.abs(b.tauxMax-70))[0];
  return { mini, conseillee };
}

'''

# Inserer juste avant le commentaire d'agregation du metre
anchor = "// AGREGATION DU METRE (regroupe par type de piece + totaux)"
n = content.count(anchor)
if n != 1:
    print(f"[ERREUR] ancre agregation trouvee {n} fois -> abandon")
    exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_brique3b"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

content = content.replace(anchor, moteur + anchor, 1)
open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] Moteur de dimensionnement insere (EC5_*, dimensionnerPiece, ec5DescenteCharge)")
print("1 MODIFICATION APPLIQUEE")
