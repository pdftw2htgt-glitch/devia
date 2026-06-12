#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Etape 1.2.A : Detection du type de projet par l'IA
Modifie devia.jsx pour :
1. Ajouter type_projet au prompt envoye a Claude
2. Donner des instructions claires pour la detection
3. Stocker le type_projet recu dans le state

NE TOUCHE PAS A Viewer3D (on fera apres validation).

A lancer depuis ~/Desktop/devia :
    python3 add_type_projet_detection.py
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

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_type_projet"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MODIFICATION 1 : Enrichir le prompt systeme avec instructions de detection
# ================================================================

old_prompt_intro = 'const systemPrompt = "Tu es DEVIA, expert charpente bois. Genere un devis professionnel EN FRANCAIS. " +'
new_prompt_intro = '''const systemPrompt = "Tu es DEVIA, expert charpente bois. Genere un devis professionnel EN FRANCAIS. " +
"DETECTION DU TYPE DE PROJET : analyse la description et choisis 1 valeur pour type_projet : " +
"'carport' (si carport, abri voiture, auvent ouvert sans murs, structure sur potaux), " +
"'charpente_trad' (charpente traditionnelle de maison, toit 2 pans avec murs), " +
"'hangar' (hangar agricole, batiment industriel, grand volume couvert), " +
"'abri' (abri jardin, abri petit volume), " +
"'autre' (si rien ne correspond clairement). " +'''

if "DETECTION DU TYPE DE PROJET" in content:
    print("[INFO] Detection type_projet deja presente, skip modification 1")
else:
    if old_prompt_intro not in content:
        print("ERREUR : impossible de trouver le debut du systemPrompt.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_prompt_intro, new_prompt_intro, 1)
    print("[OK] Instructions de detection type_projet ajoutees")

# ================================================================
# MODIFICATION 2 : Ajouter type_projet au JSON demande
# ================================================================

old_json_combles = '\'"essence":"\' + (finalParams.essence || "sapin") + \'","combles":"\' + (finalParams.combles || "perdus") + \'"},\' +'
new_json_combles = '''\'"essence":"\' + (finalParams.essence || "sapin") + \'","combles":"\' + (finalParams.combles || "perdus") + \'",\' +
'"type_projet":"carport_OU_charpente_trad_OU_hangar_OU_abri_OU_autre"},' +'''

if '"type_projet":"' in content:
    print("[INFO] Champ type_projet deja present dans le JSON, skip modification 2")
else:
    if old_json_combles not in content:
        print("ERREUR : impossible de trouver la ligne combles dans le JSON.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_json_combles, new_json_combles, 1)
    print("[OK] Champ type_projet ajoute au JSON demande")

# ================================================================
# MODIFICATION 3 : Stocker type_projet dans le state apres parsing
# ================================================================

# On cherche le bloc "if (parsed.projet) { const p = parsed.projet;"
# et on ajoute un log + un stockage du type_projet juste apres setView3DParams

old_view3d_set = 'setView3DParams({ longueur: p.longueur || 10, largeur: p.largeur || 8, hauteur: p.hauteur || 3, pente: p.pente || 35 });'
new_view3d_set = '''setView3DParams({
        longueur: p.longueur || 10,
        largeur: p.largeur || 8,
        hauteur: p.hauteur || 3,
        pente: p.pente || 35,
        type_projet: p.type_projet || "autre"
      });
      console.log("[DEVIA] Type de projet detecte par l'IA :", p.type_projet || "non specifie");'''

if 'type_projet: p.type_projet' in content:
    print("[INFO] type_projet deja stocke dans view3DParams, skip modification 3")
else:
    if old_view3d_set not in content:
        print("ERREUR : impossible de trouver setView3DParams.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_view3d_set, new_view3d_set, 1)
    print("[OK] type_projet stocke dans view3DParams + log console")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("ETAPE 1.2.A APPLIQUEE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Prompt IA enrichi avec instructions de detection")
print("  2. JSON demande inclut maintenant 'type_projet'")
print("  3. type_projet stocke dans view3DParams + log console")
print()
print("PROCHAINE ETAPE :")
print("  1. Push sur GitHub :")
print("     git add devia.jsx")
print("     git commit -m 'Detection type_projet par IA'")
print("     git push")
print("  2. Attendre redeploiement Vercel (1-2 min)")
print("  3. Aller sur devia-iota.vercel.app")
print("  4. Generer un devis avec : 'Carport simple 6x4m 1 pente 30%'")
print("  5. Ouvrir la console (Cmd+Option+I) et chercher :")
print("     [DEVIA] Type de projet detecte par l'IA : carport")
print()
print(f"BACKUP : {backup_name}")
