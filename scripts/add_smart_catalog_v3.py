#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Modif 3 v3 : Ajout intelligent au catalogue
FIX TEMPORAL DEAD ZONE :
- Les useEffect qui lisent catalogForm sont places APRES la declaration de catalogForm
- Au lieu d'apres themeMode (qui est ligne 501, avant catalogForm ligne 584)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_smart_v3"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : MATERIAL_TYPES + detectMateriauType (avant DeviaMain)
# ================================================================

old_marker = 'function DeviaMain() {'

new_with_detection = '''// ====== Detection intelligente du type de materiau ======
const MATERIAL_TYPES = {
  bois_structure: {
    label: "Bois structure",
    color: "#a78bfa",
    keywords: ["panne", "chevron", "sabliere", "poteau", "ferme", "arbaletrier", "lambourde", "solive", "poutre", "muraille", "entrait", "blochet", "jambette", "contrefiche", "echantignole"],
    showDimensions: true,
    suggestedUnits: ["ml", "m3", "u"],
    defaultUnit: "ml",
    placeholder: "Ex: 75x175 mm"
  },
  bois_ossature: {
    label: "Bois ossature",
    color: "#a78bfa",
    keywords: ["ossature", "montant", "traverse", "osb", "lamelle-colle", "lamellecolle", "kvh", "bois lamelle", "agglomere", "contreplaque"],
    showDimensions: true,
    suggestedUnits: ["ml", "m2", "u"],
    defaultUnit: "ml",
    placeholder: "Ex: 45x95 mm"
  },
  couverture: {
    label: "Couverture",
    color: "#60a5fa",
    keywords: ["tuile", "ardoise", "volige", "liteau", "fait", "ecran sous-toiture", "ecran sous toiture", "membrane", "bac acier", "shingle", "zinc", "cuivre", "noue", "rive", "gouttiere", "descente"],
    showDimensions: false,
    suggestedUnits: ["m2", "u", "ml"],
    defaultUnit: "m2",
    placeholder: ""
  },
  visserie: {
    label: "Visserie / fixations",
    color: "#fcd34d",
    keywords: ["vis", "clou", "boulon", "ecrou", "rondelle", "equerre", "sabot", "etrier", "tirefond", "agrafe", "cheville", "scellement", "broche", "pointe"],
    showDimensions: true,
    suggestedUnits: ["u", "kg", "forfait"],
    defaultUnit: "u",
    placeholder: "Ex: 5x80 mm"
  },
  outillage: {
    label: "Outillage",
    color: "#fb923c",
    keywords: ["marteau", "scie", "perceuse", "visseuse", "niveau", "metre", "decametre", "rabot", "ciseau", "burin", "pied de biche", "echelle", "echafaudage", "tronconneuse", "ponceuse", "meuleuse", "cordeau", "outils"],
    showDimensions: false,
    suggestedUnits: ["u", "forfait"],
    defaultUnit: "u",
    placeholder: ""
  },
  isolation: {
    label: "Isolation",
    color: "#3ecf8e",
    keywords: ["laine", "isolant", "ouate", "polystyrene", "panneau isolant", "chanvre", "lin", "fibre de bois", "fibralith", "knauf", "rockwool", "isover", "soufflage"],
    showDimensions: true,
    suggestedUnits: ["m2", "m3", "u"],
    defaultUnit: "m2",
    placeholder: "Ex: 200mm ep, R=5"
  },
  quincaillerie: {
    label: "Quincaillerie",
    color: "#94a3b8",
    keywords: ["charniere", "gond", "poignee", "serrure", "verrou", "cremone", "fermeture", "loquet", "espagnolette"],
    showDimensions: false,
    suggestedUnits: ["u", "forfait"],
    defaultUnit: "u",
    placeholder: ""
  },
  epi: {
    label: "EPI / Securite",
    color: "#ef4444",
    keywords: ["casque", "harnais", "gants", "chaussures securite", "lunettes", "masque", "protection", "antichute", "longe", "baudrier", "epi"],
    showDimensions: false,
    suggestedUnits: ["u", "forfait"],
    defaultUnit: "u",
    placeholder: ""
  },
  main_oeuvre: {
    label: "Main d'oeuvre",
    color: "#f0c040",
    keywords: ["main d'oeuvre", "main doeuvre", "charpentier", "manoeuvre", "pose", "depose", "installation", "demontage", "ouvrier", "chef equipe", "compagnon"],
    showDimensions: false,
    suggestedUnits: ["h", "forfait", "m2"],
    defaultUnit: "h",
    placeholder: ""
  },
  autre: {
    label: "Autre",
    color: "#7a7d92",
    keywords: [],
    showDimensions: true,
    suggestedUnits: ["u", "ml", "m2", "m3", "kg", "h", "forfait"],
    defaultUnit: "u",
    placeholder: ""
  }
};

function detectMateriauType(designation) {
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
// ====================================================

function DeviaMain() {'''

if "const MATERIAL_TYPES =" in content:
    print("[INFO] MATERIAL_TYPES deja en place")
elif old_marker in content:
    content = content.replace(old_marker, new_with_detection, 1)
    print("[OK] MATERIAL_TYPES + detectMateriauType ajoutes")
    modifs += 1
else:
    print("[ERREUR] function DeviaMain() non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : States detectedType + typeOverride + showTypeMenu
# Place APRES catalogForm pour eviter TDZ
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
  const [typeOverride, setTypeOverride] = useState(null);
  const [showTypeMenu, setShowTypeMenu] = useState(false);'''

if "const [detectedType" in content:
    print("[INFO] State detectedType deja present")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] States detectedType + typeOverride + showTypeMenu ajoutes")
    modifs += 1
else:
    print("[ERREUR] State catalogForm non trouve")
    sys.exit(1)

# ================================================================
# MOD 3 : resetCatalogForm - ajout des reset detectType/Override/Menu
# ================================================================

old_reset = '''  const resetCatalogForm = () => {
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
  };'''

new_reset = '''  const resetCatalogForm = () => {
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
    setDetectedType("autre");
    setTypeOverride(null);
    setShowTypeMenu(false);
  };'''

if "setDetectedType(\"autre\");\n    setTypeOverride(null);" in content:
    print("[INFO] resetCatalogForm deja modifie")
elif old_reset in content:
    content = content.replace(old_reset, new_reset, 1)
    print("[OK] resetCatalogForm correctement modifie")
    modifs += 1
else:
    print("[ERREUR] resetCatalogForm exact non trouve")
    sys.exit(1)

# ================================================================
# MOD 4 *FIX* : useEffects places APRES catalogForm (donc apres resetCatalogForm)
# Pas apres themeMode comme avant
# ================================================================

# On insere les useEffects APRES la fonction resetCatalogForm
# Le marqueur est la fonction openEditCatalogModal qui suit resetCatalogForm
old_eff_marker = '''  const openEditCatalogModal = (material) => {'''

new_with_effects = '''  // Re-detection du type quand designation change (utile en mode edition)
  useEffect(() => {
    if (catalogForm.designation && catalogForm.designation.trim().length >= 2) {
      setDetectedType(detectMateriauType(catalogForm.designation));
    }
  }, [catalogForm.designation]);

  // Auto-suggestion de l'unite selon le type detecte
  useEffect(() => {
    const activeType = typeOverride || detectedType;
    const config = MATERIAL_TYPES[activeType];
    if (!config) return;
    if (!editingCatalogId && !config.suggestedUnits.includes(catalogForm.unite)) {
      setCatalogForm(prev => ({ ...prev, unite: config.defaultUnit }));
    }
  }, [detectedType, typeOverride]);

  // Fermeture du menu type au clic externe
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
  }, [showTypeMenu]);

  const openEditCatalogModal = (material) => {'''

if "Re-detection du type quand designation change" in content:
    print("[INFO] useEffects deja en place")
elif old_eff_marker in content:
    content = content.replace(old_eff_marker, new_with_effects, 1)
    print("[OK] useEffects places APRES catalogForm (fix TDZ)")
    modifs += 1
else:
    print("[ERREUR] openEditCatalogModal non trouve")
    sys.exit(1)

# ================================================================
# MOD 5 : Champ Designation avec detection live + badge
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
                const v = e.target.value;
                setCatalogForm({ ...catalogForm, designation: v });
                setDetectedType(detectMateriauType(v));
              }}
              placeholder="Ex: Chevron sapin C24, Tuile mecanique, Vis 6x180..."
              style={inputStyle} />
            {catalogForm.designation.trim().length >= 2 && (() => {
              const activeType = typeOverride || detectedType;
              const config = MATERIAL_TYPES[activeType];
              const cBg = activeType === "main_oeuvre" ? "240, 192, 64" : activeType === "outillage" ? "251, 146, 60" : activeType === "couverture" ? "96, 165, 250" : activeType === "visserie" ? "252, 211, 77" : activeType === "isolation" ? "62, 207, 142" : activeType === "epi" ? "239, 68, 68" : activeType === "bois_structure" || activeType === "bois_ossature" ? "167, 139, 250" : "122, 125, 146";
              return (
                <div style={{ marginTop: 8, position: "relative", display: "inline-block" }}>
                  <button onClick={(e) => { e.preventDefault(); e.stopPropagation(); setShowTypeMenu(!showTypeMenu); }}
                    type="button"
                    style={{
                      background: "rgba(" + cBg + ", 0.12)",
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
                      {Object.entries(MATERIAL_TYPES).map(([t2, c]) => (
                        <button key={t2} type="button"
                          onClick={(ev) => { ev.preventDefault(); ev.stopPropagation(); setTypeOverride(t2); setShowTypeMenu(false); }}
                          style={{
                            width: "100%", background: "transparent", border: "none",
                            color: activeType === t2 ? c.color : "#e8eaf2",
                            textAlign: "left", padding: "7px 12px",
                            fontSize: 12, cursor: "pointer", borderRadius: 7,
                            display: "flex", alignItems: "center", gap: 7, transition: "background 0.12s",
                            fontWeight: activeType === t2 ? 600 : 500
                          }}
                          onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; }}
                          onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                          <span style={{ width: 6, height: 6, borderRadius: "50%", background: c.color, flexShrink: 0 }}></span>
                          {c.label}
                          {activeType === t2 && (
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

if "Type detecte : {config.label}" in content:
    print("[INFO] Champ Designation deja modifie")
elif old_designation in content:
    content = content.replace(old_designation, new_designation, 1)
    print("[OK] Champ Designation avec detection live + badge override")
    modifs += 1
else:
    print("[ERREUR] Champ Designation non trouve")
    sys.exit(1)

# ================================================================
# MOD 6 : Bloc Dimensions/Unite conditionnel
# ================================================================

old_dim_block = '''          {/* Dimensions et Unite */}
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

new_dim_block = '''          {/* Dimensions et Unite - conditionnels */}
          {(() => {
            const activeType = typeOverride || detectedType;
            const config = MATERIAL_TYPES[activeType] || MATERIAL_TYPES.autre;
            const labels = { ml: "ml (metre lineaire)", m2: "m2 (metre carre)", m3: "m3 (metre cube)", u: "u (unite)", kg: "kg (kilo)", h: "h (heure)", forfait: "forfait" };
            const others = ["ml", "m2", "m3", "u", "kg", "h", "forfait"].filter(u => !config.suggestedUnits.includes(u));
            return (
              <div style={{ display: "grid", gridTemplateColumns: config.showDimensions ? "1fr 1fr" : "1fr", gap: 12 }}>
                {config.showDimensions && (
                  <div>
                    <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Dimensions</label>
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
                    {config.suggestedUnits.map(u => <option key={u} value={u}>{labels[u]}</option>)}
                    {others.map(u => <option key={u} value={u}>{labels[u]}</option>)}
                  </select>
                </div>
              </div>
            );
          })()}'''

if "Dimensions et Unite - conditionnels" in content:
    print("[INFO] Dimensions deja conditionnelles")
elif old_dim_block in content:
    content = content.replace(old_dim_block, new_dim_block, 1)
    print("[OK] Dimensions masquees conditionnellement")
    modifs += 1
else:
    print("[ERREUR] Bloc Dimensions/Unite non trouve")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("DIFFERENCE AVEC V2 :")
print("  - useEffects places APRES catalogForm (ligne ~595)")
print("  - Plus de Temporal Dead Zone sur catalogForm")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
