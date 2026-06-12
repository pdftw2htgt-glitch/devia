#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Suppression du champ Categorie + mapping automatique
- Le champ Categorie est SUPPRIME du formulaire visible
- La categorie est CALCULEE automatiquement depuis le type detecte au moment du save
- Compatible BDD existante (categorie toujours sauvegardee)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_remove_categorie"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter la fonction de mapping type -> categorie
# On l'ajoute juste apres detectMateriauType
# ================================================================

old_marker = '''function detectMateriauType(designation) {
  if (!designation || designation.trim().length < 2) return "autre";
  const text = designation.toLowerCase().trim();
  let bestMatch = { type: "autre", score: 0 };
  for (const [type, config] of Object.entries(MATERIAL_TYPES)) {
    if (type === "autre") continue;
    let score = 0;
    for (const keyword of config.keywords) {
      if (text.includes(keyword)) {
        score += keyword.length > 4 ? 2 : 1;
      }
    }
    if (score > bestMatch.score) {
      bestMatch = { type, score };
    }
  }
  return bestMatch.type;
}'''

new_marker = '''function detectMateriauType(designation) {
  if (!designation || designation.trim().length < 2) return "autre";
  const text = designation.toLowerCase().trim();
  let bestMatch = { type: "autre", score: 0 };
  for (const [type, config] of Object.entries(MATERIAL_TYPES)) {
    if (type === "autre") continue;
    let score = 0;
    for (const keyword of config.keywords) {
      if (text.includes(keyword)) {
        score += keyword.length > 4 ? 2 : 1;
      }
    }
    if (score > bestMatch.score) {
      bestMatch = { type, score };
    }
  }
  return bestMatch.type;
}

// Mapping : type detecte -> categorie sauvegardee en BDD
function typeToCategorie(type) {
  const mapping = {
    bois_structure: "Charpente",
    bois_ossature: "Charpente",
    couverture: "Couverture",
    isolation: "Isolation",
    visserie: "Quincaillerie",
    quincaillerie: "Quincaillerie",
    main_oeuvre: "Main d'oeuvre",
    outillage: "Outillage",
    epi: "Outillage",
    autre: "Autre"
  };
  return mapping[type] || "Autre";
}

// Mapping inverse : categorie BDD -> type (pour le mode edition)
function categorieToType(categorie) {
  const reverseMap = {
    "Charpente": "bois_structure",
    "Bardage": "bois_ossature",
    "Couverture": "couverture",
    "Isolation": "isolation",
    "Quincaillerie": "quincaillerie",
    "Main d'oeuvre": "main_oeuvre",
    "Outillage": "outillage"
  };
  return reverseMap[categorie] || null;
}'''

if "function typeToCategorie" in content:
    print("[INFO] Mapping deja en place")
elif old_marker in content:
    content = content.replace(old_marker, new_marker, 1)
    print("[OK] Fonctions typeToCategorie + categorieToType ajoutees")
    modifs += 1
else:
    print("[ERREUR] detectMateriauType non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Au moment du SAVE, calculer la categorie depuis le type
# Trouver la ligne ou on construit l'objet pour insertion BDD
# ================================================================

old_save_logic = '''    const categorieFinal = catalogForm.categorie === "Autre"
      ? catalogForm.categorieAutre.trim()
      : catalogForm.categorie;'''

new_save_logic = '''    // Categorie calculee automatiquement depuis le type detecte (ou override)
    const activeType = typeOverride || detectedType;
    const categorieFinal = typeToCategorie(activeType);'''

if "typeToCategorie(activeType)" in content:
    print("[INFO] Logique save deja modifiee")
elif old_save_logic in content:
    content = content.replace(old_save_logic, new_save_logic, 1)
    print("[OK] Categorie calculee auto depuis type detecte")
    modifs += 1
else:
    print("[ERREUR] Logique save non trouvee")
    sys.exit(1)

# ================================================================
# MOD 3 : SUPPRIMER le champ Categorie de la modale (le bloc complet)
# ================================================================

# On cible le bloc complet de la categorie dans la modale
old_categorie_block = '''        <div style={{ display: "grid", gap: 14 }}>
          {/* Categorie */}
          <div>
            <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Categorie <span style={{ color: "#f0c040" }}>*</span></label>
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

          {/* Designation - avec detection intelligente */}'''

new_categorie_block = '''        <div style={{ display: "grid", gap: 14 }}>
          {/* Designation - avec detection intelligente */}'''

if old_categorie_block in content:
    content = content.replace(old_categorie_block, new_categorie_block, 1)
    print("[OK] Champ Categorie SUPPRIME du formulaire")
    modifs += 1
else:
    print("[ERREUR] Bloc Categorie non trouve")
    sys.exit(1)

# ================================================================
# MOD 4 : En mode EDITION, pre-remplir le typeOverride depuis la categorie BDD
# pour que le badge corresponde au materiau qu'on edite
# ================================================================

old_open_edit = '''  const openEditCatalogModal = (material) => {
    const isStandardCat = ["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie", "Main d'oeuvre"].includes(material.categorie);
    setCatalogForm({'''

new_open_edit = '''  const openEditCatalogModal = (material) => {
    const isStandardCat = ["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie", "Main d'oeuvre", "Outillage"].includes(material.categorie);
    // Pre-remplir le typeOverride depuis la categorie BDD
    const typeFromCat = categorieToType(material.categorie);
    if (typeFromCat) {
      setTypeOverride(typeFromCat);
    }
    setCatalogForm({'''

if "Pre-remplir le typeOverride depuis la categorie BDD" in content:
    print("[INFO] Mode edition deja adapte")
elif old_open_edit in content:
    content = content.replace(old_open_edit, new_open_edit, 1)
    print("[OK] Mode edition pre-remplit le type depuis la categorie BDD")
    modifs += 1
else:
    print("[WARN] openEditCatalogModal non trouve - mode edition pas adapte")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Fonctions typeToCategorie() et categorieToType() ajoutees")
print("  2. Au SAVE : categorie calculee auto depuis le type detecte/override")
print("  3. Champ Categorie SUPPRIME du formulaire (visible)")
print("  4. Mode edition : type pre-rempli depuis la categorie BDD")
print()
print("MAPPING APPLIQUE :")
print("  bois_structure / bois_ossature -> Charpente")
print("  couverture                      -> Couverture")
print("  isolation                       -> Isolation")
print("  visserie / quincaillerie        -> Quincaillerie")
print("  main_oeuvre                     -> Main d'oeuvre")
print("  outillage / epi                 -> Outillage")
print("  autre                           -> Autre")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
