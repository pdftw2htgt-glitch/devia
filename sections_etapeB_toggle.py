#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Sections etape B : toggle mini/conseillee + tableau reactif"""
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

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_sectionsB"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) State sectionMode
apply(
    '  const [metreBrut, setMetreBrut] = useState(null);',
    '  const [metreBrut, setMetreBrut] = useState(null);\n  const [sectionMode, setSectionMode] = useState("conseillee"); // "mini" | "conseillee"',
    "State sectionMode"
)

# 2) Boutons mini/conseillee juste apres le bouton Exporter IFC
apply(
    '''                    Exporter IFC
                  </button>''',
    '''                    Exporter IFC
                  </button>
                  {[{ id: "mini", label: "Section mini" }, { id: "conseillee", label: "Section conseillee" }].map(m => (
                    <button key={m.id} onClick={() => setSectionMode(m.id)}
                      style={{
                        padding: "7px 14px", borderRadius: 8, cursor: "pointer",
                        fontSize: 12.5, fontWeight: sectionMode === m.id ? 600 : 500,
                        border: "1px solid " + (sectionMode === m.id ? "rgba(96,165,250,0.5)" : "rgba(255,255,255,0.08)"),
                        background: sectionMode === m.id ? "rgba(96,165,250,0.12)" : "transparent",
                        color: sectionMode === m.id ? "#60a5fa" : "#7a7d92",
                        transition: "all 0.12s"
                      }}>
                      {m.label}
                    </button>
                  ))}''',
    "Boutons mini/conseillee"
)

# 3) Passer sectionMode au PanneauTechnique
apply(
    "<PanneauTechnique data={metreData} params={view3DParams} zoneInfo={zoneInfo} />",
    "<PanneauTechnique data={metreData} params={view3DParams} zoneInfo={zoneInfo} sectionMode={sectionMode} />",
    "sectionMode passe au panneau"
)

# 4) PanneauTechnique accepte sectionMode
apply(
    "function PanneauTechnique({ data, params, zoneInfo }) {",
    'function PanneauTechnique({ data, params, zoneInfo, sectionMode = "conseillee" }) {',
    "PanneauTechnique : prop sectionMode"
)

# 5) Dans la cellule EC5, mettre en evidence la section choisie (gras + couleur)
apply(
    '''                    if (!dim) return <span style={{ color: "#545870" }}>-</span>;
                    return (
                      <span>
                        <span style={{ color: "#e8eaf2" }}>{dim.mini.b}x{dim.mini.h} {dim.mini.classe}</span>
                        <span style={{ color: "#545870" }}> / </span>
                        <span style={{ color: "#f0c040" }}>{dim.conseillee.b}x{dim.conseillee.h} {dim.conseillee.classe}</span>
                      </span>
                    );''',
    '''                    if (!dim) return <span style={{ color: "#545870" }}>-</span>;
                    const miniSel = sectionMode === "mini";
                    return (
                      <span>
                        <span style={{ color: miniSel ? "#60a5fa" : "#7a7d92", fontWeight: miniSel ? 700 : 400 }}>{dim.mini.b}x{dim.mini.h} {dim.mini.classe}</span>
                        <span style={{ color: "#545870" }}> / </span>
                        <span style={{ color: !miniSel ? "#60a5fa" : "#7a7d92", fontWeight: !miniSel ? 700 : 400 }}>{dim.conseillee.b}x{dim.conseillee.h} {dim.conseillee.classe}</span>
                      </span>
                    );''',
    "Mise en evidence section selon mode"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
