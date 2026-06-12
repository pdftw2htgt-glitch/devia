#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Modif 4 : Ajout des accents sur les textes affiches
ATTENTION : on ne touche QUE aux chaines de caracteres affichees (entre " ou >),
PAS aux noms de variables/fonctions/cles BDD.
"""

import os
import sys
import shutil
import re
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_accents"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# REMPLACEMENTS CIBLES (contexte explicite pour eviter les variables)
# Format : (old, new, description)
# On cible des phrases COMPLETES pour ne JAMAIS toucher au code
# ================================================================

replacements = [
    # === LABELS DE FORMULAIRES (uppercased dans le code) ===
    ('>Categorie <', '>Catégorie <'),
    ('>Designation <', '>Désignation <'),
    ('>Parametres ', '>Paramètres '),
    ('>Parametres<', '>Paramètres<'),
    ('Mes parametres', 'Mes paramètres'),
    ('Vos parametres', 'Vos paramètres'),
    ('label: "Parametres"', 'label: "Paramètres"'),
    ('>Detection ', '>Détection '),
    ('>Materiau<', '>Matériau<'),
    ('>Materiaux<', '>Matériaux<'),

    # === PLACEHOLDERS et TEXTES ===
    ('Generer le devis', 'Générer le devis'),
    ('Generer un devis', 'Générer un devis'),
    ('"Generer"', '"Générer"'),
    ('Generation en cours', 'Génération en cours'),
    ('"Generation', '"Génération'),
    ('Generation du', 'Génération du'),
    ('Generation du modele 3D', 'Génération du modèle 3D'),
    ('Generation d\'un', 'Génération d\'un'),
    ('Ajouter un materiau', 'Ajouter un matériau'),
    ('Modifier un materiau', 'Modifier un matériau'),

    # === MATERIAUX/MATERIAU dans les textes affiches ===
    ('"Aucun materiau ', '"Aucun matériau '),
    ('un materiau', 'un matériau'),
    ('le materiau', 'le matériau'),
    ('Le materiau', 'Le matériau'),
    ('des materiaux', 'des matériaux'),
    ('Les materiaux', 'Les matériaux'),
    ('vos materiaux', 'vos matériaux'),
    ('Mes materiaux', 'Mes matériaux'),
    ('catalogue materiaux', 'catalogue matériaux'),

    # === DETECTION / DETECTE ===
    ('"Type detecte', '"Type détecté'),
    ('Type detecte :', 'Type détecté :'),
    ('Type detecte:', 'Type détecté:'),
    ('"Detection', '"Détection'),
    (' detecte ', ' détecté '),
    (' detecte"', ' détecté"'),
    ('detecte automatiquement', 'détecté automatiquement'),

    # === CREE / CREES ===
    ('"cree', '"créé'),
    (' cree ', ' créé '),
    (' cree\n', ' créé\n'),
    ('Devis cree', 'Devis créé'),
    ('Projet cree', 'Projet créé'),
    ('Compte cree', 'Compte créé'),
    ('a ete cree', 'a été créé'),

    # === DEJA ===
    ('deja existant', 'déjà existant'),
    ('deja inclus', 'déjà inclus'),
    ('"deja', '"déjà'),
    (' deja ', ' déjà '),

    # === REFERENCE ===
    ('"Reference', '"Référence'),
    (' reference ', ' référence '),

    # === COMPLETE ===
    ('Completer avec', 'Compléter avec'),
    ('completer avec', 'compléter avec'),
    ('"Complete', '"Complété'),
    ('Devis complete', 'Devis complété'),
    ('"complete par', '"complété par'),

    # === METRE ===
    ('metre lineaire', 'mètre linéaire'),
    ('metre carre', 'mètre carré'),
    ('metre cube', 'mètre cube'),
    ('au metre', 'au mètre'),

    # === SECURITE ===
    ('"securite', '"sécurité'),
    (' securite ', ' sécurité '),
    ('EPI / Securite', 'EPI / Sécurité'),

    # === AUTRES MOTS COURANTS DEVIA ===
    ('charpenterie', 'charpenterie'),  # deja correct
    ('"Charpenterie"', '"Charpenterie"'),  # deja correct
    ('"Generee', '"Générée'),
    ('"Genere', '"Généré'),
    ('Reglages', 'Réglages'),
    ('estimee', 'estimée'),
    ('estimees', 'estimées'),
    ('estime', 'estimé'),
    ('Numero', 'Numéro'),
    ('numero', 'numéro'),
    ('Apercu', 'Aperçu'),
    ('apercu', 'aperçu'),
    ('verifie', 'vérifié'),
    ('Verifier', 'Vérifier'),
    ('Verifie', 'Vérifié'),
    ('verifier', 'vérifier'),
    ('Telecharger', 'Télécharger'),
    ('telecharger', 'télécharger'),
    ('Telechargement', 'Téléchargement'),
    ('Modele 3D', 'Modèle 3D'),
    ('"modele 3D', '"modèle 3D'),

    # === MOTS COURTS SOUVENT UTILISES ===
    (' a la ', ' à la '),
    (' a un ', ' à un '),
    (' a une ', ' à une '),
    (' a votre ', ' à votre '),
    (' a vos ', ' à vos '),
    (' a tous', ' à tous'),
    (' a ce ', ' à ce '),
    (' a cette ', ' à cette '),
    (' a partir ', ' à partir '),
]

modifs = 0
modifs_per_pattern = {}

for old, new in replacements:
    if old in content:
        nb = content.count(old)
        content = content.replace(old, new)
        modifs += nb
        modifs_per_pattern[old] = nb

# ================================================================
# AFFICHAGE
# ================================================================

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} REMPLACEMENTS EFFECTUES")
print("=" * 60)
print()
print("DETAILS PAR PATTERN :")
for old, nb in sorted(modifs_per_pattern.items(), key=lambda x: -x[1]):
    print(f"  {nb}x : '{old[:50]}...' " if len(old) > 50 else f"  {nb}x : '{old}'")
print()
print("CE QUI N'A PAS ETE TOUCHE :")
print("  - Noms de variables (detectedType, categorieAutre, etc.)")
print("  - Cles BDD (categorie:, designation:, etc.)")
print("  - Valeurs de selects (value='Materiau' reste tel quel)")
print("  - Comments")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
