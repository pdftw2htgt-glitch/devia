#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA — Fix Unicode corruption
Remplace les caracteres typographiques corrompus par leurs equivalents ASCII
dans tous les fichiers .jsx, .js, .html

A lancer depuis ~/Desktop/devia :
    python3 fix_unicode.py
"""

import os
import sys

# Dictionnaire des remplacements (caractere corrompu -> caractere correct)
REPLACEMENTS = {
    "\u2026": "...",    # … points de suspension -> trois points
    "\u201c": '"',      # " guillemet ouvrant -> guillemet droit
    "\u201d": '"',      # " guillemet fermant -> guillemet droit
    "\u2018": "'",      # ' apostrophe ouvrante -> apostrophe droite
    "\u2019": "'",      # ' apostrophe fermante -> apostrophe droite
    "\u2013": "-",      # – tiret demi-cadratin -> tiret
    "\u2014": "-",      # — tiret cadratin -> tiret
    "\u00a0": " ",      # espace insecable -> espace normal
}

# Extensions a scanner
EXTENSIONS = (".jsx", ".js", ".html", ".json")

# Dossiers a ignorer
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".vercel"}


def fix_file(path):
    """Remplace les caracteres corrompus dans un fichier."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    stats = {}

    for bad, good in REPLACEMENTS.items():
        count = content.count(bad)
        if count > 0:
            content = content.replace(bad, good)
            stats[bad] = count

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return stats
    return None


def walk_and_fix(root="."):
    """Scanne tous les fichiers cibles et les corrige."""
    total_files_fixed = 0
    total_replacements = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # Ignorer les dossiers systeme
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for filename in filenames:
            if filename.endswith(EXTENSIONS):
                filepath = os.path.join(dirpath, filename)
                stats = fix_file(filepath)
                if stats:
                    total_files_fixed += 1
                    rel_path = os.path.relpath(filepath, root)
                    print(f"[FIX] {rel_path}")
                    for bad, count in stats.items():
                        name = {
                            "\u2026": "...(ellipsis)",
                            "\u201c": '"(open quote)',
                            "\u201d": '"(close quote)',
                            "\u2018": "'(open apos)",
                            "\u2019": "'(close apos)",
                            "\u2013": "-(en dash)",
                            "\u2014": "-(em dash)",
                            "\u00a0": "(nbsp)",
                        }.get(bad, bad)
                        print(f"       {count}x remplace: {name}")
                        total_replacements += count

    return total_files_fixed, total_replacements


if __name__ == "__main__":
    if not os.path.exists("package.json"):
        print("ERREUR : package.json introuvable.")
        print("Lance ce script depuis ~/Desktop/devia")
        sys.exit(1)

    print("Scan des fichiers du projet DEVIA...")
    print()

    files_fixed, replacements = walk_and_fix(".")

    print()
    print("=" * 60)
    if files_fixed == 0:
        print("Aucun caractere corrompu trouve. Tout est propre.")
    else:
        print(f"Termine : {files_fixed} fichier(s) corrige(s), "
              f"{replacements} remplacement(s) total")
    print("=" * 60)
