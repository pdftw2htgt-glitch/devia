#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 2.B : Edition et suppression de groupes
- Icone '...' au hover du pill
- Menu deroulant Renommer / Supprimer
- Reutilise la modale de creation pour le mode 'edition'
- Modale custom de confirmation pour la suppression
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_edit_delete_groupe"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter les states pour edition/suppression
# ================================================================

old_state = '''const [savingGroup, setSavingGroup] = useState(false);
  const [groupError, setGroupError] = useState(null);'''

new_state = '''const [savingGroup, setSavingGroup] = useState(false);
  const [groupError, setGroupError] = useState(null);
  const [editingGroupId, setEditingGroupId] = useState(null); // null = creation, sinon UUID
  const [openMenuGroupId, setOpenMenuGroupId] = useState(null); // pour le menu '...'
  const [deleteConfirmGroup, setDeleteConfirmGroup] = useState(null); // objet groupe ou null
  const [deletingGroup, setDeletingGroup] = useState(false);'''

if "const [editingGroupId" in content:
    print("[INFO] States edition deja presents")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] States edition/suppression ajoutes")
    modifs += 1
else:
    print("[ERREUR] State groupError non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Modifier handleCreateGroup pour gerer aussi l'edition (upsert)
# ================================================================

old_create = '''const handleCreateGroup = async () => {
    const nom = newGroupName.trim();
    if (!nom) {
      setGroupError("Le nom est obligatoire");
      return;
    }
    if (nom.length > 50) {
      setGroupError("Le nom est trop long (50 caracteres maximum)");
      return;
    }
    setSavingGroup(true);
    setGroupError(null);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        setGroupError("Vous devez etre connecte");
        setSavingGroup(false);
        return;
      }
      const { data, error } = await supabase
        .from("groupes_projets")
        .insert([{ user_id: user.id, nom }])
        .select()
        .single();
      if (error) {
        console.error("Erreur creation groupe:", error);
        setGroupError("Erreur : " + (error.message || "echec de la creation"));
        setSavingGroup(false);
        return;
      }
      // Ajoute le groupe dans la liste et le selectionne
      setGroupes(prev => [...prev, data].sort((a, b) => a.nom.localeCompare(b.nom)));
      setSelectedGroupe(data.id);
      // Reset modale
      setShowGroupModal(false);
      setNewGroupName("");
      setSavingGroup(false);
    } catch (e) {
      console.error("Erreur handleCreateGroup:", e);
      setGroupError("Erreur inattendue");
      setSavingGroup(false);
    }
  };'''

new_create_or_edit = '''const handleCreateGroup = async () => {
    const nom = newGroupName.trim();
    if (!nom) {
      setGroupError("Le nom est obligatoire");
      return;
    }
    if (nom.length > 50) {
      setGroupError("Le nom est trop long (50 caracteres maximum)");
      return;
    }
    setSavingGroup(true);
    setGroupError(null);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        setGroupError("Vous devez etre connecte");
        setSavingGroup(false);
        return;
      }

      if (editingGroupId) {
        // Mode EDITION
        const { error } = await supabase
          .from("groupes_projets")
          .update({ nom, updated_at: new Date().toISOString() })
          .eq("id", editingGroupId)
          .eq("user_id", user.id);
        if (error) {
          console.error("Erreur edition groupe:", error);
          setGroupError("Erreur : " + (error.message || "echec de la modification"));
          setSavingGroup(false);
          return;
        }
        // Met a jour le groupe dans la liste
        setGroupes(prev => prev.map(g => g.id === editingGroupId ? { ...g, nom } : g).sort((a, b) => a.nom.localeCompare(b.nom)));
      } else {
        // Mode CREATION
        const { data, error } = await supabase
          .from("groupes_projets")
          .insert([{ user_id: user.id, nom }])
          .select()
          .single();
        if (error) {
          console.error("Erreur creation groupe:", error);
          setGroupError("Erreur : " + (error.message || "echec de la creation"));
          setSavingGroup(false);
          return;
        }
        setGroupes(prev => [...prev, data].sort((a, b) => a.nom.localeCompare(b.nom)));
        setSelectedGroupe(data.id);
      }

      // Reset modale
      setShowGroupModal(false);
      setNewGroupName("");
      setEditingGroupId(null);
      setSavingGroup(false);
    } catch (e) {
      console.error("Erreur handleCreateGroup:", e);
      setGroupError("Erreur inattendue");
      setSavingGroup(false);
    }
  };

  // Suppression d'un groupe (les projets reviennent a 'Sans groupe')
  const handleDeleteGroup = async () => {
    if (!deleteConfirmGroup) return;
    setDeletingGroup(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        setDeletingGroup(false);
        return;
      }
      const { error } = await supabase
        .from("groupes_projets")
        .delete()
        .eq("id", deleteConfirmGroup.id)
        .eq("user_id", user.id);
      if (error) {
        console.error("Erreur suppression groupe:", error);
        alert("Erreur lors de la suppression du groupe");
        setDeletingGroup(false);
        return;
      }
      // Retire le groupe de la liste
      setGroupes(prev => prev.filter(g => g.id !== deleteConfirmGroup.id));
      // Si c'etait le groupe selectionne, retour a 'Tous'
      if (selectedGroupe === deleteConfirmGroup.id) setSelectedGroupe("all");
      // Met a jour les projets : ceux qui etaient dans ce groupe -> groupe_id null
      setProjects(prev => prev.map(p => p.groupe_id === deleteConfirmGroup.id ? { ...p, groupe_id: null } : p));
      setDeleteConfirmGroup(null);
      setDeletingGroup(false);
    } catch (e) {
      console.error("Erreur handleDeleteGroup:", e);
      setDeletingGroup(false);
    }
  };'''

if "handleDeleteGroup" in content:
    print("[INFO] handleDeleteGroup deja present")
elif old_create in content:
    content = content.replace(old_create, new_create_or_edit, 1)
    print("[OK] handleCreateGroup mis a jour (creation + edition) + handleDeleteGroup")
    modifs += 1
else:
    print("[ERREUR] Fonction handleCreateGroup non trouvee")
    sys.exit(1)

# ================================================================
# MOD 3 : Modifier le pill de groupe pour ajouter l'icone '...' au hover
# ================================================================

old_pill = '''            {/* Pills par groupe */}
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
            })}'''

new_pill = '''            {/* Pills par groupe */}
            {groupes.map(g => {
              const count = projects.filter(p => p.groupe_id === g.id).length;
              const isActive = selectedGroupe === g.id;
              const menuOpen = openMenuGroupId === g.id;
              return (
                <div key={g.id} style={{ position: "relative", display: "inline-flex" }}>
                  <div
                    style={{
                      background: isActive ? "rgba(240, 192, 64, 0.12)" : "rgba(255, 255, 255, 0.03)",
                      border: "1px solid " + (isActive ? "rgba(240, 192, 64, 0.35)" : "rgba(255, 255, 255, 0.06)"),
                      borderRadius: 999,
                      padding: "0 4px 0 14px",
                      fontSize: 12,
                      fontWeight: isActive ? 600 : 500,
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 7,
                      transition: "all 0.15s",
                      letterSpacing: "0.005em",
                      color: isActive ? "#f0c040" : "#9ca0b8",
                      cursor: "pointer"
                    }}
                    onMouseEnter={(e) => { if (!isActive) { e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)"; e.currentTarget.style.color = "#d0d2dc"; } }}
                    onMouseLeave={(e) => { if (!isActive) { e.currentTarget.style.background = "rgba(255, 255, 255, 0.03)"; e.currentTarget.style.color = "#9ca0b8"; } }}>
                    <span onClick={() => setSelectedGroupe(g.id)} style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "7px 4px 7px 0" }}>
                      <span style={{ width: 5, height: 5, borderRadius: "50%", background: isActive ? "#f0c040" : "#545870" }}></span>
                      {g.nom}
                      <span style={{ color: isActive ? "#a8841f" : "#545870", fontWeight: 500 }}>{count}</span>
                    </span>
                    <button
                      onClick={(e) => { e.stopPropagation(); setOpenMenuGroupId(menuOpen ? null : g.id); }}
                      title="Options"
                      style={{
                        background: menuOpen ? "rgba(255, 255, 255, 0.08)" : "transparent",
                        border: "none",
                        color: "inherit",
                        cursor: "pointer",
                        padding: "4px 6px",
                        borderRadius: 999,
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        opacity: menuOpen ? 1 : 0.55,
                        transition: "opacity 0.15s, background 0.15s"
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.opacity = "1"; }}
                      onMouseLeave={(e) => { e.currentTarget.style.opacity = menuOpen ? "1" : "0.55"; }}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/>
                      </svg>
                    </button>
                  </div>
                  {menuOpen && (
                    <div style={{
                      position: "absolute",
                      top: "calc(100% + 4px)",
                      right: 0,
                      background: "rgba(22, 25, 35, 0.98)",
                      backdropFilter: "blur(20px) saturate(140%)",
                      WebkitBackdropFilter: "blur(20px) saturate(140%)",
                      border: "1px solid rgba(255, 255, 255, 0.08)",
                      borderRadius: 10,
                      padding: 4,
                      minWidth: 140,
                      boxShadow: "0 8px 24px rgba(0, 0, 0, 0.35)",
                      zIndex: 10
                    }}>
                      <button onClick={() => {
                        setEditingGroupId(g.id);
                        setNewGroupName(g.nom);
                        setGroupError(null);
                        setShowGroupModal(true);
                        setOpenMenuGroupId(null);
                      }}
                        style={{
                          width: "100%", background: "transparent", border: "none",
                          color: "#e8eaf2", textAlign: "left", padding: "8px 12px",
                          fontSize: 13, cursor: "pointer", borderRadius: 7,
                          display: "flex", alignItems: "center", gap: 8, transition: "background 0.12s"
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; }}
                        onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                        Renommer
                      </button>
                      <button onClick={() => {
                        setDeleteConfirmGroup(g);
                        setOpenMenuGroupId(null);
                      }}
                        style={{
                          width: "100%", background: "transparent", border: "none",
                          color: "#fca5a5", textAlign: "left", padding: "8px 12px",
                          fontSize: 13, cursor: "pointer", borderRadius: 7,
                          display: "flex", alignItems: "center", gap: 8, transition: "background 0.12s"
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)"; e.currentTarget.style.color = "#ef4444"; }}
                        onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "#fca5a5"; }}>
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                        </svg>
                        Supprimer
                      </button>
                    </div>
                  )}
                </div>
              );
            })}'''

if "openMenuGroupId === g.id" in content:
    print("[INFO] Icone '...' deja en place")
elif old_pill in content:
    content = content.replace(old_pill, new_pill, 1)
    print("[OK] Icone '...' + menu Renommer/Supprimer ajoute aux pills")
    modifs += 1
else:
    print("[ERREUR] Bloc pills groupes non trouve")
    sys.exit(1)

# ================================================================
# MOD 4 : Mettre a jour le titre de la modale pour gerer mode edition
# ================================================================

old_title = '''<h2 style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>Nouveau groupe</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>Organisez vos projets par categorie</div>'''

new_title = '''<h2 style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>{editingGroupId ? "Renommer le groupe" : "Nouveau groupe"}</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>{editingGroupId ? "Modifiez le nom du groupe" : "Organisez vos projets par categorie"}</div>'''

if "{editingGroupId ?" in content and "Renommer le groupe" in content:
    print("[INFO] Titre modale deja contextuel")
elif old_title in content:
    content = content.replace(old_title, new_title, 1)
    print("[OK] Titre modale rendu contextuel (creation/edition)")
    modifs += 1
else:
    print("[WARN] Titre modale non trouve")

# ================================================================
# MOD 5 : Mettre a jour le bouton 'Creer' pour devenir 'Enregistrer' en mode edition
# ================================================================

old_btn_text = '''<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Creer
              </>'''

new_btn_text = '''{editingGroupId ? (
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                ) : (
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                  </svg>
                )}
                {editingGroupId ? "Enregistrer" : "Creer"}
              </>'''

if "{editingGroupId ? \"Enregistrer\" : \"Creer\"}" in content:
    print("[INFO] Bouton Creer/Enregistrer deja contextuel")
elif old_btn_text in content:
    content = content.replace(old_btn_text, new_btn_text, 1)
    print("[OK] Bouton Creer/Enregistrer rendu contextuel")
    modifs += 1
else:
    print("[WARN] Bouton Creer non trouve")

# ================================================================
# MOD 6 : Mettre a jour le spinner pour dire 'Sauvegarde...' en mode edition
# ================================================================

old_spinner = '''<span>Creation...</span>'''
new_spinner = '''<span>{editingGroupId ? "Sauvegarde..." : "Creation..."}</span>'''

if "{editingGroupId ? \"Sauvegarde...\" : \"Creation...\"}" in content:
    print("[INFO] Spinner deja contextuel")
elif old_spinner in content:
    content = content.replace(old_spinner, new_spinner, 1)
    print("[OK] Spinner contextuel")
    modifs += 1

# ================================================================
# MOD 7 : Reset editingGroupId quand on ferme la modale
# (3 endroits : click backdrop, X, Annuler)
# ================================================================

old_close_backdrop = 'onClick={(e) => { if (e.target === e.currentTarget && !savingGroup) { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); } }}>'
new_close_backdrop = 'onClick={(e) => { if (e.target === e.currentTarget && !savingGroup) { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); setEditingGroupId(null); } }}>'

if old_close_backdrop in content:
    content = content.replace(old_close_backdrop, new_close_backdrop, 1)
    print("[OK] Reset editingGroupId au clic backdrop")
    modifs += 1

old_close_x = 'onClick={() => { if (!savingGroup) { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); } }}'
new_close_x = 'onClick={() => { if (!savingGroup) { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); setEditingGroupId(null); } }}'

if old_close_x in content:
    content = content.replace(old_close_x, new_close_x, 1)
    print("[OK] Reset editingGroupId au clic X")
    modifs += 1

old_close_cancel = '<button onClick={() => { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); }}\n            disabled={savingGroup}'
new_close_cancel = '<button onClick={() => { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); setEditingGroupId(null); }}\n            disabled={savingGroup}'

if old_close_cancel in content:
    content = content.replace(old_close_cancel, new_close_cancel, 1)
    print("[OK] Reset editingGroupId au clic Annuler")
    modifs += 1

# ================================================================
# MOD 8 : Ajouter la modale de confirmation de suppression
# (juste avant la modale showGroupModal pour rester logique)
# ================================================================

old_modal_marker = '{showGroupModal && ('

new_with_confirm_modal = '''{deleteConfirmGroup && (
    <div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0, 0, 0, 0.55)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 1001, padding: 16,
        animation: "fadeInUp 0.18s ease-out"
      }}
      onClick={(e) => { if (e.target === e.currentTarget && !deletingGroup) setDeleteConfirmGroup(null); }}>
      <div style={{
        background: "rgba(22, 25, 35, 0.95)",
        backdropFilter: "blur(24px) saturate(140%)",
        WebkitBackdropFilter: "blur(24px) saturate(140%)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: 20,
        padding: 28,
        maxWidth: 440,
        width: "100%",
        boxShadow: "0 24px 64px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,0.04) inset"
      }}>
        <div style={{ display: "flex", alignItems: "start", gap: 14, marginBottom: 20 }}>
          <div style={{
            width: 40, height: 40, borderRadius: 10,
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.25)",
            display: "flex", alignItems: "center", justifyContent: "center",
            flexShrink: 0
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>Supprimer le groupe ?</h2>
            <div style={{ color: "#9ca0b8", fontSize: 13, lineHeight: 1.55 }}>
              Le groupe <span style={{ color: "#e8eaf2", fontWeight: 600 }}>&quot;{deleteConfirmGroup.nom}&quot;</span> sera supprime. Les projets associes ne seront pas supprimes, ils reviendront a &quot;Tous&quot; sans groupe.
            </div>
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12, paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <button onClick={() => setDeleteConfirmGroup(null)}
            disabled={deletingGroup}
            style={{ ...btnSecondary, opacity: deletingGroup ? 0.5 : 1 }}>
            Annuler
          </button>
          <button onClick={handleDeleteGroup}
            disabled={deletingGroup}
            style={{
              background: "#ef4444",
              color: "#fff",
              border: "1px solid #ef4444",
              borderRadius: 10,
              padding: "11px 22px",
              fontSize: 13,
              fontWeight: 600,
              cursor: deletingGroup ? "not-allowed" : "pointer",
              opacity: deletingGroup ? 0.7 : 1,
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              transition: "background 0.15s",
              boxShadow: "0 4px 14px rgba(239, 68, 68, 0.25)"
            }}
            onMouseEnter={(e) => { if (!deletingGroup) e.currentTarget.style.background = "#dc2626"; }}
            onMouseLeave={(e) => { if (!deletingGroup) e.currentTarget.style.background = "#ef4444"; }}>
            {deletingGroup ? (
              <>
                <span style={{ display: "inline-block", width: 13, height: 13, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                <span>Suppression...</span>
              </>
            ) : (
              <>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                </svg>
                Supprimer
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )}

  {showGroupModal && ('''

if "{deleteConfirmGroup && (" in content:
    print("[INFO] Modale confirmation suppression deja presente")
elif old_modal_marker in content:
    content = content.replace(old_modal_marker, new_with_confirm_modal, 1)
    print("[OK] Modale de confirmation de suppression ajoutee")
    modifs += 1
else:
    print("[ERREUR] Marqueur showGroupModal non trouve")
    sys.exit(1)

# ================================================================
# MOD 9 : Fermer le menu si on clique ailleurs
# On ajoute un useEffect global qui ferme le menu au clic externe
# ================================================================

old_loadgroupes_end = '''    loadGroupes();
  }, []);'''

new_loadgroupes_with_close = '''    loadGroupes();
  }, []);

  // Ferme le menu '...' au clic externe
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

if "Ferme le menu '...' au clic externe" in content:
    print("[INFO] useEffect fermeture menu deja present")
elif old_loadgroupes_end in content:
    content = content.replace(old_loadgroupes_end, new_loadgroupes_with_close, 1)
    print("[OK] useEffect fermeture menu au clic externe ajoute")
    modifs += 1
else:
    print("[WARN] Fin loadGroupes non trouvee, le menu ne se fermera pas auto")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. States edition/suppression (editingGroupId, openMenuGroupId, etc.)")
print("  2. handleCreateGroup mis a jour pour gerer aussi l'edition")
print("  3. handleDeleteGroup ajoute")
print("  4. Pills : icone '...' au hover, menu Renommer/Supprimer")
print("  5. Modale : titre contextuel ('Nouveau' ou 'Renommer')")
print("  6. Bouton contextuel ('Creer' ou 'Enregistrer' avec icone check)")
print("  7. Reset editingGroupId aux 3 fermetures de modale")
print("  8. Modale de confirmation de suppression (rouge)")
print("  9. Fermeture auto du menu au clic externe")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
