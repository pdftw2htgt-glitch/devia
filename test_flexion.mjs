// ============================================================
// TEST BRIQUE 1 : calcul flexion EC5 (formules cours TCB Gojon)
// Etalon = exemple solive du cours : 75x175, C18, portee 4m,
//          classe service 2, ENTRAXE 0.6m, G=0.5 Q=1.5 kN/m2
// Resultats attendus du prof : ELU 83%, Winst 75%, Wnet,fin 92%
// ============================================================

const BOIS = {
  C18: { fmk: 18, E: 9000 },
  C24: { fmk: 24, E: 11000 },
  C30: { fmk: 30, E: 12000 },
};
const GAMMA_M = 1.3; // bois massif

// kmod (cours EC5 p4) : [classe service][duree]
const KMOD = {
  1: { permanent: 0.6, long: 0.7, moyen: 0.8, court: 0.9, instant: 1.1 },
  2: { permanent: 0.6, long: 0.7, moyen: 0.8, court: 0.9, instant: 0.9 },
  3: { permanent: 0.5, long: 0.55, moyen: 0.65, court: 0.7, instant: 0.9 },
};
const KDEF = { 1: 0.6, 2: 0.8, 3: 2.0 };

const FLECHE_ADM = {
  courant:  { winst: 300, wnetfin: 200, wfin: 125 },
  agricole: { winst: 200, wnetfin: 150, wfin: 100 },
};

function verifierFlexion({ b, h, classe, portee, entraxe, G, Q, S, classeService, typeBatiment, dureeVariable }) {
  const mat = BOIS[classe];
  const L = portee * 1000; // mm
  const IGz = (b * Math.pow(h, 3)) / 12; // mm4

  // --- ELU : 1.35G + 1.5Q (+0.5S) ---
  let qELU = 1.35 * G + 1.5 * Q;
  if (S && S > 0) qELU += 0.5 * S;
  const qLin = qELU * entraxe;        // kN/m = N/mm
  const Mfz = (qLin * L * L) / 8;     // N.mm
  const sigmaMax = Mfz / (IGz / (0.5 * h));
  const kmod = KMOD[classeService][dureeVariable] || KMOD[classeService].moyen;
  const Fmd = mat.fmk * kmod / GAMMA_M;
  const tauxELU = (sigmaMax / Fmd) * 100;

  // --- ELS Winst : charges variables seules ---
  const qInst = Math.max(Q, S || 0);
  const qInstLin = qInst * entraxe;
  const Winst = (5 * qInstLin * Math.pow(L, 4)) / (384 * mat.E * IGz);
  const WinstAdm = L / FLECHE_ADM[typeBatiment].winst;
  const tauxWinst = (Winst / WinstAdm) * 100;

  // --- ELS Wnet,fin : G(1+psi2*kdef) + Q(1+psi2*kdef) ---
  const kdef = KDEF[classeService];
  const psi2_G = 1, psi2_Q = 0.3;
  const qNetFin = G * (1 + psi2_G * kdef) + Q * (1 + psi2_Q * kdef);
  const qNetFinLin = qNetFin * entraxe;
  const WnetFin = (5 * qNetFinLin * Math.pow(L, 4)) / (384 * mat.E * IGz);
  const WnetFinAdm = L / FLECHE_ADM[typeBatiment].wnetfin;
  const tauxWnetFin = (WnetFin / WnetFinAdm) * 100;

  return { IGz, Mfz, sigmaMax, Fmd, kmod, tauxELU, Winst, WinstAdm, tauxWinst, WnetFin, WnetFinAdm, tauxWnetFin };
}

const r = verifierFlexion({
  b: 75, h: 175, classe: "C18", portee: 4, entraxe: 0.6,
  G: 0.5, Q: 1.5, S: 0,
  classeService: 2, typeBatiment: "courant", dureeVariable: "moyen",
});

const f = (x, d = 2) => Number(x).toFixed(d);
console.log("=== BRIQUE 1 : verif flexion vs cours prof ===\n");
console.log("IGz          :", f(r.IGz, 0), "mm4   (cours: 33 496 094)");
console.log("Mfz          :", f(r.Mfz, 0), "N.mm  (cours: 3 510 000)");
console.log("sigma_max    :", f(r.sigmaMax), "MPa   (cours: 9.16)");
console.log("Fm,d         :", f(r.Fmd), "MPa   (cours: 11)");
console.log("--> Taux ELU :", f(r.tauxELU), "%     (cours: 83%)");
console.log("");
console.log("Winst        :", f(r.Winst), "mm    (cours: 9.95)");
console.log("Winst adm    :", f(r.WinstAdm), "mm    (cours: 13.33)");
console.log("--> Taux Winst:", f(r.tauxWinst), "%    (cours: 75%)");
console.log("");
console.log("Wnet,fin     :", f(r.WnetFin), "mm    (cours: 18.31)");
console.log("Wnet,fin adm :", f(r.WnetFinAdm), "mm    (cours: 20)");
console.log("--> Taux Wnet,fin:", f(r.tauxWnetFin), "% (cours: 92%)");
