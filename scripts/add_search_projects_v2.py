#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Barre de recherche projets - approche simple

Approche :
1. Ajouter state searchProjects
2. Ajouter la barre de recherche apres le header
3. Calculer 'projectsFiltered' avec une const declaree AVANT le bloc projets
4. Remplacer juste projects.map -> projectsFiltered.map
5. Ajouter un cas "aucun resultat" qui prend la place de l'etat vide quand searchProjects n'est pas vide

Pas de modification de la structure JSX, juste des modifs ciblees.
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_search_v2"
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
# MOD 2 : Ajouter la barre de recherche apres le header de la page Projets
# (juste avant le test projects.length === 0)
# ================================================================

old_before_empty = '''<span style={{ width: 6, height: 6, borderRadius: "50%", background: "#60a5fa" }}></span>
            {projects.length} devis
          </div>
        </div>
        {projects.length === 0 ? ('''

new_with_search = '''<span style={{ width: 6, height: 6, borderRadius: "50%", background: "#60a5fa" }}></span>
            {projects.length} devis
          </div>
        </div>

        {/* Barre de recherche */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 20 }}>
          <div style={{ position: "relative", width: "100%", maxWidth: 360, display: "flex", alignItems: "center" }}>
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
                  position: "absolute", right: 8,
                  background: "transparent", border: "none", color: "#7a7d92",
                  cursor: "pointer", borderRadius: 999, padding: 6,
                  display: "inline-flex", alignItems: "center", justifyContent: "center",
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
        </div>

        {projects.length === 0 ? ('''

if 'placeholder="Rechercher un projet..."' in content:
    print("[INFO] Barre de recherche deja en place")
elif old_before_empty in content:
    content = content.replace(old_before_empty, new_with_search, 1)
    print("[OK] Barre de recherche ajoutee")
    modifs += 1
else:
    print("[ERREUR] Header projets non trouve")
    sys.exit(1)

# ================================================================
# MOD 3 : Filtrage - remplacer projects.map par filter+map inline
# avec gestion du cas "aucun resultat"
# ================================================================

# On cible juste la ligne du .map et on l'enrichit
old_map_start = '''<div style={{ display: "grid", gap: 10 }}>
            {projects.map(p => ('''

# Strategie : on garde la grille, mais on filtre AVANT de map.
# Si le filtre rend 0, on affiche un message a la place dans la grille.
new_map_start = '''<div style={{ display: "grid", gap: 10 }}>
            {projects.filter(p => {
              const s = searchProjects.trim().toLowerCase();
              if (s === "") return true;
              const nom = (p.nom || "").toLowerCase();
              const commune = (p.commune || "").toLowerCase();
              const dims = (p.dims || "").toLowerCase();
              return nom.includes(s) || commune.includes(s) || dims.includes(s);
            }).length === 0 && searchProjects.trim() !== "" ? (
              <div style={{ ...cardStyle, textAlign: "center", padding: "48px 24px", marginBottom: 0 }}>
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
                  Aucun projet ne correspond a votre recherche.
                </div>
              </div>
            ) : projects.filter(p => {
              const s = searchProjects.trim().toLowerCase();
              if (s === "") return true;
              const nom = (p.nom || "").toLowerCase();
              const commune = (p.commune || "").toLowerCase();
              const dims = (p.dims || "").toLowerCase();
              return nom.includes(s) || commune.includes(s) || dims.includes(s);
            }).map(p => ('''

if "projects.filter(p => {" in content:
    print("[INFO] Filtrage deja en place")
elif old_map_start in content:
    content = content.replace(old_map_start, new_map_start, 1)
    print("[OK] Filtrage + etat 'aucun resultat' ajoute")
    modifs += 1
else:
    print("[ERREUR] Bloc projects.map non trouve")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("APPROCHE :")
print("  - Pas de IIFE compliquee")
print("  - Filtrage inline avec .filter().map()")
print("  - Cas 'aucun resultat' geré par condition ternaire")
print("  - Pas de changement structurel du JSX")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print('    git commit -m "Ajout barre de recherche page Projets"')
print("    git push")
print()
print(f"BACKUP : {backup_name}")
