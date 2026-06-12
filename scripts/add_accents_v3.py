#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Modif 4 v3 : Derniers residus d'accents
Cible les textes qui n'ont pas ete pris par v2 (souvent du contenu dynamique
ou concatene)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_accents_v3"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# RESIDUS A CORRIGER
# ================================================================

replacements = [
    # === PAGE CATALOGUE ===
    ('Gerez les prix de reference', 'Gérez les prix de référence'),
    ('reference utilises', 'référence utilisés'),
    (' materiaux<', ' matériaux<'),
    ('{nbMateriaux} materiaux', '{nbMateriaux} matériaux'),
    ('Arbaletrier', 'Arbalétrier'),
    ('arbaletrier', 'arbalétrier'),
    ('"UNITE"', '"UNITÉ"'),
    ('>UNITE<', '>UNITÉ<'),
    ('UNITE</', 'UNITÉ</'),
    ('DESIGNATION</', 'DÉSIGNATION</'),

    # === PAGE PARAMETRES ===
    ('Choisissez le theme', 'Choisissez le thème'),
    ('theme de l\'application', 'thème de l\'application'),
    ('accents dores', 'accents dorés'),
    ('Noir profond, accents dores', 'Noir profond, accents dorés'),
    ('design epure', 'design épuré'),
    ('Blanc pur, design epure', 'Blanc pur, design épuré'),
    ('configurez votre entreprise', 'configurez votre entreprise'),
    ('vos tarifs par defaut', 'vos tarifs par défaut'),
    ('Ces informations apparaitront', 'Ces informations apparaîtront'),

    # === PAGE COMPTE ===
    ('Apercu de votre activite', 'Aperçu de votre activité'),
    ('activite DEVIA', 'activité DEVIA'),
    ('"Apercu', '"Aperçu'),
    ('Apercu', 'Aperçu'),
    ('Cliquez pour deplier', 'Cliquez pour déplier'),
    ('Plan actuel et offres a venir', 'Plan actuel et offres à venir'),
    ('offres a venir', 'offres à venir'),
    ('Devis de charpente assistes', 'Devis de charpente assistés'),
    ('charpente assistes', 'charpente assistés'),

    # === PARAMETRES TEXTES INTERNES ===
    ('Configurez votre entreprise et vos tarifs par defaut', 'Configurez votre entreprise et vos tarifs par défaut'),
    ('"Parametres"', '"Paramètres"'),
    ('>Parametres<', '>Paramètres<'),
    ('Parametres<', 'Paramètres<'),

    # === DIVERS PETITS ===
    ('charpenteee', 'charpente'),  # au cas où il y aurait des erreurs
    ('"Charpente"', '"Charpente"'),  # OK
    ('"Bardage"', '"Bardage"'),  # OK
    ('"Maconnerie"', '"Maçonnerie"'),
    ('Maconnerie', 'Maçonnerie'),
    ('"Outillage"', '"Outillage"'),  # OK

    # === CATALOGUE INFO BOX ===
    ('mis a jour regulierement', 'mis à jour régulièrement'),
    ('regulierement par DEVIA', 'régulièrement par DEVIA'),
    ('priorite sur ces references', 'priorité sur ces références'),
    ('priorite sur ces', 'priorité sur ces'),
    ('ces references', 'ces références'),

    # === DEVIS / FORM ===
    ('Decrivez votre projet', 'Décrivez votre projet'),
    ('DEVIA genere', 'DEVIA génère'),
    ('un devis professionnel', 'un devis professionnel'),  # OK

    # === SIMPLES MOTS SUR LESQUELS ON A PEUT-ETRE LOUPE ===
    ('"Reference', '"Référence'),
    ('"reference', '"référence'),
    ('"reference"', '"référence"'),
    ('reference"', 'référence"'),
    ('references<', 'références<'),
    ('utilises<', 'utilisés<'),
    ('utilises ', 'utilisés '),
    ('Materiaux', 'Matériaux'),
    ('materiaux<', 'matériaux<'),
    ('"materiaux"', '"matériaux"'),
    ('">matériaux<', '">matériaux<'),  # OK

    # === BADGES / STATS ===
    ('"EMPREINTE CO2"', '"EMPREINTE CO₂"'),  # CO2 -> CO₂
    ('EMPREINTE CO2<', 'EMPREINTE CO₂<'),
]

modifs = 0
modifs_per_pattern = {}

for old, new in replacements:
    if old != new and old in content:
        nb = content.count(old)
        content = content.replace(old, new)
        modifs += nb
        if nb > 0:
            modifs_per_pattern[old] = nb

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} REMPLACEMENTS COMPLEMENTAIRES EFFECTUES")
print("=" * 60)
print()
if modifs > 0:
    print("PATTERNS REMPLACES :")
    for old, nb in sorted(modifs_per_pattern.items(), key=lambda x: -x[1]):
        display = old[:55] + "..." if len(old) > 55 else old
        print(f"  {nb}x : {display}")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
