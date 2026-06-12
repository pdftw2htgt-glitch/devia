#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 1 Groupes : Chargement + Pills de filtre
- State groupes + selectedGroupe
- Chargement Supabase + groupe_id dans les projets
- Pills 'Tous / Groupe A / Groupe B' au-dessus de la barre de recherche
- Filtrage combine avec la recherche existante
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_groupes_s1"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter les states groupes + selectedGroupe
# ================================================================

old_state = 'const [searchProjects, setSearchProjects] = useState("");'
new_state = '''const [searchProjects, setSearchProjects] = useState("");
  const [groupes, setGroupes] = useState([]);
  const [selectedGroupe, setSelectedGroupe] = useState("all"); // "all" ou un UUID de groupe'''

if "const [groupes, setGroupes]" in content:
    print("[INFO] States groupes deja presents")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] States groupes + selectedGroupe ajoutes")
    modifs += 1
else:
    print("[ERREUR] State searchProjects non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Ajouter le chargement des groupes au demarrage
# On ajoute un useEffect apres loadProjects
# ================================================================

old_loadprojects_end = '''    loadProjects();
  }, []);'''

new_loadprojects_with_groupes = '''    loadProjects();

    // Chargement des groupes
    const loadGroupes = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;
        const { data, error } = await supabase
          .from("groupes_projets")
          .select("*")
          .eq("user_id", user.id)
          .order("nom", { ascending: true });
        if (error) {
          console.error("Erreur chargement groupes:", error);
          return;
        }
        if (data) setGroupes(data);
      } catch (e) {
        console.error("Erreur loadGroupes:", e);
      }
    };
    loadGroupes();
  }, []);'''

if "const loadGroupes = async" in content:
    print("[INFO] loadGroupes deja present")
elif old_loadprojects_end in content:
    content = content.replace(old_loadprojects_end, new_loadprojects_with_groupes, 1)
    print("[OK] loadGroupes ajoute au demarrage")
    modifs += 1
else:
    print("[ERREUR] Fin de loadProjects non trouvee")
    sys.exit(1)

# ================================================================
# MOD 3 : Ajouter groupe_id dans le formatted des projets
# ================================================================

old_formatted = '''const formatted = data.map(p => ({
            id: p.id,
            nom: p.nom,
            commune: p.commune || "",
            date: p.created_at ? p.created_at.split("T")[0] : "",
            ttc: p.total_ttc || 0,
            dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m",
            devis_data: p.devis_data,
            zone_data: p.zone_data,
          }));'''

new_formatted = '''const formatted = data.map(p => ({
            id: p.id,
            nom: p.nom,
            commune: p.commune || "",
            date: p.created_at ? p.created_at.split("T")[0] : "",
            ttc: p.total_ttc || 0,
            dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m",
            devis_data: p.devis_data,
            zone_data: p.zone_data,
            groupe_id: p.groupe_id || null,
          }));'''

if "groupe_id: p.groupe_id" in content:
    print("[INFO] groupe_id deja dans formatted")
elif old_formatted in content:
    content = content.replace(old_formatted, new_formatted, 1)
    print("[OK] groupe_id ajoute dans le formatted")
    modifs += 1
else:
    print("[WARN] Bloc formatted non trouve exactement")

# ================================================================
# MOD 4 : Ajouter les pills de filtre entre header et barre de recherche
# ================================================================

# On vise la fin du header (avant le commentaire Barre de recherche)
old_avant_search = '''{projects.length} devis
          </div>
        </div>

        {/* Barre de recherche */}'''

new_avec_pills = '''{projects.length} devis
          </div>
        </div>

        {/* Pills de filtre par groupe */}
        {(groupes.length > 0 || true) && (
          <div style={{
            display: "flex",
            gap: 6,
            marginBottom: 16,
            flexWrap: "wrap"
          }}>
            {/* Pill Tous */}
            <button
              onClick={() => setSelectedGroupe("all")}
              style={{
                background: selectedGroupe === "all" ? "rgba(240, 192, 64, 0.12)" : "rgba(255, 255, 255, 0.03)",
                border: "1px solid " + (selectedGroupe === "all" ? "rgba(240, 192, 64, 0.35)" : "rgba(255, 255, 255, 0.06)"),
                color: selectedGroupe === "all" ? "#f0c040" : "#9ca0b8",
                borderRadius: 999,
                padding: "7px 14px",
                fontSize: 12,
                fontWeight: selectedGroupe === "all" ? 600 : 500,
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: 7,
                transition: "all 0.15s",
                letterSpacing: "0.005em"
              }}
              onMouseEnter={(e) => { if (selectedGroupe !== "all") { e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)"; e.currentTarget.style.color = "#d0d2dc"; } }}
              onMouseLeave={(e) => { if (selectedGroupe !== "all") { e.currentTarget.style.background = "rgba(255, 255, 255, 0.03)"; e.currentTarget.style.color = "#9ca0b8"; } }}>
              <span style={{ width: 5, height: 5, borderRadius: "50%", background: selectedGroupe === "all" ? "#f0c040" : "#545870" }}></span>
              Tous
              <span style={{ color: selectedGroupe === "all" ? "#a8841f" : "#545870", fontWeight: 500 }}>{projects.length}</span>
            </button>
            {/* Pills par groupe */}
            {groupes.map(g => {
              const count = projects.filter(p => p.groupe_id === g.id).length;
              const isActive = selectedGroupe === g.id;
              return (
                <button
                  key={g.id}
                  onClick={() => setSelectedGroupe(g.id)}
                  style={{
                    background: isActive ? "rgba(240, 192, 64, 0.12)" : "rgba(255, 255, 255, 0.03)",
                    border: "1px solid " + (isActive ? "rgba(240, 192, 64, 0.35)" : "rgba(255, 255, 255, 0.06)"),
                    color: isActive ? "#f0c040" : "#9ca0b8",
                    borderRadius: 999,
                    padding: "7px 14px",
                    fontSize: 12,
                    fontWeight: isActive ? 600 : 500,
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 7,
                    transition: "all 0.15s",
                    letterSpacing: "0.005em"
                  }}
                  onMouseEnter={(e) => { if (!isActive) { e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)"; e.currentTarget.style.color = "#d0d2dc"; } }}
                  onMouseLeave={(e) => { if (!isActive) { e.currentTarget.style.background = "rgba(255, 255, 255, 0.03)"; e.currentTarget.style.color = "#9ca0b8"; } }}>
                  <span style={{ width: 5, height: 5, borderRadius: "50%", background: isActive ? "#f0c040" : "#545870" }}></span>
                  {g.nom}
                  <span style={{ color: isActive ? "#a8841f" : "#545870", fontWeight: 500 }}>{count}</span>
                </button>
              );
            })}
          </div>
        )}

        {/* Barre de recherche */}'''

if "Pills de filtre par groupe" in content:
    print("[INFO] Pills deja en place")
elif old_avant_search in content:
    content = content.replace(old_avant_search, new_avec_pills, 1)
    print("[OK] Pills de filtre ajoutes")
    modifs += 1
else:
    print("[ERREUR] Marqueur avant 'Barre de recherche' non trouve")
    sys.exit(1)

# ================================================================
# MOD 5 : Modifier le filtre existant pour inclure le filtre par groupe
# ================================================================

# Le filtre actuel : .filter(p => { ... return nom/commune/dims.includes(s); })
# On enrichit en ajoutant un test sur groupe_id

old_filter = '''{projects.filter(p => {
              const s = searchProjects.trim().toLowerCase();
              if (s === "") return true;
              const nom = (p.nom || "").toLowerCase();
              const commune = (p.commune || "").toLowerCase();
              const dims = (p.dims || "").toLowerCase();
              return nom.includes(s) || commune.includes(s) || dims.includes(s);
            }).length === 0 && searchProjects.trim() !== "" ? ('''

new_filter = '''{projects.filter(p => {
              // Filtre par groupe
              if (selectedGroupe !== "all" && p.groupe_id !== selectedGroupe) return false;
              // Filtre par recherche
              const s = searchProjects.trim().toLowerCase();
              if (s === "") return true;
              const nom = (p.nom || "").toLowerCase();
              const commune = (p.commune || "").toLowerCase();
              const dims = (p.dims || "").toLowerCase();
              return nom.includes(s) || commune.includes(s) || dims.includes(s);
            }).length === 0 ? ('''

if "Filtre par groupe" in content:
    print("[INFO] Filtre groupe deja en place dans la condition")
elif old_filter in content:
    content = content.replace(old_filter, new_filter, 1)
    print("[OK] Premiere occurrence du filtre mise a jour")
    modifs += 1
else:
    print("[WARN] Premier filtre non trouve")

# Et la deuxieme occurrence (le .map qui rend les cards)
old_filter_2 = ''') : projects.filter(p => {
              const s = searchProjects.trim().toLowerCase();
              if (s === "") return true;
              const nom = (p.nom || "").toLowerCase();
              const commune = (p.commune || "").toLowerCase();
              const dims = (p.dims || "").toLowerCase();
              return nom.includes(s) || commune.includes(s) || dims.includes(s);
            }).map(p => ('''

new_filter_2 = ''') : projects.filter(p => {
              // Filtre par groupe
              if (selectedGroupe !== "all" && p.groupe_id !== selectedGroupe) return false;
              // Filtre par recherche
              const s = searchProjects.trim().toLowerCase();
              if (s === "") return true;
              const nom = (p.nom || "").toLowerCase();
              const commune = (p.commune || "").toLowerCase();
              const dims = (p.dims || "").toLowerCase();
              return nom.includes(s) || commune.includes(s) || dims.includes(s);
            }).map(p => ('''

if ") : projects.filter(p => {\n              // Filtre par groupe" in content:
    print("[INFO] Filtre groupe deja en place dans .map")
elif old_filter_2 in content:
    content = content.replace(old_filter_2, new_filter_2, 1)
    print("[OK] Deuxieme occurrence du filtre mise a jour")
    modifs += 1
else:
    print("[WARN] Deuxieme filtre non trouve")

# ================================================================
# MOD 6 : Modifier le message 'Aucun resultat' pour inclure le contexte groupe
# ================================================================

old_msg = '''<div style={{ color: "#e8eaf2", fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Aucun resultat</div>
                <div style={{ color: "#7a7d92", fontSize: 13, maxWidth: 360, margin: "0 auto", lineHeight: 1.5 }}>
                  Aucun projet ne correspond a votre recherche.
                </div>'''

new_msg = '''<div style={{ color: "#e8eaf2", fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Aucun resultat</div>
                <div style={{ color: "#7a7d92", fontSize: 13, maxWidth: 360, margin: "0 auto", lineHeight: 1.5 }}>
                  {selectedGroupe !== "all" && searchProjects.trim() !== ""
                    ? "Aucun projet ne correspond a votre recherche dans ce groupe."
                    : selectedGroupe !== "all"
                    ? "Aucun projet dans ce groupe."
                    : "Aucun projet ne correspond a votre recherche."}
                </div>'''

if "Aucun projet dans ce groupe" in content:
    print("[INFO] Message contextuel deja en place")
elif old_msg in content:
    content = content.replace(old_msg, new_msg, 1)
    print("[OK] Message 'Aucun resultat' contextuel")
    modifs += 1
else:
    print("[WARN] Message 'Aucun resultat' non trouve")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. States groupes + selectedGroupe ajoutes")
print("  2. loadGroupes() au demarrage")
print("  3. groupe_id charge dans chaque projet")
print("  4. Pills 'Tous / Carports / Charpentes' avec compteurs")
print("  5. Filtrage combine (groupe + recherche)")
print("  6. Message 'Aucun resultat' adapte au contexte")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print('    git commit -m "Groupes projets Session 1 - Pills + filtrage"')
print("    git push")
print()
print(f"BACKUP : {backup_name}")
