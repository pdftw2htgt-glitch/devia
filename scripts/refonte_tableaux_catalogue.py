#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 3.B.1 : Tableaux Catalogue (Marche DEVIA + Mon catalogue)
Refait :
1. Tableau Marche DEVIA (groupe par categorie)
2. Tableau Mon catalogue
Style coherent avec le tableau du devis genere :
- Headers UPPERCASE, fins, espaces
- Plus de fond zebra, juste separateurs subtils
- Hover sur ligne discret
- Chiffres alignes a droite (tabular-nums)
- Categorie en pill

A lancer depuis ~/Desktop/devia :
    python3 refonte_tableaux_catalogue.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_tableaux_catalogue"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD 1 : Tableau MARCHE DEVIA (a l'interieur de la boucle de categories)
# ================================================================

old_marche_table = '''<div style={{ ...cardStyle, padding: 0, overflow: "hidden" }}>
                          <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                              <tr style={{ background: "#0f1117" }}>
                                <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Designation</th>
                                <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Dimensions</th>
                                <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Unite</th>
                                <th style={{ padding: "10px 12px", textAlign: "right", color: "#545870", fontSize: 12, fontWeight: 600 }}>Prix HT</th>
                              </tr>
                            </thead>
                            <tbody>
                              {items.map((m, i) => (
                                <tr key={m.id} style={{ borderTop: "1px solid #1e2231", background: i % 2 === 0 ? "transparent" : "#0f111740" }}>
                                  <td style={{ padding: "10px 12px", fontSize: 13 }}>{m.designation}</td>
                                  <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.dimensions || "-"}</td>
                                  <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.unite}</td>
                                  <td style={{ padding: "10px 12px", textAlign: "right", fontSize: 13, color: "#f0c040", fontWeight: 600 }}>
                                    {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} EUR
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>'''

new_marche_table = '''<div style={{ borderRadius: 12, overflow: "hidden", border: "1px solid rgba(255, 255, 255, 0.05)", background: "rgba(255, 255, 255, 0.015)" }}>
                          <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                              <tr style={{ background: "rgba(255, 255, 255, 0.025)", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                                <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Designation</th>
                                <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Dimensions</th>
                                <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Unite</th>
                                <th style={{ padding: "12px 16px", textAlign: "right", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Prix HT</th>
                              </tr>
                            </thead>
                            <tbody>
                              {items.map((m, i) => (
                                <tr key={m.id} style={{ borderBottom: i < items.length - 1 ? "1px solid rgba(255, 255, 255, 0.04)" : "none", transition: "background 0.12s" }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.025)"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                                  <td style={{ padding: "12px 16px", fontSize: 13, color: "#e8eaf2", fontWeight: 500 }}>{m.designation}</td>
                                  <td style={{ padding: "12px 16px", fontSize: 13, color: "#9ca0b8" }}>{m.dimensions || "\u2014"}</td>
                                  <td style={{ padding: "12px 16px", fontSize: 13, color: "#7a7d92" }}>{m.unite}</td>
                                  <td style={{ padding: "12px 16px", textAlign: "right", fontSize: 13, color: "#f0c040", fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>
                                    {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} <span style={{ color: "#a8841f", fontSize: 11 }}>EUR</span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>'''

if 'fontVariantNumeric: "tabular-nums"' in content and 'borderBottom: i < items.length - 1' in content:
    print("[INFO] Tableau Marche deja refondu")
elif old_marche_table in content:
    content = content.replace(old_marche_table, new_marche_table, 1)
    print("[OK] Tableau Marche DEVIA refondu")
else:
    print("[ERREUR] Tableau Marche non trouve.")
    sys.exit(1)

# ================================================================
# MOD 2 : Tableau MON CATALOGUE (avec colonnes + Actions)
# ================================================================

# La partie thead + debut tbody (jusqu'au td Prix HT)
# Ensuite les boutons Modifier/Supprimer sont refondus separement en 3.B.2

old_perso_thead_tbody = '''<table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead>
                        <tr style={{ background: "#0f1117" }}>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Categorie</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Designation</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Dimensions</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Unite</th>
                          <th style={{ padding: "10px 12px", textAlign: "right", color: "#545870", fontSize: 12, fontWeight: 600 }}>Prix HT</th>
                          <th style={{ padding: "10px 12px", textAlign: "right", color: "#545870", fontSize: 12, fontWeight: 600 }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {catalogueEntreprise.map((m, i) => (
                          <tr key={m.id} style={{ borderTop: "1px solid #1e2231", background: i % 2 === 0 ? "transparent" : "#0f111740" }}>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#60a5fa" }}>{m.categorie}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13 }}>{m.designation}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.dimensions || "-"}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.unite}</td>
                            <td style={{ padding: "10px 12px", textAlign: "right", fontSize: 13, color: "#3ecf8e", fontWeight: 600 }}>
                              {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} EUR
                            </td>'''

new_perso_thead_tbody = '''<table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead>
                        <tr style={{ background: "rgba(255, 255, 255, 0.025)", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Categorie</th>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Designation</th>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Dimensions</th>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Unite</th>
                          <th style={{ padding: "12px 16px", textAlign: "right", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Prix HT</th>
                          <th style={{ padding: "12px 16px", textAlign: "right", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {catalogueEntreprise.map((m, i) => (
                          <tr key={m.id} style={{ borderBottom: i < catalogueEntreprise.length - 1 ? "1px solid rgba(255, 255, 255, 0.04)" : "none", transition: "background 0.12s" }}
                            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.025)"; }}
                            onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                            <td style={{ padding: "12px 16px", fontSize: 13 }}>
                              <span style={{ color: "#60a5fa", fontSize: 11, fontWeight: 600, padding: "3px 8px", background: "rgba(96, 165, 250, 0.08)", borderRadius: 999, letterSpacing: "0.02em" }}>{m.categorie}</span>
                            </td>
                            <td style={{ padding: "12px 16px", fontSize: 13, color: "#e8eaf2", fontWeight: 500 }}>{m.designation}</td>
                            <td style={{ padding: "12px 16px", fontSize: 13, color: "#9ca0b8" }}>{m.dimensions || "\u2014"}</td>
                            <td style={{ padding: "12px 16px", fontSize: 13, color: "#7a7d92" }}>{m.unite}</td>
                            <td style={{ padding: "12px 16px", textAlign: "right", fontSize: 13, color: "#3ecf8e", fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>
                              {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} <span style={{ color: "#1f7a4c", fontSize: 11 }}>EUR</span>
                            </td>'''

if 'borderBottom: i < catalogueEntreprise.length - 1' in content:
    print("[INFO] Tableau Mon catalogue deja refondu")
elif old_perso_thead_tbody in content:
    content = content.replace(old_perso_thead_tbody, new_perso_thead_tbody, 1)
    print("[OK] Tableau Mon catalogue refondu (headers uppercase, hover, pill categorie)")
else:
    print("[WARN] Tableau Mon catalogue non trouve exactement")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 3.B.1 APPLIQUEE - Tableaux Catalogue")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Tableau Marche DEVIA (par categorie) :")
print("     - Headers UPPERCASE tres subtils")
print("     - Plus de fond zebra")
print("     - Lignes separees par traits fins")
print("     - Hover : highlight discret")
print("     - Prix HT : chiffres tabular-nums + EUR plus discret")
print()
print("  2. Tableau Mon catalogue :")
print("     - Meme refonte que Marche DEVIA")
print("     - Categorie en pill bleu arrondi (style badge)")
print("     - Prix en vert avec EUR vert fonce")
print()
print("NOTE :")
print("  - Boutons Modifier/Supprimer pas encore refondus")
print("  - Cards d'intro pas encore refondues")
print("  -> Ce sera Session 3.B.2")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Refonte design Session 3.B.1 - Tableaux catalogue'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
