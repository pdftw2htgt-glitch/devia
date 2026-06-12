#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 2.B.3.b : Tableau postes + totaux + stats projet + notes
Refait :
1. Stats projet (4 cards : Surface, Dimensions, Pente, Type)
2. Tableau des postes (headers, lignes, hover)
3. Totaux HT / TVA / TTC (style facture pro)
4. Notes techniques (mise en valeur)

A lancer depuis ~/Desktop/devia :
    python3 refonte_tableau_totaux.py

Apres : npm run build
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_tableau_totaux"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD 1 : Stats projet (4 cards)
# ================================================================

old_stats = '''<div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 }}>
                  {[
                    { label: "Surface", val: (result.projet.surface || "?") + "m2" },
                    { label: "Dimensions", val: (result.projet.longueur || "?") + "x" + (result.projet.largeur || "?") + "m" },
                    { label: "Pente", val: (result.projet.pente || "?") + " deg" },
                    { label: "Type", val: result.projet.type || "?" }
                  ].map(info => (
                    <div key={info.label} style={{ background: "#0f1117", borderRadius: 8, padding: 12, border: "1px solid #1e2231" }}>
                      <div style={{ color: "#545870", fontSize: 12 }}>{info.label}</div>
                      <div style={{ color: "#f0c040", fontWeight: 700, fontSize: 16, marginTop: 2 }}>{info.val}</div>
                    </div>
                  ))}
                </div>'''

new_stats = '''<div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 24 }}>
                  {[
                    { label: "Surface", val: (result.projet.surface || "?") + "m\u00b2" },
                    { label: "Dimensions", val: (result.projet.longueur || "?") + "\u00d7" + (result.projet.largeur || "?") + "m" },
                    { label: "Pente", val: (result.projet.pente || "?") + "\u00b0" },
                    { label: "Type", val: result.projet.type || "?" }
                  ].map(info => (
                    <div key={info.label} style={{
                      background: "rgba(255, 255, 255, 0.02)",
                      borderRadius: 12,
                      padding: "14px 16px",
                      border: "1px solid rgba(255, 255, 255, 0.05)",
                      transition: "border-color 0.15s"
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.05)"; }}>
                      <div style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 6 }}>{info.label}</div>
                      <div style={{ color: "#f5f6fa", fontWeight: 700, fontSize: 18, letterSpacing: "-0.01em" }}>{info.val}</div>
                    </div>
                  ))}
                </div>'''

if 'letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 6' in content:
    print("[INFO] Stats projet deja refondus")
elif old_stats in content:
    content = content.replace(old_stats, new_stats, 1)
    print("[OK] Stats projet refondus (cards minimal + uppercase labels)")
else:
    print("[ERREUR] Stats projet non trouves.")
    sys.exit(1)

# ================================================================
# MOD 2 : Tableau des postes (headers + body)
# ================================================================

old_table = '''<table style={{ width: "100%", borderCollapse: "collapse", marginBottom: 20 }}>
                  <thead>
                    <tr style={{ background: "#2a2e40" }}>
                      {["Categorie", "Designation", "U", "Qte", "PU HT", "Total HT"].map(h => (
                        <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "#545870", fontSize: 12 }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(result.postes || []).map((p, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid #1e2231", background: i % 2 === 0 ? "transparent" : "#0f1117" }}>
                        <td style={{ padding: "8px 12px", color: "#60a5fa", fontSize: 13 }}>{p.categorie}</td>
                        <td style={{ padding: "8px 12px", color: "#e8eaf2", fontSize: 13 }}>{p.designation}</td>
                        <td style={{ padding: "8px 12px", color: "#545870", fontSize: 13 }}>{p.unite}</td>
                        <td style={{ padding: "8px 12px", color: "#e8eaf2", fontSize: 13 }}>{p.quantite}</td>
                        <td style={{ padding: "8px 12px", color: "#e8eaf2", fontSize: 13 }}>{p.prixUnitaireHT ? p.prixUnitaireHT.toLocaleString("fr-FR") : 0} EUR</td>
                        <td style={{ padding: "8px 12px", color: "#f0c040", fontWeight: 600, fontSize: 13 }}>{p.totalHT ? p.totalHT.toLocaleString("fr-FR") : 0} EUR</td>
                      </tr>
                    ))}
                  </tbody>
                </table>'''

new_table = '''<div style={{ borderRadius: 12, overflow: "hidden", border: "1px solid rgba(255, 255, 255, 0.05)", marginBottom: 20 }}>
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ background: "rgba(255, 255, 255, 0.025)", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                        {[
                          { label: "Categorie", align: "left" },
                          { label: "Designation", align: "left" },
                          { label: "U", align: "left" },
                          { label: "Qte", align: "right" },
                          { label: "PU HT", align: "right" },
                          { label: "Total HT", align: "right" }
                        ].map(h => (
                          <th key={h.label} style={{ padding: "12px 16px", textAlign: h.align, color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>{h.label}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(result.postes || []).map((p, i) => (
                        <tr key={i} style={{ borderBottom: i < (result.postes || []).length - 1 ? "1px solid rgba(255, 255, 255, 0.04)" : "none", transition: "background 0.12s" }}
                          onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.025)"; }}
                          onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                          <td style={{ padding: "12px 16px", fontSize: 13 }}>
                            <span style={{ color: "#60a5fa", fontSize: 11, fontWeight: 600, padding: "3px 8px", background: "rgba(96, 165, 250, 0.08)", borderRadius: 999, letterSpacing: "0.02em" }}>{p.categorie}</span>
                          </td>
                          <td style={{ padding: "12px 16px", color: "#e8eaf2", fontSize: 13, fontWeight: 500 }}>{p.designation}</td>
                          <td style={{ padding: "12px 16px", color: "#7a7d92", fontSize: 13 }}>{p.unite}</td>
                          <td style={{ padding: "12px 16px", color: "#d0d2dc", fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{p.quantite}</td>
                          <td style={{ padding: "12px 16px", color: "#d0d2dc", fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{p.prixUnitaireHT ? p.prixUnitaireHT.toLocaleString("fr-FR") : 0} <span style={{ color: "#545870", fontSize: 11 }}>EUR</span></td>
                          <td style={{ padding: "12px 16px", color: "#f0c040", fontWeight: 600, fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{p.totalHT ? p.totalHT.toLocaleString("fr-FR") : 0} <span style={{ color: "#a8841f", fontSize: 11 }}>EUR</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>'''

if 'fontVariantNumeric: "tabular-nums"' in content:
    print("[INFO] Tableau deja refondu")
elif old_table in content:
    content = content.replace(old_table, new_table, 1)
    print("[OK] Tableau postes refondu (headers uppercase, hover, chiffres alignes)")
else:
    print("[ERREUR] Tableau non trouve.")
    print("Continuons avec les modifs deja faites...")

# ================================================================
# MOD 3 : Totaux (HT / TVA / TTC)
# ================================================================

old_totaux = '''<div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <div style={{ background: "#0f1117", border: "1px solid #1e2231", borderRadius: 10, padding: 16, minWidth: 220 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8, color: "#545870" }}>
                      <span>Total HT</span><span style={{ color: "#e8eaf2" }}>{result.totaux ? result.totaux.totalHT.toLocaleString("fr-FR") : 0} EUR</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12, color: "#545870" }}>
                      <span>TVA</span><span style={{ color: "#e8eaf2" }}>{result.totaux ? result.totaux.tva.toLocaleString("fr-FR") : 0} EUR</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700, fontSize: 18, color: "#f0c040", borderTop: "1px solid #1e2231", paddingTop: 12 }}>
                      <span>Total TTC</span><span>{result.totaux ? result.totaux.totalTTC.toLocaleString("fr-FR") : 0} EUR</span>
                    </div>
                  </div>
                </div>'''

new_totaux = '''<div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <div style={{
                    background: "linear-gradient(135deg, rgba(240, 192, 64, 0.04) 0%, rgba(255, 255, 255, 0.02) 100%)",
                    border: "1px solid rgba(240, 192, 64, 0.15)",
                    borderRadius: 14,
                    padding: "18px 22px",
                    minWidth: 280,
                    boxShadow: "0 4px 16px rgba(0, 0, 0, 0.2)"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                      <span style={{ color: "#7a7d92", fontSize: 12, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Total HT</span>
                      <span style={{ color: "#e8eaf2", fontSize: 14, fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>{result.totaux ? result.totaux.totalHT.toLocaleString("fr-FR") : 0} <span style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500 }}>EUR</span></span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, paddingBottom: 14, borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                      <span style={{ color: "#7a7d92", fontSize: 12, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>TVA</span>
                      <span style={{ color: "#e8eaf2", fontSize: 14, fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>{result.totaux ? result.totaux.tva.toLocaleString("fr-FR") : 0} <span style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500 }}>EUR</span></span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                      <span style={{ color: "#f0c040", fontSize: 13, fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase" }}>Total TTC</span>
                      <span style={{
                        color: "#f0c040",
                        fontWeight: 700,
                        fontSize: 24,
                        fontVariantNumeric: "tabular-nums",
                        letterSpacing: "-0.02em",
                        textShadow: "0 0 24px rgba(240, 192, 64, 0.25)"
                      }}>{result.totaux ? result.totaux.totalTTC.toLocaleString("fr-FR") : 0} <span style={{ fontSize: 14, fontWeight: 600 }}>EUR</span></span>
                    </div>
                  </div>
                </div>'''

if 'textShadow: "0 0 24px rgba(240, 192, 64, 0.25)"' in content:
    print("[INFO] Totaux deja refondus")
elif old_totaux in content:
    content = content.replace(old_totaux, new_totaux, 1)
    print("[OK] Totaux refondus (TTC grand jaune avec glow)")
else:
    print("[ERREUR] Totaux non trouves.")

# ================================================================
# MOD 4 : Notes techniques
# ================================================================

old_notes = '''<div style={{ marginTop: 16, padding: 14, background: "#0f1117", borderRadius: 8, border: "1px solid #1e2231" }}>
                    <div style={{ color: "#545870", fontSize: 12, marginBottom: 8, textTransform: "uppercase" }}>Notes techniques</div>
                    {result.notes.map((n, i) => <div key={i} style={{ color: "#e8eaf2", fontSize: 13, marginBottom: 4 }}>{n}</div>)}
                  </div>'''

new_notes = '''<div style={{ marginTop: 20, padding: 18, background: "rgba(255, 255, 255, 0.02)", borderRadius: 12, border: "1px solid rgba(255, 255, 255, 0.05)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca0b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
                      </svg>
                      <div style={{ color: "#9ca0b8", fontSize: 11, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Notes techniques</div>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                      {result.notes.map((n, i) => (
                        <div key={i} style={{ color: "#d0d2dc", fontSize: 13, lineHeight: 1.55, paddingLeft: 14, position: "relative" }}>
                          <span style={{ position: "absolute", left: 0, top: 8, width: 4, height: 4, borderRadius: "50%", background: "#7a7d92" }}></span>
                          {n}
                        </div>
                      ))}
                    </div>
                  </div>'''

if 'letterSpacing: "0.06em", textTransform: "uppercase" }}>Notes techniques</div>' in content:
    print("[INFO] Notes deja refondues")
elif old_notes in content:
    content = content.replace(old_notes, new_notes, 1)
    print("[OK] Notes techniques refondues (icone + bullets)")
else:
    print("[WARN] Notes non trouvees exactement")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 2.B.3.b APPLIQUEE - Tableau + Totaux + Stats + Notes")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Stats projet (4 cards) :")
print("     - Labels en MAJUSCULES tres subtiles")
print("     - Valeurs plus grandes en blanc (pas jaune)")
print("     - Symboles unicodes : m\u00b2, \u00d7, \u00b0")
print("  2. Tableau des postes :")
print("     - Headers uppercase tres subtils")
print("     - Categorie : pill bleu arrondi")
print("     - Chiffres alignes a droite avec tabular-nums")
print("     - Hover ligne : highlight subtil")
print("     - Plus de fond zebre")
print("  3. Totaux :")
print("     - Card avec gradient jaune subtil")
print("     - HT et TVA en discret")
print("     - TTC en gros (24px) jaune avec glow")
print("  4. Notes techniques :")
print("     - Icone info + label uppercase")
print("     - Bullets ronds devant chaque note")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Refonte design Session 2.B.3.b - Tableau + totaux'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
