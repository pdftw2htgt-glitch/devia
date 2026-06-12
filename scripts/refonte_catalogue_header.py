#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 3.A : Header Catalogue + onglets internes + bouton Ajouter
Refait :
1. Header de la page Catalogue (titre + badge count)
2. Onglets Marche DEVIA / Mon catalogue en style pills
3. Bouton '+ Ajouter un materiau' CTA marquant
4. Etat 'Aucun materiau' avec icone SVG (plus pro que l'emoji)

A lancer depuis ~/Desktop/devia :
    python3 refonte_catalogue_header.py

Apres : npm run build
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_catalogue_header"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD 1 : Header Catalogue + onglets internes
# ================================================================

old_header_tabs = '''<div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700 }}>Catalogue</h2>
          <Badge color="#60a5fa">
            {activeCatalogTab === "marche" ? marchePrix.length + " materiaux" : catalogueEntreprise.length + " materiaux"}
          </Badge>
        </div>

        {/* Onglets internes */}
        <div style={{ display: "flex", gap: 4, marginBottom: 20, borderBottom: "1px solid #1e2231" }}>
          {[
            { id: "marche", label: "Marche DEVIA", icon: "&#x1F4CA;" },
            { id: "perso", label: "Mon catalogue", icon: "&#x1F4DD;" }
          ].map(t => (
            <button key={t.id} onClick={() => setActiveCatalogTab(t.id)}
              style={{
                background: "transparent",
                border: "none",
                borderBottom: activeCatalogTab === t.id ? "2px solid #f0c040" : "2px solid transparent",
                color: activeCatalogTab === t.id ? "#f0c040" : "#545870",
                cursor: "pointer",
                padding: "10px 18px",
                fontSize: 14,
                fontWeight: activeCatalogTab === t.id ? 600 : 400,
                transition: "all 0.15s"
              }}
              dangerouslySetInnerHTML={{ __html: t.icon + " " + t.label }} />
          ))}
        </div>'''

new_header_tabs = '''<div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Catalogue</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>Gerez les prix de reference utilises pour vos devis</div>
          </div>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 6,
            background: "rgba(96, 165, 250, 0.08)",
            border: "1px solid rgba(96, 165, 250, 0.2)",
            borderRadius: 999,
            padding: "6px 14px",
            fontSize: 12,
            fontWeight: 600,
            color: "#60a5fa"
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#60a5fa" }}></span>
            {activeCatalogTab === "marche" ? marchePrix.length + " materiaux" : catalogueEntreprise.length + " materiaux"}
          </div>
        </div>

        {/* Onglets internes - style pills */}
        <div style={{ display: "inline-flex", gap: 2, marginBottom: 24, background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 999, padding: 4 }}>
          {[
            { id: "marche", label: "Marche DEVIA", color: "#f0c040" },
            { id: "perso", label: "Mon catalogue", color: "#3ecf8e" }
          ].map(t => (
            <button key={t.id} onClick={() => setActiveCatalogTab(t.id)}
              style={{
                background: activeCatalogTab === t.id ? "rgba(255,255,255,0.08)" : "transparent",
                border: "none",
                color: activeCatalogTab === t.id ? "#ffffff" : "#7a7d92",
                borderRadius: 999,
                padding: "8px 18px",
                cursor: "pointer",
                fontSize: 13,
                fontWeight: activeCatalogTab === t.id ? 600 : 500,
                letterSpacing: "-0.005em",
                transition: "all 0.15s",
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                boxShadow: activeCatalogTab === t.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
              }}
              onMouseEnter={(e) => { if (activeCatalogTab !== t.id) e.currentTarget.style.color = "#d0d2dc"; }}
              onMouseLeave={(e) => { if (activeCatalogTab !== t.id) e.currentTarget.style.color = "#7a7d92"; }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: activeCatalogTab === t.id ? t.color : "#3a3d4f", transition: "background 0.15s" }}></span>
              {t.label}
            </button>
          ))}
        </div>'''

if 'border: "1px solid rgba(96, 165, 250, 0.2)"' in content and "Gerez les prix de reference" in content:
    print("[INFO] Header + onglets deja refondus")
elif old_header_tabs in content:
    content = content.replace(old_header_tabs, new_header_tabs, 1)
    print("[OK] Header Catalogue + onglets refondus (titre + pills + badge)")
else:
    print("[ERREUR] Header/onglets non trouves.")
    sys.exit(1)

# ================================================================
# MOD 2 : Bouton '+ Ajouter un materiau'
# ================================================================

old_btn = '''<button
                    onClick={() => { resetCatalogForm(); setShowAddCatalogModal(true); }}
                    style={{ background: "#f0c040", color: "#08090c", border: "none", borderRadius: 8, padding: "12px 20px", cursor: "pointer", fontSize: 14, fontWeight: 700, whiteSpace: "nowrap" }}>
                    + Ajouter un materiau
                  </button>'''

new_btn = '''<button
                    onClick={() => { resetCatalogForm(); setShowAddCatalogModal(true); }}
                    style={{
                      background: "#f0c040",
                      color: "#0a0a0a",
                      border: "1px solid #f0c040",
                      borderRadius: 999,
                      padding: "11px 20px",
                      cursor: "pointer",
                      fontSize: 13,
                      fontWeight: 700,
                      letterSpacing: "0.01em",
                      whiteSpace: "nowrap",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 8,
                      boxShadow: "0 4px 14px rgba(240, 192, 64, 0.22)",
                      transition: "transform 0.1s, box-shadow 0.15s"
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 8px 20px rgba(240, 192, 64, 0.3)"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 4px 14px rgba(240, 192, 64, 0.22)"; }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    Ajouter un materiau
                  </button>'''

if "translateY(-1px)" in content and "rgba(240, 192, 64, 0.22)" in content:
    print("[INFO] Bouton Ajouter deja refondu")
elif old_btn in content:
    content = content.replace(old_btn, new_btn, 1)
    print("[OK] Bouton '+ Ajouter un materiau' refondu (icone SVG + hover lift)")
else:
    print("[WARN] Bouton Ajouter non trouve")

# ================================================================
# MOD 3 : Etat 'Aucun materiau' avec icone SVG
# ================================================================

old_empty = '''<div style={{ ...cardStyle, textAlign: "center", padding: 40 }}>
                    <div style={{ fontSize: 40, marginBottom: 12 }}>&#x1F4DD;</div>
                    <div style={{ color: "#545870", marginBottom: 8 }}>Aucun materiau dans votre catalogue.</div>
                    <div style={{ color: "#545870", fontSize: 13 }}>Bientot vous pourrez ajouter vos propres prix.</div>
                  </div>'''

new_empty = '''<div style={{ ...cardStyle, textAlign: "center", padding: "48px 24px" }}>
                    <div style={{
                      width: 56, height: 56, borderRadius: 14,
                      background: "rgba(255, 255, 255, 0.03)",
                      border: "1px solid rgba(255, 255, 255, 0.06)",
                      display: "inline-flex", alignItems: "center", justifyContent: "center",
                      marginBottom: 16
                    }}>
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/>
                      </svg>
                    </div>
                    <div style={{ color: "#e8eaf2", fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Aucun materiau dans votre catalogue</div>
                    <div style={{ color: "#7a7d92", fontSize: 13, maxWidth: 360, margin: "0 auto", lineHeight: 1.5 }}>Cliquez sur &quot;Ajouter un materiau&quot; pour creer votre premier prix personnalise.</div>
                  </div>'''

if 'rgba(255, 255, 255, 0.03)' in content and 'M14 2H6a2 2 0 00-2 2v16' in content:
    print("[INFO] Etat vide deja refondu")
elif old_empty in content:
    content = content.replace(old_empty, new_empty, 1)
    print("[OK] Etat 'Aucun materiau' refondu (icone SVG document)")
else:
    print("[WARN] Etat vide non trouve")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 3.A APPLIQUEE - Header Catalogue + onglets + bouton")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Header Catalogue :")
print("     - Titre 'Catalogue' plus grand + sous-titre descriptif")
print("     - Badge count (N materiaux) en pill bleue avec point")
print("  2. Onglets internes Marche DEVIA / Mon catalogue :")
print("     - Style pills coherent (comme menu principal)")
print("     - Point colore devant chaque onglet")
print("       (jaune pour marche, vert pour perso)")
print("  3. Bouton '+ Ajouter un materiau' :")
print("     - Icone SVG plus propre")
print("     - Ombre doree + hover lift -1px")
print("     - Texte simplifie")
print("  4. Etat 'Aucun materiau' :")
print("     - Icone SVG document (plus pro que l'emoji)")
print("     - Message plus accueillant")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Refonte design Session 3.A - Header Catalogue + onglets'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
