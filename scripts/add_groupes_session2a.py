#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 2.A : Creation de groupes
- Pill ghost '+ Nouveau groupe' a la fin de la liste
- Modale simple avec input + boutons Annuler/Creer
- Insert Supabase
- Auto-selection du nouveau groupe
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_creation_groupe"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter les states pour la modale de creation
# ================================================================

old_state = 'const [selectedGroupe, setSelectedGroupe] = useState("all"); // "all" ou un UUID de groupe'
new_state = '''const [selectedGroupe, setSelectedGroupe] = useState("all"); // "all" ou un UUID de groupe
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");
  const [savingGroup, setSavingGroup] = useState(false);
  const [groupError, setGroupError] = useState(null);'''

if "const [showGroupModal" in content:
    print("[INFO] States modale deja presents")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] States modale ajoutes")
    modifs += 1
else:
    print("[ERREUR] State selectedGroupe non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Ajouter la fonction handleCreateGroup
# (juste avant le useEffect de loadProjects, on l'ajoute apres les states)
# ================================================================

# On la place avant 'const handleGenerate' qui existe dans le fichier
old_marker = 'const handleGenerate = async (finalParams) => {'

new_with_function = '''const handleCreateGroup = async () => {
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
  };

  const handleGenerate = async (finalParams) => {'''

if "const handleCreateGroup" in content:
    print("[INFO] handleCreateGroup deja present")
elif old_marker in content:
    content = content.replace(old_marker, new_with_function, 1)
    print("[OK] Fonction handleCreateGroup ajoutee")
    modifs += 1
else:
    print("[ERREUR] handleGenerate non trouve")
    sys.exit(1)

# ================================================================
# MOD 3 : Ajouter le pill ghost '+ Nouveau groupe' apres les pills
# On l'insere apres la boucle .map(g => ...) qui rend les pills
# ================================================================

old_end_pills = '''            {/* Pills par groupe */}
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
        )}'''

new_with_ghost_pill = '''            {/* Pills par groupe */}
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
            {/* Pill ghost : creer un nouveau groupe */}
            <button
              onClick={() => { setNewGroupName(""); setGroupError(null); setShowGroupModal(true); }}
              style={{
                background: "transparent",
                border: "1px dashed rgba(255, 255, 255, 0.12)",
                color: "#7a7d92",
                borderRadius: 999,
                padding: "7px 14px",
                fontSize: 12,
                fontWeight: 500,
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                transition: "all 0.15s"
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "rgba(240, 192, 64, 0.4)";
                e.currentTarget.style.color = "#f0c040";
                e.currentTarget.style.background = "rgba(240, 192, 64, 0.04)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)";
                e.currentTarget.style.color = "#7a7d92";
                e.currentTarget.style.background = "transparent";
              }}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              Nouveau groupe
            </button>
          </div>
        )}'''

if "Pill ghost : creer un nouveau groupe" in content:
    print("[INFO] Pill ghost deja en place")
elif old_end_pills in content:
    content = content.replace(old_end_pills, new_with_ghost_pill, 1)
    print("[OK] Pill ghost '+ Nouveau groupe' ajoute")
    modifs += 1
else:
    print("[ERREUR] Fin de la boucle pills non trouvee")
    sys.exit(1)

# ================================================================
# MOD 4 : Ajouter la modale de creation de groupe
# On l'insere juste avant la modale showAddCatalogModal qui existe deja
# ================================================================

old_modal_marker = '{showAddCatalogModal && ('

new_with_modal = '''{showGroupModal && (
    <div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0, 0, 0, 0.55)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 1000, padding: 16,
        animation: "fadeInUp 0.18s ease-out"
      }}
      onClick={(e) => { if (e.target === e.currentTarget && !savingGroup) { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); } }}>
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
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: 24, gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>Nouveau groupe</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>Organisez vos projets par categorie</div>
          </div>
          <button onClick={() => { if (!savingGroup) { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); } }}
            style={{
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              color: "#7a7d92",
              cursor: savingGroup ? "not-allowed" : "pointer",
              borderRadius: 10,
              padding: 8,
              flexShrink: 0,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.15s",
              opacity: savingGroup ? 0.5 : 1
            }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Nom du groupe <span style={{ color: "#f0c040" }}>*</span></label>
          <input
            type="text"
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !savingGroup) handleCreateGroup(); }}
            placeholder="Ex: Maisons neuves, Renovations..."
            autoFocus
            disabled={savingGroup}
            style={inputStyle}
            maxLength={50}
          />
        </div>

        {groupError && (
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
            <div>{groupError}</div>
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12, paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <button onClick={() => { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); }}
            disabled={savingGroup}
            style={{ ...btnSecondary, opacity: savingGroup ? 0.5 : 1 }}>
            Annuler
          </button>
          <button onClick={handleCreateGroup}
            disabled={savingGroup || !newGroupName.trim()}
            style={{
              ...btnPrimary,
              padding: "11px 22px",
              opacity: (savingGroup || !newGroupName.trim()) ? 0.5 : 1,
              cursor: (savingGroup || !newGroupName.trim()) ? "not-allowed" : "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              boxShadow: savingGroup ? "none" : "0 4px 14px rgba(240, 192, 64, 0.25)"
            }}>
            {savingGroup ? (
              <>
                <span style={{ display: "inline-block", width: 13, height: 13, border: "2px solid rgba(10,10,10,0.25)", borderTopColor: "#0a0a0a", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                <span>Creation...</span>
              </>
            ) : (
              <>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Creer
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )}

  {showAddCatalogModal && ('''

if "{showGroupModal && (" in content:
    print("[INFO] Modale creation groupe deja presente")
elif old_modal_marker in content:
    content = content.replace(old_modal_marker, new_with_modal, 1)
    print("[OK] Modale de creation de groupe ajoutee")
    modifs += 1
else:
    print("[ERREUR] Marqueur showAddCatalogModal non trouve")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. States showGroupModal, newGroupName, savingGroup, groupError")
print("  2. Fonction handleCreateGroup avec :")
print("     - Validation du nom (obligatoire, max 50 char)")
print("     - Insert Supabase")
print("     - Refresh liste + auto-select du nouveau groupe")
print("  3. Pill ghost '+ Nouveau groupe' a la fin de la liste")
print("  4. Modale de creation : label uppercase, input + boutons")
print()
print("COMMENT TESTER :")
print("  1. npm run build")
print("  2. Si OK : npm run dev (ou recharger Safari)")
print("  3. Va sur Projets")
print("  4. Click sur '+ Nouveau groupe' (le pill ghost a la fin)")
print("  5. Modale s'ouvre : tape un nom (ex: 'Maisons neuves')")
print("  6. Click Creer")
print("  7. Le groupe apparait dans les pills + auto-selectionne")
print("  8. Pour l'instant : 0 projet dans ce groupe (normal, on assignera en 2.C)")
print()
print(f"BACKUP : {backup_name}")
