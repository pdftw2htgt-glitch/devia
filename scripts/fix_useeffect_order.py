#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix l'ordre du useEffect (doit etre apres TOUS les useState)
+ Ajoute des logs console pour debug

A lancer depuis ~/Desktop/devia :
    python3 fix_useeffect_order.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_fix_order"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD 1 : Retirer le useEffect mal place (apres le state addressData)
# ================================================================

old_misplaced_effect = '''const [addressData, setAddressData] = useState(null); // lat/lng/nom officiel pour modif #6
  const [extractingAddress, setExtractingAddress] = useState(false); // indicateur visuel

  // Auto-extraction de l'adresse depuis le prompt (debounce 1s)
  useEffect(() => {
    if (!prompt || prompt.trim().length < 10) return;
    if (commune && commune.trim() !== "") return; // Ne touche pas si l'user a deja rempli

    const timer = setTimeout(async () => {
      setExtractingAddress(true);
      const extracted = await extractAddressFromPrompt(prompt);
      if (extracted && (!commune || commune.trim() === "")) {
        setCommune(extracted.ville || extracted.label);
        setAddressData(extracted);
      }
      setExtractingAddress(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, [prompt]);'''

new_states_only = '''const [addressData, setAddressData] = useState(null); // lat/lng/nom officiel pour modif #6
  const [extractingAddress, setExtractingAddress] = useState(false); // indicateur visuel'''

if old_misplaced_effect in content:
    content = content.replace(old_misplaced_effect, new_states_only, 1)
    print("[OK] useEffect mal place retire")
else:
    print("[INFO] useEffect mal place deja retire")

# ================================================================
# MOD 2 : Ajouter le useEffect APRES tous les useState
# On le place juste apres la declaration de error (dernier state)
# ================================================================

# On cherche un endroit sur APRES tous les useState
# Le marqueur sera la fin de la fonction extractAddressFromPrompt
old_marker = '''const extractAddressFromPrompt = async (text) => {
    if (!text || text.trim().length < 3) return null;'''

# On veut placer le useEffect AVANT la fonction extractAddressFromPrompt
# Mais APRES tous les useState. Strategie : on injecte avant l'extractAddressFromPrompt

new_with_effect_correct_place = '''// Auto-extraction de l'adresse depuis le prompt (debounce 1s)
  useEffect(() => {
    if (!prompt || prompt.trim().length < 10) {
      console.log("[DEVIA] Prompt trop court, pas d'extraction");
      return;
    }
    if (commune && commune.trim() !== "") {
      console.log("[DEVIA] Localisation deja remplie, pas d'extraction");
      return;
    }

    console.log("[DEVIA] Debounce demarre, attente 1s avant extraction...");
    const timer = setTimeout(async () => {
      console.log("[DEVIA] Lancement extraction adresse pour:", prompt);
      setExtractingAddress(true);
      const extracted = await extractAddressFromPrompt(prompt);
      console.log("[DEVIA] Resultat extraction:", extracted);
      if (extracted && (!commune || commune.trim() === "")) {
        const villeDetectee = extracted.ville || extracted.label;
        console.log("[DEVIA] Remplissage du champ Localisation avec:", villeDetectee);
        setCommune(villeDetectee);
        setAddressData(extracted);
      }
      setExtractingAddress(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, [prompt]);

  const extractAddressFromPrompt = async (text) => {
    if (!text || text.trim().length < 3) return null;'''

if "[DEVIA] Debounce demarre" in content:
    print("[INFO] useEffect avec logs deja en place au bon endroit")
elif old_marker in content:
    content = content.replace(old_marker, new_with_effect_correct_place, 1)
    print("[OK] useEffect avec logs ajoute au bon endroit (avant extractAddressFromPrompt)")
else:
    print("[ERREUR] Marqueur extractAddressFromPrompt non trouve.")
    sys.exit(1)

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("FIX APPLIQUE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. useEffect deplace au bon endroit (apres tous les useState)")
print("  2. Logs console ajoutes pour debug :")
print("     [DEVIA] Prompt trop court...")
print("     [DEVIA] Debounce demarre...")
print("     [DEVIA] Lancement extraction...")
print("     [DEVIA] Resultat extraction:...")
print("     [DEVIA] Remplissage du champ Localisation...")
print()
print("PROCHAINE ETAPE :")
print("  1. npm run build")
print("  2. npm run dev (pour tester en local)")
print("  3. Ouvre la page Devis dans le navigateur")
print("  4. Console (F12 -> Console)")
print("  5. Tape 'Carport 4x6m, Lyon' dans le prompt")
print("  6. Tu DOIS voir les logs [DEVIA] s'afficher en direct")
print("  7. Le champ Localisation se remplit ~1s apres")
print()
print(f"BACKUP : {backup_name}")
