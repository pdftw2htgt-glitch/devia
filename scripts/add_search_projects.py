#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Ajouter une barre de recherche dans la page Projets
- State searchProjects
- Filtre live sur nom, commune, dims
- Etat vide specifique si rien ne correspond
- Bouton X pour effacer la recherche
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_search_projects"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter le state searchProjects
# ================================================================

old_state = 'const [addressData, setAddressData] = useState(null); // lat/lng/nom officiel pour modif #6'
new_state = '''const [addressData, setAddressData] = useState(null); // lat/lng/nom officiel pour modif #6
  const [searchProjects, setSearchProjects] = useState("");'''

if "const [searchProjects, setSearchProjects]" in content:
    print("[INFO] State searchProjects deja present")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] State searchProjects ajoute")
    modifs += 1
else:
    print("[ERREUR] State addressData non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Remplacer le bloc projets pour ajouter la barre de recherche
# et le filtrage
# ================================================================

old_block_header = '''<div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
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
        </div>'''

new_block_header = '''<div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20, flexWrap: "wrap", gap: 12 }}>
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

        {/* Barre de recherche */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 20 }}>
          <div style={{
            position: "relative",
            width: "100%",
            maxWidth: 360,
            display: "flex",
            alignItems: "center"
          }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
              style={{ position: "absolute", left: 14, pointerEvents: "none" }}>
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              type="text"
              value={searchProjects}
              onChange={(e) => setSearchProjects(e.target.value)}
              placeholder="Rechercher un projet..."
              style={{
                width: "100%",
                background: "rgba(255, 255, 255, 0.025)",
                border: "1px solid rgba(255, 255, 255, 0.06)",
                borderRadius: 999,
                padding: "10px 38px 10px 40px",
                color: "#e8eaf2",
                fontSize: 13,
                outline: "none",
                transition: "border-color 0.15s, background 0.15s"
              }}
              onFocus={(e) => { e.target.style.borderColor = "rgba(240, 192, 64, 0.3)"; e.target.style.background = "rgba(255, 255, 255, 0.04)"; }}
              onBlur={(e) => { e.target.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.target.style.background = "rgba(255, 255, 255, 0.025)"; }}
            />
            {searchProjects && (
              <button
                onClick={() => setSearchProjects("")}
                title="Effacer"
                style={{
                  position: "absolute",
                  right: 8,
                  background: "transparent",
                  border: "none",
                  color: "#7a7d92",
                  cursor: "pointer",
                  borderRadius: 999,
                  padding: 6,
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "color 0.15s"
                }}
                onMouseEnter={(e) => { e.currentTarget.style.color = "#e8eaf2"; }}
                onMouseLeave={(e) => { e.currentTarget.style.color = "#7a7d92"; }}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            )}
          </div>
        </div>'''

if 'placeholder="Rechercher un projet..."' in content:
    print("[INFO] Barre de recherche deja en place")
elif old_block_header in content:
    content = content.replace(old_block_header, new_block_header, 1)
    print("[OK] Barre de recherche ajoutee")
    modifs += 1
else:
    print("[ERREUR] Header projets non trouve")
    sys.exit(1)

# ================================================================
# MOD 3 : Ajouter le filtrage + etat vide specifique
# On remplace le bloc qui boucle sur projects.map
# ================================================================

old_map = '''{projects.length === 0 ? (
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
            {projects.map(p => ('''

new_map = '''{(() => {
          // Filtrage des projets selon la recherche
          const searchLower = searchProjects.trim().toLowerCase();
          const projectsFiltres = searchLower === "" ? projects : projects.filter(p => {
            const nom = (p.nom || "").toLowerCase();
            const commune = (p.commune || "").toLowerCase();
            const dims = (p.dims || "").toLowerCase();
            return nom.includes(searchLower) || commune.includes(searchLower) || dims.includes(searchLower);
          });

          if (projects.length === 0) {
            return (
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
            );
          }

          if (projectsFiltres.length === 0) {
            return (
              <div style={{ ...cardStyle, textAlign: "center", padding: "48px 24px" }}>
                <div style={{
                  width: 56, height: 56, borderRadius: 14,
                  background: "rgba(255, 255, 255, 0.03)",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                  display: "inline-flex", alignItems: "center", justifyContent: "center",
                  marginBottom: 16
                }}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                  </svg>
                </div>
                <div style={{ color: "#e8eaf2", fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Aucun resultat</div>
                <div style={{ color: "#7a7d92", fontSize: 13, maxWidth: 360, margin: "0 auto", lineHeight: 1.5 }}>
                  Aucun projet ne correspond a &quot;{searchProjects}&quot;.
                </div>
              </div>
            );
          }

          return (
          <div style={{ display: "grid", gap: 10 }}>
            {projectsFiltres.map(p => ('''

if "projectsFiltres" in content:
    print("[INFO] Filtrage deja en place")
elif old_map in content:
    content = content.replace(old_map, new_map, 1)
    print("[OK] Filtrage + etat vide specifique ajoutes")
    modifs += 1
else:
    print("[ERREUR] Bloc projects.map non trouve")
    sys.exit(1)

# ================================================================
# MOD 4 : Fermer la fonction IIFE et la condition
# On remplace la fermeture du <div> + ); par )(}))
# ================================================================

old_closing = '''))}
          </div>
        )}'''

new_closing = '''))}
          </div>
          );
        })()}'''

if "})()}" in content:
    print("[INFO] Fermeture IIFE deja en place")
elif old_closing in content:
    content = content.replace(old_closing, new_closing, 1)
    print("[OK] Fermeture IIFE en place")
    modifs += 1
else:
    print("[WARN] Fermeture non trouvee, le code peut etre malforme")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. State searchProjects ajoute")
print("  2. Barre de recherche : icone loupe + input + X pour effacer")
print("  3. Filtrage live sur nom, commune, dimensions")
print("  4. Etat vide specifique 'Aucun resultat' quand recherche sans match")
print()
print("COMMENT TESTER :")
print("  1. npm run build (pour verifier que ca compile)")
print("  2. Recharger la page Safari")
print("  3. Aller sur la page Projets")
print("  4. Taper dans la barre de recherche")
print("  5. La liste se filtre en live")
print()
print(f"BACKUP : {backup_name}")
