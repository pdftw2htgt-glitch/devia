#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - State mode3D + bouton toggle Technique/Realiste au-dessus de la 3D"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()
modifs = 0

def apply(old, new, label):
    global content, modifs
    n = content.count(old)
    if n == 1:
        content = content.replace(old, new, 1); print(f"[OK] {label}"); modifs += 1
    elif n == 0:
        print(f"[WARN] {label} : NON trouve")
    else:
        print(f"[WARN] {label} : trouve {n}x (ambigu) -> ignore")

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_toggle_mode3d"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) State mode3D juste apres activeResultTab
apply(
    'const [activeResultTab, setActiveResultTab] = useState("devis");',
    'const [activeResultTab, setActiveResultTab] = useState("devis");\n  const [mode3D, setMode3D] = useState("technique"); // "technique" | "realiste"',
    "State mode3D ajoute"
)

# 2) Bloc Vue 3D : toggle + injection mode3D dans params
old_block = '''            {activeResultTab === "3d" && (
              <div style={{ ...cardStyle, height: 420, padding: 0, overflow: "hidden" }}>
                <Viewer3D params={view3DParams} />
              </div>
            )}'''
new_block = '''            {activeResultTab === "3d" && (
              <div>
                <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
                  {[{ id: "technique", label: "Vue technique" }, { id: "realiste", label: "Vue realiste" }].map(m => (
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
                </div>
                <div style={{ ...cardStyle, height: 420, padding: 0, overflow: "hidden" }}>
                  <Viewer3D params={{ ...view3DParams, mode3D }} />
                </div>
              </div>
            )}'''
apply(old_block, new_block, "Toggle Technique/Realiste + injection mode3D")

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
