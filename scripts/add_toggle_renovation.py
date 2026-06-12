#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Ajouter un toggle 'Neuf / Renovation' en haut du formulaire devis
- State React typeTravaux ('neuf' par defaut)
- Toggle slide style iOS
- N'influence PAS la generation du devis pour l'instant (UI seulement)

A lancer depuis ~/Desktop/devia :
    python3 add_toggle_renovation.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_toggle_renovation"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter le state React typeTravaux
# ================================================================

old_state = 'const [commune, setCommune] = useState("");'
new_state = 'const [commune, setCommune] = useState("");\n  const [typeTravaux, setTypeTravaux] = useState("neuf");'

if "const [typeTravaux, setTypeTravaux]" in content:
    print("[INFO] State typeTravaux deja present")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] State typeTravaux ajoute (defaut: 'neuf')")
    modifs += 1
else:
    print("[ERREUR] State commune non trouve.")
    sys.exit(1)

# ================================================================
# MOD 2 : Ajouter le toggle UI juste apres le sous-titre du hero
# ================================================================

old_hero = '''<div style={{ marginBottom: 24, paddingTop: 4 }}>
              <p style={{ color: "#7a7d92", fontSize: 14, lineHeight: 1.55 }}>Decrivez votre projet en langage naturel. DEVIA genere un devis professionnel et une visualisation 3D.</p>
            </div>'''

new_hero = '''<div style={{ marginBottom: 20, paddingTop: 4 }}>
              <p style={{ color: "#7a7d92", fontSize: 14, lineHeight: 1.55 }}>Decrivez votre projet en langage naturel. DEVIA genere un devis professionnel et une visualisation 3D.</p>
            </div>

            {/* Toggle Neuf / Renovation */}
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 20,
              padding: "14px 18px",
              background: "rgba(255, 255, 255, 0.02)",
              border: "1px solid rgba(255, 255, 255, 0.05)",
              borderRadius: 12
            }}>
              <div>
                <div style={{ color: "#9ca0b8", fontSize: 11, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>
                  Type de travaux
                </div>
                <div style={{ color: "#e8eaf2", fontSize: 13, fontWeight: 500 }}>
                  {typeTravaux === "neuf" ? "Construction neuve" : "Renovation"}
                </div>
              </div>
              <div style={{
                display: "inline-flex",
                gap: 2,
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 999,
                padding: 4
              }}>
                {[
                  { id: "neuf", label: "Neuf", color: "#f0c040" },
                  { id: "renovation", label: "Renovation", color: "#3ecf8e" }
                ].map(t => (
                  <button key={t.id} type="button" onClick={() => setTypeTravaux(t.id)}
                    style={{
                      background: typeTravaux === t.id ? "rgba(255,255,255,0.08)" : "transparent",
                      border: "none",
                      color: typeTravaux === t.id ? "#ffffff" : "#7a7d92",
                      borderRadius: 999,
                      padding: "7px 16px",
                      cursor: "pointer",
                      fontSize: 13,
                      fontWeight: typeTravaux === t.id ? 600 : 500,
                      letterSpacing: "-0.005em",
                      transition: "all 0.15s",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 7,
                      boxShadow: typeTravaux === t.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
                    }}
                    onMouseEnter={(e) => { if (typeTravaux !== t.id) e.currentTarget.style.color = "#d0d2dc"; }}
                    onMouseLeave={(e) => { if (typeTravaux !== t.id) e.currentTarget.style.color = "#7a7d92"; }}>
                    <span style={{
                      width: 6, height: 6, borderRadius: "50%",
                      background: typeTravaux === t.id ? t.color : "#3a3d4f",
                      transition: "background 0.15s"
                    }}></span>
                    {t.label}
                  </button>
                ))}
              </div>
            </div>'''

if "Type de travaux" in content:
    print("[INFO] Toggle Type travaux deja present")
elif old_hero in content:
    content = content.replace(old_hero, new_hero, 1)
    print("[OK] Toggle Neuf/Renovation ajoute (en haut, avant prompt)")
    modifs += 1
else:
    print("[ERREUR] Hero non trouve. Le titre a peut-etre ete modifie autrement.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print(f"=== {modifs} modifications appliquees ===")
print()
print("CE QUI A CHANGE :")
print("  1. State React 'typeTravaux' ajoute (defaut 'neuf')")
print("  2. Toggle visuel en haut du formulaire :")
print("     - Label 'TYPE DE TRAVAUX' + statut actuel a gauche")
print("     - 2 boutons pills 'Neuf' / 'Renovation' a droite")
print("     - Point colore (jaune Neuf / vert Renovation)")
print("     - Anime au clic")
print()
print("IMPORTANT :")
print("  Le toggle est UI seulement.")
print("  Il n'influence pas encore la generation du devis.")
print("  La logique metier sera ajoutee plus tard.")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print('    git commit -m "Ajout toggle Neuf/Renovation (UI seulement)"')
print("    git push")
print()
print(f"BACKUP : {backup_name}")
