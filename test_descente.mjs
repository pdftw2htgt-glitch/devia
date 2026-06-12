// ============================================================
// TEST BRIQUE 3a : descente de charge G/Q/S
// !!! TOUTES LES VALEURS MARQUEES "A VALIDER" PAR LE PROF !!!
// ============================================================

// Poids couvertures (kg/m2) - depuis le registre DEVIA
const COUV_POIDS = {
  tuile_terre: 45, tuile_beton: 48, ardoise: 30,
  bac_acier: 10, zinc: 12, shingle: 12, fibrociment: 18,
};

// ---- CONSTANTES A VALIDER AVEC LE PROF ----
const POIDS_CHARPENTE = 0.15;   // kN/m2 - poids propre charpente (A VALIDER, cours utilisait 0.15)
const MU_NEIGE = 0.8;           // coef de forme toiture (A VALIDER, depend pente - cours ~0.8)
const Q_TOITURE = 0.0;          // kN/m2 - charge exploitation toiture non accessible (A VALIDER)
const G_TO_KN = 0.0098;         // 1 kg/m2 = 0.00981 kN/m2 (g=9.81)

// ============================================================
// Calcule G, Q, S (kN/m2) pour une charpente donnee
// ============================================================
function descenteCharge({ couverture, sk, pente }) {
  const poidsCouv = (COUV_POIDS[couverture] || 45) * G_TO_KN; // kg/m2 -> kN/m2

  // G = couverture + poids propre charpente
  const G = poidsCouv + POIDS_CHARPENTE;

  // S = neige au sol * coef de forme (projetee sur le rampant)
  // NOTE A VALIDER : le cours applique parfois un facteur lie a la pente
  const S = sk * MU_NEIGE;

  // Q = exploitation toiture (souvent 0 en toiture non accessible)
  const Q = Q_TOITURE;

  return {
    G: Math.round(G * 1000) / 1000,
    Q: Math.round(Q * 1000) / 1000,
    S: Math.round(S * 1000) / 1000,
    detail: {
      poidsCouv: Math.round(poidsCouv * 1000) / 1000,
      poidsCharpente: POIDS_CHARPENTE,
    },
  };
}

// ============================================================
// TESTS sur quelques cas
// ============================================================
function test(label, params) {
  const r = descenteCharge(params);
  console.log(`\n${label}`);
  console.log(`  couverture=${params.couverture}, sk=${params.sk} kN/m2, pente=${params.pente}deg`);
  console.log(`  G = ${r.G} kN/m2  (couv ${r.detail.poidsCouv} + charpente ${r.detail.poidsCharpente})`);
  console.log(`  Q = ${r.Q} kN/m2`);
  console.log(`  S = ${r.S} kN/m2  (sk ${params.sk} x mu ${MU_NEIGE})`);
}

console.log("=== BRIQUE 3a : descente de charge (VALEURS A VALIDER PROF) ===");
test("Hangar tuile, Lyon (sk~0.45)", { couverture:"tuile_terre", sk:0.45, pente:35 });
test("Hangar bac acier, Lyon (sk~0.45)", { couverture:"bac_acier", sk:0.45, pente:15 });
test("Maison tuile, Grenoble (sk~0.90)", { couverture:"tuile_beton", sk:0.90, pente:35 });
test("Chalet ardoise, Chamonix (sk~1.40)", { couverture:"ardoise", sk:1.40, pente:40 });

console.log("\n--- Comparaison avec exemples du cours ---");
console.log("Cours arbaletrier p4 : G=1.0, S=0.95 (charpente industrielle lourde)");
console.log("Nos valeurs sont plus legeres (charpente trad) - coherent si poids couv < tuile beton");
