#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Projets cliquables + suppression
Modifie devia.jsx pour :
1. Cliquer sur un projet -> recharge les details du devis
2. Bouton 'Supprimer' avec confirmation sur chaque projet

A lancer depuis ~/Desktop/devia :
    python3 add_project_clickable.py
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

# Backup
backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_clickable"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MODIFICATION 1 : Ajouter les fonctions loadProjectDetails et deleteProject
# On les insere juste avant le 'const handleSubmit'
# ================================================================

handle_submit_marker = "const handleSubmit = () => {"
if handle_submit_marker not in content:
    print("ERREUR : impossible de trouver handleSubmit.")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

# Verifier si deja present
if "loadProjectDetails" in content:
    print("[INFO] loadProjectDetails deja present, skip modification 1")
else:
    new_functions = '''const loadProjectDetails = (project) => {
    if (!project.devis_data) {
      setError("Donnees du devis non disponibles pour ce projet.");
      return;
    }
    setResult(project.devis_data);
    if (project.devis_data.projet) {
      const p = project.devis_data.projet;
      setView3DParams({
        longueur: p.longueur || 10,
        largeur: p.largeur || 8,
        hauteur: p.hauteur || 3,
        pente: p.pente || 35
      });
    }
    setActiveResultTab("devis");
    setActiveTab("devis");
    setError(null);
  };

  const deleteProject = async (projectId, projectNom) => {
    const confirmed = window.confirm("Supprimer le projet \\"" + projectNom + "\\" ? Cette action est irreversible.");
    if (!confirmed) return;
    try {
      const { error } = await supabase.from("projects").delete().eq("id", projectId);
      if (error) {
        console.error("Erreur suppression:", error);
        alert("Erreur lors de la suppression : " + error.message);
        return;
      }
      setProjects(prev => prev.filter(p => p.id !== projectId));
    } catch (e) {
      console.error("Erreur deleteProject:", e);
      alert("Erreur lors de la suppression");
    }
  };

  ''' + handle_submit_marker

    content = content.replace(handle_submit_marker, new_functions, 1)
    print("[OK] Fonctions loadProjectDetails et deleteProject ajoutees")

# ================================================================
# MODIFICATION 2 : Modifier la liste des projets pour les rendre interactifs
# ================================================================

# La div actuelle qui affiche un projet
old_project_card = '''            {projects.map(p => (
              <div key={p.id} style={{ ...cardStyle, display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer", marginBottom: 0 }}
                onClick={() => setActiveTab("devis")}>
                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  <div style={{ width: 44, height: 44, background: "#f0c04018", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22 }}>🏠</div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 15 }}>{p.nom}</div>
                    <div style={{ color: "#545870", fontSize: 13 }}>{p.commune} - {p.dims} - {new Date(p.date).toLocaleDateString("fr-FR")}</div>
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ color: "#f0c040", fontWeight: 700, fontSize: 18 }}>{p.ttc.toLocaleString("fr-FR")} EUR</div>
                  <div style={{ color: "#545870", fontSize: 12 }}>TTC</div>
                </div>
              </div>
            ))}'''

new_project_card = '''            {projects.map(p => (
              <div key={p.id} style={{ ...cardStyle, display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer", marginBottom: 0, transition: "border 0.15s" }}
                onMouseEnter={(e) => e.currentTarget.style.border = "1px solid #f0c040"}
                onMouseLeave={(e) => e.currentTarget.style.border = "1px solid #1e2231"}
                onClick={() => loadProjectDetails(p)}>
                <div style={{ display: "flex", alignItems: "center", gap: 16, flex: 1 }}>
                  <div style={{ width: 44, height: 44, background: "#f0c04018", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22 }}>🏠</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 15 }}>{p.nom}</div>
                    <div style={{ color: "#545870", fontSize: 13 }}>{p.commune} - {p.dims} - {new Date(p.date).toLocaleDateString("fr-FR")}</div>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: "#f0c040", fontWeight: 700, fontSize: 18 }}>{p.ttc.toLocaleString("fr-FR")} EUR</div>
                    <div style={{ color: "#545870", fontSize: 12 }}>TTC</div>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteProject(p.id, p.nom); }}
                    title="Supprimer ce projet"
                    style={{ background: "transparent", border: "1px solid #2a2e40", color: "#ef4444", borderRadius: 6, padding: "6px 10px", cursor: "pointer", fontSize: 13, fontWeight: 600, transition: "all 0.15s" }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = "#ef444418"; e.currentTarget.style.borderColor = "#ef4444"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "#2a2e40"; }}>
                    Supprimer
                  </button>
                </div>
              </div>
            ))}'''

if old_project_card not in content:
    if "loadProjectDetails(p)" in content:
        print("[INFO] Carte projet deja modifiee, skip modification 2")
    else:
        print("ERREUR : impossible de trouver la carte projet exacte.")
        print("Restoration du backup...")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
else:
    content = content.replace(old_project_card, new_project_card, 1)
    print("[OK] Carte projet rendue cliquable + bouton supprimer ajoute")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Cliquer sur un projet -> recharge le devis (3D + tableau)")
print("  2. Bouton 'Supprimer' (rouge) sur chaque projet")
print("  3. Effet hover : bordure jaune au survol d'un projet")
print()
print("PROCHAINES ETAPES :")
print("  1. Verifier la syntaxe en local : npm run dev")
print("  2. Si OK, push sur GitHub :")
print("     git add devia.jsx")
print("     git commit -m 'Projets cliquables + suppression'")
print("     git push")
print("  3. Tester sur devia-iota.vercel.app")
print()
print(f"BACKUP : {backup_name}")
