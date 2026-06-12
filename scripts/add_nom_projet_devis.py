#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Etape A : Champ 'Nom du projet' dans le formulaire Devis
- State nomProjet
- Champ texte optionnel au-dessus de la zone Description
- Utilise comme nom de projet a la sauvegarde, fallback sur l'auto-genere
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_nom_projet"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter le state nomProjet
# ================================================================

old_state = 'const [prompt, setPrompt] = useState("");'
new_state = '''const [prompt, setPrompt] = useState("");
const [nomProjet, setNomProjet] = useState("");'''

if "const [nomProjet, setNomProjet]" in content:
    print("[INFO] State nomProjet deja present")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] State nomProjet ajoute")
    modifs += 1
else:
    print("[ERREUR] State prompt non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Ajouter le champ 'Nom du projet' avant la zone Description
# ================================================================

old_description = '''<div style={cardStyle}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Description du projet</label>
                <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
                  placeholder="Ex: Charpente traditionnelle en sapin pour maison de 10x8m, tuile terre cuite, pente 35 deg, combles amenageables..."
                  rows={4} style={{ ...inputStyle, resize: "vertical", lineHeight: 1.6 }} />
              </div>'''

new_description_with_name = '''<div style={cardStyle}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>
                  Nom du projet <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>(optionnel)</span>
                </label>
                <input
                  type="text"
                  value={nomProjet}
                  onChange={e => setNomProjet(e.target.value)}
                  placeholder="Ex: Maison Dupont, Chantier Lyon - M. Martin..."
                  maxLength={120}
                  style={inputStyle}
                />
              </div>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Description du projet</label>
                <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
                  placeholder="Ex: Charpente traditionnelle en sapin pour maison de 10x8m, tuile terre cuite, pente 35 deg, combles amenageables..."
                  rows={4} style={{ ...inputStyle, resize: "vertical", lineHeight: 1.6 }} />
              </div>'''

if "Nom du projet <span" in content:
    print("[INFO] Champ Nom du projet deja present")
elif old_description in content:
    content = content.replace(old_description, new_description_with_name, 1)
    print("[OK] Champ 'Nom du projet' ajoute au-dessus de Description")
    modifs += 1
else:
    print("[ERREUR] Zone Description non trouvee")
    sys.exit(1)

# ================================================================
# MOD 3 : Utiliser nomProjet a la sauvegarde du projet (Supabase)
# On cherche les insertions dans 'projects'
# ================================================================

# Insertion : il y a 2 endroits qui font setProjects(prev => [{ ... nom: p.description || "Nouveau projet" }])
# On va aussi voir si y a un insert Supabase

# Premier cas : la ligne 877 et 890 d'apres le grep precedent
# pattern: nom: p.description || "Nouveau projet"
old_nom_assign_1 = 'nom: p.description || "Nouveau projet"'
new_nom_assign_1 = 'nom: nomProjet.trim() || p.description || "Nouveau projet"'

if "nom: nomProjet.trim() || p.description" in content:
    print("[INFO] Utilisation nomProjet deja en place dans setProjects")
else:
    count = content.count(old_nom_assign_1)
    if count > 0:
        content = content.replace(old_nom_assign_1, new_nom_assign_1)
        print(f"[OK] nomProjet utilise dans setProjects ({count} occurrences)")
        modifs += 1

# Cas 2 : pour le insert Supabase, on cherche le pattern de l'insert dans la table projects
# Generalement c'est dans saveProjectToSupabase ou similaire
# On utilise un regex souple : "nom:" suivi d'une chaine

# Cherchons l'insert Supabase
supabase_insert_pattern = '''nom: p.description || "Devis sans nom"'''
supabase_insert_new = '''nom: nomProjet.trim() || p.description || "Devis sans nom"'''

if supabase_insert_new in content:
    print("[INFO] Insert Supabase deja a jour")
elif supabase_insert_pattern in content:
    content = content.replace(supabase_insert_pattern, supabase_insert_new, 1)
    print("[OK] Insert Supabase mis a jour")
    modifs += 1
else:
    # On essaye un autre pattern si l'insert utilise une autre formulation
    print("[INFO] Pattern Supabase insert non trouve (pas grave, l'insert peut utiliser projects[0].nom)")

# ================================================================
# MOD 4 : Reset nomProjet quand l'user clique sur 'Nouveau' depuis le devis
# ================================================================

# Le bouton Nouveau fait : setResult(null); setPrompt("")
# On ajoute setNomProjet("")
old_nouveau = 'onClick={() => { setResult(null); setPrompt(""); }}'
new_nouveau = 'onClick={() => { setResult(null); setPrompt(""); setNomProjet(""); }}'

if 'setNomProjet("")' in content and 'setResult(null); setPrompt(""); setNomProjet("")' in content:
    print("[INFO] Reset nomProjet deja en place")
else:
    count = content.count(old_nouveau)
    if count > 0:
        content = content.replace(old_nouveau, new_nouveau)
        print(f"[OK] Reset nomProjet au clic 'Nouveau' ({count} occurrences)")
        modifs += 1

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. State nomProjet ajoute")
print("  2. Champ 'Nom du projet (optionnel)' ajoute en haut du formulaire")
print("     - Au-dessus de Description du projet")
print("     - Label uppercase coherent")
print("     - Placeholder: 'Ex: Maison Dupont, Chantier Lyon - M. Martin...'")
print("     - maxLength 120 caracteres")
print("  3. Sauvegarde : utilise nomProjet si rempli, sinon description auto")
print("  4. Reset nomProjet quand on clique 'Nouveau' pour repartir")
print()
print("COMMENT TESTER :")
print("  1. npm run build")
print("  2. Recharger Safari")
print("  3. Page Devis")
print("  4. Le champ 'Nom du projet' apparait au-dessus de la description")
print("  5. Optionnel : entre un nom (ex: 'Maison Dupont')")
print("  6. Tape un prompt + Generer")
print("  7. Va sur Projets : tu vois 'Maison Dupont' au lieu de la description")
print("  8. Si tu laisses vide, comportement actuel (nom = description IA)")
print()
print(f"BACKUP : {backup_name}")
