#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Modif 3 : Ajout intelligent au catalogue
- Detection auto du type via mots-cles (bois/visserie/outillage/isolant/EPI/...)
- Champ 'dimensions' MASQUE si type ne le necessite pas (outillage, EPI, etc.)
- Badge 'Type detecte' au-dessus du formulaire (cliquable pour override manuel)
- Suggestions intelligentes pour le champ 'Unite' selon le type
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_smart_catalog"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter fonction detectMateriauType + objet typeConfig
# On l'ajoute juste avant le composant DeviaMain
# ================================================================

old_marker = 'function DeviaMain() {'

new_with_detection = '''// ====== Detection intelligente du type de materiau ======
// Mappe les mots-cles aux types de materiaux pour adapter le formulaire d'ajout
const MATERIAL_TYPES = {
  bois_structure: {
    label: "Bois structure",
    icon: "tree",
    color: "#a78bfa",
    keywords: ["panne", "chevron", "sabliere", "poteau", "ferme", "arbaletrier", "lambourde", "solive", "poutre", "muraille", "entrait", "blochet", "jambette", "contrefiche", "echantignole"],
    showDimensions: true,
    suggestedUnits: ["ml", "m3", "u"],
    defaultUnit: "ml",
    dimensionsRequired: true,
    placeholder: "Ex: 75x175 mm"
  },
  bois_ossature: {
    label: "Bois ossature",
    icon: "frame",
    color: "#a78bfa",
    keywords: ["ossature", "montant", "traverse", "osb", "lamelle-colle", "lamellecolle", "kvh", "bois lamelle", "agglomere", "contreplaque"],
    showDimensions: true,
    suggestedUnits: ["ml", "m2", "u"],
    defaultUnit: "ml",
    dimensionsRequired: true,
    placeholder: "Ex: 45x95 mm"
  },
  couverture: {
    label: "Couverture",
    icon: "roof",
    color: "#60a5fa",
    keywords: ["tuile", "ardoise", "volige", "liteau", "fait", "ecran sous-toiture", "ecran sous toiture", "membrane", "bac acier", "shingle", "zinc", "cuivre", "noue", "rive", "gouttiere", "descente"],
    showDimensions: false,
    suggestedUnits: ["m2", "u", "ml"],
    defaultUnit: "m2",
    dimensionsRequired: false,
    placeholder: ""
  },
  visserie: {
    label: "Visserie / fixations",
    icon: "screw",
    color: "#fcd34d",
    keywords: ["vis", "clou", "boulon", "ecrou", "rondelle", "equerre", "sabot", "etrier", "tirefond", "agrafe", "boucher", "cheville", "scellement", "broche", "pointe"],
    showDimensions: true,
    suggestedUnits: ["u", "kg", "forfait"],
    defaultUnit: "u",
    dimensionsRequired: false,
    placeholder: "Ex: 5x80 mm"
  },
  outillage: {
    label: "Outillage",
    icon: "tool",
    color: "#fb923c",
    keywords: ["marteau", "scie", "perceuse", "visseuse", "niveau", "metre", "decametre", "fil a plomb", "rabot", "ciseau", "burin", "pied de biche", "echelle", "echafaudage", "tronconneuse", "ponceuse", "meuleuse", "cordeau", "trace au bleu", "fil a craie", "outils"],
    showDimensions: false,
    suggestedUnits: ["u", "forfait"],
    defaultUnit: "u",
    dimensionsRequired: false,
    placeholder: ""
  },
  isolation: {
    label: "Isolation",
    icon: "thermal",
    color: "#3ecf8e",
    keywords: ["laine", "isolant", "ouate", "polystyrene", "panneau isolant", "chanvre", "lin", "fibre de bois", "fibralith", "knauf", "rockwool", "isover", "soufflage"],
    showDimensions: true,
    suggestedUnits: ["m2", "m3", "u"],
    defaultUnit: "m2",
    dimensionsRequired: false,
    placeholder: "Ex: 200mm ep, R=5"
  },
  quincaillerie: {
    label: "Quincaillerie",
    icon: "lock",
    color: "#94a3b8",
    keywords: ["charniere", "gond", "poignee", "serrure", "verrou", "cremone", "fermeture", "loquet", "espagnolette"],
    showDimensions: false,
    suggestedUnits: ["u", "forfait"],
    defaultUnit: "u",
    dimensionsRequired: false,
    placeholder: ""
  },
  epi: {
    label: "EPI / Securite",
    icon: "shield",
    color: "#ef4444",
    keywords: ["casque", "harnais", "gants", "chaussures securite", "lunettes", "masque", "protection", "antichute", "longe", "baudrier", "epi"],
    showDimensions: false,
    suggestedUnits: ["u", "forfait"],
    defaultUnit: "u",
    dimensionsRequired: false,
    placeholder: ""
  },
  main_oeuvre: {
    label: "Main d'oeuvre",
    icon: "hand",
    color: "#f0c040",
    keywords: ["main d'oeuvre", "main doeuvre", "charpentier", "manoeuvre", "pose", "depose", "installation", "demontage", "ouvrier", "chef equipe", "compagnon"],
    showDimensions: false,
    suggestedUnits: ["h", "forfait", "m2"],
    defaultUnit: "h",
    dimensionsRequired: false,
    placeholder: ""
  },
  autre: {
    label: "Autre",
    icon: "box",
    color: "#7a7d92",
    keywords: [],
    showDimensions: true,
    suggestedUnits: ["u", "ml", "m2", "m3", "kg", "h", "forfait"],
    defaultUnit: "u",
    dimensionsRequired: false,
    placeholder: ""
  }
};

function detectMateriauType(designation) {
  if (!designation || designation.trim().length < 2) return "autre";
  const text = designation.toLowerCase().trim();
  // Cherche le type avec le plus de mots-cles matchant (le plus specifique gagne)
  let bestMatch = { type: "autre", score: 0 };
  for (const [type, config] of Object.entries(MATERIAL_TYPES)) {
    if (type === "autre") continue;
    let score = 0;
    for (const keyword of config.keywords) {
      if (text.includes(keyword)) {
        // Mot complet > mot dans une chaine
        score += keyword.length > 4 ? 2 : 1;
      }
    }
    if (score > bestMatch.score) {
      bestMatch = { type, score };
    }
  }
  return bestMatch.type;
}
// ====================================================

function DeviaMain() {'''

if "const MATERIAL_TYPES =" in content:
    print("[INFO] Detection deja en place")
elif old_marker in content:
    content = content.replace(old_marker, new_with_detection, 1)
    print("[OK] MATERIAL_TYPES + detectMateriauType ajoutes")
    modifs += 1
else:
    print("[ERREUR] function DeviaMain() non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Ajouter state pour le type detecte + override manuel
# ================================================================

old_state = '''const [catalogForm, setCatalogForm] = useState({
    categorie: "Charpente",
    categorieAutre: "",
    designation: "",
    dimensions: "",
    unite: "ml",
    prix_ht: "",
    notes: "",
  });'''

new_state = '''const [catalogForm, setCatalogForm] = useState({
    categorie: "Charpente",
    categorieAutre: "",
    designation: "",
    dimensions: "",
    unite: "ml",
    prix_ht: "",
    notes: "",
  });
  const [detectedType, setDetectedType] = useState("autre");
  const [typeOverride, setTypeOverride] = useState(null); // si user choisit manuellement
  const [showTypeMenu, setShowTypeMenu] = useState(false);'''

if "const [detectedType" in content:
    print("[INFO] State detectedType deja present")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] State detectedType + typeOverride ajoutes")
    modifs += 1
else:
    print("[ERREUR] State catalogForm non trouve")
    sys.exit(1)

# ================================================================
# MOD 3 : Remplacer le champ 'Designation' pour declencher la detection
# ================================================================

old_designation = '''          {/* Designation */}
          <div>
            <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Designation <span style={{ color: "#f0c040" }}>*</span></label>
            <input type="text" value={catalogForm.designation}
              onChange={(e) => setCatalogForm({ ...catalogForm, designation: e.target.value })}
              placeholder="Ex: Chevron sapin C24, Tuile mecanique, Vis 6x180..."
              style={inputStyle} />
          </div>'''

new_designation = '''          {/* Designation - avec detection intelligente */}
          <div>
            <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Designation <span style={{ color: "#f0c040" }}>*</span></label>
            <input type="text" value={catalogForm.designation}
              onChange={(e) => {
                const newDesignation = e.target.value;
                const newDetected = detectMateriauType(newDesignation);
                setCatalogForm({ ...catalogForm, designation: newDesignation });
                setDetectedType(newDetected);
                // Reset l'override si l'user retape (sinon il est bloque sur l'ancien override)
                if (typeOverride && newDetected !== typeOverride) {
                  // Pas de reset auto, on garde l'override jusqu'a ce que l'user le change
                }
              }}
              placeholder="Ex: Chevron sapin C24, Tuile mecanique, Vis 6x180..."
              style={inputStyle} />
            {/* Badge type detecte */}
            {catalogForm.designation.trim().length >= 2 && (() => {
              const activeType = typeOverride || detectedType;
              const config = MATERIAL_TYPES[activeType];
              return (
                <div style={{ marginTop: 8, position: "relative", display: "inline-block" }}>
                  <button onClick={(e) => { e.preventDefault(); setShowTypeMenu(!showTypeMenu); }}
                    type="button"
                    style={{
                      background: "rgba(" + (activeType === "main_oeuvre" ? "240, 192, 64" : activeType === "outillage" ? "251, 146, 60" : activeType === "couverture" ? "96, 165, 250" : activeType === "visserie" ? "252, 211, 77" : activeType === "isolation" ? "62, 207, 142" : activeType === "epi" ? "239, 68, 68" : activeType === "bois_structure" || activeType === "bois_ossature" ? "167, 139, 250" : "122, 125, 146") + ", 0.12)",
                      border: "1px solid " + config.color + "40",
                      color: config.color,
                      borderRadius: 999,
                      padding: "4px 10px",
                      fontSize: 11,
                      fontWeight: 600,
                      cursor: "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 6,
                      letterSpacing: "0.02em"
                    }}>
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Type detecte : {config.label}
                    <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.7, marginLeft: 2 }}>
                      <polyline points="6 9 12 15 18 9"/>
                    </svg>
                  </button>
                  {showTypeMenu && (
                    <div style={{
                      position: "absolute",
                      top: "calc(100% + 6px)",
                      left: 0,
                      background: "rgba(22, 25, 35, 0.98)",
                      backdropFilter: "blur(20px) saturate(140%)",
                      WebkitBackdropFilter: "blur(20px) saturate(140%)",
                      border: "1px solid rgba(255, 255, 255, 0.08)",
                      borderRadius: 10,
                      padding: 4,
                      minWidth: 200,
                      boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
                      zIndex: 100
                    }}>
                      <div style={{ padding: "6px 12px 4px 12px", color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Changer le type</div>
                      {Object.entries(MATERIAL_TYPES).map(([t, c]) => (
                        <button key={t} type="button"
                          onClick={() => { setTypeOverride(t); setShowTypeMenu(false); }}
                          style={{
                            width: "100%", background: "transparent", border: "none",
                            color: activeType === t ? c.color : "#e8eaf2",
                            textAlign: "left", padding: "7px 12px",
                            fontSize: 12, cursor: "pointer", borderRadius: 7,
                            display: "flex", alignItems: "center", gap: 7, transition: "background 0.12s",
                            fontWeight: activeType === t ? 600 : 500
                          }}
                          onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; }}
                          onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                          <span style={{ width: 6, height: 6, borderRadius: "50%", background: c.color, flexShrink: 0 }}></span>
                          {c.label}
                          {activeType === t && (
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: "auto" }}>
                              <polyline points="20 6 9 17 4 12"/>
                            </svg>
                          )}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })()}
          </div>'''

if "Detection deja en place" in content or "Type detecte :" in content:
    print("[INFO] Champ Designation deja modifie")
elif old_designation in content:
    content = content.replace(old_designation, new_designation, 1)
    print("[OK] Champ Designation avec detection intelligente")
    modifs += 1
else:
    print("[ERREUR] Champ Designation non trouve")
    sys.exit(1)

# ================================================================
# MOD 4 : Rendre le bloc Dimensions/Unite conditionnel
# ================================================================

old_dimensions_block = '''          {/* Dimensions et Unite */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Dimensions</label>
              <input type="text" value={catalogForm.dimensions}
                onChange={(e) => setCatalogForm({ ...catalogForm, dimensions: e.target.value })}
                placeholder="Ex: 75x175 mm"
                style={inputStyle} />
            </div>
            <div>
              <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Unite <span style={{ color: "#f0c040" }}>*</span></label>
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
          </div>'''

new_dimensions_block = '''          {/* Dimensions et Unite - conditionnels selon le type */}
          {(() => {
            const activeType = typeOverride || detectedType;
            const config = MATERIAL_TYPES[activeType] || MATERIAL_TYPES.autre;
            return (
              <div style={{ display: "grid", gridTemplateColumns: config.showDimensions ? "1fr 1fr" : "1fr", gap: 12 }}>
                {config.showDimensions && (
                  <div>
                    <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>
                      Dimensions
                      {config.dimensionsRequired && <span style={{ color: "#7a7d92", fontWeight: 400, textTransform: "none", marginLeft: 6 }}>(recommande)</span>}
                    </label>
                    <input type="text" value={catalogForm.dimensions}
                      onChange={(e) => setCatalogForm({ ...catalogForm, dimensions: e.target.value })}
                      placeholder={config.placeholder || "Ex: 75x175 mm"}
                      style={inputStyle} />
                  </div>
                )}
                <div>
                  <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Unite <span style={{ color: "#f0c040" }}>*</span></label>
                  <select value={catalogForm.unite}
                    onChange={(e) => setCatalogForm({ ...catalogForm, unite: e.target.value })}
                    style={{ ...inputStyle, cursor: "pointer" }}>
                    {/* On affiche d'abord les unites suggerees, puis les autres en gris */}
                    {config.suggestedUnits.map(u => {
                      const labels = { ml: "ml (metre lineaire)", m2: "m2 (metre carre)", m3: "m3 (metre cube)", u: "u (unite)", kg: "kg (kilo)", h: "h (heure)", forfait: "forfait" };
                      return <option key={u} value={u}>{labels[u] || u}</option>;
                    })}
                    {/* Autres unites (non suggerees) */}
                    {["ml", "m2", "m3", "u", "kg", "h", "forfait"].filter(u => !config.suggestedUnits.includes(u)).map(u => {
                      const labels = { ml: "ml (metre lineaire)", m2: "m2 (metre carre)", m3: "m3 (metre cube)", u: "u (unite)", kg: "kg (kilo)", h: "h (heure)", forfait: "forfait" };
                      return <option key={u} value={u}>{labels[u]}</option>;
                    })}
                  </select>
                </div>
              </div>
            );
          })()}'''

if "Dimensions et Unite - conditionnels" in content:
    print("[INFO] Bloc dimensions deja conditionnel")
elif old_dimensions_block in content:
    content = content.replace(old_dimensions_block, new_dimensions_block, 1)
    print("[OK] Dimensions masquees pour outillage/EPI/quincaillerie/etc.")
    modifs += 1
else:
    print("[ERREUR] Bloc Dimensions/Unite non trouve")
    sys.exit(1)

# ================================================================
# MOD 5 : useEffect pour suggerer auto l'unite quand le type change
# (Reset l'unite si elle n'est pas dans suggestedUnits du type detecte)
# ================================================================

old_useeffect_marker = '''  // Persistance du theme
  useEffect(() => {
    try {
      localStorage.setItem("devia_theme", themeMode);
    } catch (e) {}
  }, [themeMode]);'''

new_useeffect = '''  // Persistance du theme
  useEffect(() => {
    try {
      localStorage.setItem("devia_theme", themeMode);
    } catch (e) {}
  }, [themeMode]);

  // Auto-suggestion de l'unite selon le type detecte
  useEffect(() => {
    const activeType = typeOverride || detectedType;
    const config = MATERIAL_TYPES[activeType];
    if (!config) return;
    // Si l'unite actuelle n'est pas dans les suggerees du nouveau type, on suggere la defaultUnit
    // SAUF si l'user a deja sauvegarde un edit (editingCatalogId existe)
    if (!editingCatalogId && !config.suggestedUnits.includes(catalogForm.unite)) {
      setCatalogForm(prev => ({ ...prev, unite: config.defaultUnit }));
    }
  }, [detectedType, typeOverride]);'''

if "Auto-suggestion de l'unite" in content:
    print("[INFO] useEffect auto-suggestion deja present")
elif old_useeffect_marker in content:
    content = content.replace(old_useeffect_marker, new_useeffect, 1)
    print("[OK] Auto-suggestion de l'unite selon le type detecte")
    modifs += 1
else:
    print("[WARN] useEffect themeMode non trouve")

# ================================================================
# MOD 6 : Reset detectedType + typeOverride quand on ferme/ouvre la modale
# On modifie resetCatalogForm
# ================================================================

# On cherche la fonction resetCatalogForm
import re
match = re.search(r'(const|function)\s+resetCatalogForm\s*[=]?\s*[(]?[)]?\s*[=]?\s*[>]?\s*\{[^}]+\}', content)
if match:
    print("[INFO] resetCatalogForm trouve - on ajoute reset des types")
    old_reset = match.group(0)
    # Verifier qu'on n'a pas deja modifie
    if "setDetectedType" not in old_reset:
        # Ajouter setDetectedType("autre") et setTypeOverride(null) avant la fermeture }
        new_reset = old_reset.rstrip('}').rstrip() + '\n    setDetectedType("autre");\n    setTypeOverride(null);\n    setShowTypeMenu(false);\n  }'
        content = content.replace(old_reset, new_reset, 1)
        print("[OK] Reset detectedType/typeOverride/showTypeMenu ajoute dans resetCatalogForm")
        modifs += 1

# ================================================================
# MOD 7 : Pre-remplir detectedType en mode edition
# Quand on ouvre la modale en mode 'edit', il faut detecter le type depuis la designation existante
# ================================================================

# On cherche le moment ou on ouvre la modale en mode edit
# C'est lie a setEditingCatalogId(...)
# Approche : on ajoute un useEffect qui re-detecte le type quand catalogForm.designation change
# DEJA fait via le onChange du champ designation, mais pas au moment du open en edit

# En fait, quand on ouvre en edition, on setCatalogForm({...materiau}) ce qui ne declenche pas le onChange
# Donc on ajoute un useEffect qui ecoute catalogForm.designation
old_useeffect_marker2 = '''  // Auto-suggestion de l'unite selon le type detecte
  useEffect(() => {'''

new_useeffect_full = '''  // Re-detecte le type quand designation change (utile en mode edition)
  useEffect(() => {
    if (catalogForm.designation && catalogForm.designation.trim().length >= 2) {
      setDetectedType(detectMateriauType(catalogForm.designation));
    }
  }, [catalogForm.designation]);

  // Auto-suggestion de l'unite selon le type detecte
  useEffect(() => {'''

if "Re-detecte le type quand designation change" in content:
    print("[INFO] Re-detection sur designation deja en place")
elif old_useeffect_marker2 in content:
    content = content.replace(old_useeffect_marker2, new_useeffect_full, 1)
    print("[OK] Re-detection automatique en mode edition")
    modifs += 1

# ================================================================
# MOD 8 : Fermer le menu type au clic externe
# ================================================================

old_close_menus_marker = '''  // Ferme le menu '...' projet au clic externe
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

new_close_menus = '''  // Ferme le menu '...' projet au clic externe
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
  }, [openProjectMenuId]);

  // Ferme le menu de type detecte au clic externe
  useEffect(() => {
    if (!showTypeMenu) return;
    const handleClickOutside = () => setShowTypeMenu(false);
    const timer = setTimeout(() => {
      document.addEventListener("click", handleClickOutside);
    }, 50);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("click", handleClickOutside);
    };
  }, [showTypeMenu]);'''

if "Ferme le menu de type detecte au clic externe" in content:
    print("[INFO] Fermeture menu type deja en place")
elif old_close_menus_marker in content:
    content = content.replace(old_close_menus_marker, new_close_menus, 1)
    print("[OK] Fermeture menu type au clic externe")
    modifs += 1

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Objet MATERIAL_TYPES avec 10 types et leurs mots-cles")
print("  2. Fonction detectMateriauType() qui scanne le libelle")
print("  3. State detectedType + typeOverride + showTypeMenu")
print("  4. Detection live au moment ou l'user tape la designation")
print("  5. Badge 'Type detecte : X' colore + cliquable pour override")
print("  6. Champ Dimensions MASQUE pour : outillage, EPI, quincaillerie, couverture, main d'oeuvre")
print("  7. Unites suggerees en priorite selon le type")
print("  8. Auto-suggestion de l'unite par defaut quand type change")
print("  9. Re-detection en mode edition")
print(" 10. Fermeture du menu au clic externe")
print()
print("COMMENT TESTER :")
print("  1. npm run build")
print("  2. Va sur Catalogue -> Mes prix -> Ajouter un materiau")
print("  3. Tape 'marteau' -> Badge orange 'Type detecte : Outillage'")
print("     -> Champ Dimensions DISPARAIT")
print("     -> Unite suggere 'u (unite)'")
print("  4. Tape 'panne 200x80' -> Badge violet 'Type detecte : Bois structure'")
print("     -> Champ Dimensions REVIENT")
print("     -> Unite suggere 'ml'")
print("  5. Tape 'tuile' -> Badge bleu 'Type detecte : Couverture'")
print("     -> Unite suggere 'm2'")
print("  6. Click sur le badge type -> menu pour override manuel")
print()
print(f"BACKUP : {backup_name}")
