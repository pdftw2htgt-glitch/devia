#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - IFC etape 3 : faire remonter le metre brut + bouton export IFC"""
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

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_ifc_bouton"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) Faire remonter le metre BRUT en plus de l'agrege (2e argument)
apply(
    "      onMetreRef.current(agregerMetre(buildResultViewer.metre, buildResultViewer.densiteBois || 450));",
    "      onMetreRef.current(agregerMetre(buildResultViewer.metre, buildResultViewer.densiteBois || 450), buildResultViewer.metre);",
    "metre brut remonte (2e arg)"
)

# 2) State metreBrut a cote de metreData
apply(
    "  const [metreData, setMetreData] = useState(null);",
    "  const [metreData, setMetreData] = useState(null);\n  const [metreBrut, setMetreBrut] = useState(null);",
    "State metreBrut ajoute"
)

# 3) Le callback onMetre stocke les deux (agrege + brut)
#    -> on remplace le simple setMetreData passe en prop par une fonction
apply(
    '<Viewer3D params={{ ...view3DParams, mode3D }} onMetre={setMetreData} />',
    '<Viewer3D params={{ ...view3DParams, mode3D }} onMetre={(agg, brut) => { setMetreData(agg); setMetreBrut(brut); }} />',
    "onMetre stocke agg + brut"
)

# 4) Fonction d'export (telechargement) + bouton, juste apres les boutons de mode
#    On insere le bouton dans la barre des modes (apres le .map des boutons technique/realiste)
apply(
    '''                  {[{ id: "technique", label: "Vue technique" }, { id: "realiste", label: "Vue realiste" }].map(m => (
                    <button key={m.id} onClick={() => setMode3D(m.id)}
                      style={{
                        padding: "7px 16px", borderRadius: 8, cursor: "pointer",
                        fontSize: 13, fontWeight: mode3D === m.id ? 600 : 500,
                        border: "1px solid " + (mode3D === m.id ? "rgba(240,192,64,0.5)" : "rgba(255,255,255,0.08)"),
                        background: mode3D === m.id ? "rgba(240,192,64,0.12)" : "transparent",
                        color: mode3D === m.id ? "#f0c040" : "#7a7d92",
                        transition: "all 0.12s"
                      }}>
                      {m.label}
                    </button>
                  ))}''',
    '''                  {[{ id: "technique", label: "Vue technique" }, { id: "realiste", label: "Vue realiste" }].map(m => (
                    <button key={m.id} onClick={() => setMode3D(m.id)}
                      style={{
                        padding: "7px 16px", borderRadius: 8, cursor: "pointer",
                        fontSize: 13, fontWeight: mode3D === m.id ? 600 : 500,
                        border: "1px solid " + (mode3D === m.id ? "rgba(240,192,64,0.5)" : "rgba(255,255,255,0.08)"),
                        background: mode3D === m.id ? "rgba(240,192,64,0.12)" : "transparent",
                        color: mode3D === m.id ? "#f0c040" : "#7a7d92",
                        transition: "all 0.12s"
                      }}>
                      {m.label}
                    </button>
                  ))}
                  <button
                    onClick={() => {
                      if (!metreBrut || metreBrut.length === 0) { alert("Genere d'abord un devis avec une charpente."); return; }
                      const ifc = genererIFC(metreBrut, view3DParams);
                      const blob = new Blob([ifc], { type: "application/x-step" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = "devia_charpente.ifc";
                      document.body.appendChild(a); a.click(); document.body.removeChild(a);
                      URL.revokeObjectURL(url);
                    }}
                    style={{
                      marginLeft: "auto", padding: "7px 16px", borderRadius: 8, cursor: "pointer",
                      fontSize: 13, fontWeight: 600,
                      border: "1px solid rgba(240,192,64,0.5)",
                      background: "rgba(240,192,64,0.12)", color: "#f0c040",
                      transition: "all 0.12s"
                    }}>
                    Exporter IFC
                  </button>''',
    "Bouton Exporter IFC ajoute"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
