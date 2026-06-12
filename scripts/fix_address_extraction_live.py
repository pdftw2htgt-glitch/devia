#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Bascule l'extraction d'adresse en mode LIVE (debounce 1s)
- Quand l'user tape dans le prompt, 1 seconde apres avoir arrete,
  DEVIA appelle l'API et remplit auto le champ Localisation
- On RETIRE l'extraction au clic Generer (puisqu'on l'a maintenant en live)

A lancer depuis ~/Desktop/devia :
    python3 fix_address_extraction_live.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_live_extraction"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Retirer le bloc d'extraction de handleGenerate
# (on remet le code d'avant - simple)
# ================================================================

old_with_extract = '''const handleGenerate = async (finalParams) => {
setShowQuestions(false);
setLoading(true);
setError(null);

    // Si le champ Localisation est vide, on tente d'extraire l'adresse depuis le prompt
    let effectiveCommune = commune;
    if (!commune || commune.trim() === "") {
      const extracted = await extractAddressFromPrompt(prompt);
      if (extracted) {
        effectiveCommune = extracted.ville || extracted.label;
        setCommune(effectiveCommune); // Auto-remplit le champ visuel
        setAddressData(extracted); // Stocke lat/lng pour modif #6 (altitude)
      }
    }

const zoneInfo = getZone(effectiveCommune, altitude);'''

new_simple = '''const handleGenerate = async (finalParams) => {
setShowQuestions(false);
setLoading(true);
setError(null);
const zoneInfo = getZone(commune, altitude);'''

if old_with_extract in content:
    content = content.replace(old_with_extract, new_simple, 1)
    print("[OK] Extraction au clic Generer retiree")
    modifs += 1
else:
    print("[INFO] Pas d'extraction au clic Generer a retirer")

# ================================================================
# MOD 2 : Remettre 'commune' dans le prompt (au lieu de effectiveCommune)
# ================================================================

old_eff = '"Commune=" + effectiveCommune + ", Altitude="'
new_back = '"Commune=" + commune + ", Altitude="'

if old_eff in content:
    content = content.replace(old_eff, new_back, 1)
    print("[OK] Prompt utilise 'commune' (au lieu de effectiveCommune)")
    modifs += 1
else:
    print("[INFO] Prompt deja sur 'commune'")

# ================================================================
# MOD 3 : Ajouter le useEffect debounce qui declenche l'extraction
# Quand le prompt change ET que Localisation est vide
# ================================================================

# On va chercher le state addressData et ajouter le useEffect juste apres
old_state_addressData = 'const [addressData, setAddressData] = useState(null); // lat/lng/nom officiel pour modif #6'

new_state_with_effect = '''const [addressData, setAddressData] = useState(null); // lat/lng/nom officiel pour modif #6
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

if "Auto-extraction de l'adresse depuis le prompt (debounce 1s)" in content:
    print("[INFO] useEffect debounce deja present")
elif old_state_addressData in content:
    content = content.replace(old_state_addressData, new_state_with_effect, 1)
    print("[OK] useEffect debounce ajoute (1s apres derniere frappe)")
    modifs += 1
else:
    print("[ERREUR] State addressData non trouve. Le script precedent a pu echouer.")
    sys.exit(1)

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  - L'extraction se fait maintenant LIVE (pendant la saisie)")
print("  - 1 seconde apres derniere touche, DEVIA appelle l'API")
print("  - Si une ville est trouvee, le champ Localisation se remplit")
print("  - Le code de l'extraction au clic Generer est retire (inutile)")
print()
print("COMMENT TESTER :")
print("  1. Va sur la page Devis")
print("  2. Tape dans le prompt: 'Carport 4x6m, ardoise, Lyon'")
print("  3. Arrete de taper")
print("  4. ~1 seconde plus tard, le champ Localisation se remplit avec 'Lyon'")
print("  5. Tu peux ensuite cliquer Generer normalement")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print('    git commit -m "Extraction adresse en mode live (debounce 1s)"')
print("    git push")
print()
print(f"BACKUP : {backup_name}")
