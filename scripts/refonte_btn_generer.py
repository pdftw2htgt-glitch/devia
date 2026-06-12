#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 2.B.1 : Bouton 'Generer le devis' refondu
Modifie UNIQUEMENT le bouton Generer (et son etat loading).

A lancer depuis ~/Desktop/devia :
    python3 refonte_btn_generer.py

Apres : npm run build (pour tester la syntaxe)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_btn_generer"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD 1 : Style du bouton (style + texte/icone)
# ================================================================

old_btn = '''<button onClick={handleSubmit} disabled={loading || !prompt.trim() || !commune.trim()}
                style={{ ...btnPrimary, width: "100%", padding: 14, fontSize: 15, opacity: loading || !prompt.trim() || !commune.trim() ? 0.5 : 1, cursor: loading || !prompt.trim() || !commune.trim() ? "not-allowed" : "pointer" }}>
                {loading ? "⏳ Analyse en cours..." : "Generer le devis"}
              </button>'''

new_btn = '''<button onClick={handleSubmit} disabled={loading || !prompt.trim() || !commune.trim()}
                style={{
                  ...btnPrimary,
                  width: "100%",
                  padding: "16px 24px",
                  fontSize: 15,
                  fontWeight: 700,
                  letterSpacing: "0.01em",
                  marginTop: 8,
                  opacity: loading || !prompt.trim() || !commune.trim() ? 0.45 : 1,
                  cursor: loading || !prompt.trim() || !commune.trim() ? "not-allowed" : "pointer",
                  boxShadow: loading || !prompt.trim() || !commune.trim() ? "none" : "0 8px 24px rgba(240, 192, 64, 0.28), 0 2px 6px rgba(240, 192, 64, 0.15)",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 10
                }}
                onMouseEnter={(e) => { if (!loading && prompt.trim() && commune.trim()) { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 12px 32px rgba(240, 192, 64, 0.35), 0 4px 8px rgba(240, 192, 64, 0.2)"; } }}
                onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = loading || !prompt.trim() || !commune.trim() ? "none" : "0 8px 24px rgba(240, 192, 64, 0.28), 0 2px 6px rgba(240, 192, 64, 0.15)"; }}>
                {loading ? (
                  <>
                    <span style={{ display: "inline-block", width: 14, height: 14, border: "2px solid rgba(10,10,10,0.25)", borderTopColor: "#0a0a0a", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                    <span>Analyse en cours...</span>
                  </>
                ) : (
                  <>
                    <span>Generer le devis</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M5 12h14M13 5l7 7-7 7"/>
                    </svg>
                  </>
                )}
              </button>'''

if "translateY(-1px)" in content and "borderTopColor:" in content:
    print("[INFO] Bouton Generer deja refondu")
elif old_btn in content:
    content = content.replace(old_btn, new_btn, 1)
    print("[OK] Bouton 'Generer le devis' refondu")
else:
    print("[ERREUR] Bouton Generer non trouve exactement.")
    print("Aucune modification appliquee.")
    sys.exit(1)

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 2.B.1 APPLIQUEE - Bouton Generer")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Bouton plus haut (16px padding au lieu de 14)")
print("  2. Ombre jaune douce qui s'amplifie au hover")
print("  3. Leger lift (-1px) au hover (effet flottant)")
print("  4. Spinner moderne pendant le chargement (au lieu de l'emoji)")
print("  5. Fleche -> apres 'Generer le devis' (icone SVG)")
print()
print("PROCHAINE ETAPE :")
print("  npm run build  # TESTER EN LOCAL")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Refonte bouton Generer'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
