import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

BLOC_CAT = '''            // ---- Donnees categorielles (communes, types, couvertures, montants) ----
            const compteurVers = (obj, cle) => { obj[cle] = (obj[cle] || 0) + 1; };
            const parCommune = {};
            projects.forEach(p => { compteurVers(parCommune, (p.commune && String(p.commune).trim()) || "Non renseignee"); });
            const topCommunes = Object.keys(parCommune).map(k => ({ label: k, val: parCommune[k] })).sort((a, b) => b.val - a.val).slice(0, 6);
            const LABEL_TYPE = { charpente_trad: "Traditionnelle", traditionnelle: "Traditionnelle", fermette: "Fermette", monopente: "Monopente", carport: "Carport", hangar: "Hangar", appentis: "Appentis", "4_pans": "4 pans", terrasse: "Terrasse", etage: "Plancher etage", balcon: "Balcon", garde_corps: "Garde-corps", sas_liaison: "Sas", multi: "Multi-ouvrages", autre: "Autre" };
            const parType = {};
            projects.forEach(p => { const brut = p.type_charpente || (p.devis_data && p.devis_data.projet && p.devis_data.projet.type_projet) || ""; compteurVers(parType, LABEL_TYPE[brut] || "Autre"); });
            const topTypes = Object.keys(parType).map(k => ({ label: k, val: parType[k] })).sort((a, b) => b.val - a.val).slice(0, 7);
            const LABEL_COUV = { tuile_terre: "Tuile terre cuite", tuile_beton: "Tuile beton", ardoise: "Ardoise", bac_acier: "Bac acier", zinc: "Zinc", shingle: "Shingle", fibrociment: "Fibrociment" };
            const parCouv = {};
            projects.forEach(p => { const cv = p.devis_data && p.devis_data.projet && p.devis_data.projet.couverture; if (cv) compteurVers(parCouv, LABEL_COUV[cv] || cv); });
            const topCouv = Object.keys(parCouv).map(k => ({ label: k, val: parCouv[k] })).sort((a, b) => b.val - a.val).slice(0, 6);
            const montantsParMois = clesMois.map(c => projects.filter(p => dansMois(p.created_at, c)).reduce((s, p) => s + (Number(p.total_ttc) || 0), 0));
            const formatEuros = (v) => v >= 1000 ? (v / 1000).toFixed(1) + " k\\u20ac" : Math.round(v) + " \\u20ac";

            const graphBarresH = (paires, couleur, formatV) => {
              const W2 = 720, ligneH = 30, pT = 6, pL = 150, pR = 80;
              const H2 = pT + Math.max(1, paires.length) * ligneH + 6;
              const vMax = Math.max(1, Math.max.apply(null, paires.map(p2 => p2.val).concat([1])));
              return (
                <svg viewBox={"0 0 " + W2 + " " + H2} style={{ width: "100%", height: "auto", display: "block" }}>
                  {paires.map((p2, i) => {
                    const y2 = pT + i * ligneH;
                    const bw2 = Math.max(2, (p2.val / vMax) * (W2 - pL - pR));
                    return (
                      <g key={p2.label}>
                        <text x={pL - 10} y={y2 + ligneH / 2 + 4} fill="#9ca0b8" fontSize="12" textAnchor="end">{p2.label.length > 20 ? p2.label.slice(0, 19) + "\\u2026" : p2.label}</text>
                        <rect x={pL} y={y2 + 6} width={bw2} height={ligneH - 12} rx="4" fill={couleur} fillOpacity="0.85"><title>{p2.label + " : " + formatV(p2.val)}</title></rect>
                        <text x={pL + bw2 + 8} y={y2 + ligneH / 2 + 4} fill={couleur} fontSize="12" fontWeight="600">{formatV(p2.val)}</text>
                      </g>
                    );
                  })}
                </svg>
              );
            };

            const stats = ['''

ANC_GRILLE = '''              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 10, marginTop: 10 }}>
                {[
                  { titre: "Devis - " + nomMois[thisMonth] + " " + thisYear, g: graphBarres(devisParJour, devisParJour.map((v, i) => (i + 1) % 5 === 0 ? String(i + 1) : ""), "#60a5fa", (v) => String(v)) },
                  { titre: "Devis cumules - 12 mois", g: graphLigne(devisCumule, labelsMois, "#3ecf8e", (v) => String(v)) },
                  { titre: "Tokens IA par mois", g: graphBarres(tokensParMois, labelsMois, "#f0c040", formatTokens) },
                  { titre: "Empreinte CO2 cumulee", g: graphLigne(co2Cumule, labelsMois, "#3ecf8e", formatCO2) },
                ].map(c => (
                  <div key={c.titre} style={{ background: "rgba(255, 255, 255, 0.02)", borderRadius: 12, padding: 14, border: "1px solid rgba(255, 255, 255, 0.05)" }}>
                    <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: 8 }}>{c.titre}</div>
                    {c.g}
                  </div>
                ))}
              </div>'''

NOUV_GRILLE = '''              {(() => {
                const LISTE_GRAPHES = [
                  { id: "devisJour", titre: "Devis - " + nomMois[thisMonth] + " " + thisYear, rendu: () => graphBarres(devisParJour, devisParJour.map((v, i) => (i + 1) % 2 === 0 ? String(i + 1) : ""), "#60a5fa", (v) => String(v)) },
                  { id: "devisCumul", titre: "Devis cumules - 12 mois", rendu: () => graphLigne(devisCumule, labelsMois, "#3ecf8e", (v) => String(v)) },
                  { id: "montants", titre: "Montant devise par mois (TTC)", rendu: () => graphBarres(montantsParMois, labelsMois, "#a78bfa", formatEuros) },
                  { id: "tokens", titre: "Tokens IA par mois", rendu: () => graphBarres(tokensParMois, labelsMois, "#f0c040", formatTokens) },
                  { id: "co2", titre: "Empreinte CO2 cumulee", rendu: () => graphLigne(co2Cumule, labelsMois, "#3ecf8e", formatCO2) },
                  { id: "communes", titre: "Lieux de creation", rendu: () => graphBarresH(topCommunes, "#60a5fa", (v) => v + " devis") },
                  { id: "types", titre: "Types de structure", rendu: () => graphBarresH(topTypes, "#f0c040", (v) => v + " devis") },
                  { id: "couvertures", titre: "Couvertures utilisees", rendu: () => graphBarresH(topCouv, "#3ecf8e", (v) => v + " devis") },
                ];
                return (
                  <div style={{ marginTop: 14 }}>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 10 }}>
                      {LISTE_GRAPHES.map(gr => (
                        <button key={gr.id} onClick={() => basculerGraphe(gr.id)}
                          style={{ padding: "5px 11px", borderRadius: 20, cursor: "pointer", fontSize: 11, fontWeight: 500,
                            border: "1px solid " + (graphesActifs[gr.id] === true ? "rgba(240,192,64,0.5)" : "rgba(255,255,255,0.08)"),
                            background: graphesActifs[gr.id] === true ? "rgba(240,192,64,0.10)" : "transparent",
                            color: graphesActifs[gr.id] === true ? "#f0c040" : "#545870", transition: "all 0.12s" }}>
                          {gr.titre}
                        </button>
                      ))}
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 12 }}>
                      {LISTE_GRAPHES.filter(gr => graphesActifs[gr.id] === true).map(gr => (
                        <div key={gr.id} style={{ background: "rgba(255, 255, 255, 0.02)", borderRadius: 12, padding: 18, border: "1px solid rgba(255, 255, 255, 0.05)" }}>
                          <div style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500, letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: 10 }}>{gr.titre}</div>
                          {gr.rendu()}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })()}'''

ETAT = '''const [vue3D, setVue3D] = useState("assemble"); // assemble | explose | sol
  const GRAPHES_DEFAUT = { devisJour: true, devisCumul: true, montants: true, tokens: true, co2: true, communes: true, types: true, couvertures: true };
  const [graphesActifs, setGraphesActifs] = useState(() => { try { const s = localStorage.getItem("devia_graphes_compte"); if (s) return { ...GRAPHES_DEFAUT, ...JSON.parse(s) }; } catch (e) {} return { ...GRAPHES_DEFAUT }; });
  const basculerGraphe = (id) => setGraphesActifs(prev => { const nx = { ...prev, [id]: prev[id] === true ? false : true }; try { localStorage.setItem("devia_graphes_compte", JSON.stringify(nx)); } catch (e) {} return nx; });'''

REMPL = [
    ('const [vue3D, setVue3D] = useState("assemble"); // assemble | explose | sol', ETAT, 1),
    ('const labelsMois = clesMois.map((c, i) => i % 3 === 1 ? nomMois[c.m] : "");',
     'const labelsMois = clesMois.map((c) => nomMois[c.m]);', 1),
    ('const W2 = 320, H2 = 120, pB = 18, pT = 14, pL = 6, pR = 6;',
     'const W2 = 720, H2 = 200, pB = 22, pT = 18, pL = 8, pR = 8;', 1),
    ('const W2 = 320, H2 = 120, pB = 18, pT = 14, pL = 6, pR = 40;',
     'const W2 = 720, H2 = 200, pB = 22, pT = 18, pL = 8, pR = 56;', 1),
    ('fill="#545870" fontSize="9" textAnchor="middle"', 'fill="#545870" fontSize="11" textAnchor="middle"', 2),
    ('fontSize="10" fontWeight="600" textAnchor="end"', 'fontSize="12" fontWeight="600" textAnchor="end"', 2),
    ("            const stats = [", BLOC_CAT, 1),
    (ANC_GRILLE, NOUV_GRILLE, 1),
]

ok = True
for a, b, attendu in REMPL:
    n = txt.count(a)
    if n != attendu:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu", attendu, ":", a[:70].replace(chr(10), " / "))
        ok = False
if ok == False:
    raise SystemExit(1)

for a, b, attendu in REMPL:
    txt = txt.replace(a, b)

txt = txt.replace("\\\\u20ac", "\\u20ac").replace("\\\\u2026", "\\u2026")

shutil.copy(CHEMIN, CHEMIN + ".backup_compte_graphes2_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : graphiques empiles, activables, + communes / types / couvertures / montants")
