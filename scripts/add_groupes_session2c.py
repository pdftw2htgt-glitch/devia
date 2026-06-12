#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 2.C : Assigner un projet a un groupe
- Badge cliquable sur chaque card de projet
- Dropdown avec liste des groupes + 'Sans groupe' + '+ Nouveau groupe'
- Update Supabase + etat local
- Cliquer en dehors ferme le dropdown
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_assign_group_to_project"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter le state du dropdown ouvert (sur quelle card)
# ================================================================

old_state = '''const [deleteConfirmGroup, setDeleteConfirmGroup] = useState(null); // objet groupe ou null
  const [deletingGroup, setDeletingGroup] = useState(false);'''

new_state = '''const [deleteConfirmGroup, setDeleteConfirmGroup] = useState(null); // objet groupe ou null
  const [deletingGroup, setDeletingGroup] = useState(false);
  const [openProjectGroupDropdown, setOpenProjectGroupDropdown] = useState(null); // id du projet dont le dropdown est ouvert'''

if "const [openProjectGroupDropdown" in content:
    print("[INFO] State dropdown projet deja present")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] State openProjectGroupDropdown ajoute")
    modifs += 1
else:
    print("[ERREUR] State deleteConfirmGroup non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Ajouter la fonction assignProjectToGroup
# (On l'ajoute apres handleDeleteGroup)
# ================================================================

old_marker = '''const handleDeleteGroup = async () => {'''

# On veut l'ajouter AVANT cette fonction
new_with_assign = '''const assignProjectToGroup = async (projectId, groupeId) => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      const { error } = await supabase
        .from("projects")
        .update({ groupe_id: groupeId, updated_at: new Date().toISOString() })
        .eq("id", projectId)
        .eq("user_id", user.id);
      if (error) {
        console.error("Erreur assignation groupe:", error);
        return;
      }
      // Met a jour l'etat local
      setProjects(prev => prev.map(p => p.id === projectId ? { ...p, groupe_id: groupeId } : p));
      setOpenProjectGroupDropdown(null);
    } catch (e) {
      console.error("Erreur assignProjectToGroup:", e);
    }
  };

  const handleDeleteGroup = async () => {'''

if "const assignProjectToGroup" in content:
    print("[INFO] Fonction assignProjectToGroup deja presente")
elif old_marker in content:
    content = content.replace(old_marker, new_with_assign, 1)
    print("[OK] Fonction assignProjectToGroup ajoutee")
    modifs += 1
else:
    print("[ERREUR] handleDeleteGroup non trouve")
    sys.exit(1)

# ================================================================
# MOD 3 : Ajouter le badge dans la card du projet
# Le badge est ajoute juste avant la fermeture du div des infos (ligne avec icones epingle/dates)
# On vise la ligne <div style=... color: "#7a7d92", fontSize: 12... avec gap: 6, flexWrap: "wrap" }}>
# ================================================================

# Pour le placement, on va chercher la fermeture du div d'infos (date)
# Le pattern : juste apres la fin de la ligne d'infos commune/dims/date
# On insere le badge a la fin du contenu du div principal (avant fermeture)

# Strategie : on trouve la div principale infos (commune, dims, date)
# et on ajoute le badge dans son flow

old_infos_block = '''<div style={{ color: "#7a7d92", fontSize: 12, display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
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
                    </div>'''

new_infos_with_badge = '''<div style={{ color: "#7a7d92", fontSize: 12, display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
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
                    {/* Badge groupe */}
                    <div style={{ position: "relative", marginTop: 8, display: "inline-block" }} onClick={(e) => e.stopPropagation()}>
                      {(() => {
                        const groupeCourant = groupes.find(g => g.id === p.groupe_id);
                        const isOpen = openProjectGroupDropdown === p.id;
                        return (
                          <>
                            <button
                              onClick={(e) => { e.stopPropagation(); setOpenProjectGroupDropdown(isOpen ? null : p.id); }}
                              style={{
                                background: groupeCourant ? "rgba(96, 165, 250, 0.08)" : "transparent",
                                border: "1px " + (groupeCourant ? "solid rgba(96, 165, 250, 0.25)" : "dashed rgba(255, 255, 255, 0.12)"),
                                color: groupeCourant ? "#60a5fa" : "#7a7d92",
                                borderRadius: 999,
                                padding: "3px 10px",
                                fontSize: 11,
                                fontWeight: 500,
                                cursor: "pointer",
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 5,
                                transition: "all 0.15s",
                                letterSpacing: "0.01em"
                              }}
                              onMouseEnter={(e) => {
                                if (groupeCourant) { e.currentTarget.style.background = "rgba(96, 165, 250, 0.14)"; }
                                else { e.currentTarget.style.borderColor = "rgba(240, 192, 64, 0.4)"; e.currentTarget.style.color = "#f0c040"; }
                              }}
                              onMouseLeave={(e) => {
                                if (groupeCourant) { e.currentTarget.style.background = "rgba(96, 165, 250, 0.08)"; }
                                else { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)"; e.currentTarget.style.color = "#7a7d92"; }
                              }}>
                              {groupeCourant ? (
                                <>
                                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
                                  </svg>
                                  {groupeCourant.nom}
                                </>
                              ) : (
                                <>
                                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                                    <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                                  </svg>
                                  Ajouter a un groupe
                                </>
                              )}
                              <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.7 }}>
                                <polyline points="6 9 12 15 18 9"/>
                              </svg>
                            </button>
                            {isOpen && (
                              <div style={{
                                position: "absolute",
                                top: "calc(100% + 4px)",
                                left: 0,
                                background: "rgba(22, 25, 35, 0.98)",
                                backdropFilter: "blur(20px) saturate(140%)",
                                WebkitBackdropFilter: "blur(20px) saturate(140%)",
                                border: "1px solid rgba(255, 255, 255, 0.08)",
                                borderRadius: 10,
                                padding: 4,
                                minWidth: 200,
                                maxHeight: 280,
                                overflowY: "auto",
                                boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
                                zIndex: 20
                              }}>
                                {/* Option Sans groupe */}
                                <button
                                  onClick={(e) => { e.stopPropagation(); assignProjectToGroup(p.id, null); }}
                                  style={{
                                    width: "100%", background: "transparent", border: "none",
                                    color: !p.groupe_id ? "#f0c040" : "#9ca0b8", textAlign: "left",
                                    padding: "8px 12px", fontSize: 13, cursor: "pointer", borderRadius: 7,
                                    display: "flex", alignItems: "center", gap: 8, transition: "background 0.12s",
                                    fontWeight: !p.groupe_id ? 600 : 500
                                  }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                                  <span style={{ width: 14, display: "inline-flex" }}>
                                    {!p.groupe_id && (
                                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                        <polyline points="20 6 9 17 4 12"/>
                                      </svg>
                                    )}
                                  </span>
                                  Sans groupe
                                </button>
                                {/* Liste des groupes */}
                                {groupes.map(g => (
                                  <button
                                    key={g.id}
                                    onClick={(e) => { e.stopPropagation(); assignProjectToGroup(p.id, g.id); }}
                                    style={{
                                      width: "100%", background: "transparent", border: "none",
                                      color: p.groupe_id === g.id ? "#f0c040" : "#e8eaf2", textAlign: "left",
                                      padding: "8px 12px", fontSize: 13, cursor: "pointer", borderRadius: 7,
                                      display: "flex", alignItems: "center", gap: 8, transition: "background 0.12s",
                                      fontWeight: p.groupe_id === g.id ? 600 : 500
                                    }}
                                    onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; }}
                                    onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                                    <span style={{ width: 14, display: "inline-flex" }}>
                                      {p.groupe_id === g.id && (
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                          <polyline points="20 6 9 17 4 12"/>
                                        </svg>
                                      )}
                                    </span>
                                    {g.nom}
                                  </button>
                                ))}
                                <div style={{ height: 1, background: "rgba(255, 255, 255, 0.06)", margin: "4px 0" }}></div>
                                {/* Nouveau groupe */}
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setOpenProjectGroupDropdown(null);
                                    setNewGroupName(""); setGroupError(null); setEditingGroupId(null);
                                    setShowGroupModal(true);
                                  }}
                                  style={{
                                    width: "100%", background: "transparent", border: "none",
                                    color: "#7a7d92", textAlign: "left",
                                    padding: "8px 12px", fontSize: 13, cursor: "pointer", borderRadius: 7,
                                    display: "flex", alignItems: "center", gap: 8, transition: "background 0.12s"
                                  }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(240, 192, 64, 0.08)"; e.currentTarget.style.color = "#f0c040"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "#7a7d92"; }}>
                                  <span style={{ width: 14, display: "inline-flex", alignItems: "center" }}>
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                                      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                                    </svg>
                                  </span>
                                  Nouveau groupe
                                </button>
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </div>'''

if "openProjectGroupDropdown === p.id" in content:
    print("[INFO] Badge groupe deja sur les cards")
elif old_infos_block in content:
    content = content.replace(old_infos_block, new_infos_with_badge, 1)
    print("[OK] Badge groupe ajoute sur les cards (avec dropdown)")
    modifs += 1
else:
    print("[ERREUR] Bloc infos card non trouve")
    sys.exit(1)

# ================================================================
# MOD 4 : Fermer le dropdown au clic externe
# ================================================================

old_useeffect = '''  // Ferme le menu '...' au clic externe
  useEffect(() => {
    if (!openMenuGroupId) return;
    const handleClickOutside = () => setOpenMenuGroupId(null);
    // setTimeout pour eviter de fermer immediatement (au moment du click qui a ouvert)
    const timer = setTimeout(() => {
      document.addEventListener("click", handleClickOutside);
    }, 50);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("click", handleClickOutside);
    };
  }, [openMenuGroupId]);'''

new_useeffect = '''  // Ferme le menu '...' au clic externe
  useEffect(() => {
    if (!openMenuGroupId) return;
    const handleClickOutside = () => setOpenMenuGroupId(null);
    const timer = setTimeout(() => {
      document.addEventListener("click", handleClickOutside);
    }, 50);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("click", handleClickOutside);
    };
  }, [openMenuGroupId]);

  // Ferme le dropdown 'groupe du projet' au clic externe
  useEffect(() => {
    if (!openProjectGroupDropdown) return;
    const handleClickOutside = () => setOpenProjectGroupDropdown(null);
    const timer = setTimeout(() => {
      document.addEventListener("click", handleClickOutside);
    }, 50);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("click", handleClickOutside);
    };
  }, [openProjectGroupDropdown]);'''

if "openProjectGroupDropdown\");" in content and "handleClickOutside" in content:
    # Verifier si le hook est deja ajoute pour le dropdown projet
    if "if (!openProjectGroupDropdown) return;" in content:
        print("[INFO] useEffect fermeture dropdown projet deja present")
    else:
        if old_useeffect in content:
            content = content.replace(old_useeffect, new_useeffect, 1)
            print("[OK] useEffect fermeture dropdown projet ajoute")
            modifs += 1
elif old_useeffect in content:
    content = content.replace(old_useeffect, new_useeffect, 1)
    print("[OK] useEffect fermeture dropdown projet ajoute")
    modifs += 1
else:
    print("[WARN] useEffect fermeture menu '...' non trouve")

# ================================================================
# MOD 5 : Quand un nouveau groupe est cree depuis le dropdown card,
# auto-assigner le projet au nouveau groupe.
# Pour ca, on ajoute un state pour memoriser le projet en cours
# (si on clique 'Nouveau groupe' depuis le dropdown d'un projet)
# ================================================================

old_state_extra = 'const [openProjectGroupDropdown, setOpenProjectGroupDropdown] = useState(null); // id du projet dont le dropdown est ouvert'
new_state_extra = '''const [openProjectGroupDropdown, setOpenProjectGroupDropdown] = useState(null); // id du projet dont le dropdown est ouvert
  const [pendingAssignProjectId, setPendingAssignProjectId] = useState(null); // si on cree un groupe depuis une card, on assigne apres'''

if "const [pendingAssignProjectId" in content:
    print("[INFO] State pendingAssignProjectId deja present")
elif old_state_extra in content:
    content = content.replace(old_state_extra, new_state_extra, 1)
    print("[OK] State pendingAssignProjectId ajoute")
    modifs += 1

# Modifier le onClick 'Nouveau groupe' du dropdown projet pour memoriser le projet
old_nouveau_groupe_click = '''onClick={(e) => {
                                    e.stopPropagation();
                                    setOpenProjectGroupDropdown(null);
                                    setNewGroupName(""); setGroupError(null); setEditingGroupId(null);
                                    setShowGroupModal(true);
                                  }}'''

new_nouveau_groupe_click = '''onClick={(e) => {
                                    e.stopPropagation();
                                    setPendingAssignProjectId(p.id); // memorise le projet pour l'assigner ensuite
                                    setOpenProjectGroupDropdown(null);
                                    setNewGroupName(""); setGroupError(null); setEditingGroupId(null);
                                    setShowGroupModal(true);
                                  }}'''

if "setPendingAssignProjectId(p.id)" in content:
    print("[INFO] Memorisation projet deja en place")
elif old_nouveau_groupe_click in content:
    content = content.replace(old_nouveau_groupe_click, new_nouveau_groupe_click, 1)
    print("[OK] Memorisation projet pour assignation post-creation")
    modifs += 1

# Modifier handleCreateGroup pour faire l'assignation auto si pendingAssignProjectId
# Le 'mode CREATION' deja existant : on ajoute apres setSelectedGroupe(data.id)
old_creation_block = '''setGroupes(prev => [...prev, data].sort((a, b) => a.nom.localeCompare(b.nom)));
        setSelectedGroupe(data.id);
      }'''

new_creation_block_with_assign = '''setGroupes(prev => [...prev, data].sort((a, b) => a.nom.localeCompare(b.nom)));
        setSelectedGroupe(data.id);
        // Si on creait depuis une card projet, on assigne le projet a ce nouveau groupe
        if (pendingAssignProjectId) {
          await assignProjectToGroup(pendingAssignProjectId, data.id);
          setPendingAssignProjectId(null);
        }
      }'''

if "if (pendingAssignProjectId)" in content:
    print("[INFO] Assignation post-creation deja en place")
elif old_creation_block in content:
    content = content.replace(old_creation_block, new_creation_block_with_assign, 1)
    print("[OK] Assignation auto apres creation depuis card projet")
    modifs += 1

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. State openProjectGroupDropdown + pendingAssignProjectId")
print("  2. Fonction assignProjectToGroup (UPDATE Supabase + etat local)")
print("  3. Badge clicable sur chaque card de projet :")
print("     - Si groupe : bleu avec nom et chevron")
print("     - Si pas de groupe : dashed gris '+ Ajouter a un groupe'")
print("  4. Dropdown au click sur le badge :")
print("     - Option 'Sans groupe' (check si actif)")
print("     - Liste des groupes (check si actif)")
print("     - Separateur")
print("     - '+ Nouveau groupe' (ouvre la modale)")
print("  5. Fermeture auto au clic externe")
print("  6. Si on cree un groupe depuis une card, le projet est auto-assigne")
print()
print("COMMENT TESTER :")
print("  1. npm run build")
print("  2. Recharger Safari")
print("  3. Page Projets")
print("  4. Voir le badge 'Carports' (ou autre) sur chaque card")
print("  5. Cliquer dessus -> dropdown s'ouvre")
print("  6. Cliquer sur un groupe -> changement immediat")
print("  7. Cliquer 'Sans groupe' -> retire le projet du groupe")
print("  8. Cliquer 'Nouveau groupe' -> modale s'ouvre, on cree, et le projet")
print("     est auto-assigne au nouveau groupe")
print()
print(f"BACKUP : {backup_name}")
