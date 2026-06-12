#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 2.B.2 : Selecteur de catalogue refondu
Transforme les radio buttons en cards cliquables elegantes.

A lancer depuis ~/Desktop/devia :
    python3 refonte_selecteur_catalogue.py

Apres : npm run build
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_selecteur_catalogue"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD : Tout le bloc selecteur de catalogue
# ================================================================

old_selecteur = '''{/* Selecteur de catalogue */}
              <div style={{ ...cardStyle, padding: 16, marginBottom: 16, background: "#0f1117" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                  <span style={{ fontSize: 16 }}>&#x1F4D6;</span>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>Catalogue a utiliser pour ce devis</div>
                </div>
                <div style={{ display: "grid", gap: 8 }}>
                  <label style={{ display: "flex", alignItems: "center", gap: 10, padding: 10, borderRadius: 6, background: catalogChoice === "marche" ? "#f0c04018" : "transparent", border: catalogChoice === "marche" ? "1px solid #f0c040" : "1px solid #1e2231", cursor: "pointer" }}>
                    <input type="radio" name="catalog" checked={catalogChoice === "marche"}
                      onChange={() => setCatalogChoice("marche")}
                      style={{ accentColor: "#f0c040" }} />
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600 }}>Catalogue marche DEVIA</div>
                      <div style={{ fontSize: 12, color: "#545870" }}>{marchePrix.length} materiaux - prix moyens du marche</div>
                    </div>
                  </label>
                  <label style={{ display: "flex", alignItems: "center", gap: 10, padding: 10, borderRadius: 6, background: catalogChoice === "perso" ? "#3ecf8e18" : "transparent", border: catalogChoice === "perso" ? "1px solid #3ecf8e" : "1px solid #1e2231", cursor: "pointer" }}>
                    <input type="radio" name="catalog" checked={catalogChoice === "perso"}
                      onChange={() => setCatalogChoice("perso")}
                      style={{ accentColor: "#3ecf8e" }} />
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600 }}>Mon catalogue d'entreprise</div>
                      <div style={{ fontSize: 12, color: "#545870" }}>{catalogueEntreprise.length} materiaux personnels</div>
                    </div>
                  </label>
                  {catalogChoice === "perso" && (
                    <label style={{ display: "flex", alignItems: "center", gap: 10, padding: "6px 10px", marginLeft: 28, fontSize: 13, cursor: "pointer", color: completeWithMarket ? "#e8eaf2" : "#545870" }}>
                      <input type="checkbox" checked={completeWithMarket}
                        onChange={(e) => setCompleteWithMarket(e.target.checked)}
                        style={{ accentColor: "#f0c040" }} />
                      <span>Completer les materiaux manquants avec les prix marche DEVIA</span>
                    </label>
                  )}
                </div>
              </div>'''

new_selecteur = '''{/* Selecteur de catalogue - v2 cards elegantes */}
              <div style={{ marginBottom: 20 }}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 12, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Catalogue a utiliser pour ce devis</label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  {/* Card MARCHE */}
                  <div onClick={() => setCatalogChoice("marche")}
                    style={{
                      position: "relative",
                      padding: 16,
                      borderRadius: 12,
                      background: catalogChoice === "marche" ? "rgba(240, 192, 64, 0.06)" : "rgba(255, 255, 255, 0.02)",
                      border: catalogChoice === "marche" ? "1px solid rgba(240, 192, 64, 0.45)" : "1px solid rgba(255, 255, 255, 0.06)",
                      cursor: "pointer",
                      transition: "all 0.18s",
                      boxShadow: catalogChoice === "marche" ? "0 0 0 3px rgba(240, 192, 64, 0.08), inset 0 0 0 1px rgba(240, 192, 64, 0.1)" : "none"
                    }}
                    onMouseEnter={(e) => { if (catalogChoice !== "marche") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.035)"; } }}
                    onMouseLeave={(e) => { if (catalogChoice !== "marche") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)"; } }}>
                    <div style={{ display: "flex", alignItems: "start", gap: 10, marginBottom: 6 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: 8,
                        background: catalogChoice === "marche" ? "linear-gradient(135deg, rgba(240, 192, 64, 0.25), rgba(240, 192, 64, 0.1))" : "rgba(255, 255, 255, 0.04)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        flexShrink: 0,
                        transition: "background 0.18s"
                      }}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={catalogChoice === "marche" ? "#f0c040" : "#7a7d92"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <div style={{ fontSize: 13, fontWeight: 600, color: catalogChoice === "marche" ? "#f5f6fa" : "#d0d2dc" }}>Marche DEVIA</div>
                          {catalogChoice === "marche" && (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: "auto" }}>
                              <path d="M20 6L9 17l-5-5"/>
                            </svg>
                          )}
                        </div>
                        <div style={{ fontSize: 11, color: "#7a7d92", marginTop: 2 }}>{marchePrix.length} materiaux du marche</div>
                      </div>
                    </div>
                  </div>
                  {/* Card PERSO */}
                  <div onClick={() => setCatalogChoice("perso")}
                    style={{
                      position: "relative",
                      padding: 16,
                      borderRadius: 12,
                      background: catalogChoice === "perso" ? "rgba(62, 207, 142, 0.06)" : "rgba(255, 255, 255, 0.02)",
                      border: catalogChoice === "perso" ? "1px solid rgba(62, 207, 142, 0.45)" : "1px solid rgba(255, 255, 255, 0.06)",
                      cursor: "pointer",
                      transition: "all 0.18s",
                      boxShadow: catalogChoice === "perso" ? "0 0 0 3px rgba(62, 207, 142, 0.08), inset 0 0 0 1px rgba(62, 207, 142, 0.1)" : "none"
                    }}
                    onMouseEnter={(e) => { if (catalogChoice !== "perso") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.035)"; } }}
                    onMouseLeave={(e) => { if (catalogChoice !== "perso") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)"; } }}>
                    <div style={{ display: "flex", alignItems: "start", gap: 10, marginBottom: 6 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: 8,
                        background: catalogChoice === "perso" ? "linear-gradient(135deg, rgba(62, 207, 142, 0.25), rgba(62, 207, 142, 0.1))" : "rgba(255, 255, 255, 0.04)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        flexShrink: 0,
                        transition: "background 0.18s"
                      }}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={catalogChoice === "perso" ? "#3ecf8e" : "#7a7d92"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                          <circle cx="12" cy="7" r="4" />
                        </svg>
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <div style={{ fontSize: 13, fontWeight: 600, color: catalogChoice === "perso" ? "#f5f6fa" : "#d0d2dc" }}>Mon catalogue</div>
                          {catalogChoice === "perso" && (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: "auto" }}>
                              <path d="M20 6L9 17l-5-5"/>
                            </svg>
                          )}
                        </div>
                        <div style={{ fontSize: 11, color: "#7a7d92", marginTop: 2 }}>{catalogueEntreprise.length} materiaux personnels</div>
                      </div>
                    </div>
                  </div>
                </div>
                {catalogChoice === "perso" && (
                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "10px 14px",
                    marginTop: 10,
                    fontSize: 13,
                    cursor: "pointer",
                    background: "rgba(240, 192, 64, 0.04)",
                    border: "1px solid rgba(240, 192, 64, 0.18)",
                    borderRadius: 10,
                    color: completeWithMarket ? "#e8eaf2" : "#9ca0b8",
                    transition: "all 0.15s"
                  }}>
                    <input type="checkbox" checked={completeWithMarket}
                      onChange={(e) => setCompleteWithMarket(e.target.checked)}
                      style={{ accentColor: "#f0c040", width: 16, height: 16, cursor: "pointer" }} />
                    <span>Completer les materiaux manquants avec les prix marche DEVIA</span>
                  </label>
                )}
              </div>'''

if "Selecteur de catalogue - v2 cards elegantes" in content:
    print("[INFO] Selecteur deja refondu")
elif old_selecteur in content:
    content = content.replace(old_selecteur, new_selecteur, 1)
    print("[OK] Selecteur de catalogue refondu en cards elegantes")
else:
    print("[ERREUR] Bloc selecteur non trouve exactement.")
    print("Aucune modification appliquee.")
    sys.exit(1)

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 2.B.2 APPLIQUEE - Selecteur de catalogue")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Label en MAJUSCULES (coherent avec autres labels)")
print("  2. 2 cards cote a cote au lieu de listing vertical :")
print("     - Card 'Marche DEVIA' (gauche) : icone maison + jaune")
print("     - Card 'Mon catalogue' (droite) : icone utilisateur + vert")
print("  3. Au survol : bordure devient plus claire + fond legerement plus clair")
print("  4. Selectionnee : glow doux autour + cocher de validation")
print("  5. Compteur de materiaux affiche sur chaque card")
print("  6. Checkbox 'Completer' : pill jaune subtile quand visible")
print()
print("PROCHAINE ETAPE :")
print("  npm run build  # TESTER")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Refonte selecteur catalogue'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
