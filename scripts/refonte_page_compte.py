#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 4.C : Refonte page Compte (DERNIERE)
Refait :
1. Header
2. Avatar + identite (gradient initiales)
3. Badge plan (style coherent)
4. 3 mini-cards stats (icones SVG + valeurs grosses)

A lancer depuis ~/Desktop/devia :
    python3 refonte_page_compte.py

Apres : npm run build
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_page_compte"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD : Tout le bloc page Compte
# ================================================================

old_block = '''<h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20 }}>Mon compte</h2>
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
            <div style={{ width: 56, height: 56, background: "#f0c040", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28 }}>👤</div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 18 }}>{params.entreprise || "Mon entreprise"}</div>
              <Badge color="#3ecf8e">Plan Pro</Badge>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
            {[{ label: "Devis ce mois", val: projects.length, icon: "📋" }, { label: "Total generes", val: projects.length, icon: "📁" }, { label: "Jours restants", val: "23", icon: "📅" }].map(s => (
              <div key={s.label} style={{ background: "#0f1117", borderRadius: 8, padding: 16, border: "1px solid #1e2231", textAlign: "center" }}>
                <div style={{ fontSize: 28, marginBottom: 8 }}>{s.icon}</div>
                <div style={{ fontSize: 24, fontWeight: 700, color: "#f0c040" }}>{s.val}</div>
                <div style={{ color: "#545870", fontSize: 13 }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>'''

new_block = '''<div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Mon compte</h2>
          <div style={{ color: "#7a7d92", fontSize: 13 }}>Apercu de votre activite DEVIA</div>
        </div>

        {/* Card Identite + Plan */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
            <div style={{
              width: 56, height: 56,
              background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)",
              borderRadius: 14,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 22,
              fontWeight: 700,
              color: "#0a0a0a",
              boxShadow: "0 4px 14px rgba(240, 192, 64, 0.25)",
              flexShrink: 0
            }}>
              {(params.entreprise || "M E").split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase()}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: 700, fontSize: 18, color: "#e8eaf2", marginBottom: 6, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {params.entreprise || "Mon entreprise"}
              </div>
              <div style={{
                display: "inline-flex", alignItems: "center", gap: 6,
                background: "rgba(62, 207, 142, 0.1)",
                border: "1px solid rgba(62, 207, 142, 0.25)",
                borderRadius: 999,
                padding: "4px 11px",
                fontSize: 11,
                fontWeight: 600,
                color: "#3ecf8e",
                letterSpacing: "0.02em",
                textTransform: "uppercase"
              }}>
                <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#3ecf8e" }}></span>
                Plan Pro
              </div>
            </div>
          </div>

          {/* 3 stats */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>
            {[
              {
                label: "Devis ce mois",
                val: projects.length,
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 11H7v8h2v-8zm6 0h-2v8h2v-8zM11 11v8h2v-8h-2zM4 7h16M5 7v14h14V7M9 4h6v3H9z"/></svg>,
                color: "#60a5fa"
              },
              {
                label: "Total generes",
                val: projects.length,
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>,
                color: "#3ecf8e"
              },
              {
                label: "Jours restants",
                val: "23",
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>,
                color: "#a78bfa"
              }
            ].map(s => (
              <div key={s.label} style={{
                background: "rgba(255, 255, 255, 0.02)",
                borderRadius: 12,
                padding: 16,
                border: "1px solid rgba(255, 255, 255, 0.05)",
                transition: "border-color 0.15s"
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.05)"; }}>
                <div style={{
                  width: 32, height: 32, borderRadius: 8,
                  background: "rgba(255, 255, 255, 0.04)",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                  display: "inline-flex", alignItems: "center", justifyContent: "center",
                  marginBottom: 10
                }}>
                  {s.icon}
                </div>
                <div style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 4 }}>{s.label}</div>
                <div style={{ fontSize: 24, fontWeight: 700, color: "#f5f6fa", letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums" }}>{s.val}</div>
              </div>
            ))}
          </div>
        </div>'''

if "Apercu de votre activite DEVIA" in content:
    print("[INFO] Page Compte deja refondue")
elif old_block in content:
    content = content.replace(old_block, new_block, 1)
    print("[OK] Page Compte refondue (header + identite + 3 stats SVG)")
else:
    print("[ERREUR] Bloc page Compte non trouve.")
    sys.exit(1)

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 4.C APPLIQUEE - Page Compte (DERNIERE !)")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Header :")
print("     - Titre 'Mon compte' plus grand + sous-titre")
print("  2. Avatar :")
print("     - Initiales du nom d'entreprise (au lieu de l'emoji)")
print("     - Gradient jaune + ombre doree")
print("  3. Plan :")
print("     - Pill 'Plan Pro' avec point vert (coherent badge)")
print("  4. 3 stats :")
print("     - Icones SVG colorees dans des carres subtils :")
print("       - Devis ce mois : bleu (icone calculatrice)")
print("       - Total generes : vert (icone dossier)")
print("       - Jours restants : violet (icone calendrier)")
print("     - Labels en MAJUSCULES")
print("     - Valeurs en gros chiffres tabular-nums")
print("     - Hover : bordure plus claire")
print()
print("=" * 60)
print("REFONTE DESIGN TERMINEE A 100% ! BRAVO !")
print("=" * 60)
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Refonte design Session 4.C - Page Compte (FIN)'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
