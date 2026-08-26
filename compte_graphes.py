import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

BLOC_DATA = '''            // ---- Donnees et mini-graphiques SVG ----
            const joursDuMois = new Date(thisYear, thisMonth + 1, 0).getDate();
            const devisParJour = Array.from({ length: joursDuMois }, () => 0);
            projetsThisMonth.forEach(p => { const d = new Date(p.created_at); devisParJour[d.getDate() - 1] += 1; });
            const clesMois = [];
            for (let i = 11; i >= 0; i--) { const d = new Date(thisYear, thisMonth - i, 1); clesMois.push({ y: d.getFullYear(), m: d.getMonth() }); }
            const nomMois = ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Juil", "Aou", "Sep", "Oct", "Nov", "Dec"];
            const labelsMois = clesMois.map((c, i) => i % 3 === 1 ? nomMois[c.m] : "");
            const dansMois = (dateStr, c) => { if (dateStr === null || dateStr === undefined) return false; const d = new Date(dateStr); return d.getMonth() === c.m && d.getFullYear() === c.y; };
            const devisParMois = clesMois.map(c => projects.filter(p => dansMois(p.created_at, c)).length);
            const debutFenetre = new Date(clesMois[0].y, clesMois[0].m, 1);
            const devisAvant = projects.filter(p => { if (p.created_at === null || p.created_at === undefined) return false; return new Date(p.created_at) < debutFenetre; }).length;
            const devisCumule = []; let accD = devisAvant;
            devisParMois.forEach(v => { accD += v; devisCumule.push(accD); });
            const tokensParMois = clesMois.map(c => usageLogs.filter(l => dansMois(l.created_at, c)).reduce((s, l) => s + (l.tokens_in || 0) + (l.tokens_out || 0), 0));
            const tokensAvant = Math.max(0, tokensTotal - tokensParMois.reduce((s, v) => s + v, 0));
            const co2Cumule = []; let accT = tokensAvant;
            tokensParMois.forEach(v => { accT += v; co2Cumule.push(accT * 0.000175); });

            const graphBarres = (valeurs, labels, couleur, formatV) => {
              const W2 = 320, H2 = 120, pB = 18, pT = 14, pL = 6, pR = 6;
              const n = Math.max(1, valeurs.length);
              const vMax = Math.max(1, Math.max.apply(null, valeurs));
              const zw = (W2 - pL - pR) / n;
              const bw = Math.max(2, zw * 0.65);
              return (
                <svg viewBox={"0 0 " + W2 + " " + H2} style={{ width: "100%", height: "auto", display: "block" }}>
                  {[0.5, 1].map(f2 => (
                    <line key={f2} x1={pL} y1={H2 - pB - f2 * (H2 - pB - pT)} x2={W2 - pR} y2={H2 - pB - f2 * (H2 - pB - pT)} stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
                  ))}
                  {valeurs.map((v, i) => {
                    const h2 = (v / vMax) * (H2 - pB - pT);
                    return (
                      <rect key={i} x={pL + i * zw + (zw - bw) / 2} y={H2 - pB - Math.max(v > 0 ? 2 : 0, h2)} width={bw} height={Math.max(v > 0 ? 2 : 0, h2)} rx="1.5" fill={couleur} fillOpacity={v > 0 ? 0.85 : 0.15}>
                        <title>{(labels[i] || String(i + 1)) + " : " + formatV(v)}</title>
                      </rect>
                    );
                  })}
                  {labels.map((l, i) => (l ? <text key={"t" + i} x={pL + i * zw + zw / 2} y={H2 - 5} fill="#545870" fontSize="9" textAnchor="middle">{l}</text> : null))}
                  <text x={W2 - pR} y={pT - 3} fill={couleur} fontSize="10" fontWeight="600" textAnchor="end">{"max " + formatV(vMax)}</text>
                </svg>
              );
            };

            const graphLigne = (valeurs, labels, couleur, formatV) => {
              const W2 = 320, H2 = 120, pB = 18, pT = 14, pL = 6, pR = 40;
              const n = Math.max(2, valeurs.length);
              const vMax = Math.max(1, Math.max.apply(null, valeurs));
              const px = (i) => pL + (i / (n - 1)) * (W2 - pL - pR);
              const py = (v) => H2 - pB - (v / vMax) * (H2 - pB - pT);
              const pts = valeurs.map((v, i) => px(i) + "," + py(v)).join(" ");
              const aire = pL + "," + (H2 - pB) + " " + pts + " " + px(valeurs.length - 1) + "," + (H2 - pB);
              const dern = valeurs.length > 0 ? valeurs[valeurs.length - 1] : 0;
              return (
                <svg viewBox={"0 0 " + W2 + " " + H2} style={{ width: "100%", height: "auto", display: "block" }}>
                  {[0.5, 1].map(f2 => (
                    <line key={f2} x1={pL} y1={H2 - pB - f2 * (H2 - pB - pT)} x2={W2 - pR} y2={H2 - pB - f2 * (H2 - pB - pT)} stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
                  ))}
                  <polygon points={aire} fill={couleur} fillOpacity="0.10" />
                  <polyline points={pts} fill="none" stroke={couleur} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
                  <circle cx={px(valeurs.length - 1)} cy={py(dern)} r="3" fill={couleur} />
                  <text x={W2 - 2} y={Math.max(pT, py(dern) - 6)} fill={couleur} fontSize="10" fontWeight="600" textAnchor="end">{formatV(dern)}</text>
                  {labels.map((l, i) => (l ? <text key={"t" + i} x={px(i)} y={H2 - 5} fill="#545870" fontSize="9" textAnchor="middle">{l}</text> : null))}
                </svg>
              );
            };

            const stats = ['''

TUILE_ABO = '''              {
                label: "Jours abo",
                val: "23",
                sub: null,
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>,
                color: "#a78bfa"
              },'''

TUILE_EAU = '''              {
                label: "Eau consommee",
                val: (co2TotalG * 0.005047).toFixed(2) + " L",
                sub: co2MonthG > 0 ? (co2MonthG * 0.005047).toFixed(2) + " L ce mois" : "0 L ce mois",
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 11-11.31 0z"/></svg>,
                color: "#60a5fa"
              },'''

FIN_ACTUELLE = '''                    {s.sub && (
                      <div style={{ marginTop: 6, color: "#545870", fontSize: 10, fontVariantNumeric: "tabular-nums" }}>{s.sub}</div>
                    )}
                  </div>
                ))}
              </div>
            );
          })()}'''

FIN_NOUVELLE = '''                    {s.sub && (
                      <div style={{ marginTop: 6, color: "#545870", fontSize: 10, fontVariantNumeric: "tabular-nums" }}>{s.sub}</div>
                    )}
                  </div>
                ))}
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 10, marginTop: 10 }}>
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
              </div>
              </div>
            );
          })()}'''

DEBUT_ACTUELLE = '''            return (
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
                gap: 10
              }}>'''

DEBUT_NOUVELLE = '''            return (
              <div>
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
                gap: 10
              }}>'''

REMPL = [
    ("            const stats = [", BLOC_DATA),
    (TUILE_ABO, TUILE_EAU),
    (DEBUT_ACTUELLE, DEBUT_NOUVELLE),
    (FIN_ACTUELLE, FIN_NOUVELLE),
]

ok = True
for a, b in REMPL:
    n = txt.count(a)
    if n != 1:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu 1 :", a[:70].replace(chr(10), " / "))
        ok = False
if ok == False:
    raise SystemExit(1)

for a, b in REMPL:
    txt = txt.replace(a, b)

shutil.copy(CHEMIN, CHEMIN + ".backup_compte_graphes_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : 4 graphiques dans Compte, tuile Jours abo remplacee par Eau consommee")
