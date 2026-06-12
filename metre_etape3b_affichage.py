#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Metre 3B : panneau technique visible sous la 3D"""
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

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_metre_3b"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) State metreData a cote de mode3D
apply(
    '  const [mode3D, setMode3D] = useState("technique"); // "technique" | "realiste"',
    '  const [mode3D, setMode3D] = useState("technique"); // "technique" | "realiste"\n  const [metreData, setMetreData] = useState(null);',
    "State metreData ajoute"
)

# 2) Composant PanneauTechnique insere juste avant Viewer3D
panneau = '''// ============================================================
// PANNEAU TECHNIQUE (metre + entraxes + assemblages) sous la 3D
// ============================================================
// Assemblages recommandes par type de piece (regles TYPES, a valider)
const ASSEMBLAGES = {
  "Panne": "Posee sur arbaletriers/poteaux. Assemblage par entaille (about) + echantignole de calage. Fixation tire-fond ou equerre.",
  "Chevron": "Cloue/visse sur pannes et sabliere. Entaille a mi-bois sur sabliere possible. Echantignole sur panne intermediaire.",
  "Sabliere": "Scellee/chevillee sur arase du mur. Assemblage d'angle a mi-bois ou tenon-mortaise. Ancrage par scellement chimique.",
  "Poteau": "Pied : sabot metallique sur platine chevillee. Tete : tenon-mortaise ou ferrure sur sabliere/panne.",
  "Faitage": "Assemblage des arbaletriers en tete : tenon-mortaise ou moise. Liaison par boulons traversants.",
  "Aretier": "Piece maitresse de croupe. Assemblage en tete sur faitage/poincon. Empannons rapportes par entaille sur l'aretier.",
  "Empannon": "Chevron court entaille sur l'aretier (coupe biaise) cote bas + sur sabliere. Cloue/visse.",
  "Empannon de croupe": "Identique empannon, sur le pan de croupe. Coupe d'onglet contre l'aretier.",
  "Liteau": "Cloue/agrafe perpendiculairement sur les chevrons. Entraxe selon pureau de la couverture.",
  "Echantignole": "Petit taquet cloue sur la panne, cale le chevron a la bonne pente.",
  "Divers": "Assemblage selon piece (voir plan d'execution).",
};

function PanneauTechnique({ data, params }) {
  if (!data || !data.groupes || data.groupes.length === 0) {
    return null;
  }
  const card = { background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 12, padding: 16, marginTop: 12 };
  const stat = { flex: 1, minWidth: 120, background: "rgba(240,192,64,0.06)", border: "1px solid rgba(240,192,64,0.18)", borderRadius: 10, padding: "12px 14px" };
  const statVal = { fontSize: 22, fontWeight: 700, color: "#f0c040", fontVariantNumeric: "tabular-nums" };
  const statLbl = { fontSize: 11, color: "#7a7d92", marginTop: 2, textTransform: "uppercase", letterSpacing: "0.04em" };
  const th = { textAlign: "left", padding: "8px 10px", fontSize: 11, color: "#7a7d92", textTransform: "uppercase", letterSpacing: "0.03em", borderBottom: "1px solid rgba(255,255,255,0.08)" };
  const td = { padding: "9px 10px", fontSize: 13, color: "#d0d2dc", borderBottom: "1px solid rgba(255,255,255,0.04)", fontVariantNumeric: "tabular-nums" };

  const fmt = (n, d) => Number(n).toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d });

  return (
    <div>
      {/* Etiquettes / stats */}
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 12 }}>
        <div style={stat}><div style={statVal}>{fmt(data.totalVolume, 3)} m3</div><div style={statLbl}>Volume bois</div></div>
        <div style={stat}><div style={statVal}>{fmt(data.totalPoids, 0)} kg</div><div style={statLbl}>Poids estime</div></div>
        <div style={stat}><div style={statVal}>{data.nbPieces}</div><div style={statLbl}>Pieces</div></div>
        <div style={stat}><div style={statVal}>{data.groupes.length}</div><div style={statLbl}>Types differents</div></div>
      </div>

      {/* Tableau de metre */}
      <div style={card}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#e8eaf2", marginBottom: 10 }}>Metre detaille</div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Piece</th>
                <th style={th}>Section (mm)</th>
                <th style={{ ...th, textAlign: "right" }}>Nb</th>
                <th style={{ ...th, textAlign: "right" }}>Long. unit. (m)</th>
                <th style={{ ...th, textAlign: "right" }}>Long. tot. (m)</th>
                <th style={{ ...th, textAlign: "right" }}>Volume (m3)</th>
                <th style={{ ...th, textAlign: "right" }}>Poids (kg)</th>
              </tr>
            </thead>
            <tbody>
              {data.groupes.map((g, i) => (
                <tr key={i}>
                  <td style={{ ...td, color: "#e8eaf2", fontWeight: 500 }}>{g.nom}</td>
                  <td style={td}>{g.section[0]} x {g.section[1]}</td>
                  <td style={{ ...td, textAlign: "right" }}>{g.nombre}</td>
                  <td style={{ ...td, textAlign: "right" }}>{fmt(g.longueurUnitMax, 2)}</td>
                  <td style={{ ...td, textAlign: "right" }}>{fmt(g.longueurTotale, 2)}</td>
                  <td style={{ ...td, textAlign: "right" }}>{fmt(g.volume, 3)}</td>
                  <td style={{ ...td, textAlign: "right", color: "#f0c040" }}>{fmt(g.poids, 0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div style={{ fontSize: 11, color: "#545870", marginTop: 8, fontStyle: "italic" }}>
          Essence : {data.essence || params.essence || "sapin"} - sections indicatives, a valider (DTU / Eurocode 5).
        </div>
      </div>

      {/* Assemblages recommandes */}
      <div style={card}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#e8eaf2", marginBottom: 10 }}>Assemblages recommandes (types)</div>
        {data.groupes.map((g, i) => (
          <div key={i} style={{ display: "flex", gap: 12, padding: "8px 0", borderBottom: i < data.groupes.length - 1 ? "1px solid rgba(255,255,255,0.04)" : "none" }}>
            <div style={{ minWidth: 130, fontSize: 13, fontWeight: 600, color: "#f0c040" }}>{g.nom}</div>
            <div style={{ fontSize: 12.5, color: "#a8abbd", lineHeight: 1.5 }}>{ASSEMBLAGES[g.nom] || ASSEMBLAGES["Divers"]}</div>
          </div>
        ))}
        <div style={{ fontSize: 11, color: "#545870", marginTop: 10, fontStyle: "italic" }}>
          Recommandations types a adapter au projet. A faire valider par un professionnel.
        </div>
      </div>
    </div>
  );
}

'''
apply("function Viewer3D({ params, onMetre }) {", panneau + "function Viewer3D({ params, onMetre }) {", "Composant PanneauTechnique insere")

# 3) Brancher onMetre + afficher le panneau sous la 3D
apply(
    '''                <div style={{ ...cardStyle, height: 420, padding: 0, overflow: "hidden" }}>
                  <Viewer3D params={{ ...view3DParams, mode3D }} />
                </div>
              </div>
            )}''',
    '''                <div style={{ ...cardStyle, height: 420, padding: 0, overflow: "hidden" }}>
                  <Viewer3D params={{ ...view3DParams, mode3D }} onMetre={setMetreData} />
                </div>
                <PanneauTechnique data={metreData} params={view3DParams} />
              </div>
            )}''',
    "onMetre branche + PanneauTechnique affiche"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
