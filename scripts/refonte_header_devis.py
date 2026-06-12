#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 2.B.3.a : Header devis genere + onglets internes
Refait :
1. Header du devis (titre, date, badge catalogue, boutons actions)
2. Bandeau 'Devis partiel'
3. Onglets internes (Devis / Vue 3D / Calcul) en style pills

A lancer depuis ~/Desktop/devia :
    python3 refonte_header_devis.py

Apres : npm run build
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_header_devis"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD 1 : Header complet du devis (titre + date + badge + bandeau + boutons)
# ================================================================

old_header = '''<div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
              <div>
                <h2 style={{ fontSize: 20, fontWeight: 700 }}>{result.projet ? result.projet.description : "Devis charpente"}</h2>
                <div style={{ color: "#545870", fontSize: 14, display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                  <span>{result.projet ? result.projet.commune : ""} - {new Date().toLocaleDateString("fr-FR")}</span>
                  {result._catalogSource && (
                    <span style={{
                      fontSize: 11,
                      fontWeight: 600,
                      padding: "2px 8px",
                      borderRadius: 12,
                      background: result._catalogSource === "perso" ? "#3ecf8e18" : (result._catalogSource === "perso+marche" ? "#a78bfa18" : "#f0c04018"),
                      color: result._catalogSource === "perso" ? "#3ecf8e" : (result._catalogSource === "perso+marche" ? "#a78bfa" : "#f0c040"),
                      border: "1px solid " + (result._catalogSource === "perso" ? "#3ecf8e44" : (result._catalogSource === "perso+marche" ? "#a78bfa44" : "#f0c04044"))
                    }}>
                      {result._catalogSource === "perso" ? "Catalogue perso" : (result._catalogSource === "perso+marche" ? "Perso + complement marche" : "Catalogue marche DEVIA")}
                    </span>
                  )}
                </div>
                {result._catalogSource === "perso" && (
                  <div style={{ marginTop: 12, padding: 12, background: "#f9731618", border: "1px solid #f97316", borderRadius: 8, display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: 18 }}>&#x26A0;&#xFE0F;</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 13, fontWeight: 600, color: "#f97316" }}>Devis partiel</div>
                      <div style={{ fontSize: 12, color: "#fdba74", marginTop: 2 }}>
                        Ce devis ne contient que les materiaux presents dans votre catalogue d&apos;entreprise.
                        Les autres postes (couverture, fixations, etc.) doivent etre ajoutes manuellement,
                        ou cochez &quot;Completer avec marche&quot; pour un devis complet.
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button style={btnSecondary} onClick={() => { setResult(null); setPrompt(""); }}>Nouveau</button>
                <button style={btnPrimary}>PDF</button>
              </div>
            </div>'''

new_header = '''<div style={{ marginBottom: 24 }}>
              <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between", gap: 16, marginBottom: 14, flexWrap: "wrap" }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6, flexWrap: "wrap" }}>
                    <h2 style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-0.015em", lineHeight: 1.2 }}>{result.projet ? result.projet.description : "Devis charpente"}</h2>
                    {result._catalogSource && (
                      <span style={{
                        fontSize: 10,
                        fontWeight: 600,
                        padding: "3px 9px",
                        borderRadius: 999,
                        letterSpacing: "0.02em",
                        textTransform: "uppercase",
                        background: result._catalogSource === "perso" ? "rgba(62, 207, 142, 0.1)" : (result._catalogSource === "perso+marche" ? "rgba(167, 139, 250, 0.1)" : "rgba(240, 192, 64, 0.1)"),
                        color: result._catalogSource === "perso" ? "#3ecf8e" : (result._catalogSource === "perso+marche" ? "#a78bfa" : "#f0c040"),
                        border: "1px solid " + (result._catalogSource === "perso" ? "rgba(62, 207, 142, 0.3)" : (result._catalogSource === "perso+marche" ? "rgba(167, 139, 250, 0.3)" : "rgba(240, 192, 64, 0.3)")),
                        display: "inline-flex", alignItems: "center", gap: 5
                      }}>
                        <span style={{ width: 5, height: 5, borderRadius: "50%", background: result._catalogSource === "perso" ? "#3ecf8e" : (result._catalogSource === "perso+marche" ? "#a78bfa" : "#f0c040") }}></span>
                        {result._catalogSource === "perso" ? "Catalogue perso" : (result._catalogSource === "perso+marche" ? "Perso + marche" : "Marche DEVIA")}
                      </span>
                    )}
                  </div>
                  <div style={{ color: "#7a7d92", fontSize: 13, display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                    {result.projet && result.projet.commune && (<>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
                      </svg>
                      <span>{result.projet.commune}</span>
                      <span style={{ opacity: 0.4 }}>&bull;</span>
                    </>)}
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                    <span>{new Date().toLocaleDateString("fr-FR")}</span>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
                  <button style={btnSecondary} onClick={() => { setResult(null); setPrompt(""); }}>Nouveau</button>
                  <button style={btnPrimary}>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                      </svg>
                      PDF
                    </span>
                  </button>
                </div>
              </div>
              {result._catalogSource === "perso" && (
                <div style={{ padding: 14, background: "rgba(249, 115, 22, 0.06)", border: "1px solid rgba(249, 115, 22, 0.25)", borderRadius: 12, display: "flex", alignItems: "start", gap: 12 }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 2 }}>
                    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "#fb923c", marginBottom: 3 }}>Devis partiel</div>
                    <div style={{ fontSize: 12, color: "#fdba74", lineHeight: 1.5 }}>
                      Ce devis ne contient que les materiaux presents dans votre catalogue d&apos;entreprise.
                      Pour un devis complet, cochez &quot;Completer avec marche&quot; lors de la prochaine generation.
                    </div>
                  </div>
                </div>
              )}
            </div>'''

if 'background: "rgba(249, 115, 22, 0.06)"' in content:
    print("[INFO] Header devis deja refondu")
elif old_header in content:
    content = content.replace(old_header, new_header, 1)
    print("[OK] Header devis refondu (titre + badge + bandeau + actions)")
else:
    print("[ERREUR] Header devis non trouve exactement.")
    print("Aucune modification appliquee.")
    sys.exit(1)

# ================================================================
# MOD 2 : Onglets internes (Devis / Vue 3D / Calcul)
# ================================================================

old_tabs = '''<div style={{ display: "flex", gap: 8, marginBottom: 16, borderBottom: "1px solid #1e2231" }}>
              {[{ id: "devis", label: "Devis" }, { id: "3d", label: "Vue 3D" }, { id: "calcul", label: "Calcul" }].map(t => (
                <button key={t.id} onClick={() => setActiveResultTab(t.id)}
                  style={{ background: activeResultTab === t.id ? "#0f1117" : "transparent", border: activeResultTab === t.id ? "1px solid #1e2231" : "1px solid transparent", borderBottom: activeResultTab === t.id ? "2px solid #f0c040" : "2px solid transparent", color: activeResultTab === t.id ? "#e8eaf2" : "#545870", padding: "8px 16px", cursor: "pointer", fontSize: 14, fontWeight: activeResultTab === t.id ? 600 : 400, borderRadius: "6px 6px 0 0" }}>
                  {t.label}
                </button>
              ))}
            </div>'''

new_tabs = '''<div style={{ display: "inline-flex", gap: 2, marginBottom: 20, background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 999, padding: 4 }}>
              {[{ id: "devis", label: "Devis" }, { id: "3d", label: "Vue 3D" }, { id: "calcul", label: "Calcul" }].map(t => (
                <button key={t.id} onClick={() => setActiveResultTab(t.id)}
                  style={{
                    background: activeResultTab === t.id ? "rgba(255,255,255,0.08)" : "transparent",
                    border: "none",
                    color: activeResultTab === t.id ? "#ffffff" : "#7a7d92",
                    borderRadius: 999,
                    padding: "7px 18px",
                    cursor: "pointer",
                    fontSize: 13,
                    fontWeight: activeResultTab === t.id ? 600 : 500,
                    letterSpacing: "-0.005em",
                    transition: "all 0.15s",
                    boxShadow: activeResultTab === t.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
                  }}
                  onMouseEnter={(e) => { if (activeResultTab !== t.id) e.currentTarget.style.color = "#d0d2dc"; }}
                  onMouseLeave={(e) => { if (activeResultTab !== t.id) e.currentTarget.style.color = "#7a7d92"; }}>
                  {t.label}
                </button>
              ))}
            </div>'''

if 'borderRadius: 999, padding: 4 }}>\n              {[{ id: "devis", label: "Devis" }' in content:
    print("[INFO] Onglets internes deja refondus")
elif old_tabs in content:
    content = content.replace(old_tabs, new_tabs, 1)
    print("[OK] Onglets internes refondus en style pills")
else:
    print("[WARN] Onglets internes non trouves exactement (peut-etre deja modifies)")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 2.B.3.a APPLIQUEE - Header devis + onglets")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Titre du devis :")
print("     - Plus grand (22px), letter-spacing serre")
print("     - Badge catalogue style pill avec point colore (a cote du titre)")
print("  2. Date + commune :")
print("     - Icones SVG fines (epingle + calendrier)")
print("     - Separateur 'bullet' subtil")
print("  3. Boutons actions :")
print("     - 'Nouveau' garde le style secondaire")
print("     - 'PDF' avec icone telechargement")
print("  4. Bandeau 'Devis partiel' :")
print("     - Icone SVG warning (au lieu d'emoji)")
print("     - Bordure et fond plus subtils mais visibles")
print("  5. Onglets Devis / Vue 3D / Calcul :")
print("     - Style pills coherent avec le menu principal")
print("     - Container arrondi + transitions douces")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Refonte design Session 2.B.3.a - Header devis + onglets'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
