// ============================================================
// TEST BRIQUE 2b : sections realistes (ratio h/b<=3 + largeur mini/type)
// ============================================================
const BOIS = { C18:{fmk:18,E:9000}, C24:{fmk:24,E:11000}, C30:{fmk:30,E:12000} };
const GAMMA_M = 1.3;
const KMOD = {
  1:{permanent:0.6,long:0.7,moyen:0.8,court:0.9,instant:1.1},
  2:{permanent:0.6,long:0.7,moyen:0.8,court:0.9,instant:0.9},
  3:{permanent:0.5,long:0.55,moyen:0.65,court:0.7,instant:0.9},
};
const KDEF = {1:0.6,2:0.8,3:2.0};
const FLECHE_ADM = { courant:{winst:300,wnetfin:200}, agricole:{winst:200,wnetfin:150} };

const SECTIONS = [
  [38,100],[38,120],[38,150],[38,175],[38,200],[38,225],
  [50,150],[50,175],[50,200],[50,225],[50,250],
  [63,150],[63,175],[63,200],[63,225],[63,250],
  [75,175],[75,200],[75,225],[75,250],[75,300],
  [100,200],[100,225],[100,250],[100,300],
  [150,300],[150,350],[150,400],
];

// largeur mini realiste par type de piece (mm)
const LARGEUR_MINI = {
  Chevron: 60, Panne: 75, Sabliere: 75, Arbaletrier: 75,
  Ferme: 75, Poteau: 100, Entrait: 60, Defaut: 60,
};
const RATIO_MAX = 3; // h/b max

function verifierFlexion({ b,h,classe,portee,entraxe,G,Q,S,classeService,typeBatiment,dureeVariable }) {
  const mat = BOIS[classe];
  const L = portee*1000;
  const IGz = (b*Math.pow(h,3))/12;
  let qELU = 1.35*G + 1.5*Q; if (S&&S>0) qELU += 0.5*S;
  const Mfz = (qELU*entraxe*L*L)/8;
  const sigmaMax = Mfz/(IGz/(0.5*h));
  const kmod = KMOD[classeService][dureeVariable]||KMOD[classeService].moyen;
  const Fmd = mat.fmk*kmod/GAMMA_M;
  const tauxELU = (sigmaMax/Fmd)*100;
  const qInst = Math.max(Q,S||0);
  const Winst = (5*qInst*entraxe*Math.pow(L,4))/(384*mat.E*IGz);
  const tauxWinst = (Winst/(L/FLECHE_ADM[typeBatiment].winst))*100;
  const kdef = KDEF[classeService];
  const qNetFin = G*(1+1*kdef) + Q*(1+0.3*kdef);
  const WnetFin = (5*qNetFin*entraxe*Math.pow(L,4))/(384*mat.E*IGz);
  const tauxWnetFin = (WnetFin/(L/FLECHE_ADM[typeBatiment].wnetfin))*100;
  return { tauxELU, tauxWinst, tauxWnetFin, tauxMax: Math.max(tauxELU,tauxWinst,tauxWnetFin) };
}

function dimensionner(charge, typePiece) {
  const wMini = LARGEUR_MINI[typePiece] || LARGEUR_MINI.Defaut;
  const ordreClasse = { C18:0, C24:1, C30:2 };
  const candidats = [];
  for (const classe of ["C18","C24","C30"]) {
    for (const [b,h] of SECTIONS) {
      if (b < wMini) continue;              // largeur mini par type
      if (h/b > RATIO_MAX) continue;        // ratio realiste
      const r = verifierFlexion({ ...charge, b, h, classe });
      if (r.tauxMax <= 100) candidats.push({ b,h,classe,...r, aire:b*h });
    }
  }
  if (!candidats.length) return null;
  const mini = [...candidats].sort((a,b)=> a.aire-b.aire || ordreClasse[a.classe]-ordreClasse[b.classe])[0];
  const conseillee = [...candidats].sort((a,b)=> Math.abs(a.tauxMax-70)-Math.abs(b.tauxMax-70))[0];
  return { mini, conseillee, nb: candidats.length };
}

const fmt = (s) => s ? `${s.b}x${s.h} ${s.classe} (max ${s.tauxMax.toFixed(0)}%)` : "AUCUNE";
function test(label, charge, type) {
  const r = dimensionner(charge, type);
  console.log(`\n${label}`);
  if (!r) { console.log("  -> aucune section ne passe"); return; }
  console.log("  MINI      :", fmt(r.mini));
  console.log("  CONSEILLEE:", fmt(r.conseillee));
}

const base = { classeService:2, typeBatiment:"courant", dureeVariable:"moyen" };

console.log("=== BRIQUE 2b : sections realistes (h/b<=3, largeur mini/type) ===");
test("SOLIVE/CHEVRON 4m, entraxe 0.6, G0.5 Q1.5 (etalon prof ~75x175)",
  { ...base, portee:4, entraxe:0.6, G:0.5, Q:1.5, S:0 }, "Chevron");
test("PANNE 5m, entraxe 1.5, G0.4 Q0 S0.9",
  { ...base, portee:5, entraxe:1.5, G:0.4, Q:0, S:0.9 }, "Panne");
test("CHEVRON 4.5m, entraxe 0.6, G0.35 S0.9",
  { ...base, portee:4.5, entraxe:0.6, G:0.35, Q:0, S:0.9 }, "Chevron");
test("ARBALETRIER 4.27m, entraxe 0.45, G1 S0.95 (cas cours p4)",
  { ...base, portee:4.27, entraxe:0.45, G:1, Q:0, S:0.95 }, "Arbaletrier");
