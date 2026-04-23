#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA — Micro-etape 2.1
Setup du client Supabase + fichier .env.local (vide, a remplir par toi)

Ce script :
  1. Cree le dossier src/lib/
  2. Cree src/lib/supabase.js (le client Supabase)
  3. Cree .env.local (vide, tu y colles tes cles)
  4. Cree .env.example (template sans secrets, safe pour GitHub)
  5. Met a jour .gitignore pour ne JAMAIS commit les secrets

A lancer depuis le dossier ~/Desktop/devia :
    python3 setup_supabase.py
"""

import os
import sys

# --- Verifications prealables ---
if not os.path.exists("package.json"):
    print("ERREUR : package.json introuvable.")
    print("Tu dois lancer ce script depuis ~/Desktop/devia")
    sys.exit(1)

print("Demarrage du setup Supabase pour DEVIA...")
print()

# --- 1. Creer src/lib/ ---
os.makedirs("src/lib", exist_ok=True)
print("[OK] Dossier src/lib/ cree")

# --- 2. Creer src/lib/supabase.js ---
supabase_client = '''// src/lib/supabase.js
// Client Supabase partage par toute l'application DEVIA
// Utilise les variables d'environnement (jamais de cles en dur dans le code)

import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    "Variables d'environnement Supabase manquantes. Verifie ton fichier .env.local"
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
'''

with open("src/lib/supabase.js", "w", encoding="utf-8") as f:
    f.write(supabase_client)
print("[OK] src/lib/supabase.js cree")

# --- 3. Creer .env.local (tu y mets tes cles) ---
env_local = '''# .env.local
# FICHIER SECRET — NE JAMAIS COMMIT SUR GITHUB
# Remplace les valeurs ci-dessous par celles de ton projet Supabase
# (Project Settings > API dans le dashboard Supabase)

VITE_SUPABASE_URL=REMPLACE_PAR_TON_PROJECT_URL
VITE_SUPABASE_ANON_KEY=REMPLACE_PAR_TON_ANON_KEY
'''

# On ne l'ecrase pas s'il existe deja (au cas ou)
if os.path.exists(".env.local"):
    print("[SKIP] .env.local existe deja, non ecrase")
else:
    with open(".env.local", "w", encoding="utf-8") as f:
        f.write(env_local)
    print("[OK] .env.local cree (a remplir avec tes cles)")

# --- 4. Creer .env.example (template safe pour GitHub) ---
env_example = '''# .env.example
# Template des variables d'environnement requises
# Ce fichier est commit sur GitHub pour documenter la config
# NE PAS mettre de vraies cles ici

VITE_SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOi...
'''

with open(".env.example", "w", encoding="utf-8") as f:
    f.write(env_example)
print("[OK] .env.example cree")

# --- 5. Mettre a jour .gitignore ---
gitignore_entries = [
    "# Dependances",
    "node_modules/",
    "",
    "# Build",
    "dist/",
    "build/",
    "",
    "# Secrets — NE JAMAIS COMMIT",
    ".env.local",
    ".env.*.local",
    "",
    "# OS",
    ".DS_Store",
    "",
    "# Logs",
    "*.log",
    "npm-debug.log*",
    "",
    "# Editeur",
    ".vscode/",
    ".idea/",
]

new_gitignore_content = "\n".join(gitignore_entries) + "\n"

if os.path.exists(".gitignore"):
    with open(".gitignore", "r", encoding="utf-8") as f:
        existing = f.read()
    # On verifie juste que .env.local y est bien
    if ".env.local" not in existing:
        with open(".gitignore", "a", encoding="utf-8") as f:
            f.write("\n# Ajoute par setup_supabase.py\n.env.local\n.env.*.local\n")
        print("[OK] .gitignore mis a jour (ajout des regles .env.local)")
    else:
        print("[SKIP] .gitignore contient deja .env.local")
else:
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(new_gitignore_content)
    print("[OK] .gitignore cree")

print()
print("=" * 60)
print("Setup Supabase termine avec succes !")
print("=" * 60)
print()
print("PROCHAINES ETAPES A FAIRE MANUELLEMENT :")
print()
print("1. Installer la dependance Supabase :")
print("   npm install @supabase/supabase-js")
print()
print("2. Ouvrir .env.local dans un editeur et remplacer les valeurs :")
print("   nano .env.local")
print("   (ou ouvre-le dans VS Code)")
print()
print("3. Verifier que .env.local est bien ignore par git :")
print("   git status")
print("   (tu dois voir .env.example mais PAS .env.local)")
print()
