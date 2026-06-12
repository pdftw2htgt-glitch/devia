#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Section C : Plans d'abonnement sur page Compte
- Plan actuel : DEVIA Charpente avec features detaillees
- Autres plans : DEVIA Menuiserie + DEVIA Maconnerie (Coming soon)
- Coherent avec design liquid glass
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_plans_abonnement"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# La section plans s'insere APRES la grille des 5 stats
# qui se termine juste avant </div>\n      </div>\n    )}
# On vise la fin de la condition {activeTab === "compte" &&
# ================================================================

# On cible la fin de la card Identite + Plan (juste avant la fermeture du activeTab compte)
# Le pattern : la fermeture du bloc 5 stats puis la fermeture de la card
# Structure : ...stats grid...
#             </div>  <-- ferme la card stats
#           </div>  <-- ferme le cardStyle Identite+Plan
#         </div>  <-- ferme le div principal
#       )}

# Mais en fait notre nouvelle section doit etre HORS de la cardStyle (a cote)
# Pas DANS la cardStyle Identite + Plan

# On cible la fermeture de la cardStyle Identite + Plan
# La structure : la grille 5 stats est dedans, puis la card ferme
# On insere notre nouvelle section JUSTE APRES la fermeture de cette card

# Pattern a cibler : la fin de la grille 5 stats (le )())()) qui ferme l'IIFE)
# Puis </div> qui ferme la cardStyle Identite

# Approche : on cherche le dernier `</div>\n      </div>\n    )}` du bloc compte
# Mais c'est fragile. Plus sur : on cherche un marqueur specifique avant la fin

# Strategie : insere apres la fermeture de la grille 5 stats
# Le code se termine par : ); })()}\n        </div>\n      </div>\n    )}

old_end_marker = '''            );
          })()}
        </div>
      </div>
    )}'''

new_with_plans = '''            );
          })()}
        </div>

        {/* Section Plans d'abonnement */}
        <div style={{ marginTop: 20 }}>
          <div style={{ marginBottom: 14 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, letterSpacing: "-0.01em", marginBottom: 2 }}>Votre abonnement</h3>
            <div style={{ color: "#7a7d92", fontSize: 12 }}>Plan actuel et offres a venir</div>
          </div>

          {/* PLAN ACTUEL : DEVIA Charpente */}
          <div style={{
            background: "linear-gradient(135deg, rgba(240, 192, 64, 0.06) 0%, rgba(240, 192, 64, 0.02) 100%)",
            border: "1px solid rgba(240, 192, 64, 0.25)",
            borderRadius: 14,
            padding: 20,
            marginBottom: 14,
            boxShadow: "0 0 0 1px rgba(255,255,255,0.02) inset"
          }}>
            <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between", gap: 14, marginBottom: 16, flexWrap: "wrap" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, flex: "1 1 auto", minWidth: 0 }}>
                <div style={{
                  width: 44, height: 44,
                  background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)",
                  borderRadius: 11,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0,
                  boxShadow: "0 4px 14px rgba(240, 192, 64, 0.25)"
                }}>
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0a0a0a" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
                  </svg>
                </div>
                <div style={{ minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3, flexWrap: "wrap" }}>
                    <span style={{ fontSize: 17, fontWeight: 700, color: "#f5f6fa", letterSpacing: "-0.01em" }}>DEVIA Charpente</span>
                    <span style={{
                      display: "inline-flex", alignItems: "center", gap: 5,
                      background: "rgba(62, 207, 142, 0.12)",
                      border: "1px solid rgba(62, 207, 142, 0.3)",
                      borderRadius: 999,
                      padding: "2px 9px",
                      fontSize: 10,
                      fontWeight: 600,
                      color: "#3ecf8e",
                      letterSpacing: "0.04em",
                      textTransform: "uppercase"
                    }}>
                      <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#3ecf8e" }}></span>
                      Plan actuel
                    </span>
                  </div>
                  <div style={{ color: "#9ca0b8", fontSize: 12 }}>Devis de charpente assistes par intelligence artificielle</div>
                </div>
              </div>
              <div style={{ textAlign: "right", flexShrink: 0 }}>
                <div style={{ fontSize: 11, color: "#7a7d92", marginBottom: 2 }}>Installation</div>
                <div style={{ fontSize: 16, fontWeight: 700, color: "#f5f6fa", fontVariantNumeric: "tabular-nums" }}>2 000 <span style={{ fontSize: 11, color: "#7a7d92", fontWeight: 500 }}>EUR</span></div>
                <div style={{ fontSize: 11, color: "#7a7d92", marginTop: 4 }}>puis</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "#f0c040", fontVariantNumeric: "tabular-nums" }}>35 <span style={{ fontSize: 11, color: "#7a7d92", fontWeight: 500 }}>EUR/mois</span></div>
              </div>
            </div>

            {/* Features */}
            <div style={{
              background: "rgba(0, 0, 0, 0.15)",
              border: "1px solid rgba(255, 255, 255, 0.04)",
              borderRadius: 10,
              padding: 14,
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: 8
            }}>
              {[
                "Devis IA illimites",
                "Visualisation 3D",
                "Catalogue personnalise",
                "Calculs Eurocode",
                "Export PDF"
              ].map(f => (
                <div key={f} style={{ display: "flex", alignItems: "center", gap: 8, color: "#e8eaf2", fontSize: 12 }}>
                  <div style={{
                    width: 18, height: 18, borderRadius: "50%",
                    background: "rgba(62, 207, 142, 0.12)",
                    border: "1px solid rgba(62, 207, 142, 0.3)",
                    display: "inline-flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0
                  }}>
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  </div>
                  <span>{f}</span>
                </div>
              ))}
            </div>
          </div>

          {/* AUTRES PLANS DEVIA : Coming soon */}
          <div style={{ marginTop: 18, marginBottom: 8 }}>
            <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 10 }}>Autres plans DEVIA</div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
            {[
              {
                nom: "DEVIA Menuiserie",
                desc: "Devis fenetres, portes, escaliers",
                color1: "#60a5fa",
                color2: "#3b82f6",
                icon: (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="1"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="12" y1="3" x2="12" y2="21"/>
                  </svg>
                )
              },
              {
                nom: "DEVIA Maconnerie",
                desc: "Devis gros oeuvre, fondations, murs",
                color1: "#a78bfa",
                color2: "#8b5cf6",
                icon: (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="14" width="6" height="6" rx="0.5"/><rect x="9" y="14" width="6" height="6" rx="0.5"/><rect x="16" y="14" width="6" height="6" rx="0.5"/><rect x="5" y="7" width="6" height="6" rx="0.5"/><rect x="12" y="7" width="6" height="6" rx="0.5"/>
                  </svg>
                )
              }
            ].map(plan => (
              <div key={plan.nom} style={{
                background: "rgba(255, 255, 255, 0.02)",
                border: "1px solid rgba(255, 255, 255, 0.05)",
                borderRadius: 12,
                padding: 16,
                transition: "all 0.18s",
                position: "relative",
                overflow: "hidden"
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.03)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.05)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)"; }}>
                {/* Halo decoratif */}
                <div style={{
                  position: "absolute",
                  top: -30, right: -30,
                  width: 100, height: 100,
                  background: "radial-gradient(circle, " + plan.color1 + "15 0%, transparent 70%)",
                  pointerEvents: "none"
                }}></div>
                <div style={{ display: "flex", alignItems: "center", gap: 11, marginBottom: 10, position: "relative" }}>
                  <div style={{
                    width: 38, height: 38,
                    background: "linear-gradient(135deg, " + plan.color1 + "30 0%, " + plan.color2 + "15 100%)",
                    border: "1px solid " + plan.color1 + "40",
                    borderRadius: 10,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    color: plan.color1,
                    flexShrink: 0
                  }}>
                    {plan.icon}
                  </div>
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div style={{ fontSize: 14, fontWeight: 700, color: "#e8eaf2", letterSpacing: "-0.005em", marginBottom: 2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{plan.nom}</div>
                    <div style={{ fontSize: 11, color: "#7a7d92", lineHeight: 1.4 }}>{plan.desc}</div>
                  </div>
                </div>
                <div style={{
                  display: "inline-flex", alignItems: "center", gap: 6,
                  background: "rgba(255, 255, 255, 0.04)",
                  border: "1px dashed rgba(255, 255, 255, 0.1)",
                  borderRadius: 999,
                  padding: "5px 12px",
                  fontSize: 11,
                  fontWeight: 500,
                  color: "#9ca0b8",
                  letterSpacing: "0.02em"
                }}>
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                  </svg>
                  Disponible bientot
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )}'''

if "Section Plans d'abonnement" in content:
    print("[INFO] Section Plans deja en place")
elif old_end_marker in content:
    content = content.replace(old_end_marker, new_with_plans, 1)
    print("[OK] Section Plans d'abonnement ajoutee")
    modifs += 1
else:
    print("[ERREUR] Fin du bloc compte non trouvee")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Nouvelle section 'Votre abonnement' apres les stats")
print("  2. Card plan actuel : DEVIA Charpente (gradient or, premium)")
print("     - Icone maison")
print("     - Badge 'Plan actuel' vert")
print("     - Prix : 2000 EUR install + 35 EUR/mois")
print("     - 5 features avec checks verts")
print("  3. Section 'Autres plans DEVIA' (Coming soon)")
print("     - DEVIA Menuiserie (bleu)")
print("     - DEVIA Maconnerie (violet)")
print("     - Badge dashed 'Disponible bientot'")
print("  4. Responsive : auto-fit grids")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
