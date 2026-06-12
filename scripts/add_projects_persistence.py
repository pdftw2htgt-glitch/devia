#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Persistance des projets dans Supabase
Modifie devia.jsx pour :
1. Importer le client Supabase
2. Charger les projets de l'utilisateur au demarrage
3. Sauvegarder chaque devis genere dans la table 'projects'

A lancer depuis ~/Desktop/devia :
    python3 add_projects_persistence.py

Backup automatique cree avant modification.
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("package.json"):
    print("ERREUR : package.json introuvable.")
    print("Lance ce script depuis ~/Desktop/devia")
    sys.exit(1)

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

# Backup
backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_persistence"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

# Lire le fichier
with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MODIFICATION 1 : Ajouter l'import Supabase en haut du fichier
# ================================================================

# On cherche la 1ere ligne d'import et on ajoute notre import juste apres
import_marker = 'import React'
if import_marker not in content:
    print("ERREUR : impossible de trouver les imports React.")
    print("Le fichier a peut-etre une structure differente.")
    sys.exit(1)

# Verifier si l'import Supabase n'est pas deja present
if 'from "./src/lib/supabase"' in content or "from './src/lib/supabase'" in content:
    print("[INFO] Import Supabase deja present, skip modification 1")
else:
    # Trouver la premiere ligne d'import et inserer apres
    lines = content.split("\n")
    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if not inserted and line.strip().startswith("import ") and "react" in line.lower():
            new_lines.append('import { supabase } from "./src/lib/supabase";')
            inserted = True
    content = "\n".join(new_lines)
    print("[OK] Import Supabase ajoute")

# ================================================================
# MODIFICATION 2 : Ajouter useEffect pour charger les projets au demarrage
# ================================================================

# On cherche la ligne avec "const [projects, setProjects] = useState([]);"
# et on ajoute un useEffect juste apres

projects_state_line = "const [projects, setProjects] = useState([]);"
if projects_state_line not in content:
    print("ERREUR : impossible de trouver le useState projects.")
    sys.exit(1)

# Le useEffect a injecter
load_effect = '''const [projects, setProjects] = useState([]);

  // Charge les projets de l'utilisateur depuis Supabase au demarrage
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;
        const { data, error } = await supabase
          .from("projects")
          .select("*")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false });
        if (error) {
          console.error("Erreur chargement projets:", error);
          return;
        }
        if (data) {
          // Conversion format DB vers format affichage
          const formatted = data.map(p => ({
            id: p.id,
            nom: p.nom,
            commune: p.commune || "",
            date: p.created_at ? p.created_at.split("T")[0] : "",
            ttc: p.total_ttc || 0,
            dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m",
            devis_data: p.devis_data,
            zone_data: p.zone_data,
          }));
          setProjects(formatted);
        }
      } catch (e) {
        console.error("Erreur loadProjects:", e);
      }
    };
    loadProjects();
  }, []);
'''

# Verifier si le useEffect est deja present
if "loadProjects" in content:
    print("[INFO] useEffect loadProjects deja present, skip modification 2")
else:
    content = content.replace(projects_state_line, load_effect, 1)
    print("[OK] useEffect chargement projets ajoute")

# ================================================================
# MODIFICATION 3 : Sauvegarder dans Supabase quand on cree un projet
# ================================================================

# La ligne actuelle :
old_save_line = 'setProjects(prev => [{ id: Date.now(), nom: p.description || "Nouveau projet", commune: p.commune || commune, date: new Date().toISOString().split("T")[0], ttc: parsed.totaux ? parsed.totaux.totalTTC : 0, dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m" }, ...prev]);'

new_save_block = '''// Sauvegarde dans Supabase + ajout local
    (async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (user) {
          const totalTTC = parsed.totaux ? parsed.totaux.totalTTC : 0;
          const totalHT = parsed.totaux ? parsed.totaux.totalHT : 0;
          const newProject = {
            user_id: user.id,
            nom: p.description || "Nouveau projet",
            commune: p.commune || commune,
            longueur: p.longueur || null,
            largeur: p.largeur || null,
            hauteur: p.hauteur || null,
            pente: p.pente || null,
            surface: p.surface || null,
            type_charpente: p.type || null,
            total_ttc: totalTTC,
            total_ht: totalHT,
            devis_data: parsed,
            zone_data: zoneInfo,
          };
          const { data: inserted, error: insertError } = await supabase
            .from("projects")
            .insert(newProject)
            .select()
            .single();
          if (insertError) {
            console.error("Erreur sauvegarde projet:", insertError);
            // Fallback : ajout local seulement
            setProjects(prev => [{ id: Date.now(), nom: p.description || "Nouveau projet", commune: p.commune || commune, date: new Date().toISOString().split("T")[0], ttc: totalTTC, dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m" }, ...prev]);
          } else if (inserted) {
            // Ajout local avec l'ID Supabase
            setProjects(prev => [{
              id: inserted.id,
              nom: inserted.nom,
              commune: inserted.commune || "",
              date: inserted.created_at ? inserted.created_at.split("T")[0] : "",
              ttc: inserted.total_ttc || 0,
              dims: (inserted.longueur || "?") + "x" + (inserted.largeur || "?") + "m",
              devis_data: inserted.devis_data,
              zone_data: inserted.zone_data,
            }, ...prev]);
          }
        } else {
          // Pas connecte : fallback local
          setProjects(prev => [{ id: Date.now(), nom: p.description || "Nouveau projet", commune: p.commune || commune, date: new Date().toISOString().split("T")[0], ttc: parsed.totaux ? parsed.totaux.totalTTC : 0, dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m" }, ...prev]);
        }
      } catch (e) {
        console.error("Erreur sauvegarde:", e);
      }
    })();'''

if old_save_line not in content:
    print("ATTENTION : ligne setProjects exacte introuvable.")
    print("Le fichier a peut-etre deja ete modifie.")
    print("Verification de presence d'un saveProjects async...")
    if "supabase.from(\"projects\").insert" in content:
        print("[INFO] Sauvegarde Supabase deja en place, skip modification 3")
    else:
        print("ERREUR : impossible de localiser la ligne setProjects.")
        print("Restoration du backup...")
        shutil.copy(backup_name, "devia.jsx")
        print(f"[OK] devia.jsx restaure depuis {backup_name}")
        sys.exit(1)
else:
    content = content.replace(old_save_line, new_save_block, 1)
    print("[OK] Sauvegarde Supabase ajoutee a handleGenerate")

# ================================================================
# MODIFICATION 4 : Recuperer zoneInfo dans le scope (deja dispo normalement)
# ================================================================
# zoneInfo est deja calcule plus haut dans handleGenerate, on n'a rien a faire

# Ecrire le fichier modifie
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("MODIFICATIONS APPLIQUEES AVEC SUCCES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Import Supabase ajoute en haut de devia.jsx")
print("  2. useEffect : charge les projets au demarrage")
print("  3. handleGenerate : sauvegarde dans Supabase + ajout local")
print()
print("PROCHAINES ETAPES :")
print("  1. Tester en local : npm run dev")
print("  2. Aller sur http://localhost:5173")
print("  3. Se connecter, generer un devis test")
print("  4. Verifier que le devis apparait dans 'Projets'")
print("  5. Rafraichir la page : le devis doit toujours etre la !")
print()
print(f"BACKUP DISPO : {backup_name}")
print("(en cas de probleme : cp BACKUP devia.jsx)")
