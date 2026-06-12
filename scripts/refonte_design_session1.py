#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 1 / Refonte design : Design system Liquid Glass + Header
Modifie :
1. Les styles globaux (cardStyle, inputStyle, btnPrimary, btnSecondary)
   -> passage au look 'liquid glass' (translucide + flou + bordures fines)
2. Le header (logo + menu) -> style epure type Linear / iOS 26
3. Ajout d'un fond global avec gradient subtil et grain
4. Conservation 100% de la logique : aucune feature touchee

A lancer depuis ~/Desktop/devia :
    python3 refonte_design_session1.py

CE QUI NE CHANGE PAS :
- La logique de toutes les pages
- Les noms cardStyle/inputStyle/btnPrimary/btnSecondary (donc partout dans
  le code, les composants utilisent automatiquement le nouveau look)

CE QUI CHANGE VISUELLEMENT :
- Toutes les cards deviennent translucides avec flou
- Tous les inputs deviennent plus elegants
- Tous les boutons gagnent en classe
- Le header devient minimal et translucide
- Le fond global gagne un gradient subtil
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("package.json"):
    print("ERREUR : package.json introuvable. Lance depuis ~/Desktop/devia")
    sys.exit(1)

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_design_session1"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MODIFICATION 1 : Refonte des styles globaux (lignes 913-916)
# ================================================================

old_styles = '''const cardStyle = { background: "#13161f", border: "1px solid #1e2231", borderRadius: 12, padding: 20, marginBottom: 16 };
const inputStyle = { width: "100%", background: "#0f1117", border: "1px solid #1e2231", borderRadius: 8, padding: "10px 14px", color: "#e8eaf2", fontSize: 14, outline: "none", boxSizing: "border-box", fontFamily: "inherit" };
const btnPrimary = { background: "#f0c040", color: "#000", border: "1px solid #f0c040", borderRadius: 8, padding: "10px 20px", cursor: "pointer", fontSize: 14, fontWeight: 600 };
const btnSecondary = { background: "#0f1117", color: "#e8eaf2", border: "1px solid #1e2231", borderRadius: 8, padding: "10px 20px", cursor: "pointer", fontSize: 14, fontWeight: 600 };'''

new_styles = '''// === DEVIA Design System v2 - Liquid Glass ===
// Cards translucides avec backdrop-filter, bordures ultra-fines, plus d'espace
const cardStyle = {
  background: "rgba(22, 25, 35, 0.55)",
  backdropFilter: "blur(24px) saturate(140%)",
  WebkitBackdropFilter: "blur(24px) saturate(140%)",
  border: "1px solid rgba(255, 255, 255, 0.06)",
  borderRadius: 16,
  padding: 24,
  marginBottom: 16,
  boxShadow: "0 1px 0 rgba(255,255,255,0.03) inset, 0 8px 32px rgba(0,0,0,0.25)"
};
const inputStyle = {
  width: "100%",
  background: "rgba(255, 255, 255, 0.03)",
  border: "1px solid rgba(255, 255, 255, 0.08)",
  borderRadius: 10,
  padding: "12px 16px",
  color: "#e8eaf2",
  fontSize: 14,
  outline: "none",
  boxSizing: "border-box",
  fontFamily: "inherit",
  transition: "border-color 0.15s, background 0.15s"
};
const btnPrimary = {
  background: "#f0c040",
  color: "#0a0a0a",
  border: "1px solid #f0c040",
  borderRadius: 999,
  padding: "11px 24px",
  cursor: "pointer",
  fontSize: 14,
  fontWeight: 600,
  letterSpacing: "0.01em",
  boxShadow: "0 4px 14px rgba(240, 192, 64, 0.18)",
  transition: "transform 0.1s, box-shadow 0.15s"
};
const btnSecondary = {
  background: "rgba(255, 255, 255, 0.04)",
  backdropFilter: "blur(16px)",
  WebkitBackdropFilter: "blur(16px)",
  color: "#e8eaf2",
  border: "1px solid rgba(255, 255, 255, 0.08)",
  borderRadius: 999,
  padding: "11px 24px",
  cursor: "pointer",
  fontSize: 14,
  fontWeight: 500,
  letterSpacing: "0.01em",
  transition: "background 0.15s, border-color 0.15s"
};'''

if "Liquid Glass" in content:
    print("[INFO] Design System v2 deja applique, skip modification 1")
else:
    if old_styles not in content:
        print("ERREUR : impossible de trouver les styles globaux actuels.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_styles, new_styles, 1)
    print("[OK] Styles globaux refondus (Liquid Glass)")

# ================================================================
# MODIFICATION 2 : Refonte du <style> global (scrollbar + animations)
# ================================================================

old_global_style = '<style>{"* { box-sizing: border-box; margin: 0; padding: 0; } @keyframes spin { to { transform: rotate(360deg); } } ::-webkit-scrollbar { width: 5px; } ::-webkit-scrollbar-track { background: #0f1117; } ::-webkit-scrollbar-thumb { background: #2a2e40; border-radius: 3px; }"}</style>'

new_global_style = '''<style>{`
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-feature-settings: "ss01", "cv11"; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; letter-spacing: -0.005em; }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }
    input:focus, select:focus, textarea:focus { border-color: rgba(240,192,64,0.4) !important; background: rgba(255,255,255,0.05) !important; }
    button:active { transform: scale(0.97); }
    .devia-page { animation: fadeInUp 0.35s ease-out; }
    .devia-bg-noise { background-image: radial-gradient(at 0% 0%, rgba(240, 192, 64, 0.04) 0px, transparent 40%), radial-gradient(at 100% 100%, rgba(96, 165, 250, 0.03) 0px, transparent 40%); }
  `}</style>'''

if "devia-bg-noise" in content:
    print("[INFO] Styles globaux v2 deja appliques, skip modification 2")
else:
    if old_global_style not in content:
        print("ATTENTION : <style> global non trouve, skip")
    else:
        content = content.replace(old_global_style, new_global_style, 1)
        print("[OK] Styles globaux v2 appliques (scrollbar, animations, focus)")

# ================================================================
# MODIFICATION 3 : Refonte du <header>
# ================================================================

old_header = '''<header style={{ background: "#0f1117", borderBottom: "1px solid #1e2231", padding: "0 24px", display: "flex", alignItems: "center", justifyContent: "space-between", height: 56 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div style={{ width: 32, height: 32, background: "#f0c040", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>⚡</div>
      <span style={{ fontWeight: 800, fontSize: 16 }}>DEVIA</span>
      <span style={{ color: "#545870", fontSize: 12 }}>Devis charpente IA</span>
    </div>
    <nav style={{ display: "flex", gap: 4 }}>
      {[{ id: "devis", label: "Devis" }, { id: "projets", label: "Projets" }, { id: "catalogue", label: "Catalogue" }, { id: "parametres", label: "Parametres" }, { id: "compte", label: "Compte" }].map(tab => (
        <button key={tab.id} onClick={() => setActiveTab(tab.id)}
          style={{ background: activeTab === tab.id ? "#f0c04018" : "transparent", border: activeTab === tab.id ? "1px solid #f0c040" : "1px solid transparent", color: activeTab === tab.id ? "#f0c040" : "#545870", borderRadius: 6, padding: "6px 14px", cursor: "pointer", fontSize: 14, fontWeight: activeTab === tab.id ? 600 : 400 }}>
          {tab.label}
        </button>
      ))}
    </nav>
  </header>'''

new_header = '''<header style={{
    background: "rgba(8, 9, 12, 0.7)",
    backdropFilter: "blur(20px) saturate(180%)",
    WebkitBackdropFilter: "blur(20px) saturate(180%)",
    borderBottom: "1px solid rgba(255,255,255,0.05)",
    padding: "0 28px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    height: 64,
    position: "sticky",
    top: 0,
    zIndex: 100
  }}>
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <div style={{
        width: 30,
        height: 30,
        background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)",
        borderRadius: 9,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 15,
        fontWeight: 800,
        color: "#0a0a0a",
        boxShadow: "0 2px 8px rgba(240,192,64,0.25)"
      }}>D</div>
      <span style={{ fontWeight: 700, fontSize: 15, letterSpacing: "-0.01em" }}>DEVIA</span>
      <span style={{ color: "#545870", fontSize: 11, fontWeight: 500, marginLeft: 4, paddingLeft: 12, borderLeft: "1px solid rgba(255,255,255,0.08)" }}>Devis charpente IA</span>
    </div>
    <nav style={{
      display: "flex",
      gap: 2,
      background: "rgba(255,255,255,0.03)",
      border: "1px solid rgba(255,255,255,0.06)",
      borderRadius: 999,
      padding: 4
    }}>
      {[{ id: "devis", label: "Devis" }, { id: "projets", label: "Projets" }, { id: "catalogue", label: "Catalogue" }, { id: "parametres", label: "Parametres" }, { id: "compte", label: "Compte" }].map(tab => (
        <button key={tab.id} onClick={() => setActiveTab(tab.id)}
          style={{
            background: activeTab === tab.id ? "rgba(255,255,255,0.08)" : "transparent",
            border: "none",
            color: activeTab === tab.id ? "#ffffff" : "#7a7d92",
            borderRadius: 999,
            padding: "7px 16px",
            cursor: "pointer",
            fontSize: 13,
            fontWeight: activeTab === tab.id ? 600 : 500,
            letterSpacing: "-0.005em",
            transition: "all 0.15s",
            boxShadow: activeTab === tab.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
          }}
          onMouseEnter={(e) => { if (activeTab !== tab.id) e.currentTarget.style.color = "#d0d2dc"; }}
          onMouseLeave={(e) => { if (activeTab !== tab.id) e.currentTarget.style.color = "#7a7d92"; }}>
          {tab.label}
        </button>
      ))}
    </nav>
  </header>'''

if 'position: "sticky"' in content and "linear-gradient(135deg, #f0c040" in content:
    print("[INFO] Header v2 deja applique, skip modification 3")
else:
    if old_header not in content:
        print("ERREUR : header actuel non trouve.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_header, new_header, 1)
    print("[OK] Header refondu (sticky, glass, pills arrondies)")

# ================================================================
# MODIFICATION 4 : Ajouter un fond global gradient + classe page
# ================================================================

# Le main element existant : modifier pour ajouter le fond gradient
old_main = '<main style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 16px" }}>'

new_main = '''<main className="devia-page devia-bg-noise" style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 20px" }}>'''

if 'className="devia-page' in content:
    print("[INFO] Main v2 deja applique, skip modification 4")
else:
    if old_main not in content:
        print("ATTENTION : main element non trouve, skip")
    else:
        content = content.replace(old_main, new_main, 1)
        print("[OK] Main element : className + padding augmente")

# ================================================================
# MODIFICATION 5 : Fond du container racine
# On cherche le div principal qui englobe tout (DeviaMain return)
# Typiquement le 1er div apres "return ("
# ================================================================

# On cherche un pattern typique du conteneur principal
old_container_patterns = [
    'style={{ minHeight: "100vh", background: "#08090c", color: "#e8eaf2"',
    'style={{minHeight: "100vh", background: "#08090c", color: "#e8eaf2"',
    'background: "#08090c", color: "#e8eaf2", minHeight: "100vh"',
]

new_container_bg = 'style={{ minHeight: "100vh", background: "radial-gradient(ellipse at top, rgba(30, 35, 50, 0.4) 0%, #08090c 50%), #08090c", color: "#e8eaf2"'

found_container = False
for pattern in old_container_patterns:
    if pattern in content:
        content = content.replace(pattern, new_container_bg, 1)
        print("[OK] Fond global : gradient subtil ajoute")
        found_container = True
        break

if not found_container:
    print("[INFO] Conteneur racine non trouve, fond non modifie (pas grave, le bg-noise s'en charge)")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 1 APPLIQUEE - Design System Liquid Glass + Header")
print("=" * 60)
print()
print("CE QUI A CHANGE VISUELLEMENT :")
print("  1. Toutes les cards : translucides + flou + bordures ultra-fines")
print("  2. Tous les inputs : look plus elegant + focus jaune subtil")
print("  3. Tous les boutons : pills arrondies + ombres douces")
print("  4. Header : sticky + glass + pills nav")
print("  5. Logo : gradient jaune + lettre 'D'")
print("  6. Fond : gradient radial subtil + grain colore")
print("  7. Scrollbar : plus discrete, arrondie")
print("  8. Animations : transitions fluides + fadeInUp au changement de page")
print()
print("CE QUI N'A PAS CHANGE :")
print("  - Aucune fonctionnalite touchee")
print("  - Aucune page modifiee dans son contenu")
print("  - Le code reste 100% retrocompatible")
print()
print("PROCHAINE ETAPE :")
print("  git add devia.jsx")
print("  git commit -m 'Refonte design Session 1 - Liquid Glass + Header'")
print("  git push")
print()
print("TESTS :")
print("  1. Ouvrir devia-iota.vercel.app")
print("  2. Constater l'effet glass sur les cards")
print("  3. Tester le header : navigation entre Devis/Projets/Catalogue/...")
print("  4. Verifier la lisibilite sur toutes les pages")
print()
print("APRES VALIDATION :")
print("  - Session 2 : Refonte page Devis (inputs, selecteur catalogue, devis genere)")
print("  - Session 3 : Refonte page Catalogue + modales")
print("  - Session 4 : Pages restantes (Projets, Parametres, Compte)")
print()
print(f"BACKUP : {backup_name}")
