// ============================================================
// TEST BRIQUE 2 : balayage de sections + plus defavorable
// Reutilise le coeur flexion valide en Brique 1
// ============================================================

const BOIS = {
  C18: { fmk: 18, E: 9000 },
  C24: { fmk: 24, E: 11000 },
  C30: { fmk: 30, E: 12000 },
};
const GAMMA_M = 1.3;
const KMOD = {
  1: { permanent: 0.6, long: 0.7, moyen: 0.8, court: 0.9, instant: 1.1 },
  2: { permanent: 0.6, long: 0.7, moyen: 0.8, court: 0.9, instant: 0.9 },
  3: { permanent: 0.5, long: 0.55, moyen: 0.65, court: 0.7, instant: 0.9 },
};
const KDEF = { 1: 0.6, 2: 0.8, 3: 2.0 };
const FLECHE_ADM = {
  courant:  { winst: 300, wnetfin: 200 },
  agricole: { winst: 200, wnetfin: 150 },
};

// --- Liste de sections standard FR (b x h en mm) ---
const SECTIONS = [
  [38, 100], [38, 120], [38, 150], [38, 175], [38, 200], [38, 225],
  [50, 150], [50, 175], [50, 200], [50, 225], [50, 250],
  [63, 150], [63, 175], [63, 200], [63, 225], [63, 250],
  [75, 175], [75, 200], [75, 225], [75, 250], [75, 300],
  [100, 200], [100, 225], [100, 250], [100, 300],
  [150, 300], [150, 350], [150, 400],
];

function verifierFlexion({ b, h, classe, portee, entraxe, G, Q, S, classeService, typeBatiment, dureeVariable }) {
  const mat = BOIS[classe];
  const L = portee * 1000;
  const IGz = (b * Math.pow(h, 3)) / 12;

  let qELU = 1.35 * G + 1.5 * Q;
  if (S && S > 0) qELU += 0.5 * S;
  const qLin = qELU * entraxe;
  const Mfz = (qLin * L * L) / 8;
  const sigmaMax = Mfz / (IGz / (0.5 * h));
  const kmod = KMOD[classeService][dureeVariable] || KMOD[classeService].moyen;
  const Fmd = mat.fmk * kmod / GAMMA_M;
  const tauxELU = (sigmaMax / Fmd) * 100;

  const qInst = Math.max(Q, S || 0);
  const Winst = (5 * qInst * entraxe * Math.pow(L, 4)) / (384 * mat.E * IGz);
  const WinstAdm = L / FLECHE_ADM[typeBatiment].winst;
  const tauxWinst = (Winst / WinstAdm) * 100;

  const kdef = KDEF[classeService];
  const qNetFin = G * (1 + 1 * kdef) + Q * (1 + 0.3 * kdef);
  const WnetFin = (5 * qNetFin * entraxe * Math.pow(L, 4)) / (384 * mat.E * IGz);
  const WnetFinAdm = L / FLECHE_ADM[typeBatiment].wnetfin;
  const tauxWnetFin = (WnetFin / WnetFinAdm) * 100;

  // taux global = le plus defavorable des 3 verifications
  const tauxMax = Math.max(tauxELU, tauxWinst, tauxWnetFin);
  return { tauxELU, tauxWinst, tauxWnetFin, tauxMax };
}

// ============================================================
// MOTEUR : trouve section mini + conseillee, classe la + economique
// ============================================================
function dimensionner(charge) {
  const classes = ["C18", "C24", "C30"];
  const candidats = [];

  for (const classe of classes) {
    for (const [b, h] of SECTIONS) {
      const r = verifierFlexion({ ...charge, b, h, classe });
      if (r.tauxMax <= 100) {
        candidats.push({ b, h, classe, ...r, aire: b * h });
      }
    }
  }
  if (candidats.length === 0) return null;

  // SECTION MINI = celle qui passe avec le taux le plus ELEVE (la plus tendue, la + petite)
  // -> on prend la plus economique en matiere (aire mini), classe la moins chere (C18<C24<C30)
  const ordreClasse = { C18: 0, C24: 1, C30: 2 };
  const mini = [...candidats].sort((a, b) =>
    a.aire - b.aire || ordreClasse[a.classe] - ordreClasse[b.classe]
  )[0];

  // SECTION CONSEILLEE = taux le plus proche de 70%
  const conseillee = [...candidats].sort((a, b) =>
    Math.abs(a.tauxMax - 70) - Math.abs(b.tauxMax - 70)
  )[0];

  return { mini, conseillee, nbCandidats: candidats.length };
}

// ============================================================
// TEST : on reprend la solive du prof (doit passer en 75x175 C18 ~83%)
// ============================================================
const charge = {
  portee: 4, entraxe: 0.6, G: 0.5, Q: 1.5, S: 0,
  classeService: 2, typeBatiment: "courant", dureeVariable: "moyen",
};

const res = dimensionner(charge);
console.log("=== BRIQUE 2 : dimensionnement solive (portee 4m, entraxe 0.6m) ===\n");
if (!res) {
  console.log("Aucune section ne passe !");
} else {
  const fmt = (s) => `${s.b}x${s.h} ${s.classe} (ELU ${s.tauxELU.toFixed(0)}%, Winst ${s.tauxWinst.toFixed(0)}%, Wfin ${s.tauxWnetFin.toFixed(0)}% -> max ${s.tauxMax.toFixed(0)}%)`;
  console.log("Section MINI      :", fmt(res.mini));
  console.log("Section CONSEILLEE:", fmt(res.conseillee));
  console.log("Nb sections valides:", res.nbCandidats);
}

// Test 2 : une grande portee pour voir le moteur monter en section
console.log("\n=== Test portee 6m, entraxe 0.6m, avec neige ===\n");
const res2 = dimensionner({ ...charge, portee: 6, S: 0.9 });
if (res2) {
  const fmt = (s) => `${s.b}x${s.h} ${s.classe} (max ${s.tauxMax.toFixed(0)}%)`;
  console.log("Section MINI      :", fmt(res2.mini));
  console.log("Section CONSEILLEE:", fmt(res2.conseillee));
}
