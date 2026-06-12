#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Modif 4 v2 : Ajout EXHAUSTIF des accents
Cible les textes affiches dans toutes les pages (Devis, Projets, Catalogue, Parametres, Compte)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_accents_v2"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# REMPLACEMENTS CIBLES - PHRASES COMPLETES
# Important : on cible des phrases ou expressions COMPLETES pour ne pas casser le code
# ================================================================

replacements = [
    # ============ PAGE DEVIS ============
    ('Decrivez votre projet en langage naturel', 'Décrivez votre projet en langage naturel'),
    ('DEVIA genere un devis professionnel', 'DEVIA génère un devis professionnel'),
    ('et une visualisation 3D.', 'et une visualisation 3D.'),
    ('"Ex: Charpente traditionnelle en sapin pour maison de 10x8m, tuile terre cuite, pente 35 deg, combles amenageables..."', '"Ex: Charpente traditionnelle en sapin pour maison de 10x8m, tuile terre cuite, pente 35°, combles aménageables..."'),
    ('combles amenageables', 'combles aménageables'),
    ('Ville, code postal ou adresse complete', 'Ville, code postal ou adresse complète'),
    ('"Generer le devis"', '"Générer le devis"'),
    ('Generer le devis', 'Générer le devis'),
    ('Cliquez pour ajouter des fichiers', 'Cliquez pour ajouter des fichiers'),  # OK
    ('NOM DU PROJET', 'NOM DU PROJET'),  # OK
    ('DESCRIPTION DU PROJET', 'DESCRIPTION DU PROJET'),  # OK
    ('Devis charpente IA', 'Devis charpente IA'),  # sigle, on garde

    # ============ PAGE PROJETS ============
    ('Retrouvez tous vos devis sauvegardes', 'Retrouvez tous vos devis sauvegardés'),
    ('Mes projets', 'Mes projets'),  # OK
    ('Rechercher un projet', 'Rechercher un projet'),  # OK
    ('Nouveau groupe', 'Nouveau groupe'),  # OK

    # ============ PAGE CATALOGUE ============
    ('Gerez les prix de reference utilises pour vos devis', 'Gérez les prix de référence utilisés pour vos devis'),
    ('"materiaux"', '"matériaux"'),
    ('Marche DEVIA', 'Marché DEVIA'),
    ('Mon catalogue', 'Mon catalogue'),  # OK
    ('Catalogue marche DEVIA', 'Catalogue marché DEVIA'),
    ('Prix moyens du marche francais 2026, mis a jour regulierement par DEVIA', 'Prix moyens du marché français 2026, mis à jour régulièrement par DEVIA'),
    ('Vos prix dans "Mon catalogue" ont la priorite sur ces references', 'Vos prix dans "Mon catalogue" ont la priorité sur ces références'),
    ('priorite sur ces references', 'priorité sur ces références'),
    ('"Arbaletrier', '"Arbalétrier'),
    ('Arbaletrier ', 'Arbalétrier '),
    ('>DESIGNATION<', '>DÉSIGNATION<'),
    ('>DIMENSIONS<', '>DIMENSIONS<'),  # OK pas d'accents
    ('>UNITE<', '>UNITÉ<'),
    ('>PRIX HT<', '>PRIX HT<'),  # OK
    ('epicea', 'épicéa'),
    ('Epicea', 'Épicéa'),
    ('sapin du nord', 'sapin du nord'),  # OK
    ('meleze', 'mélèze'),
    ('Meleze', 'Mélèze'),
    ('"Sabliere ', '"Sablière '),
    ('Sabliere ', 'Sablière '),
    ('"Liteau ', '"Liteau '),
    ('"Volige ', '"Volige '),
    ('faitiere', 'faîtière'),
    ('Faitiere', 'Faîtière'),
    ('"Bac acier', '"Bac acier'),
    ('tole prelaquee', 'tôle prélaquée'),
    ('Ecran sous-toiture', 'Écran sous-toiture'),
    ('"Tuile beton', '"Tuile béton'),
    ('Tuile beton', 'Tuile béton'),
    ('"Tuile terre cuite mecanique', '"Tuile terre cuite mécanique'),
    ('terre cuite mecanique', 'terre cuite mécanique'),
    ('"Closoir ventile', '"Closoir ventilé'),
    ('Closoir ventile', 'Closoir ventilé'),
    ('Gouttiere zinc demi-ronde', 'Gouttière zinc demi-ronde'),
    ('Crochet de gouttiere', 'Crochet de gouttière'),
    ('"Liteau sapin traite', '"Liteau sapin traité'),
    ('Contre-latte', 'Contre-latte'),  # OK
    ('Ardoise fibre-ciment', 'Ardoise fibre-ciment'),  # OK
    ('Apprenti / Aide charpentier', 'Apprenti / Aide charpentier'),  # OK
    ('"taux horaire"', '"taux horaire"'),  # OK
    ('Charpentier confirme', 'Charpentier confirmé'),
    ('Deplacement / Transport', 'Déplacement / Transport'),
    ('forfait chantier', 'forfait chantier'),  # OK
    ('Boulons et tirefonds', 'Boulons et tirefonds'),  # OK
    ('Connecteur metallique', 'Connecteur métallique'),
    ('galvanise', 'galvanisé'),
    ('Etrier ailes inclinees', 'Étrier ailes inclinées'),
    ('"Vis charpente"', '"Vis charpente"'),  # OK
    ('tete fraisee', 'tête fraisée'),
    ('Cheville chimique', 'Cheville chimique'),  # OK
    ('Cheville frapper', 'Cheville frapper'),  # OK
    ('Goujon expansion', 'Goujon expansion'),  # OK
    ('Equerre renforcee', 'Équerre renforcée'),
    ('Equerre simple', 'Équerre simple'),
    ('Tirefond tete hexagonale', 'Tirefond tête hexagonale'),
    ('"Pointe annelee', '"Pointe annelée'),
    ('Pointe annelee', 'Pointe annelée'),
    ('Connecteur faitiere', 'Connecteur faîtière'),
    ('Marteau charpentier', 'Marteau charpentier'),  # OK
    ('"Scie egoine', '"Scie égoïne'),
    ('Scie egoine', 'Scie égoïne'),
    ('Visseuse perceuse', 'Visseuse perceuse'),  # OK
    ('Niveau a bulle', 'Niveau à bulle'),
    ('Metre ruban', 'Mètre ruban'),
    ('Cordeau a tracer', 'Cordeau à tracer'),
    ('Echelle telescopique', 'Échelle télescopique'),
    ('Equerre de charpentier', 'Équerre de charpentier'),
    ('"Burin / Ciseau a bois', '"Burin / Ciseau à bois'),
    ('Ciseau a bois', 'Ciseau à bois'),
    ('Profil de finition aluminium', 'Profil de finition aluminium'),  # OK
    ('Tasseaux fixation bardage', 'Tasseaux fixation bardage'),  # OK
    ('Bardage douglas autoclave', 'Bardage douglas autoclave'),  # OK
    ('Bardage epicea naturel', 'Bardage épicéa naturel'),
    ('Poteau bois lamelle-colle GL24h', 'Poteau bois lamellé-collé GL24h'),
    ('"Lamelle-colle GL24h"', '"Lamellé-collé GL24h"'),
    ('lamelle-colle', 'lamellé-collé'),
    ('Lamelle-colle', 'Lamellé-collé'),

    # ============ PAGE PARAMETRES ============
    ('Choisissez le theme de l\'application', 'Choisissez le thème de l\'application'),
    ('Noir profond, accents dores', 'Noir profond, accents dorés'),
    ('Blanc pur, design epure', 'Blanc pur, design épuré'),
    ('Configurez votre entreprise et vos tarifs par defaut', 'Configurez votre entreprise et vos tarifs par défaut'),
    ('Ces informations apparaitront sur vos devis', 'Ces informations apparaîtront sur vos devis'),
    ('"Apparence"', '"Apparence"'),  # OK
    ('Informations entreprise', 'Informations entreprise'),  # OK
    ('NOM DE L\'ENTREPRISE', 'NOM DE L\'ENTREPRISE'),  # OK
    ('"SIRET"', '"SIRET"'),  # OK
    ('ADRESSE', 'ADRESSE'),  # OK

    # ============ PAGE COMPTE ============
    ('Apercu de votre activite DEVIA', 'Aperçu de votre activité DEVIA'),
    ('Mon compte', 'Mon compte'),  # OK
    ('Mon entreprise', 'Mon entreprise'),  # OK
    ('Plan actuel et offres a venir', 'Plan actuel et offres à venir'),
    ('Cliquez pour deplier', 'Cliquez pour déplier'),
    ('Devis de charpente assistes par intelligence artificielle', 'Devis de charpente assistés par intelligence artificielle'),
    ('"DEVIA Menuiserie"', '"DEVIA Menuiserie"'),  # OK
    ('"DEVIA Maconnerie"', '"DEVIA Maçonnerie"'),
    ('"Maconnerie"', '"Maçonnerie"'),
    ('Coming soon', 'Coming soon'),  # OK
    ('"Bientot disponible"', '"Bientôt disponible"'),
    ('Bientot disponible', 'Bientôt disponible'),
    ('"PLAN ACTUEL"', '"PLAN ACTUEL"'),  # OK
    ('"PLAN PRO"', '"PLAN PRO"'),  # OK
    ('Votre abonnement', 'Votre abonnement'),  # OK

    # ============ STATS COMPTE ============
    ('DEVIS CE MOIS', 'DEVIS CE MOIS'),  # OK
    ('TOTAL DEVIS', 'TOTAL DEVIS'),  # OK
    ('JOURS ABO', 'JOURS ABO'),  # OK
    ('TOKENS IA', 'TOKENS IA'),  # OK
    ('EMPREINTE CO2', 'EMPREINTE CO₂'),

    # ============ MODALE AJOUT MATERIAU (deja partiellement traite) ============
    ('"Type detecte', '"Type détecté'),
    ('Type detecte :', 'Type détecté :'),
    ('"Detection', '"Détection'),
    ('Detection', 'Détection'),
    ('Changer le type', 'Changer le type'),  # OK
    ('"Outillage"', '"Outillage"'),  # OK
    ('"Visserie / fixations"', '"Visserie / fixations"'),  # OK
    ('"Bois structure"', '"Bois structure"'),  # OK
    ('"Bois ossature"', '"Bois ossature"'),  # OK
    ('"Couverture"', '"Couverture"'),  # OK
    ('"Isolation"', '"Isolation"'),  # OK
    ('"Quincaillerie"', '"Quincaillerie"'),  # OK
    ('"EPI / Securite"', '"EPI / Sécurité"'),

    # ============ POP-UP CHARGEMENT (creé recemment) ============
    ('Generation en cours', 'Génération en cours'),
    ('DEVIA prepare votre devis', 'DEVIA prépare votre devis'),
    ('Analyse de la demande', 'Analyse de la demande'),  # OK
    ('Calcul de la zone climatique', 'Calcul de la zone climatique'),  # OK
    ('Generation du modele 3D', 'Génération du modèle 3D'),
    ('Creation du devis IA', 'Création du devis IA'),
    ('"Finalisation"', '"Finalisation"'),  # OK
    ('Cela peut prendre quelques secondes', 'Cela peut prendre quelques secondes'),  # OK
    ('"EN COURS"', '"EN COURS"'),  # OK
    ('"Progression"', '"Progression"'),  # OK

    # ============ AUTRES TEXTES COURANTS ============
    ('"Ajouter a un groupe"', '"Ajouter à un groupe"'),
    ('"+ Ajouter a un groupe"', '"+ Ajouter à un groupe"'),
    ('Ajouter a un groupe', 'Ajouter à un groupe'),
    ('Modifier un materiau', 'Modifier un matériau'),
    ('Ajouter un materiau', 'Ajouter un matériau'),
    ('"Ajouter un materiau"', '"Ajouter un matériau"'),
    ('Mettez a jour les informations', 'Mettez à jour les informations'),
    ('Ajoutez un prix a votre catalogue personnel', 'Ajoutez un prix à votre catalogue personnel'),
    ('un prix a votre catalogue', 'un prix à votre catalogue'),
    ('"Annuler"', '"Annuler"'),  # OK
    ('"Enregistrer"', '"Enregistrer"'),  # OK
    ('"Sauvegarder"', '"Sauvegarder"'),  # OK
    ('"Supprimer"', '"Supprimer"'),  # OK
    ('"Renommer"', '"Renommer"'),  # OK

    # ============ ALTITUDE / LOCALISATION ============
    ('"Altitude (m)"', '"Altitude (m)"'),  # OK
    ('"Localisation"', '"Localisation"'),  # OK
    ('"Documents"', '"Documents"'),  # OK
    ('"DOCUMENTS"', '"DOCUMENTS"'),  # OK
    ('(max 5)', '(max 5)'),  # OK

    # ============ TYPE TRAVAUX ============
    ('TYPE DE TRAVAUX', 'TYPE DE TRAVAUX'),  # OK
    ('"Construction neuve"', '"Construction neuve"'),  # OK
    ('"Renovation"', '"Rénovation"'),
    ('Renovation', 'Rénovation'),
    ('"Neuf"', '"Neuf"'),  # OK

    # ============ MOTS GENERAUX COURANTS ============
    ('"Resume du devis"', '"Résumé du devis"'),
    ('Resume du devis', 'Résumé du devis'),
    ('"Tarification', '"Tarification'),
    ('"Taux horaire facture', '"Taux horaire facturé'),
    ('"Taux horaire (\u20ac/h)"', '"Taux horaire (€/h)"'),  # OK
    ('"TVA (%)"', '"TVA (%)"'),  # OK
    ('"Marge (%)"', '"Marge (%)"'),  # OK
    ('"Sauvegarde', '"Sauvegardé'),
    ('"sauvegarde"', '"sauvegardé"'),
    ('Sauvegarde', 'Sauvegardé'),
    ('"Deconnexion"', '"Déconnexion"'),
    ('Deconnexion', 'Déconnexion'),
    ('Se deconnecter', 'Se déconnecter'),
    ('"Generer un PDF"', '"Générer un PDF"'),
    ('Generer un PDF', 'Générer un PDF'),
    ('"Telecharger"', '"Télécharger"'),
    ('Telecharger', 'Télécharger'),
    ('"Imprimer"', '"Imprimer"'),  # OK
    ('"Modifier"', '"Modifier"'),  # OK
    ('cree avec succes', 'créé avec succès'),
    ('"cree"', '"créé"'),
    ('Cree le', 'Créé le'),
    ('"cree par"', '"créé par"'),
    ('Erreur lors de', 'Erreur lors de'),  # OK
    ('"Bardage"', '"Bardage"'),  # OK
    ('"Charpente"', '"Charpente"'),  # OK
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
print("TOP 15 PATTERNS REMPLACES :")
for old, nb in sorted(modifs_per_pattern.items(), key=lambda x: -x[1])[:15]:
    display = old[:55] + "..." if len(old) > 55 else old
    print(f"  {nb}x : {display}")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
