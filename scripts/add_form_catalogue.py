#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Etape 2.A.3.b : Ajout dans Mon catalogue
Ajoute :
1. Bouton '+ Ajouter un materiau' en haut de l'onglet Mon catalogue
2. Modale formulaire avec champs (categorie/designation/dimensions/unite/prix/notes)
3. INSERT en base Supabase
4. Refresh de la liste apres ajout

A lancer depuis ~/Desktop/devia :
    python3 add_form_catalogue.py
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

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_form_catalogue"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MODIFICATION 1 : Ajouter les states pour le formulaire
# ================================================================

old_loadcat_state = "const [loadingCatalogues, setLoadingCatalogues] = useState(false);"

if "showAddCatalogModal" in content:
    print("[INFO] States formulaire deja presents, skip modification 1")
else:
    new_form_states = '''const [loadingCatalogues, setLoadingCatalogues] = useState(false);
  const [showAddCatalogModal, setShowAddCatalogModal] = useState(false);
  const [catalogForm, setCatalogForm] = useState({
    categorie: "Charpente",
    categorieAutre: "",
    designation: "",
    dimensions: "",
    unite: "ml",
    prix_ht: "",
    notes: "",
  });
  const [catalogFormError, setCatalogFormError] = useState(null);
  const [savingCatalog, setSavingCatalog] = useState(false);'''

    if old_loadcat_state not in content:
        print("ERREUR : impossible de trouver les states catalogues.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_loadcat_state, new_form_states, 1)
    print("[OK] States formulaire ajoutes")

# ================================================================
# MODIFICATION 2 : Ajouter les fonctions handleAddMaterial et resetForm
# On les ajoute juste avant le const handleSubmit
# ================================================================

handle_submit_marker = "const handleSubmit = () => {"

if "handleAddMaterial" in content:
    print("[INFO] handleAddMaterial deja present, skip modification 2")
else:
    new_handlers = '''const resetCatalogForm = () => {
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
  };

  const handleAddMaterial = async () => {
    setCatalogFormError(null);

    // Validations
    const categorieFinal = catalogForm.categorie === "Autre"
      ? catalogForm.categorieAutre.trim()
      : catalogForm.categorie;
    if (!categorieFinal) {
      setCatalogFormError("La categorie est obligatoire.");
      return;
    }
    if (!catalogForm.designation.trim()) {
      setCatalogFormError("La designation est obligatoire.");
      return;
    }
    const prixHt = parseFloat(catalogForm.prix_ht);
    if (isNaN(prixHt) || prixHt < 0) {
      setCatalogFormError("Le prix HT doit etre un nombre positif.");
      return;
    }
    if (!catalogForm.unite) {
      setCatalogFormError("L'unite est obligatoire.");
      return;
    }

    setSavingCatalog(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        setCatalogFormError("Vous devez etre connecte.");
        setSavingCatalog(false);
        return;
      }
      const newRow = {
        user_id: user.id,
        categorie: categorieFinal,
        designation: catalogForm.designation.trim(),
        dimensions: catalogForm.dimensions.trim() || null,
        unite: catalogForm.unite,
        prix_ht: prixHt,
        notes: catalogForm.notes.trim() || null,
      };
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
      // Ajout local
      setCatalogueEntreprise(prev => [inserted, ...prev]);
      setShowAddCatalogModal(false);
      resetCatalogForm();
    } catch (e) {
      console.error("Erreur handleAddMaterial:", e);
      setCatalogFormError("Erreur inattendue : " + e.message);
    } finally {
      setSavingCatalog(false);
    }
  };

  ''' + handle_submit_marker

    if handle_submit_marker not in content:
        print("ERREUR : impossible de trouver handleSubmit.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(handle_submit_marker, new_handlers, 1)
    print("[OK] Fonctions handleAddMaterial et resetCatalogForm ajoutees")

# ================================================================
# MODIFICATION 3 : Ajouter le bouton + en haut de Mon catalogue
# ================================================================

old_perso_intro = '''<div style={{ ...cardStyle, padding: 16, marginBottom: 16, background: "#0f1117", borderColor: "#3ecf8e44" }}>
                  <div style={{ display: "flex", alignItems: "start", gap: 12 }}>
                    <div style={{ fontSize: 20 }}>&#x1F4A1;</div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>Mon catalogue d'entreprise</div>
                      <div style={{ color: "#545870", fontSize: 13, lineHeight: 1.5 }}>
                        Vos prix personnels, prioritaires sur le catalogue marche.
                        Ajout et modification disponibles prochainement.
                      </div>
                    </div>
                  </div>
                </div>'''

new_perso_intro = '''<div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, gap: 12 }}>
                  <div style={{ ...cardStyle, padding: 16, background: "#0f1117", borderColor: "#3ecf8e44", flex: 1, marginBottom: 0 }}>
                    <div style={{ display: "flex", alignItems: "start", gap: 12 }}>
                      <div style={{ fontSize: 20 }}>&#x1F4A1;</div>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>Mon catalogue d'entreprise</div>
                        <div style={{ color: "#545870", fontSize: 13, lineHeight: 1.5 }}>
                          Vos prix personnels, prioritaires sur le catalogue marche.
                        </div>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => { resetCatalogForm(); setShowAddCatalogModal(true); }}
                    style={{ background: "#f0c040", color: "#08090c", border: "none", borderRadius: 8, padding: "12px 20px", cursor: "pointer", fontSize: 14, fontWeight: 700, whiteSpace: "nowrap" }}>
                    + Ajouter un materiau
                  </button>
                </div>'''

if "+ Ajouter un materiau" in content:
    print("[INFO] Bouton ajout deja present, skip modification 3")
else:
    if old_perso_intro not in content:
        print("ERREUR : impossible de trouver le bloc d'intro Mon catalogue.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_perso_intro, new_perso_intro, 1)
    print("[OK] Bouton + Ajouter materiau ajoute")

# ================================================================
# MODIFICATION 4 : Ajouter la modale formulaire
# On l'insere juste apres </main> avant </div> final
# ================================================================

# On cherche un repere unique vers la fin du composant DeviaMain
# La fermeture du <main> + le footer eventuel
modale_marker = "</main>"

if "showAddCatalogModal &&" in content:
    print("[INFO] Modale ajout deja presente, skip modification 4")
else:
    # On trouve la PREMIERE occurrence de </main> (celle de DeviaMain)
    main_close_idx = content.find(modale_marker)
    if main_close_idx == -1:
        print("ERREUR : impossible de trouver </main>.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)

    modale_block = '''</main>

  {showAddCatalogModal && (
    <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: 16 }}
      onClick={(e) => { if (e.target === e.currentTarget) { setShowAddCatalogModal(false); resetCatalogForm(); } }}>
      <div style={{ background: "#13161f", border: "1px solid #1e2231", borderRadius: 12, padding: 24, maxWidth: 560, width: "100%", maxHeight: "90vh", overflowY: "auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <h2 style={{ fontSize: 18, fontWeight: 700 }}>Ajouter un materiau</h2>
          <button onClick={() => { setShowAddCatalogModal(false); resetCatalogForm(); }}
            style={{ background: "transparent", border: "none", color: "#545870", cursor: "pointer", fontSize: 22, padding: 4 }}>x</button>
        </div>

        <div style={{ display: "grid", gap: 14 }}>
          {/* Categorie */}
          <div>
            <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Categorie *</label>
            <select value={catalogForm.categorie}
              onChange={(e) => setCatalogForm({ ...catalogForm, categorie: e.target.value })}
              style={{ ...inputStyle, cursor: "pointer" }}>
              <option value="Charpente">Charpente</option>
              <option value="Bardage">Bardage</option>
              <option value="Couverture">Couverture</option>
              <option value="Isolation">Isolation</option>
              <option value="Quincaillerie">Quincaillerie</option>
              <option value="Main d'oeuvre">Main d'oeuvre</option>
              <option value="Autre">Autre (champ libre)</option>
            </select>
            {catalogForm.categorie === "Autre" && (
              <input type="text" value={catalogForm.categorieAutre}
                onChange={(e) => setCatalogForm({ ...catalogForm, categorieAutre: e.target.value })}
                placeholder="Nom de votre categorie..."
                style={{ ...inputStyle, marginTop: 8 }} />
            )}
          </div>

          {/* Designation */}
          <div>
            <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Designation *</label>
            <input type="text" value={catalogForm.designation}
              onChange={(e) => setCatalogForm({ ...catalogForm, designation: e.target.value })}
              placeholder="Ex: Chevron sapin C24, Tuile mecanique, Vis 6x180..."
              style={inputStyle} />
          </div>

          {/* Dimensions et Unite */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Dimensions</label>
              <input type="text" value={catalogForm.dimensions}
                onChange={(e) => setCatalogForm({ ...catalogForm, dimensions: e.target.value })}
                placeholder="Ex: 75x175 mm"
                style={inputStyle} />
            </div>
            <div>
              <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Unite *</label>
              <select value={catalogForm.unite}
                onChange={(e) => setCatalogForm({ ...catalogForm, unite: e.target.value })}
                style={{ ...inputStyle, cursor: "pointer" }}>
                <option value="ml">ml (metre lineaire)</option>
                <option value="m2">m2 (metre carre)</option>
                <option value="m3">m3 (metre cube)</option>
                <option value="u">u (unite)</option>
                <option value="kg">kg (kilo)</option>
                <option value="h">h (heure)</option>
                <option value="forfait">forfait</option>
              </select>
            </div>
          </div>

          {/* Prix HT */}
          <div>
            <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Prix HT (EUR) *</label>
            <input type="number" step="0.01" min="0" value={catalogForm.prix_ht}
              onChange={(e) => setCatalogForm({ ...catalogForm, prix_ht: e.target.value })}
              placeholder="Ex: 12.50"
              style={inputStyle} />
          </div>

          {/* Notes */}
          <div>
            <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Notes (optionnel)</label>
            <input type="text" value={catalogForm.notes}
              onChange={(e) => setCatalogForm({ ...catalogForm, notes: e.target.value })}
              placeholder="Ex: Fournisseur X, classe C24..."
              style={inputStyle} />
          </div>

          {catalogFormError && (
            <div style={{ background: "#ef444418", border: "1px solid #ef4444", borderRadius: 8, padding: 12, color: "#ef4444", fontSize: 13 }}>
              {catalogFormError}
            </div>
          )}

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 8 }}>
            <button onClick={() => { setShowAddCatalogModal(false); resetCatalogForm(); }}
              disabled={savingCatalog}
              style={{ ...btnSecondary, opacity: savingCatalog ? 0.5 : 1 }}>
              Annuler
            </button>
            <button onClick={handleAddMaterial}
              disabled={savingCatalog}
              style={{ background: "#f0c040", color: "#08090c", border: "none", borderRadius: 8, padding: "10px 20px", cursor: savingCatalog ? "not-allowed" : "pointer", fontSize: 14, fontWeight: 700, opacity: savingCatalog ? 0.7 : 1 }}>
              {savingCatalog ? "Ajout en cours..." : "Ajouter"}
            </button>
          </div>
        </div>
      </div>
    </div>
  )}'''

    content = content.replace(modale_marker, modale_block, 1)
    print("[OK] Modale formulaire d'ajout ajoutee")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("ETAPE 2.A.3.b APPLIQUEE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Bouton '+ Ajouter un materiau' en haut de Mon catalogue")
print("  2. Modale formulaire avec validation")
print("  3. Sauvegarde Supabase + refresh liste local")
print("  4. Categorie : 6 standards + 'Autre' (champ libre)")
print()
print("PROCHAINE ETAPE :")
print("  git add devia.jsx")
print("  git commit -m 'Ajout formulaire dans Mon catalogue'")
print("  git push")
print()
print("TESTS :")
print("  1. Va dans Catalogue > Mon catalogue")
print("  2. Clique '+ Ajouter un materiau'")
print("  3. Remplis le formulaire")
print("  4. Clique 'Ajouter'")
print("  5. Le materiau apparait dans la liste")
print("  6. Rafraichis la page : il est toujours la (sauve en base)")
print()
print(f"BACKUP : {backup_name}")
