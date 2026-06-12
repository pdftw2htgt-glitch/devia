#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Persistance des projets dans Supabase (v2 corrigee)
Modifie devia.jsx pour :
1. Importer le client Supabase
2. Charger les projets de l'utilisateur au demarrage
3. Sauvegarder chaque devis genere dans la table 'projects'

A lancer depuis ~/Desktop/devia :
    python3 add_projects_persistence_v2.py
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
# MODIFICATION 1 : Ajouter l'import Supabase
# ================================================================

# On cherche la ligne d'import existante de l'auth Supabase et on ajoute apres
auth_import_marker = 'import { signOut } from "./src/lib/auth.js";'

if 'from "./src/lib/supabase"' in content:
    print("[INFO] Import Supabase deja present, skip modification 1")
else:
    if auth_import_marker not in content:
        print("ERREUR : impossible de trouver l'import auth.js comme reference.")
        print("Restoration du backup...")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    
    new_imports = auth_import_marker + '\nimport { supabase } from "./src/lib/supabase.js";'
    content = content.replace(auth_import_marker, new_imports, 1)
    print("[OK] Import Supabase ajoute")

# ================================================================
# MODIFICATION 2 : Ajouter useEffect pour charger les projets
# ================================================================

projects_state_line = "const [projects, setProjects] = useState([]);"
if projects_state_line not in content:
    print("ERREUR : impossible de trouver le useState projects.")
    print("Restoration du backup...")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

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

if "loadProjects" in content:
    print("[INFO] useEffect loadProjects deja present, skip modification 2")
else:
    content = content.replace(projects_state_line, load_effect, 1)
    print("[OK] useEffect chargement projets ajoute")

# ================================================================
# MODIFICATION 3 : Sauvegarder dans Supabase quand on cree un projet
# ================================================================

old_save_line = 'setProjects(prev => [{ id: Date.now(), nom: p.description || "Nouveau projet", commune: p.commune || commune, date: new Date().toISOString().split("T")[0], ttc: parsed.totaux ? parsed.totaux.totalTTC : 0, dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m" }, ...prev]);'

new_save_block = '''(async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        const totalTTC = parsed.totaux ? parsed.totaux.totalTTC : 0;
        const totalHT = parsed.totaux ? parsed.totaux.totalHT : 0;
        if (user) {
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
          };
          const { data: inserted, error: insertError } = await supabase
            .from("projects")
            .insert(newProject)
            .select()
            .single();
          if (insertError) {
            console.error("Erreur sauvegarde projet:", insertError);
            setProjects(prev => [{ id: Date.now(), nom: p.description || "Nouveau projet", commune: p.commune || commune, date: new Date().toISOString().split("T")[0], ttc: totalTTC, dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m" }, ...prev]);
          } else if (inserted) {
            setProjects(prev => [{
              id: inserted.id,
              nom: inserted.nom,
              commune: inserted.commune || "",
              date: inserted.created_at ? inserted.created_at.split("T")[0] : "",
              ttc: inserted.total_ttc || 0,
              dims: (inserted.longueur || "?") + "x" + (inserted.largeur || "?") + "m",
              devis_data: inserted.devis_data,
            }, ...prev]);
          }
        } else {
          setProjects(prev => [{ id: Date.now(), nom: p.description || "Nouveau projet", commune: p.commune || commune, date: new Date().toISOString().split("T")[0], ttc: totalTTC, dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m" }, ...prev]);
        }
      } catch (e) {
        console.error("Erreur sauvegarde:", e);
      }
    })();'''

if old_save_line not in content:
    if 'supabase.from("projects").insert' in content:
        print("[INFO] Sauvegarde Supabase deja en place, skip modification 3")
    else:
        print("ERREUR : impossible de localiser la ligne setProjects exacte.")
        print("Restoration du backup...")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
else:
    content = content.replace(old_save_line, new_save_block, 1)
    print("[OK] Sauvegarde Supabase ajoutee a handleGenerate")

# Ecrire le fichier modifie
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("MODIFICATIONS APPLIQUEES AVEC SUCCES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Import Supabase ajoute")
print("  2. useEffect : charge les projets au demarrage depuis Supabase")
print("  3. handleGenerate : sauvegarde chaque devis dans Supabase")
print()
print("PROCHAINES ETAPES :")
print("  1. Lance : npm run dev")
print("  2. Va sur http://localhost:5173")
print("  3. Connecte-toi")
print("  4. Genere un devis test")
print("  5. Va dans 'Projets' : tu dois voir le devis")
print("  6. Rafraichis la page : le devis doit toujours etre la !")
print()
print(f"BACKUP DISPO : {backup_name}")
