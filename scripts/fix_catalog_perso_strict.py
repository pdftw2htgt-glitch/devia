#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix bug catalogue perso strict (option B - Limite)
Modifie devia.jsx pour :
1. Quand 'Mon catalogue' est choisi SANS 'Completer avec marche' :
   - L'IA ne genere QUE les materiaux qui sont dans le catalogue perso
   - Pas d'invention de prix
2. Bandeau orange en haut du devis quand mode "perso strict"
3. Note explicite dans les notes du devis

A lancer depuis ~/Desktop/devia :
    python3 fix_catalog_perso_strict.py
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

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_perso_strict"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MODIFICATION 1 : Renforcer le prompt selon le mode catalog
# ================================================================

old_rules = '''"REGLES PRIX : 1) Pour chaque poste de devis, utilise EN PRIORITE un materiau du catalogue ci-dessus si disponible. " +
"2) Le prix unitaire HT doit correspondre exactement au prix du catalogue. " +
"3) Si un materiau necessaire n'existe pas dans le catalogue, estime le prix au mieux mais signale-le dans les notes. " +
"4) Adapte les quantites au projet decrit. " +'''

new_rules = '''(catalogSource === "perso" ?
  // MODE STRICT : que le catalogue perso, pas d'invention
  "REGLES PRIX (MODE STRICT - CATALOGUE PERSO UNIQUEMENT) : " +
  "1) INTERDICTION ABSOLUE d'inventer un prix ou de creer un poste pour un materiau qui n'est PAS dans le catalogue ci-dessus. " +
  "2) Tu DOIS uniquement creer des postes correspondant aux materiaux LISTES dans le catalogue. " +
  "3) Le prix unitaire HT doit correspondre EXACTEMENT au prix du catalogue. " +
  "4) Si tu n'as pas assez de materiaux pour faire un devis complet (par exemple, pas de tuiles, pas de fixations), ne genere QUE les postes pour lesquels tu as un materiau dans le catalogue. " +
  "5) Le devis sera donc PARTIEL. C'est ok et voulu. " +
  "6) Adapte les quantites au projet decrit. " +
  "7) Dans le tableau 'notes' du JSON, AJOUTE en premiere note : 'Devis partiel : seuls les materiaux de votre catalogue sont inclus. Les postes manquants doivent etre completes manuellement ou en activant l option Completer avec marche.' " +
  "8) Genere entre 3 et 8 postes (selon le nombre de materiaux disponibles). "
  :
  // MODE NORMAL : avec complement marche
  "REGLES PRIX : 1) Pour chaque poste de devis, utilise EN PRIORITE un materiau du catalogue ci-dessus si disponible. " +
  "2) Le prix unitaire HT doit correspondre exactement au prix du catalogue. " +
  "3) Si un materiau necessaire n'existe pas dans le catalogue, estime le prix au mieux mais signale-le dans les notes. " +
  "4) Adapte les quantites au projet decrit. "
) +'''

if "INTERDICTION ABSOLUE" in content:
    print("[INFO] Regles strictes deja presentes, skip modification 1")
else:
    if old_rules not in content:
        print("ERREUR : impossible de trouver les regles prix.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_rules, new_rules, 1)
    print("[OK] Regles prix adaptees selon le mode catalog")

# ================================================================
# MODIFICATION 2 : Ajouter le bandeau orange dans le devis si mode perso strict
# On l'ajoute juste apres le header avec le titre du devis
# ================================================================

# On cherche la fin du div header avec le badge catalogSource
# pour ajouter le bandeau juste apres
old_header_close = '''                    </span>
                  )}
                </div>'''

new_header_close = '''                    </span>
                  )}
                </div>
                {result._catalogSource === "perso" && (
                  <div style={{ marginTop: 12, padding: 12, background: "#f9731618", border: "1px solid #f97316", borderRadius: 8, display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: 18 }}>&#x26A0;&#xFE0F;</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 13, fontWeight: 600, color: "#f97316" }}>Devis partiel</div>
                      <div style={{ fontSize: 12, color: "#fdba74", marginTop: 2 }}>
                        Ce devis ne contient que les materiaux presents dans votre catalogue d&apos;entreprise.
                        Les autres postes (couverture, fixations, etc.) doivent etre ajoutes manuellement,
                        ou cochez &quot;Completer avec marche&quot; pour un devis complet.
                      </div>
                    </div>
                  </div>
                )}'''

if 'Devis partiel' in content and 'background: "#f9731618"' in content:
    print("[INFO] Bandeau devis partiel deja present, skip modification 2")
else:
    if old_header_close not in content:
        print("ATTENTION : bloc header devis non trouve, bandeau non ajoute.")
        print("Le badge catalogSource n'a peut-etre pas ete applique correctement.")
    else:
        content = content.replace(old_header_close, new_header_close, 1)
        print("[OK] Bandeau orange 'Devis partiel' ajoute")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("FIX APPLIQUE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Mode 'Mon catalogue seul' :")
print("     - Claude refuse d'inventer des prix")
print("     - Genere uniquement les postes du catalogue perso")
print("     - Ajoute une note d'avertissement dans le devis")
print("  2. Mode 'Mon catalogue + Completer' : comportement inchange")
print("  3. Mode 'Marche DEVIA' : comportement inchange")
print("  4. Bandeau orange 'Devis partiel' visible quand mode perso strict")
print()
print("PROCHAINE ETAPE :")
print("  git add devia.jsx")
print("  git commit -m 'Fix catalogue perso strict (option B)'")
print("  git push")
print()
print("TESTS :")
print("  1. Mode Marche : test normal -> devis complet, badge jaune")
print("  2. Mode Perso + Completer : test normal -> devis complet, badge violet")
print("  3. Mode Perso seul (3 materiaux) :")
print("     - Devis avec 3 lignes (pas plus)")
print("     - Bandeau orange en haut")
print("     - Note dans les notes du devis")
print()
print(f"BACKUP : {backup_name}")
