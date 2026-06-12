#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 4.B : Refonte page Parametres
Refait :
1. Header
2. Section 'Informations entreprise' (icone batiment)
3. Section 'Tarification' (icone $ ou %)
4. Section 'Mentions legales' (icone document)
5. Labels en MAJUSCULES
6. Bouton Sauvegarder cohérent

A lancer depuis ~/Desktop/devia :
    python3 refonte_page_parametres.py

Apres : npm run build
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_page_parametres"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD : Tout le bloc page Parametres
# ================================================================

old_block = '''<h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20 }}>Parametres</h2>
        <div style={cardStyle}>
          <div style={{ fontWeight: 600, marginBottom: 16, color: "#f0c040" }}>Informations entreprise</div>
          {[{ label: "Nom de l entreprise", key: "entreprise" }, { label: "SIRET", key: "siret" }, { label: "Adresse", key: "adresse" }].map(f => (
            <div key={f.key} style={{ marginBottom: 14 }}>
              <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>{f.label}</label>
              <input value={params[f.key]} onChange={e => setParams(prev => ({ ...prev, [f.key]: e.target.value }))} style={inputStyle} />
            </div>
          ))}
        </div>
        <div style={cardStyle}>
          <div style={{ fontWeight: 600, marginBottom: 16, color: "#f0c040" }}>Tarification</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
            {[{ label: "Taux horaire EUR/h", key: "tauxHoraire" }, { label: "TVA %", key: "tva" }, { label: "Marge %", key: "marge" }].map(f => (
              <div key={f.key}>
                <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>{f.label}</label>
                <input type="number" value={params[f.key]} onChange={e => setParams(prev => ({ ...prev, [f.key]: parseFloat(e.target.value) }))} style={inputStyle} />
              </div>
            ))}
          </div>
        </div>
        <div style={cardStyle}>
          <div style={{ fontWeight: 600, marginBottom: 16, color: "#f0c040" }}>Mentions legales</div>
          <textarea value={params.mentions} onChange={e => setParams(prev => ({ ...prev, mentions: e.target.value }))} rows={3} style={{ ...inputStyle, resize: "vertical" }} />
        </div>
        <button style={{ ...btnPrimary, padding: "12px 24px" }}>Sauvegarder</button>'''

new_block = '''<div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Parametres</h2>
          <div style={{ color: "#7a7d92", fontSize: 13 }}>Configurez votre entreprise et vos tarifs par defaut</div>
        </div>

        {/* Section Informations entreprise */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(240, 192, 64, 0.1)",
              border: "1px solid rgba(240, 192, 64, 0.2)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 21h18M5 21V7l8-4v18M19 21V11l-6-4"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="9" y1="12" x2="9.01" y2="12"/><line x1="9" y1="15" x2="9.01" y2="15"/><line x1="9" y1="18" x2="9.01" y2="18"/>
              </svg>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: "#e8eaf2" }}>Informations entreprise</div>
              <div style={{ color: "#7a7d92", fontSize: 12 }}>Ces informations apparaitront sur vos devis</div>
            </div>
          </div>
          {[{ label: "Nom de l'entreprise", key: "entreprise" }, { label: "SIRET", key: "siret" }, { label: "Adresse", key: "adresse" }].map(f => (
            <div key={f.key} style={{ marginBottom: 14 }}>
              <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>{f.label}</label>
              <input value={params[f.key]} onChange={e => setParams(prev => ({ ...prev, [f.key]: e.target.value }))} style={inputStyle} />
            </div>
          ))}
        </div>

        {/* Section Tarification */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(62, 207, 142, 0.1)",
              border: "1px solid rgba(62, 207, 142, 0.2)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
              </svg>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: "#e8eaf2" }}>Tarification par defaut</div>
              <div style={{ color: "#7a7d92", fontSize: 12 }}>Ces valeurs s&apos;appliquent automatiquement a vos devis</div>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
            {[
              { label: "Taux horaire", key: "tauxHoraire", suffix: "EUR/h" },
              { label: "TVA", key: "tva", suffix: "%" },
              { label: "Marge", key: "marge", suffix: "%" }
            ].map(f => (
              <div key={f.key}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>{f.label} <span style={{ color: "#7a7d92", fontWeight: 400, textTransform: "none" }}>({f.suffix})</span></label>
                <input type="number" value={params[f.key]} onChange={e => setParams(prev => ({ ...prev, [f.key]: parseFloat(e.target.value) }))} style={inputStyle} />
              </div>
            ))}
          </div>
        </div>

        {/* Section Mentions legales */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(96, 165, 250, 0.1)",
              border: "1px solid rgba(96, 165, 250, 0.2)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
              </svg>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: "#e8eaf2" }}>Mentions legales</div>
              <div style={{ color: "#7a7d92", fontSize: 12 }}>Texte affiche en bas de vos devis</div>
            </div>
          </div>
          <textarea value={params.mentions} onChange={e => setParams(prev => ({ ...prev, mentions: e.target.value }))} rows={3} style={{ ...inputStyle, resize: "vertical", lineHeight: 1.6 }} />
        </div>

        {/* Bouton Sauvegarder */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
          <button style={{
            ...btnPrimary,
            padding: "12px 28px",
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            boxShadow: "0 4px 14px rgba(240, 192, 64, 0.22)",
            transition: "transform 0.1s, box-shadow 0.15s"
          }}
          onMouseEnter={(e) => { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 8px 20px rgba(240, 192, 64, 0.3)"; }}
          onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 4px 14px rgba(240, 192, 64, 0.22)"; }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>
            </svg>
            Sauvegarder
          </button>
        </div>'''

if "Configurez votre entreprise et vos tarifs" in content:
    print("[INFO] Page Parametres deja refondue")
elif old_block in content:
    content = content.replace(old_block, new_block, 1)
    print("[OK] Page Parametres refondue (3 sections + icones + bouton)")
else:
    print("[ERREUR] Bloc page Parametres non trouve.")
    sys.exit(1)

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 4.B APPLIQUEE - Page Parametres")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Header :")
print("     - Titre 'Parametres' plus grand + sous-titre")
print("  2. Section 'Informations entreprise' :")
print("     - Icone batiment SVG (jaune)")
print("     - Sous-titre descriptif")
print("     - Labels en MAJUSCULES")
print("  3. Section 'Tarification par defaut' :")
print("     - Icone $ SVG (vert)")
print("     - Labels avec suffixe (EUR/h, %, %) entre parentheses")
print("  4. Section 'Mentions legales' :")
print("     - Icone document SVG (bleu)")
print("  5. Bouton 'Sauvegarder' :")
print("     - Icone disquette SVG")
print("     - Ombre doree + hover lift")
print("     - Aligne a droite")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Refonte design Session 4.B - Page Parametres'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
