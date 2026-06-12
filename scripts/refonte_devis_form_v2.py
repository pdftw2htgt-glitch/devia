#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 2.A FIX : Refonte formulaire Devis (version corrigee)
Difference vs version precedente :
- Ne touche PAS au {error} (on garde la structure existante exactement)
- Refait uniquement les parties qu'on est SUR de pas casser
- Test syntaxe avec esbuild a la fin (si dispo localement)

A lancer depuis ~/Desktop/devia :
    python3 refonte_devis_form_v2.py
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

if not os.path.exists("package.json"):
    print("ERREUR : package.json introuvable. Lance depuis ~/Desktop/devia")
    sys.exit(1)

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_devis_form_v2"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MODIFICATION 1 : Hero (texte de presentation au-dessus du formulaire)
# Plus simple : juste ce bloc, sans toucher au reste
# ================================================================

old_hero = '''<div style={{ textAlign: "center", marginBottom: 32 }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>🏗️</div>
              <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>Generez votre devis charpente</h1>
              <p style={{ color: "#545870", fontSize: 15 }}>Decrivez votre projet - DEVIA genere un devis professionnel et une visualisation 3D</p>
            </div>'''

new_hero = '''<div style={{ textAlign: "center", marginBottom: 40, paddingTop: 16 }}>
              <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 12, letterSpacing: "-0.02em", lineHeight: 1.1 }}>
                Generez votre devis <span style={{ background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>charpente</span>
              </h1>
              <p style={{ color: "#7a7d92", fontSize: 15, maxWidth: 520, margin: "0 auto", lineHeight: 1.55 }}>
                Decrivez votre projet en langage naturel. DEVIA genere un devis professionnel et une visualisation 3D.
              </p>
            </div>'''

if "WebkitBackgroundClip" in content:
    print("[INFO] Hero deja refondu, skip")
else:
    if old_hero not in content:
        print("ERREUR : impossible de trouver le hero actuel.")
        print("Aucune modification appliquee, fichier intact.")
        sys.exit(1)
    content = content.replace(old_hero, new_hero, 1)
    print("[OK] Hero refondu (typo, gradient sur 'charpente')")

# ================================================================
# MODIFICATION 2 : Labels (description / commune / altitude)
# On change juste les styles des labels, pas la structure
# ================================================================

# Label Description
old_label_desc = '<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Description du projet</label>'
new_label_desc = '<label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Description du projet</label>'

if new_label_desc in content:
    print("[INFO] Label Description deja refondu, skip")
elif old_label_desc in content:
    content = content.replace(old_label_desc, new_label_desc, 1)
    print("[OK] Label 'Description du projet' style uppercase")
else:
    print("[WARN] Label Description non trouve, skip")

# Label Commune
old_label_commune = '<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Commune</label>'
new_label_commune = '<label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Commune</label>'

if new_label_commune in content:
    print("[INFO] Label Commune deja refondu, skip")
elif old_label_commune in content:
    content = content.replace(old_label_commune, new_label_commune, 1)
    print("[OK] Label 'Commune' style uppercase")
else:
    print("[WARN] Label Commune non trouve, skip")

# Label Altitude
old_label_alt = '<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Altitude (m)</label>'
new_label_alt = '<label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Altitude <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>(m)</span></label>'

if new_label_alt in content:
    print("[INFO] Label Altitude deja refondu, skip")
elif old_label_alt in content:
    content = content.replace(old_label_alt, new_label_alt, 1)
    print("[OK] Label 'Altitude (m)' style uppercase")
else:
    print("[WARN] Label Altitude non trouve, skip")

# Label Documents
old_label_doc = '<label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Documents - max 5</label>'
new_label_doc = '<label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Documents <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>(max 5)</span></label>'

if new_label_doc in content:
    print("[INFO] Label Documents deja refondu, skip")
elif old_label_doc in content:
    content = content.replace(old_label_doc, new_label_doc, 1)
    print("[OK] Label 'Documents' style uppercase")
else:
    print("[WARN] Label Documents non trouve, skip")

# ================================================================
# MODIFICATION 3 : Zone upload - juste le style du div
# ================================================================

old_upload_div = '''<div onClick={() => fileInputRef.current && fileInputRef.current.click()}
                  style={{ border: "2px dashed #1e2231", borderRadius: 8, padding: 20, textAlign: "center", cursor: "pointer", color: "#545870" }}>'''

new_upload_div = '''<div onClick={() => fileInputRef.current && fileInputRef.current.click()}
                  style={{ border: "1.5px dashed rgba(255,255,255,0.12)", background: "rgba(255,255,255,0.02)", borderRadius: 12, padding: 24, textAlign: "center", cursor: "pointer", color: "#7a7d92", transition: "all 0.15s" }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(240,192,64,0.3)"; e.currentTarget.style.background = "rgba(240,192,64,0.03)"; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.12)"; e.currentTarget.style.background = "rgba(255,255,255,0.02)"; }}>'''

if "onMouseEnter={(e) => { e.currentTarget.style.borderColor" in content and "rgba(240,192,64,0.3)" in content:
    print("[INFO] Zone upload deja refondue, skip")
elif old_upload_div in content:
    content = content.replace(old_upload_div, new_upload_div, 1)
    print("[OK] Zone upload : bordure plus fine + hover jaune subtil")
else:
    print("[WARN] Zone upload non trouvee, skip")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

# ================================================================
# TEST SYNTAXE avec esbuild
# ================================================================

print()
print("TEST SYNTAXE...")
try:
    result = subprocess.run(
        ["npx", "esbuild", "devia.jsx", "--loader=jsx", "--bundle=false"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        print("[OK] Syntaxe JSX valide")
    else:
        print("ERREUR SYNTAXE detectee :")
        print(result.stderr[:2000])
        print()
        print("RESTORE AUTO DU BACKUP...")
        shutil.copy(backup_name, "devia.jsx")
        print(f"[OK] devia.jsx restaure depuis : {backup_name}")
        sys.exit(1)
except FileNotFoundError:
    print("[INFO] esbuild non dispo localement, test syntaxe skip")
except subprocess.TimeoutExpired:
    print("[INFO] esbuild trop lent, test syntaxe skip")

print()
print("=" * 60)
print("SESSION 2.A FIX APPLIQUEE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Hero : titre plus grand, gradient jaune sur 'charpente', sans emoji")
print("  2. Labels (Description, Commune, Altitude, Documents) :")
print("     - MAJUSCULES en lettres serrees (style Linear/Stripe)")
print("     - Couleur plus subtile")
print("  3. Zone upload :")
print("     - Bordure plus fine et discrete")
print("     - Hover : bord jaune subtil + fond jaune transparent")
print()
print("CE QUI N'A PAS CHANGE :")
print("  - Badges climatiques (Neige/Vent/Sismique) : intactes")
print("  - Erreurs : intactes")
print("  - Tout le reste : intact")
print()
print("PROCHAINE ETAPE :")
print("  npm run build  # TESTER EN LOCAL D'ABORD")
print()
print("Si OK :")
print("  git add devia.jsx")
print("  git commit -m 'Refonte design Session 2.A v2 - Formulaire Devis'")
print("  git push")
print()
print(f"BACKUP : {backup_name}")
