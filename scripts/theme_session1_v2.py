#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Mode Clair/Sombre Session 1 v2
- Identique a v1 mais SUPPRIME les const globales (cardStyle, etc.)
  pour eviter le conflit 'already declared'
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_theme_v2"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 0 (NOUVEAU) : SUPPRIMER les const globales cardStyle/inputStyle/btnPrimary/btnSecondary
# ================================================================

old_globals = '''const cardStyle = {
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

# On remplace par les palettes theme + un commentaire
new_globals = '''// ====== Palettes Theme (Mode Clair / Sombre) ======
const themes = {
  dark: {
    bgRoot: "radial-gradient(ellipse at top, rgba(30, 35, 50, 0.4) 0%, #08090c 50%), #08090c",
    bgPage: "transparent",
    headerBg: "rgba(8, 9, 12, 0.7)",
    headerBorder: "rgba(255, 255, 255, 0.05)",
    cardBg: "rgba(22, 25, 35, 0.55)",
    cardBorder: "rgba(255, 255, 255, 0.06)",
    cardShadow: "0 1px 0 rgba(255,255,255,0.03) inset, 0 8px 32px rgba(0,0,0,0.25)",
    inputBg: "rgba(255, 255, 255, 0.03)",
    inputBorder: "rgba(255, 255, 255, 0.08)",
    btnSecBg: "rgba(255, 255, 255, 0.04)",
    btnSecBorder: "rgba(255, 255, 255, 0.08)",
    navBg: "rgba(255,255,255,0.03)",
    navBorder: "rgba(255,255,255,0.06)",
    navTabActive: "rgba(255,255,255,0.08)",
    navTabActiveText: "#ffffff",
    navTabText: "#7a7d92",
    navTabHover: "#d0d2dc",
    textPrimary: "#e8eaf2",
    textSecondary: "#9ca0b8",
    textMuted: "#7a7d92",
    textFaint: "#545870",
    gold: "#f0c040",
    goldDark: "#e0a020",
  },
  light: {
    bgRoot: "radial-gradient(ellipse at top, rgba(240, 192, 64, 0.05) 0%, #f5f6fa 50%), #f5f6fa",
    bgPage: "transparent",
    headerBg: "rgba(255, 255, 255, 0.85)",
    headerBorder: "rgba(0, 0, 0, 0.06)",
    cardBg: "rgba(255, 255, 255, 0.7)",
    cardBorder: "rgba(0, 0, 0, 0.06)",
    cardShadow: "0 1px 0 rgba(255,255,255,0.8) inset, 0 8px 24px rgba(0,0,0,0.04)",
    inputBg: "rgba(255, 255, 255, 0.8)",
    inputBorder: "rgba(0, 0, 0, 0.08)",
    btnSecBg: "rgba(0, 0, 0, 0.03)",
    btnSecBorder: "rgba(0, 0, 0, 0.08)",
    navBg: "rgba(255,255,255,0.7)",
    navBorder: "rgba(0,0,0,0.06)",
    navTabActive: "#1a1d2a",
    navTabActiveText: "#ffffff",
    navTabText: "#5a5e72",
    navTabHover: "#1a1d2a",
    textPrimary: "#1a1d2a",
    textSecondary: "#5a5e72",
    textMuted: "#8a8d9c",
    textFaint: "#a8abb8",
    gold: "#b8860b",
    goldDark: "#9c7000",
  }
};
// Les styles cardStyle/inputStyle/btnPrimary/btnSecondary
// sont definis dynamiquement DANS DeviaMain selon themeMode
// ===================================================='''

if "const themes = {" in content:
    print("[INFO] Themes deja definis (script deja partiellement execute)")
elif old_globals in content:
    content = content.replace(old_globals, new_globals, 1)
    print("[OK] Const globales supprimees et remplacees par les themes")
    modifs += 1
else:
    print("[ERREUR] Const globales non trouvees exactement")
    sys.exit(1)

# ================================================================
# MOD 1 : Ajouter le state themeMode + lecture localStorage
# ================================================================

old_state = 'const [usageLogs, setUsageLogs] = useState([]);'
new_state = '''const [usageLogs, setUsageLogs] = useState([]);
  const [themeMode, setThemeMode] = useState(() => {
    try {
      return localStorage.getItem("devia_theme") || "dark";
    } catch (e) {
      return "dark";
    }
  });

  // Persistance du theme
  useEffect(() => {
    try {
      localStorage.setItem("devia_theme", themeMode);
    } catch (e) {}
  }, [themeMode]);

  // Styles dynamiques selon le theme
  const t = themes[themeMode] || themes.dark;
  const cardStyle = {
    background: t.cardBg,
    backdropFilter: "blur(24px) saturate(140%)",
    WebkitBackdropFilter: "blur(24px) saturate(140%)",
    border: "1px solid " + t.cardBorder,
    borderRadius: 16,
    padding: 24,
    marginBottom: 16,
    boxShadow: t.cardShadow
  };
  const inputStyle = {
    width: "100%",
    background: t.inputBg,
    border: "1px solid " + t.inputBorder,
    borderRadius: 10,
    padding: "12px 16px",
    color: t.textPrimary,
    fontSize: 14,
    outline: "none",
    boxSizing: "border-box",
    fontFamily: "inherit",
    transition: "border-color 0.15s, background 0.15s"
  };
  const btnPrimary = {
    background: t.gold,
    color: themeMode === "light" ? "#ffffff" : "#0a0a0a",
    border: "1px solid " + t.gold,
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
    background: t.btnSecBg,
    backdropFilter: "blur(16px)",
    WebkitBackdropFilter: "blur(16px)",
    color: t.textPrimary,
    border: "1px solid " + t.btnSecBorder,
    borderRadius: 999,
    padding: "11px 24px",
    cursor: "pointer",
    fontSize: 14,
    fontWeight: 500,
    letterSpacing: "0.01em",
    transition: "background 0.15s, border-color 0.15s"
  };'''

if "const [themeMode, setThemeMode]" in content:
    print("[INFO] State themeMode deja present")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] State themeMode + styles dynamiques ajoutes")
    modifs += 1
else:
    print("[ERREUR] State usageLogs non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : DIV racine
# ================================================================

old_root_div = '<div style={{ minHeight: "100vh", background: "radial-gradient(ellipse at top, rgba(30, 35, 50, 0.4) 0%, #08090c 50%), #08090c", color: "#e8eaf2", fontFamily: "Inter, sans-serif" }}>'

new_root_div = '<div style={{ minHeight: "100vh", background: t.bgRoot, color: t.textPrimary, fontFamily: "Inter, sans-serif", transition: "background 0.3s, color 0.3s" }}>'

if "background: t.bgRoot" in content:
    print("[INFO] DIV racine deja adapte")
elif old_root_div in content:
    content = content.replace(old_root_div, new_root_div, 1)
    print("[OK] DIV racine adapte")
    modifs += 1

# ================================================================
# MOD 3 : Header
# ================================================================

old_header = '''  <header style={{
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
  }}>'''

new_header = '''  <header style={{
    background: t.headerBg,
    backdropFilter: "blur(20px) saturate(180%)",
    WebkitBackdropFilter: "blur(20px) saturate(180%)",
    borderBottom: "1px solid " + t.headerBorder,
    padding: "0 28px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    height: 64,
    position: "sticky",
    top: 0,
    zIndex: 100,
    transition: "background 0.3s, border-color 0.3s"
  }}>'''

if "background: t.headerBg" in content:
    print("[INFO] Header deja adapte")
elif old_header in content:
    content = content.replace(old_header, new_header, 1)
    print("[OK] Header adapte")
    modifs += 1

# ================================================================
# MOD 4 : Nav
# ================================================================

old_nav = '''    <nav style={{
      display: "flex",
      gap: 2,
      background: "rgba(255,255,255,0.03)",
      border: "1px solid rgba(255,255,255,0.06)",
      borderRadius: 999,
      padding: 4
    }}>'''

new_nav = '''    <nav style={{
      display: "flex",
      gap: 2,
      background: t.navBg,
      border: "1px solid " + t.navBorder,
      borderRadius: 999,
      padding: 4
    }}>'''

if "background: t.navBg" in content:
    print("[INFO] Nav deja adaptee")
elif old_nav in content:
    content = content.replace(old_nav, new_nav, 1)
    print("[OK] Nav adaptee")
    modifs += 1

# ================================================================
# MOD 5 : Tabs
# ================================================================

old_tabs = '''      {[{ id: "devis", label: "Devis" }, { id: "projets", label: "Projets" }, { id: "catalogue", label: "Catalogue" }, { id: "parametres", label: "Parametres" }, { id: "compte", label: "Compte" }].map(tab => (
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
      ))}'''

new_tabs = '''      {[{ id: "devis", label: "Devis" }, { id: "projets", label: "Projets" }, { id: "catalogue", label: "Catalogue" }, { id: "parametres", label: "Parametres" }, { id: "compte", label: "Compte" }].map(tab => (
        <button key={tab.id} onClick={() => setActiveTab(tab.id)}
          style={{
            background: activeTab === tab.id ? t.navTabActive : "transparent",
            border: "none",
            color: activeTab === tab.id ? t.navTabActiveText : t.navTabText,
            borderRadius: 999,
            padding: "7px 16px",
            cursor: "pointer",
            fontSize: 13,
            fontWeight: activeTab === tab.id ? 600 : 500,
            letterSpacing: "-0.005em",
            transition: "all 0.15s",
            boxShadow: activeTab === tab.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
          }}
          onMouseEnter={(e) => { if (activeTab !== tab.id) e.currentTarget.style.color = t.navTabHover; }}
          onMouseLeave={(e) => { if (activeTab !== tab.id) e.currentTarget.style.color = t.navTabText; }}>
          {tab.label}
        </button>
      ))}'''

if "background: activeTab === tab.id ? t.navTabActive" in content:
    print("[INFO] Tabs deja adaptees")
elif old_tabs in content:
    content = content.replace(old_tabs, new_tabs, 1)
    print("[OK] Tabs adaptees")
    modifs += 1

# ================================================================
# MOD 6 : Toggle dans Parametres
# ================================================================

old_paramsection = '''    {activeTab === "parametres" && (
      <div>'''

new_paramsection_with_toggle = '''    {activeTab === "parametres" && (
      <div>
        {/* Toggle Theme Sombre/Clair */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(167, 139, 250, 0.1)",
              border: "1px solid rgba(167, 139, 250, 0.2)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
              </svg>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: t.textPrimary }}>Apparence</div>
              <div style={{ color: t.textMuted, fontSize: 12 }}>Choisissez le theme de l&apos;application</div>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            {[
              { id: "dark", label: "Sombre", desc: "Noir profond, accents dores", isActive: themeMode === "dark" },
              { id: "light", label: "Clair", desc: "Blanc pur, design epure", isActive: themeMode === "light" }
            ].map(opt => (
              <button key={opt.id} onClick={() => setThemeMode(opt.id)}
                style={{
                  background: opt.isActive ? (opt.id === "dark" ? "linear-gradient(135deg, rgba(240, 192, 64, 0.12), rgba(240, 192, 64, 0.04))" : "linear-gradient(135deg, rgba(167, 139, 250, 0.12), rgba(167, 139, 250, 0.04))") : t.cardBg,
                  border: "1px solid " + (opt.isActive ? (opt.id === "dark" ? "rgba(240, 192, 64, 0.35)" : "rgba(167, 139, 250, 0.35)") : t.cardBorder),
                  borderRadius: 12,
                  padding: 16,
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.18s",
                  display: "flex",
                  alignItems: "center",
                  gap: 12
                }}>
                <div style={{
                  width: 40, height: 40, borderRadius: 10,
                  background: opt.id === "dark" ? "#08090c" : "#f5f6fa",
                  border: "1px solid " + (opt.id === "dark" ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.08)"),
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0
                }}>
                  {opt.id === "dark" ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
                    </svg>
                  ) : (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#b8860b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                    </svg>
                  )}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 14, fontWeight: 600, color: t.textPrimary }}>{opt.label}</span>
                    {opt.isActive && (
                      <span style={{
                        display: "inline-flex", alignItems: "center", justifyContent: "center",
                        width: 16, height: 16, borderRadius: "50%",
                        background: opt.id === "dark" ? "#f0c040" : "#b8860b"
                      }}>
                        <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke={opt.id === "dark" ? "#0a0a0a" : "#ffffff"} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                      </span>
                    )}
                  </div>
                  <div style={{ color: t.textMuted, fontSize: 11, marginTop: 2 }}>{opt.desc}</div>
                </div>
              </button>
            ))}
          </div>
        </div>'''

if "Toggle Theme Sombre/Clair" in content:
    print("[INFO] Toggle Theme deja en place")
elif old_paramsection in content:
    content = content.replace(old_paramsection, new_paramsection_with_toggle, 1)
    print("[OK] Toggle Theme ajoute dans Parametres")
    modifs += 1

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
