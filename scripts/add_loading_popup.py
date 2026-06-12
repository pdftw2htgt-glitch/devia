#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Modif 1 : Pop-up de chargement avec progression
- Modale centree (style glass cohérent)
- 5 etapes avec icônes SVG
- Jauge de progression animée
- Simulation temporisée (1.5-3s par étape)
- Si l'API finit avant -> saute a 100%
- Si l'API prend plus -> reste sur la derniere etape "Finalisation..."
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_loading_popup"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter le state loadingStep + loadingProgress
# ================================================================

old_state = 'const [loading, setLoading] = useState(false);'
new_state = '''const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [loadingProgress, setLoadingProgress] = useState(0);'''

if "const [loadingStep" in content:
    print("[INFO] States loading deja presents")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] States loadingStep + loadingProgress ajoutes")
    modifs += 1
else:
    print("[ERREUR] State loading non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Demarrer la simulation au debut de handleGenerate
# ================================================================

old_start = '''  const handleGenerate = async (finalParams) => {
setShowQuestions(false);
setLoading(true);
setError(null);'''

new_start = '''  const handleGenerate = async (finalParams) => {
setShowQuestions(false);
setLoading(true);
setLoadingStep(0);
setLoadingProgress(0);
setError(null);

// Simulation de progression par etapes
// Etape 0: Analyse de la demande (0-1.5s)
// Etape 1: Calcul de la zone climatique (1.5-3s)
// Etape 2: Generation du modele 3D (3-5s)
// Etape 3: Creation du devis IA (5-7s)
// Etape 4: Finalisation (7s+ jusqu'a la fin de l'API)
const stepTimers = [];
stepTimers.push(setTimeout(() => { setLoadingStep(1); setLoadingProgress(20); }, 1500));
stepTimers.push(setTimeout(() => { setLoadingStep(2); setLoadingProgress(40); }, 3000));
stepTimers.push(setTimeout(() => { setLoadingStep(3); setLoadingProgress(65); }, 5000));
stepTimers.push(setTimeout(() => { setLoadingStep(4); setLoadingProgress(85); }, 7000));
// Garde une reference pour nettoyer si necessaire
window._deviaStepTimers = stepTimers;
setLoadingProgress(5);'''

if "Simulation de progression par etapes" in content:
    print("[INFO] Simulation deja presente")
elif old_start in content:
    content = content.replace(old_start, new_start, 1)
    print("[OK] Demarrage de la simulation au debut de handleGenerate")
    modifs += 1
else:
    print("[ERREUR] Debut handleGenerate non trouve")
    sys.exit(1)

# ================================================================
# MOD 3 : Nettoyer les timers a la fin (succes ou erreur)
# On va chercher setLoading(false) dans handleGenerate
# ================================================================

# Trouver tous les setLoading(false) et nettoyer avant
import re

# Premier remplacement : finally avec setLoading(false)
# On va chercher les patterns de fin (try-catch-finally)
old_finally_marker = 'setLoading(false);'

# Verifier le nombre d'occurrences
count = content.count(old_finally_marker)
print(f"[INFO] {count} occurrences de setLoading(false) trouvees")

# On remplace SEULEMENT le premier setLoading(false) qui est dans handleGenerate
# Pour eviter de toucher aux autres
# On cherche la 1ere occurrence APRES handleGenerate
hg_idx = content.find("const handleGenerate = async")
if hg_idx > 0:
    # On cherche la fin de la fonction (la prochaine declaration "const ... =" au meme niveau)
    next_const_idx = content.find("\n  const ", hg_idx + 100)
    if next_const_idx > 0:
        # On extrait le bloc de la fonction
        func_block = content[hg_idx:next_const_idx]
        # On remplace setLoading(false) dans CE bloc uniquement, par une version avec cleanup
        if "_deviaStepTimers" not in func_block:
            new_func_block = func_block.replace(
                "setLoading(false);",
                """// Cleanup des timers de simulation
      if (window._deviaStepTimers) {
        window._deviaStepTimers.forEach(t => clearTimeout(t));
        window._deviaStepTimers = null;
      }
      setLoadingProgress(100);
      setLoadingStep(5);
      // Petit delai pour montrer le 100% avant de cacher
      setTimeout(() => setLoading(false), 300);"""
            )
            content = content.replace(func_block, new_func_block, 1)
            print("[OK] Nettoyage des timers + animation 100% ajoutes")
            modifs += 1
        else:
            print("[INFO] Nettoyage timers deja present")

# ================================================================
# MOD 4 : Ajouter la modale Pop-up avant la fermeture de DeviaMain
# On cherche un marqueur stable pres de la fin de DeviaMain
# Strategie : on l'ajoute juste avant le dernier </div> du return
# Plus simple : on l'ajoute apres l'ouverture du <div> racine
# Encore plus simple : on cible une modale existante
# ================================================================

# Strategie : on l'ajoute juste avant la modale d'ajout catalogue
# qui est connue (showAddCatalogModal)
old_modal_marker = '  {showAddCatalogModal && ('

new_loading_modal = '''  {/* Pop-up de chargement avec progression */}
  {loading && (
    <div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0, 0, 0, 0.65)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 2000, padding: 16,
        animation: "fadeInUp 0.18s ease-out"
      }}>
      <div style={{
        background: "rgba(22, 25, 35, 0.98)",
        backdropFilter: "blur(24px) saturate(140%)",
        WebkitBackdropFilter: "blur(24px) saturate(140%)",
        border: "1px solid rgba(240, 192, 64, 0.2)",
        borderRadius: 20,
        padding: 32,
        maxWidth: 480,
        width: "100%",
        boxShadow: "0 24px 64px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255,255,255,0.04) inset, 0 0 32px rgba(240, 192, 64, 0.08)"
      }}>
        {/* En-tete */}
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 24 }}>
          <div style={{
            width: 44, height: 44, borderRadius: 12,
            background: "linear-gradient(135deg, rgba(240, 192, 64, 0.18), rgba(240, 192, 64, 0.05))",
            border: "1px solid rgba(240, 192, 64, 0.3)",
            display: "flex", alignItems: "center", justifyContent: "center"
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" style={{ display: "none" }}/>
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>Generation en cours</h2>
            <div style={{ color: "#7a7d92", fontSize: 12 }}>DEVIA prepare votre devis...</div>
          </div>
        </div>

        {/* Jauge de progression */}
        <div style={{ marginBottom: 24 }}>
          <div style={{
            width: "100%",
            height: 6,
            background: "rgba(255, 255, 255, 0.06)",
            borderRadius: 999,
            overflow: "hidden",
            position: "relative"
          }}>
            <div style={{
              height: "100%",
              width: loadingProgress + "%",
              background: "linear-gradient(90deg, #e0a020 0%, #f0c040 50%, #fcd34d 100%)",
              borderRadius: 999,
              transition: "width 0.4s ease-out",
              boxShadow: "0 0 8px rgba(240, 192, 64, 0.5)"
            }}/>
          </div>
          <div style={{ marginTop: 8, display: "flex", justifyContent: "space-between", fontSize: 11, color: "#7a7d92" }}>
            <span>Progression</span>
            <span style={{ fontFamily: "ui-monospace, monospace", color: "#f0c040", fontWeight: 600 }}>{loadingProgress}%</span>
          </div>
        </div>

        {/* Liste des etapes */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {[
            { icon: "search", label: "Analyse de la demande" },
            { icon: "globe", label: "Calcul de la zone climatique" },
            { icon: "cube", label: "Generation du modele 3D" },
            { icon: "brain", label: "Creation du devis IA" },
            { icon: "check-circle", label: "Finalisation" }
          ].map((step, idx) => {
            const status = idx < loadingStep ? "done" : idx === loadingStep ? "active" : "pending";
            const color = status === "done" ? "#3ecf8e" : status === "active" ? "#f0c040" : "#545870";
            const bgColor = status === "done" ? "rgba(62, 207, 142, 0.08)" : status === "active" ? "rgba(240, 192, 64, 0.08)" : "rgba(255, 255, 255, 0.02)";
            const borderColor = status === "done" ? "rgba(62, 207, 142, 0.2)" : status === "active" ? "rgba(240, 192, 64, 0.25)" : "rgba(255, 255, 255, 0.04)";
            return (
              <div key={idx} style={{
                display: "flex", alignItems: "center", gap: 12,
                background: bgColor,
                border: "1px solid " + borderColor,
                borderRadius: 12,
                padding: "10px 14px",
                transition: "all 0.25s"
              }}>
                <div style={{
                  width: 30, height: 30, borderRadius: 8,
                  background: status === "active" ? "rgba(240, 192, 64, 0.15)" : status === "done" ? "rgba(62, 207, 142, 0.15)" : "rgba(255, 255, 255, 0.04)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0,
                  transition: "all 0.25s"
                }}>
                  {status === "done" ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  ) : status === "active" ? (
                    <span style={{
                      display: "inline-block",
                      width: 14, height: 14,
                      border: "2px solid rgba(240, 192, 64, 0.25)",
                      borderTopColor: "#f0c040",
                      borderRadius: "50%",
                      animation: "spin 0.7s linear infinite"
                    }}></span>
                  ) : (
                    step.icon === "search" ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                      </svg>
                    ) : step.icon === "globe" ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
                      </svg>
                    ) : step.icon === "cube" ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
                      </svg>
                    ) : step.icon === "brain" ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.96.44 2.5 2.5 0 01-2.96-3.08 3 3 0 01-.34-5.58 2.5 2.5 0 011.32-4.24 2.5 2.5 0 014.44-1.04zM14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.96.44 2.5 2.5 0 002.96-3.08 3 3 0 00.34-5.58 2.5 2.5 0 00-1.32-4.24 2.5 2.5 0 00-4.44-1.04z"/>
                      </svg>
                    ) : (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
                      </svg>
                    )
                  )}
                </div>
                <div style={{
                  flex: 1,
                  fontSize: 13,
                  fontWeight: status === "active" ? 600 : 500,
                  color: status === "pending" ? "#7a7d92" : "#e8eaf2",
                  transition: "color 0.25s"
                }}>
                  {step.label}
                </div>
                {status === "active" && (
                  <span style={{ fontSize: 11, color: "#f0c040", fontWeight: 600, letterSpacing: "0.02em" }}>EN COURS</span>
                )}
              </div>
            );
          })}
        </div>

        {/* Pied de page */}
        <div style={{
          marginTop: 20,
          paddingTop: 16,
          borderTop: "1px solid rgba(255, 255, 255, 0.05)",
          fontSize: 11,
          color: "#545870",
          textAlign: "center",
          letterSpacing: "0.02em"
        }}>
          Cela peut prendre quelques secondes
        </div>
      </div>
    </div>
  )}

  {showAddCatalogModal && ('''

if "Pop-up de chargement avec progression" in content:
    print("[INFO] Modale loading deja en place")
elif old_modal_marker in content:
    content = content.replace(old_modal_marker, new_loading_modal, 1)
    print("[OK] Pop-up de chargement ajoute (avant la modale catalogue)")
    modifs += 1
else:
    print("[ERREUR] Marqueur showAddCatalogModal non trouve")
    sys.exit(1)

# ================================================================
# MOD 5 : Ajouter @keyframes spin au CSS global si pas deja present
# ================================================================

if "@keyframes spin" not in content:
    # On va l'ajouter dans une balise <style> au debut du return de DeviaMain
    # Strategie : on l'ajoute juste apres le DIV racine
    # Marqueur : le <div style={{ minHeight: "100vh"...
    # Plus simple : on n'ajoute pas, on suppose qu'il est deja dans un fichier CSS global
    # Sinon on l'ajoute dans le head via une balise style
    # Mais en React, le mieux est un <style> tag

    # On verifie si la modale d'avatar utilise deja l'animation spin
    if "animation: \"spin" in content:
        print("[INFO] Animation spin probablement deja definie ailleurs")
    else:
        print("[WARN] Animation spin pas definie - elle est attendue dans index.css")
else:
    print("[INFO] @keyframes spin deja defini")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. States loadingStep + loadingProgress ajoutes")
print("  2. Demarrage de la simulation 5 etapes au debut de handleGenerate")
print("  3. Cleanup des timers + animation 100% a la fin")
print("  4. Modale pop-up de chargement (style glass + jauge animee + 5 etapes)")
print()
print("ETAPES SIMULEES :")
print("  0. Analyse de la demande     (icone search)")
print("  1. Calcul zone climatique    (icone globe)")
print("  2. Generation modele 3D      (icone cube)")
print("  3. Creation devis IA         (icone brain)")
print("  4. Finalisation              (icone check)")
print()
print("TIMING :")
print("  0.0s -> Etape 1 (Analyse)")
print("  1.5s -> Etape 2 (Zone)")
print("  3.0s -> Etape 3 (3D)")
print("  5.0s -> Etape 4 (Devis IA)")
print("  7.0s -> Etape 5 (Finalisation)")
print("  Fin API -> 100% + close")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
