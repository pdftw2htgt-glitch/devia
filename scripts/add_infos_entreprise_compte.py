#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Etape A : Section 'Infos entreprise' (accordeon) dans page Compte
- Affiche entreprise, siret, adresse (depuis state params)
- Plus taux horaire, TVA, marge (les 3 valeurs cles)
- Style accordeon : click sur header pour deplier/replier
- Lecture seule (modif se fait dans Parametres)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_compte_infos_entreprise"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter le state showInfosEntreprise pour l'accordeon
# ================================================================

old_state = 'const [renameError, setRenameError] = useState(null);'
new_state = '''const [renameError, setRenameError] = useState(null);
  const [showInfosEntreprise, setShowInfosEntreprise] = useState(false);'''

if "const [showInfosEntreprise" in content:
    print("[INFO] State showInfosEntreprise deja present")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] State showInfosEntreprise ajoute")
    modifs += 1
else:
    print("[ERREUR] State renameError non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Inserer l'accordeon Infos entreprise
# Juste avant la grille des 3 stats
# ================================================================

old_marker = '''          {/* 3 stats */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>'''

new_with_accordeon = '''          {/* Accordeon Infos entreprise */}
          <div style={{
            background: "rgba(255, 255, 255, 0.02)",
            border: "1px solid rgba(255, 255, 255, 0.05)",
            borderRadius: 12,
            marginBottom: 16,
            overflow: "hidden",
            transition: "border-color 0.15s"
          }}>
            <button
              onClick={() => setShowInfosEntreprise(!showInfosEntreprise)}
              style={{
                width: "100%",
                background: "transparent",
                border: "none",
                padding: "14px 16px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 12,
                color: "#e8eaf2",
                transition: "background 0.15s"
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{
                  width: 28, height: 28, borderRadius: 7,
                  background: "rgba(240, 192, 64, 0.1)",
                  border: "1px solid rgba(240, 192, 64, 0.2)",
                  display: "inline-flex", alignItems: "center", justifyContent: "center"
                }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M3 21h18M3 7h18M3 14h18M5 21V3h14v18"/>
                  </svg>
                </div>
                <div style={{ textAlign: "left" }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "#e8eaf2", marginBottom: 1 }}>Infos entreprise</div>
                  <div style={{ fontSize: 11, color: "#7a7d92" }}>{showInfosEntreprise ? "Cliquez pour replier" : "Cliquez pour deplier"}</div>
                </div>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"
                style={{ transform: showInfosEntreprise ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.2s" }}>
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </button>
            {showInfosEntreprise && (
              <div style={{
                padding: "0 16px 16px 16px",
                borderTop: "1px solid rgba(255, 255, 255, 0.04)",
                animation: "fadeInUp 0.2s ease-out"
              }}>
                {/* Bloc 1 - Identite legale */}
                <div style={{ marginTop: 16, marginBottom: 14 }}>
                  <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 10 }}>Identite</div>
                  <div style={{ display: "grid", gap: 10 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 12px", background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8 }}>
                      <span style={{ color: "#9ca0b8", fontSize: 12 }}>Nom de l'entreprise</span>
                      <span style={{ color: "#e8eaf2", fontSize: 13, fontWeight: 500, textAlign: "right" }}>{params.entreprise || <span style={{ color: "#545870", fontStyle: "italic" }}>Non renseigne</span>}</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 12px", background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8 }}>
                      <span style={{ color: "#9ca0b8", fontSize: 12 }}>SIRET</span>
                      <span style={{ color: "#e8eaf2", fontSize: 13, fontWeight: 500, fontVariantNumeric: "tabular-nums", textAlign: "right" }}>{params.siret || <span style={{ color: "#545870", fontStyle: "italic" }}>Non renseigne</span>}</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", padding: "10px 12px", background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8, gap: 12 }}>
                      <span style={{ color: "#9ca0b8", fontSize: 12, flexShrink: 0 }}>Adresse</span>
                      <span style={{ color: "#e8eaf2", fontSize: 13, fontWeight: 500, textAlign: "right" }}>{params.adresse || <span style={{ color: "#545870", fontStyle: "italic" }}>Non renseignee</span>}</span>
                    </div>
                  </div>
                </div>

                {/* Bloc 2 - Parametres financiers */}
                <div style={{ marginBottom: 6 }}>
                  <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 10 }}>Parametres financiers</div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>
                    <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8, padding: 12, textAlign: "center" }}>
                      <div style={{ color: "#7a7d92", fontSize: 10, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.04em" }}>Taux horaire</div>
                      <div style={{ color: "#e8eaf2", fontSize: 18, fontWeight: 700, letterSpacing: "-0.01em" }}>{params.tauxHoraire}<span style={{ color: "#7a7d92", fontSize: 12, marginLeft: 2 }}>EUR/h</span></div>
                    </div>
                    <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8, padding: 12, textAlign: "center" }}>
                      <div style={{ color: "#7a7d92", fontSize: 10, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.04em" }}>TVA</div>
                      <div style={{ color: "#e8eaf2", fontSize: 18, fontWeight: 700, letterSpacing: "-0.01em" }}>{params.tva}<span style={{ color: "#7a7d92", fontSize: 12, marginLeft: 2 }}>%</span></div>
                    </div>
                    <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8, padding: 12, textAlign: "center" }}>
                      <div style={{ color: "#7a7d92", fontSize: 10, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.04em" }}>Marge</div>
                      <div style={{ color: "#e8eaf2", fontSize: 18, fontWeight: 700, letterSpacing: "-0.01em" }}>{params.marge}<span style={{ color: "#7a7d92", fontSize: 12, marginLeft: 2 }}>%</span></div>
                    </div>
                  </div>
                </div>

                {/* Lien vers Parametres */}
                <div style={{ marginTop: 14, paddingTop: 12, borderTop: "1px solid rgba(255, 255, 255, 0.04)", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
                  <div style={{ color: "#545870", fontSize: 11, lineHeight: 1.4 }}>
                    Pour modifier ces informations,<br/>rendez-vous dans <span style={{ color: "#9ca0b8" }}>Parametres</span>.
                  </div>
                  <button onClick={() => setActiveTab("parametres")}
                    style={{
                      background: "rgba(240, 192, 64, 0.08)",
                      border: "1px solid rgba(240, 192, 64, 0.25)",
                      color: "#f0c040",
                      borderRadius: 8,
                      padding: "7px 13px",
                      fontSize: 12,
                      fontWeight: 600,
                      cursor: "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 6,
                      transition: "all 0.15s",
                      flexShrink: 0
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(240, 192, 64, 0.14)"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(240, 192, 64, 0.08)"; }}>
                    Modifier
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
                    </svg>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* 3 stats */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>'''

if "Accordeon Infos entreprise" in content:
    print("[INFO] Accordeon deja en place")
elif old_marker in content:
    content = content.replace(old_marker, new_with_accordeon, 1)
    print("[OK] Accordeon Infos entreprise ajoute")
    modifs += 1
else:
    print("[ERREUR] Marqueur '3 stats' non trouve")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. State showInfosEntreprise (accordeon ferme par defaut)")
print("  2. Accordeon insere entre l'avatar entreprise et les 3 stats")
print("     - Click sur l'en-tete -> deplie/replie")
print("     - Bloc Identite : Nom, SIRET, Adresse")
print("     - Bloc Parametres financiers : Taux/h, TVA, Marge")
print("     - Bouton 'Modifier' qui renvoie vers Parametres")
print()
print("COMMENT TESTER :")
print("  1. npm run build")
print("  2. Recharger Safari")
print("  3. Va sur Compte")
print("  4. Sous le profil, click sur 'Infos entreprise'")
print("  5. L'accordeon se deplie avec les infos en lecture seule")
print("  6. Click 'Modifier' -> bascule vers la page Parametres")
print()
print(f"BACKUP : {backup_name}")
