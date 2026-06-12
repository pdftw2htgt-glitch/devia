#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 4.A : Refonte page Projets
Refait :
1. Header de la page (titre + sous-titre + badge count)
2. Etat vide (icone SVG dossier + message accueillant)
3. Cards de projets (style cohérent, icônes SVG, hover, prix TTC)
4. Bouton Supprimer (icone SVG poubelle, cohérent avec catalogue)

A lancer depuis ~/Desktop/devia :
    python3 refonte_page_projets.py

Apres : npm run build
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_page_projets"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD 1 : Bloc complet de la page Projets
# ================================================================

old_block = '''<div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700 }}>Mes projets</h2>
          <Badge color="#60a5fa">{projects.length} devis</Badge>
        </div>
        {projects.length === 0 ? (
          <div style={{ ...cardStyle, textAlign: "center", padding: 40 }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>📁</div>
            <div style={{ color: "#545870" }}>Aucun projet pour l instant. Generez votre premier devis !</div>
          </div>
        ) : (
          <div style={{ display: "grid", gap: 12 }}>
            {projects.map(p => (
              <div key={p.id} style={{ ...cardStyle, display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer", marginBottom: 0, transition: "border 0.15s" }}
                onMouseEnter={(e) => e.currentTarget.style.border = "1px solid #f0c040"}
                onMouseLeave={(e) => e.currentTarget.style.border = "1px solid #1e2231"}
                onClick={() => loadProjectDetails(p)}>
                <div style={{ display: "flex", alignItems: "center", gap: 16, flex: 1 }}>
                  <div style={{ width: 44, height: 44, background: "#f0c04018", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22 }}>🏠</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 15 }}>{p.nom}</div>
                    <div style={{ color: "#545870", fontSize: 13 }}>{p.commune} - {p.dims} - {new Date(p.date).toLocaleDateString("fr-FR")}</div>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: "#f0c040", fontWeight: 700, fontSize: 18 }}>{p.ttc.toLocaleString("fr-FR")} EUR</div>
                    <div style={{ color: "#545870", fontSize: 12 }}>TTC</div>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteProject(p.id, p.nom); }}
                    title="Supprimer ce projet"
                    style={{ background: "transparent", border: "1px solid #2a2e40", color: "#ef4444", borderRadius: 6, padding: "6px 10px", cursor: "pointer", fontSize: 13, fontWeight: 600, transition: "all 0.15s" }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = "#ef444418"; e.currentTarget.style.borderColor = "#ef4444"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "#2a2e40"; }}>
                    Supprimer
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}'''

new_block = '''<div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Mes projets</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>Retrouvez tous vos devis sauvegardes</div>
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
            {projects.length} devis
          </div>
        </div>
        {projects.length === 0 ? (
          <div style={{ ...cardStyle, textAlign: "center", padding: "48px 24px" }}>
            <div style={{
              width: 56, height: 56, borderRadius: 14,
              background: "rgba(255, 255, 255, 0.03)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              display: "inline-flex", alignItems: "center", justifyContent: "center",
              marginBottom: 16
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
              </svg>
            </div>
            <div style={{ color: "#e8eaf2", fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Aucun projet pour l&apos;instant</div>
            <div style={{ color: "#7a7d92", fontSize: 13, maxWidth: 360, margin: "0 auto", lineHeight: 1.5 }}>Generez votre premier devis depuis l&apos;onglet Devis et il apparaitra ici.</div>
          </div>
        ) : (
          <div style={{ display: "grid", gap: 10 }}>
            {projects.map(p => (
              <div key={p.id} style={{
                ...cardStyle,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: "pointer",
                marginBottom: 0,
                padding: 18,
                transition: "all 0.18s",
                gap: 14
              }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = "rgba(240, 192, 64, 0.4)";
                  e.currentTarget.style.background = "rgba(240, 192, 64, 0.025)";
                  const deleteBtn = e.currentTarget.querySelector(".devia-delete-btn");
                  if (deleteBtn) deleteBtn.style.opacity = "1";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)";
                  e.currentTarget.style.background = "rgba(22, 25, 35, 0.55)";
                  const deleteBtn = e.currentTarget.querySelector(".devia-delete-btn");
                  if (deleteBtn) deleteBtn.style.opacity = "0.4";
                }}
                onClick={() => loadProjectDetails(p)}>
                <div style={{ display: "flex", alignItems: "center", gap: 14, flex: 1, minWidth: 0 }}>
                  <div style={{
                    width: 44, height: 44,
                    background: "linear-gradient(135deg, rgba(240, 192, 64, 0.18), rgba(240, 192, 64, 0.06))",
                    border: "1px solid rgba(240, 192, 64, 0.15)",
                    borderRadius: 11,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0
                  }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                    </svg>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: 15, color: "#e8eaf2", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", marginBottom: 3 }}>{p.nom}</div>
                    <div style={{ color: "#7a7d92", fontSize: 12, display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
                        </svg>
                        {p.commune || "?"}
                      </span>
                      <span style={{ opacity: 0.4 }}>&bull;</span>
                      <span>{p.dims}</span>
                      <span style={{ opacity: 0.4 }}>&bull;</span>
                      <span>{new Date(p.date).toLocaleDateString("fr-FR")}</span>
                    </div>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 12, flexShrink: 0 }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: "#f0c040", fontWeight: 700, fontSize: 17, fontVariantNumeric: "tabular-nums", letterSpacing: "-0.01em" }}>
                      {p.ttc.toLocaleString("fr-FR")} <span style={{ fontSize: 12, fontWeight: 600 }}>EUR</span>
                    </div>
                    <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase" }}>TTC</div>
                  </div>
                  <button
                    className="devia-delete-btn"
                    onClick={(e) => { e.stopPropagation(); deleteProject(p.id, p.nom); }}
                    title="Supprimer ce projet"
                    style={{
                      background: "transparent",
                      border: "1px solid rgba(255, 255, 255, 0.06)",
                      color: "#7a7d92",
                      borderRadius: 8,
                      padding: "6px 8px",
                      cursor: "pointer",
                      transition: "all 0.15s",
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      opacity: 0.4
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)"; e.currentTarget.style.borderColor = "rgba(239, 68, 68, 0.4)"; e.currentTarget.style.color = "#ef4444"; e.currentTarget.style.opacity = "1"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.color = "#7a7d92"; }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}'''

if "Retrouvez tous vos devis sauvegardes" in content:
    print("[INFO] Page Projets deja refondue")
elif old_block in content:
    content = content.replace(old_block, new_block, 1)
    print("[OK] Page Projets refondue (header + cards + bouton supprimer)")
else:
    print("[ERREUR] Bloc page Projets non trouve.")
    sys.exit(1)

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 4.A APPLIQUEE - Page Projets")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Header Projets :")
print("     - Titre 'Mes projets' plus grand + sous-titre")
print("     - Badge count en pill bleue avec point")
print("  2. Etat vide :")
print("     - Icone SVG dossier dans un carre subtil")
print("     - Message accueillant")
print("  3. Cards de projets :")
print("     - Icone maison SVG avec gradient jaune")
print("     - Titre projet + ligne d'infos (commune avec icone, dims, date)")
print("     - Prix TTC en gros jaune avec tabular-nums")
print("     - Label 'TTC' en uppercase")
print("     - Hover : bordure jaune + fond legerement jaune + bouton supprimer apparait")
print("  4. Bouton Supprimer :")
print("     - Icone SVG poubelle (au lieu du texte 'Supprimer')")
print("     - Discret au repos (opacity 0.4)")
print("     - Visible au hover de la card (opacity 1)")
print("     - Rouge vif au hover du bouton lui-meme")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Refonte design Session 4.A - Page Projets'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
