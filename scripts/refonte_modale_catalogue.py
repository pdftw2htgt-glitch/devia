#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 3.C : Modale Ajouter/Modifier materiau
Refait :
1. Overlay (backdrop-blur)
2. Container modale (style liquid glass)
3. Header (titre + bouton X en icone SVG)
4. Tous les labels en MAJUSCULES (coherence)
5. Erreur avec icone SVG
6. Boutons Annuler + Ajouter/Enregistrer (style pill coherent)

A lancer depuis ~/Desktop/devia :
    python3 refonte_modale_catalogue.py

Apres : npm run build
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_modale_catalogue"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD 1 : Overlay + container modale
# ================================================================

old_overlay = '''<div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: 16 }}
      onClick={(e) => { if (e.target === e.currentTarget) { setShowAddCatalogModal(false); resetCatalogForm(); } }}>
      <div style={{ background: "#13161f", border: "1px solid #1e2231", borderRadius: 12, padding: 24, maxWidth: 560, width: "100%", maxHeight: "90vh", overflowY: "auto" }}>'''

new_overlay = '''<div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0, 0, 0, 0.55)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 1000, padding: 16,
        animation: "fadeInUp 0.18s ease-out"
      }}
      onClick={(e) => { if (e.target === e.currentTarget) { setShowAddCatalogModal(false); resetCatalogForm(); } }}>
      <div style={{
        background: "rgba(22, 25, 35, 0.95)",
        backdropFilter: "blur(24px) saturate(140%)",
        WebkitBackdropFilter: "blur(24px) saturate(140%)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: 20,
        padding: 28,
        maxWidth: 560,
        width: "100%",
        maxHeight: "90vh",
        overflowY: "auto",
        boxShadow: "0 24px 64px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,0.04) inset"
      }}>'''

if 'background: "rgba(22, 25, 35, 0.95)"' in content and 'animation: "fadeInUp 0.18s ease-out"' in content:
    print("[INFO] Overlay + container deja refondus")
elif old_overlay in content:
    content = content.replace(old_overlay, new_overlay, 1)
    print("[OK] Overlay + container modale refondus (backdrop-blur + glass)")
else:
    print("[ERREUR] Overlay non trouve.")
    sys.exit(1)

# ================================================================
# MOD 2 : Header (titre + bouton X)
# ================================================================

old_header = '''<div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <h2 style={{ fontSize: 18, fontWeight: 700 }}>{editingCatalogId ? "Modifier un materiau" : "Ajouter un materiau"}</h2>
          <button onClick={() => { setShowAddCatalogModal(false); resetCatalogForm(); }}
            style={{ background: "transparent", border: "none", color: "#545870", cursor: "pointer", fontSize: 22, padding: 4 }}>x</button>
        </div>'''

new_header = '''<div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: 24, gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>{editingCatalogId ? "Modifier un materiau" : "Ajouter un materiau"}</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>{editingCatalogId ? "Mettez a jour les informations" : "Ajoutez un prix a votre catalogue personnel"}</div>
          </div>
          <button onClick={() => { setShowAddCatalogModal(false); resetCatalogForm(); }}
            style={{
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              color: "#7a7d92",
              cursor: "pointer",
              borderRadius: 10,
              padding: 8,
              flexShrink: 0,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.15s"
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)"; e.currentTarget.style.color = "#e8eaf2"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.04)"; e.currentTarget.style.color = "#7a7d92"; }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>'''

if "Mettez a jour les informations" in content:
    print("[INFO] Header modale deja refondu")
elif old_header in content:
    content = content.replace(old_header, new_header, 1)
    print("[OK] Header modale refondu (titre + sous-titre + bouton X SVG)")
else:
    print("[WARN] Header modale non trouve")

# ================================================================
# MOD 3 : Labels du formulaire (5 labels a mettre en uppercase)
# ================================================================

labels_changes = [
    ('<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Categorie *</label>',
     '<label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Categorie <span style={{ color: "#f0c040" }}>*</span></label>'),
    ('<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Designation *</label>',
     '<label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Designation <span style={{ color: "#f0c040" }}>*</span></label>'),
    ('<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Dimensions</label>',
     '<label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Dimensions</label>'),
    ('<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Unite *</label>',
     '<label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Unite <span style={{ color: "#f0c040" }}>*</span></label>'),
    ('<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Prix HT (EUR) *</label>',
     '<label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Prix HT <span style={{ color: "#7a7d92", fontWeight: 400, textTransform: "none" }}>(EUR)</span> <span style={{ color: "#f0c040" }}>*</span></label>'),
    ('<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Notes (optionnel)</label>',
     '<label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Notes <span style={{ color: "#7a7d92", fontWeight: 400, textTransform: "none" }}>(optionnel)</span></label>'),
]

count_labels = 0
for old_label, new_label in labels_changes:
    if new_label in content:
        continue  # Deja modifie
    if old_label in content:
        content = content.replace(old_label, new_label, 1)
        count_labels += 1

print(f"[OK] {count_labels} labels modale en MAJUSCULES")

# ================================================================
# MOD 4 : Erreur avec icone SVG
# ================================================================

old_error = '''{catalogFormError && (
            <div style={{ background: "#ef444418", border: "1px solid #ef4444", borderRadius: 8, padding: 12, color: "#ef4444", fontSize: 13 }}>
              {catalogFormError}
            </div>
          )}'''

new_error = '''{catalogFormError && (
            <div style={{
              background: "rgba(239, 68, 68, 0.08)",
              border: "1px solid rgba(239, 68, 68, 0.25)",
              borderRadius: 10,
              padding: 14,
              color: "#fca5a5",
              fontSize: 13,
              display: "flex",
              alignItems: "start",
              gap: 10
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <div>{catalogFormError}</div>
            </div>
          )}'''

if 'color: "#fca5a5"' in content and 'circle cx="12" cy="12" r="10"' in content:
    # Verifier si c'est bien celui du modal (pourrait etre l'erreur du formulaire devis)
    if old_error in content:
        content = content.replace(old_error, new_error, 1)
        print("[OK] Erreur modale refondue (icone SVG warning)")
    else:
        print("[INFO] Erreur modale deja refondue")
elif old_error in content:
    content = content.replace(old_error, new_error, 1)
    print("[OK] Erreur modale refondue (icone SVG warning)")
else:
    print("[WARN] Erreur modale non trouvee")

# ================================================================
# MOD 5 : Boutons Annuler + Ajouter/Enregistrer
# ================================================================

old_buttons = '''<div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 8 }}>
            <button onClick={() => { setShowAddCatalogModal(false); resetCatalogForm(); }}
              disabled={savingCatalog}
              style={{ ...btnSecondary, opacity: savingCatalog ? 0.5 : 1 }}>
              Annuler
            </button>
            <button onClick={handleAddMaterial}
              disabled={savingCatalog}
              style={{ background: "#f0c040", color: "#08090c", border: "none", borderRadius: 8, padding: "10px 20px", cursor: savingCatalog ? "not-allowed" : "pointer", fontSize: 14, fontWeight: 700, opacity: savingCatalog ? 0.7 : 1 }}>
              {savingCatalog ? (editingCatalogId ? "Sauvegarde..." : "Ajout en cours...") : (editingCatalogId ? "Enregistrer" : "Ajouter")}
            </button>
          </div>'''

new_buttons = '''<div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12, paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
            <button onClick={() => { setShowAddCatalogModal(false); resetCatalogForm(); }}
              disabled={savingCatalog}
              style={{ ...btnSecondary, opacity: savingCatalog ? 0.5 : 1 }}>
              Annuler
            </button>
            <button onClick={handleAddMaterial}
              disabled={savingCatalog}
              style={{
                ...btnPrimary,
                padding: "11px 22px",
                opacity: savingCatalog ? 0.7 : 1,
                cursor: savingCatalog ? "not-allowed" : "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                boxShadow: savingCatalog ? "none" : "0 4px 14px rgba(240, 192, 64, 0.25)"
              }}>
              {savingCatalog ? (
                <>
                  <span style={{ display: "inline-block", width: 13, height: 13, border: "2px solid rgba(10,10,10,0.25)", borderTopColor: "#0a0a0a", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                  <span>{editingCatalogId ? "Sauvegarde..." : "Ajout en cours..."}</span>
                </>
              ) : (
                <>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    {editingCatalogId ? <polyline points="20 6 9 17 4 12"/> : <><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></>}
                  </svg>
                  {editingCatalogId ? "Enregistrer" : "Ajouter"}
                </>
              )}
            </button>
          </div>'''

if 'borderTop: "1px solid rgba(255, 255, 255, 0.05)"' in content and "{editingCatalogId ? \"Sauvegarde...\" : \"Ajout en cours...\"}" in content:
    print("[INFO] Boutons modale deja refondus")
elif old_buttons in content:
    content = content.replace(old_buttons, new_buttons, 1)
    print("[OK] Boutons modale refondus (icone + spinner + style coherent)")
else:
    print("[WARN] Boutons modale non trouves exactement")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 3.C APPLIQUEE - Modale Ajouter/Modifier")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Overlay : backdrop-blur + fade-in animation")
print("  2. Container : glass + bordure plus arrondie + ombre")
print("  3. Header :")
print("     - Titre + sous-titre descriptif")
print("     - Bouton X en icone SVG (au lieu du caractere texte)")
print("  4. Tous les labels en MAJUSCULES (etoile jaune sur champs requis)")
print("  5. Erreur :")
print("     - Icone SVG warning")
print("     - Rouge plus subtil et lisible")
print("  6. Boutons Annuler/Ajouter :")
print("     - Separes par ligne fine en haut")
print("     - Bouton principal avec icone (+ ou check)")
print("     - Spinner moderne pendant chargement")
print("     - Ombre doree sur bouton principal")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Refonte design Session 3.C - Modale Ajouter/Modifier'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
