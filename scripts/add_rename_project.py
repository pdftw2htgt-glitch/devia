#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Etape B : Menu '...' sur card projet avec Renommer
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_rename_project"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# MOD 1 : States
old_state = 'const [pendingAssignProjectId, setPendingAssignProjectId] = useState(null); // si on cree un groupe depuis une card, on assigne apres'
new_state = '''const [pendingAssignProjectId, setPendingAssignProjectId] = useState(null); // si on cree un groupe depuis une card, on assigne apres
  const [openProjectMenuId, setOpenProjectMenuId] = useState(null);
  const [renameProjectModal, setRenameProjectModal] = useState(null);
  const [renameProjectName, setRenameProjectName] = useState("");
  const [savingRename, setSavingRename] = useState(false);
  const [renameError, setRenameError] = useState(null);'''

if "const [openProjectMenuId" in content:
    print("[INFO] States deja presents")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] States ajoutes")
    modifs += 1
else:
    print("[ERREUR] State pendingAssignProjectId non trouve")
    sys.exit(1)

# MOD 2 : handleRenameProject
old_marker = 'const assignProjectToGroup = async (projectId, groupeId) => {'
new_with_function = '''const handleRenameProject = async () => {
    if (!renameProjectModal) return;
    const newName = renameProjectName.trim();
    if (!newName) { setRenameError("Le nom est obligatoire"); return; }
    if (newName.length > 120) { setRenameError("Le nom est trop long (120 caracteres maximum)"); return; }
    setSavingRename(true);
    setRenameError(null);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) { setRenameError("Vous devez etre connecte"); setSavingRename(false); return; }
      const { error } = await supabase
        .from("projects")
        .update({ nom: newName, updated_at: new Date().toISOString() })
        .eq("id", renameProjectModal.id)
        .eq("user_id", user.id);
      if (error) {
        console.error("Erreur renommage projet:", error);
        setRenameError("Erreur : " + (error.message || "echec du renommage"));
        setSavingRename(false);
        return;
      }
      setProjects(prev => prev.map(p => p.id === renameProjectModal.id ? { ...p, nom: newName } : p));
      setRenameProjectModal(null);
      setRenameProjectName("");
      setSavingRename(false);
    } catch (e) {
      console.error("Erreur handleRenameProject:", e);
      setRenameError("Erreur inattendue");
      setSavingRename(false);
    }
  };

  const assignProjectToGroup = async (projectId, groupeId) => {'''

if "const handleRenameProject" in content:
    print("[INFO] handleRenameProject deja present")
elif old_marker in content:
    content = content.replace(old_marker, new_with_function, 1)
    print("[OK] Fonction handleRenameProject ajoutee")
    modifs += 1
else:
    print("[ERREUR] assignProjectToGroup non trouve")
    sys.exit(1)

# MOD 3 : useEffect fermeture menu
old_useeffect_marker = '''  // Ferme le dropdown 'groupe du projet' au clic externe
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

new_useeffect = '''  // Ferme le dropdown 'groupe du projet' au clic externe
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
  }, [openProjectGroupDropdown]);

  // Ferme le menu '...' projet au clic externe
  useEffect(() => {
    if (!openProjectMenuId) return;
    const handleClickOutside = () => setOpenProjectMenuId(null);
    const timer = setTimeout(() => {
      document.addEventListener("click", handleClickOutside);
    }, 50);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("click", handleClickOutside);
    };
  }, [openProjectMenuId]);'''

if "Ferme le menu '...' projet" in content:
    print("[INFO] useEffect menu projet deja present")
elif old_useeffect_marker in content:
    content = content.replace(old_useeffect_marker, new_useeffect, 1)
    print("[OK] useEffect fermeture menu projet ajoute")
    modifs += 1
else:
    print("[WARN] useEffect dropdown groupe non trouve")

# MOD 4 : Icone '...' avant le bouton supprimer
old_delete_btn = '''<button onClick={(e) => { e.stopPropagation(); handleDeleteProject(p.id); }}'''

new_with_menu = '''<div style={{ position: "relative", display: "inline-block" }} onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={(e) => { e.stopPropagation(); setOpenProjectMenuId(openProjectMenuId === p.id ? null : p.id); }}
                    title="Plus d'options"
                    style={{
                      background: openProjectMenuId === p.id ? "rgba(255, 255, 255, 0.08)" : "rgba(255, 255, 255, 0.03)",
                      border: "1px solid rgba(255, 255, 255, 0.06)",
                      color: "#7a7d92",
                      cursor: "pointer",
                      borderRadius: 10,
                      padding: 9,
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      transition: "all 0.15s"
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.color = "#d0d2dc"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = openProjectMenuId === p.id ? "rgba(255, 255, 255, 0.08)" : "rgba(255, 255, 255, 0.03)"; e.currentTarget.style.color = "#7a7d92"; }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/>
                    </svg>
                  </button>
                  {openProjectMenuId === p.id && (
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
                      minWidth: 160,
                      boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
                      zIndex: 100
                    }}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setRenameProjectModal(p);
                          setRenameProjectName(p.nom || "");
                          setRenameError(null);
                          setOpenProjectMenuId(null);
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
                    </div>
                  )}
                </div>
                <button onClick={(e) => { e.stopPropagation(); handleDeleteProject(p.id); }}'''

if 'title="Plus d\'options"' in content:
    print("[INFO] Menu '...' projet deja en place")
elif old_delete_btn in content:
    content = content.replace(old_delete_btn, new_with_menu, 1)
    print("[OK] Menu '...' ajoute aux cards")
    modifs += 1
else:
    print("[ERREUR] Bouton supprimer projet non trouve")
    sys.exit(1)

# MOD 5 : Modale renommage
old_modal_marker = '{deleteConfirmGroup && ('

new_rename_modal = '''{renameProjectModal && (
    <div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0, 0, 0, 0.55)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 1000, padding: 16,
        animation: "fadeInUp 0.18s ease-out"
      }}
      onClick={(e) => { if (e.target === e.currentTarget && !savingRename) { setRenameProjectModal(null); setRenameProjectName(""); setRenameError(null); } }}>
      <div style={{
        background: "rgba(22, 25, 35, 0.95)",
        backdropFilter: "blur(24px) saturate(140%)",
        WebkitBackdropFilter: "blur(24px) saturate(140%)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: 20,
        padding: 28,
        maxWidth: 480,
        width: "100%",
        boxShadow: "0 24px 64px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,0.04) inset"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: 24, gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>Renommer le projet</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>Modifiez le nom de ce projet</div>
          </div>
          <button onClick={() => { if (!savingRename) { setRenameProjectModal(null); setRenameProjectName(""); setRenameError(null); } }}
            style={{
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              color: "#7a7d92",
              cursor: savingRename ? "not-allowed" : "pointer",
              borderRadius: 10,
              padding: 8,
              flexShrink: 0,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.15s",
              opacity: savingRename ? 0.5 : 1
            }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Nom du projet <span style={{ color: "#f0c040" }}>*</span></label>
          <input
            type="text"
            value={renameProjectName}
            onChange={(e) => setRenameProjectName(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !savingRename) handleRenameProject(); }}
            placeholder="Ex: Maison Dupont, Chantier Lyon - M. Martin..."
            autoFocus
            disabled={savingRename}
            style={inputStyle}
            maxLength={120}
          />
        </div>

        {renameError && (
          <div style={{
            background: "rgba(239, 68, 68, 0.08)",
            border: "1px solid rgba(239, 68, 68, 0.25)",
            borderRadius: 10,
            padding: 14,
            color: "#fca5a5",
            fontSize: 13,
            display: "flex",
            alignItems: "start",
            gap: 10,
            marginBottom: 16
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <div>{renameError}</div>
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12, paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <button onClick={() => { setRenameProjectModal(null); setRenameProjectName(""); setRenameError(null); }}
            disabled={savingRename}
            style={{ ...btnSecondary, opacity: savingRename ? 0.5 : 1 }}>
            Annuler
          </button>
          <button onClick={handleRenameProject}
            disabled={savingRename || !renameProjectName.trim()}
            style={{
              ...btnPrimary,
              padding: "11px 22px",
              opacity: (savingRename || !renameProjectName.trim()) ? 0.5 : 1,
              cursor: (savingRename || !renameProjectName.trim()) ? "not-allowed" : "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              boxShadow: savingRename ? "none" : "0 4px 14px rgba(240, 192, 64, 0.25)"
            }}>
            {savingRename ? (
              <>
                <span style={{ display: "inline-block", width: 13, height: 13, border: "2px solid rgba(10,10,10,0.25)", borderTopColor: "#0a0a0a", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                <span>Sauvegarde...</span>
              </>
            ) : (
              <>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                Enregistrer
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )}

  {deleteConfirmGroup && ('''

if "{renameProjectModal && (" in content:
    print("[INFO] Modale renommage deja presente")
elif old_modal_marker in content:
    content = content.replace(old_modal_marker, new_rename_modal, 1)
    print("[OK] Modale de renommage projet ajoutee")
    modifs += 1
else:
    print("[ERREUR] Marqueur deleteConfirmGroup non trouve")
    sys.exit(1)

# MOD 6 : z-index card cumule
old_card_zindex = 'zIndex: openProjectGroupDropdown === p.id ? 50 : 1'
new_card_zindex = 'zIndex: (openProjectGroupDropdown === p.id || openProjectMenuId === p.id) ? 50 : 1'

if "openProjectMenuId === p.id) ? 50 : 1" in content:
    print("[INFO] z-index card deja cumul")
elif old_card_zindex in content:
    content = content.replace(old_card_zindex, new_card_zindex, 1)
    print("[OK] z-index card cumule (groupe + menu)")
    modifs += 1
else:
    print("[WARN] z-index card non trouve")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. States renommage projet")
print("  2. Fonction handleRenameProject")
print("  3. useEffect fermeture menu")
print("  4. Icone '...' + dropdown Renommer sur chaque card")
print("  5. Modale custom de renommage")
print("  6. z-index card cumule")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
