#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Etape 2.A.3.c : Modification + suppression catalogue entreprise
Ajoute :
1. Boutons Modifier/Supprimer sur chaque ligne de Mon catalogue
2. La modale s'adapte (Ajouter ou Modifier selon contexte)
3. UPDATE Supabase pour modifier
4. DELETE Supabase pour supprimer (avec confirmation)

A lancer depuis ~/Desktop/devia :
    python3 add_edit_delete_catalogue.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("package.json"):
    print("ERREUR : package.json introuvable. Lance depuis ~/Desktop/devia")
    sys.exit(1)

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_edit_delete"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MODIFICATION 1 : Ajouter le state editingCatalogId
# ================================================================

old_savingcat = "const [savingCatalog, setSavingCatalog] = useState(false);"

if "editingCatalogId" in content:
    print("[INFO] State editingCatalogId deja present, skip modification 1")
else:
    new_savingcat = '''const [savingCatalog, setSavingCatalog] = useState(false);
  const [editingCatalogId, setEditingCatalogId] = useState(null);'''

    if old_savingcat not in content:
        print("ERREUR : impossible de trouver savingCatalog state.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_savingcat, new_savingcat, 1)
    print("[OK] State editingCatalogId ajoute")

# ================================================================
# MODIFICATION 2 : Modifier resetCatalogForm pour reset l'id d'edition
# ================================================================

old_reset = '''const resetCatalogForm = () => {
    setCatalogForm({
      categorie: "Charpente",
      categorieAutre: "",
      designation: "",
      dimensions: "",
      unite: "ml",
      prix_ht: "",
      notes: "",
    });
    setCatalogFormError(null);
  };'''

new_reset = '''const resetCatalogForm = () => {
    setCatalogForm({
      categorie: "Charpente",
      categorieAutre: "",
      designation: "",
      dimensions: "",
      unite: "ml",
      prix_ht: "",
      notes: "",
    });
    setCatalogFormError(null);
    setEditingCatalogId(null);
  };

  const openEditCatalogModal = (material) => {
    const isStandardCat = ["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie", "Main d'oeuvre"].includes(material.categorie);
    setCatalogForm({
      categorie: isStandardCat ? material.categorie : "Autre",
      categorieAutre: isStandardCat ? "" : material.categorie,
      designation: material.designation || "",
      dimensions: material.dimensions || "",
      unite: material.unite || "ml",
      prix_ht: material.prix_ht ? String(material.prix_ht) : "",
      notes: material.notes || "",
    });
    setEditingCatalogId(material.id);
    setCatalogFormError(null);
    setShowAddCatalogModal(true);
  };

  const handleDeleteMaterial = async (material) => {
    const confirmed = window.confirm("Supprimer le materiau \\"" + material.designation + "\\" ? Cette action est irreversible.");
    if (!confirmed) return;
    try {
      const { error } = await supabase
        .from("catalogue_entreprise")
        .delete()
        .eq("id", material.id);
      if (error) {
        console.error("Erreur suppression catalogue:", error);
        alert("Erreur lors de la suppression : " + error.message);
        return;
      }
      setCatalogueEntreprise(prev => prev.filter(m => m.id !== material.id));
    } catch (e) {
      console.error("Erreur handleDeleteMaterial:", e);
      alert("Erreur inattendue lors de la suppression.");
    }
  };'''

if "openEditCatalogModal" in content:
    print("[INFO] Fonctions edit/delete deja presentes, skip modification 2")
else:
    if old_reset not in content:
        print("ERREUR : impossible de trouver resetCatalogForm.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_reset, new_reset, 1)
    print("[OK] Fonctions openEditCatalogModal et handleDeleteMaterial ajoutees")

# ================================================================
# MODIFICATION 3 : Modifier handleAddMaterial pour gerer Ajout ET Modif
# ================================================================

old_insert_block = '''const { data: inserted, error } = await supabase
        .from("catalogue_entreprise")
        .insert(newRow)
        .select()
        .single();
      if (error) {
        console.error("Erreur insertion catalogue:", error);
        setCatalogFormError("Erreur : " + error.message);
        setSavingCatalog(false);
        return;
      }
      // Ajout local
      setCatalogueEntreprise(prev => [inserted, ...prev]);
      setShowAddCatalogModal(false);
      resetCatalogForm();'''

new_insert_block = '''if (editingCatalogId) {
        // MODE MODIFICATION
        const { data: updated, error } = await supabase
          .from("catalogue_entreprise")
          .update(newRow)
          .eq("id", editingCatalogId)
          .select()
          .single();
        if (error) {
          console.error("Erreur update catalogue:", error);
          setCatalogFormError("Erreur : " + error.message);
          setSavingCatalog(false);
          return;
        }
        // Mise a jour locale
        setCatalogueEntreprise(prev => prev.map(m => m.id === editingCatalogId ? updated : m));
      } else {
        // MODE AJOUT
        const { data: inserted, error } = await supabase
          .from("catalogue_entreprise")
          .insert(newRow)
          .select()
          .single();
        if (error) {
          console.error("Erreur insertion catalogue:", error);
          setCatalogFormError("Erreur : " + error.message);
          setSavingCatalog(false);
          return;
        }
        setCatalogueEntreprise(prev => [inserted, ...prev]);
      }
      setShowAddCatalogModal(false);
      resetCatalogForm();'''

if "MODE MODIFICATION" in content:
    print("[INFO] handleAddMaterial deja modifie pour edit, skip modification 3")
else:
    if old_insert_block not in content:
        print("ERREUR : impossible de trouver le bloc insert.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_insert_block, new_insert_block, 1)
    print("[OK] handleAddMaterial gere Ajout ET Modification")

# ================================================================
# MODIFICATION 4 : Modifier le titre et le bouton de la modale
# ================================================================

old_modal_title = '''<h2 style={{ fontSize: 18, fontWeight: 700 }}>Ajouter un materiau</h2>'''
new_modal_title = '''<h2 style={{ fontSize: 18, fontWeight: 700 }}>{editingCatalogId ? "Modifier un materiau" : "Ajouter un materiau"}</h2>'''

if "Modifier un materiau" in content:
    print("[INFO] Titre modale deja adapte, skip modification 4")
else:
    if old_modal_title not in content:
        print("ATTENTION : titre modale non trouve, mais on continue.")
    else:
        content = content.replace(old_modal_title, new_modal_title, 1)
        print("[OK] Titre modale adapte (Ajouter / Modifier)")

old_modal_button = '''{savingCatalog ? "Ajout en cours..." : "Ajouter"}'''
new_modal_button = '''{savingCatalog ? (editingCatalogId ? "Sauvegarde..." : "Ajout en cours...") : (editingCatalogId ? "Enregistrer" : "Ajouter")}'''

if "Sauvegarde..." in content:
    print("[INFO] Bouton modale deja adapte, skip modification 4 bis")
else:
    if old_modal_button not in content:
        print("ATTENTION : bouton modale non trouve, mais on continue.")
    else:
        content = content.replace(old_modal_button, new_modal_button, 1)
        print("[OK] Bouton modale adapte")

# ================================================================
# MODIFICATION 5 : Ajouter les boutons Modifier/Supprimer dans la liste
# ================================================================

old_perso_table = '''<table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead>
                        <tr style={{ background: "#0f1117" }}>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Categorie</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Designation</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Dimensions</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Unite</th>
                          <th style={{ padding: "10px 12px", textAlign: "right", color: "#545870", fontSize: 12, fontWeight: 600 }}>Prix HT</th>
                        </tr>
                      </thead>
                      <tbody>
                        {catalogueEntreprise.map((m, i) => (
                          <tr key={m.id} style={{ borderTop: "1px solid #1e2231", background: i % 2 === 0 ? "transparent" : "#0f111740" }}>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#60a5fa" }}>{m.categorie}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13 }}>{m.designation}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.dimensions || "-"}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.unite}</td>
                            <td style={{ padding: "10px 12px", textAlign: "right", fontSize: 13, color: "#3ecf8e", fontWeight: 600 }}>
                              {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} EUR
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>'''

new_perso_table = '''<table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead>
                        <tr style={{ background: "#0f1117" }}>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Categorie</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Designation</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Dimensions</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Unite</th>
                          <th style={{ padding: "10px 12px", textAlign: "right", color: "#545870", fontSize: 12, fontWeight: 600 }}>Prix HT</th>
                          <th style={{ padding: "10px 12px", textAlign: "right", color: "#545870", fontSize: 12, fontWeight: 600 }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {catalogueEntreprise.map((m, i) => (
                          <tr key={m.id} style={{ borderTop: "1px solid #1e2231", background: i % 2 === 0 ? "transparent" : "#0f111740" }}>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#60a5fa" }}>{m.categorie}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13 }}>{m.designation}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.dimensions || "-"}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.unite}</td>
                            <td style={{ padding: "10px 12px", textAlign: "right", fontSize: 13, color: "#3ecf8e", fontWeight: 600 }}>
                              {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} EUR
                            </td>
                            <td style={{ padding: "8px 12px", textAlign: "right" }}>
                              <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                                <button
                                  onClick={() => openEditCatalogModal(m)}
                                  title="Modifier"
                                  style={{ background: "transparent", border: "1px solid #2a2e40", color: "#60a5fa", borderRadius: 6, padding: "4px 10px", cursor: "pointer", fontSize: 12, fontWeight: 600, transition: "all 0.15s" }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "#60a5fa18"; e.currentTarget.style.borderColor = "#60a5fa"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "#2a2e40"; }}>
                                  Modifier
                                </button>
                                <button
                                  onClick={() => handleDeleteMaterial(m)}
                                  title="Supprimer"
                                  style={{ background: "transparent", border: "1px solid #2a2e40", color: "#ef4444", borderRadius: 6, padding: "4px 10px", cursor: "pointer", fontSize: 12, fontWeight: 600, transition: "all 0.15s" }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "#ef444418"; e.currentTarget.style.borderColor = "#ef4444"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "#2a2e40"; }}>
                                  Supprimer
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>'''

if "openEditCatalogModal(m)" in content:
    print("[INFO] Boutons Modifier/Supprimer deja presents dans la liste, skip modification 5")
else:
    if old_perso_table not in content:
        print("ERREUR : impossible de trouver le tableau Mon catalogue.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_perso_table, new_perso_table, 1)
    print("[OK] Boutons Modifier/Supprimer ajoutes dans le tableau")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("ETAPE 2.A.3.c APPLIQUEE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Boutons Modifier (bleu) et Supprimer (rouge) sur chaque ligne")
print("  2. Modale adapte son titre/bouton selon le mode (Ajouter / Modifier)")
print("  3. UPDATE Supabase pour modifier")
print("  4. DELETE Supabase avec confirmation pour supprimer")
print()
print("PROCHAINE ETAPE :")
print("  git add devia.jsx")
print("  git commit -m 'Modification et suppression catalogue entreprise'")
print("  git push")
print()
print("TESTS :")
print("  1. Aller dans Catalogue > Mon catalogue")
print("  2. Cliquer Modifier sur un materiau -> changer le prix -> Enregistrer")
print("  3. Verifier que le prix est mis a jour")
print("  4. Cliquer Supprimer -> confirmer -> le materiau disparait")
print("  5. Rafraichir la page : les modifs sont persistantes")
print()
print(f"BACKUP : {backup_name}")
