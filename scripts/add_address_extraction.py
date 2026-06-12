#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Extraction automatique de l'adresse depuis le prompt
Au clic 'Generer', appelle l'API Adresse.data.gouv.fr pour extraire
une adresse/ville et remplir automatiquement le champ Localisation.

A lancer depuis ~/Desktop/devia :
    python3 add_address_extraction.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_address_extraction"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter le state addressData (pour stocker lat/lng)
# ================================================================

old_state = 'const [typeTravaux, setTypeTravaux] = useState("neuf");'
new_state = '''const [typeTravaux, setTypeTravaux] = useState("neuf");
  const [addressData, setAddressData] = useState(null); // lat/lng/nom officiel pour modif #6'''

if "const [addressData, setAddressData]" in content:
    print("[INFO] State addressData deja present")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] State addressData ajoute")
    modifs += 1
else:
    print("[ERREUR] State typeTravaux non trouve.")
    sys.exit(1)

# ================================================================
# MOD 2 : Ajouter la fonction extractAddressFromPrompt
# ================================================================

# On l'ajoute juste avant la fonction handleGenerate
old_handler_start = 'const handleGenerate = async (finalParams) => {'

new_handler_with_extract = '''// Extraction d'adresse via API gouv.fr (limite 50 req/sec, gratuit, pas de cle)
  const extractAddressFromPrompt = async (text) => {
    if (!text || text.trim().length < 3) return null;
    try {
      // L'API gouv.fr accepte une recherche libre, elle trouvera la ville/adresse meme noyee dans du texte
      const url = "https://api-adresse.data.gouv.fr/search/?q=" + encodeURIComponent(text) + "&limit=1";
      const resp = await fetch(url);
      if (!resp.ok) return null;
      const data = await resp.json();
      if (!data.features || data.features.length === 0) return null;
      const feat = data.features[0];
      // Score de confiance entre 0 et 1, on prend que si > 0.4
      if (!feat.properties.score || feat.properties.score < 0.4) return null;
      return {
        label: feat.properties.label,
        ville: feat.properties.city || feat.properties.name,
        codePostal: feat.properties.postcode || "",
        lat: feat.geometry.coordinates[1],
        lng: feat.geometry.coordinates[0],
        score: feat.properties.score
      };
    } catch (e) {
      console.warn("Extraction adresse echouee:", e);
      return null;
    }
  };

  const handleGenerate = async (finalParams) => {'''

if "extractAddressFromPrompt" in content:
    print("[INFO] Fonction extractAddressFromPrompt deja presente")
elif old_handler_start in content:
    content = content.replace(old_handler_start, new_handler_with_extract, 1)
    print("[OK] Fonction extractAddressFromPrompt ajoutee")
    modifs += 1
else:
    print("[ERREUR] handleGenerate non trouve.")
    sys.exit(1)

# ================================================================
# MOD 3 : Appeler extractAddressFromPrompt au debut de handleGenerate
# Si le champ commune est vide, on extrait depuis le prompt et on remplit
# ================================================================

# La nouvelle version a "const handleGenerate = async (finalParams) => {" suivi de :
old_setLoading = '''const handleGenerate = async (finalParams) => {
setShowQuestions(false);
setLoading(true);
setError(null);
const zoneInfo = getZone(commune, altitude);'''

new_setLoading = '''const handleGenerate = async (finalParams) => {
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

if "let effectiveCommune = commune;" in content:
    print("[INFO] Appel extractAddressFromPrompt deja dans handleGenerate")
elif old_setLoading in content:
    content = content.replace(old_setLoading, new_setLoading, 1)
    print("[OK] Appel extractAddressFromPrompt ajoute dans handleGenerate")
    modifs += 1
else:
    print("[WARN] Bloc setLoading dans handleGenerate non trouve")

# ================================================================
# MOD 4 : Remplacer les autres usages de commune par effectiveCommune
# UNIQUEMENT dans la fonction handleGenerate (apres le let effectiveCommune)
# Pour ne pas casser les autres usages dans le fichier.
# Note : on remplace pas tout commune partout, juste dans la zone concernee
# ================================================================

# On cherche le bloc "Commune=" + commune + ", Altitude=..." et on le remplace
# Ce bloc fait partie du prompt envoye a Claude
old_prompt_line = '"Commune=" + commune + ", Altitude=" + altitude + "m, Zone neige=" + zoneInfo.neige + " sk=" + zoneInfo.sk + "kN/m2, Vent=" + zoneInfo.vent + " qb=" + zoneInfo.qb + "kN/m2. " +'
new_prompt_line = '"Commune=" + effectiveCommune + ", Altitude=" + altitude + "m, Zone neige=" + zoneInfo.neige + " sk=" + zoneInfo.sk + "kN/m2, Vent=" + zoneInfo.vent + " qb=" + zoneInfo.qb + "kN/m2. " +'

if 'Commune=" + effectiveCommune' in content:
    print("[INFO] Prompt deja utilise effectiveCommune")
elif old_prompt_line in content:
    content = content.replace(old_prompt_line, new_prompt_line, 1)
    print("[OK] Prompt utilise effectiveCommune au lieu de commune")
    modifs += 1
else:
    print("[WARN] Ligne du prompt commune non trouvee exactement")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. State 'addressData' ajoute (stocke lat/lng pour modif #6)")
print("  2. Fonction 'extractAddressFromPrompt' ajoutee :")
print("     - Appelle API Adresse.data.gouv.fr (gratuite, francaise)")
print("     - Detecte ville/adresse dans le texte du prompt")
print("     - Retourne label/ville/CP/lat/lng/score")
print("  3. Au clic Generer :")
print("     - Si champ Localisation VIDE : extrait depuis le prompt")
print("     - Si champ Localisation REMPLI : ne touche pas (respecte l'user)")
print("     - Remplit auto le champ Localisation avec la ville trouvee")
print("     - Stocke lat/lng silencieusement (pour modif #6)")
print()
print("COMMENT TESTER :")
print("  1. Laisser le champ Localisation VIDE")
print("  2. Taper un prompt avec une ville/adresse, ex:")
print("     'Carport 4x6m, ardoise, 12 rue Merciere Lyon'")
print("     'Charpente 8x12m, tuile, Marseille'")
print("     'Toiture 6x5m, ardoise, 75001 Paris'")
print("  3. Cliquer Generer")
print("  4. Le champ Localisation se remplit automatiquement")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print('    git commit -m "Auto-extraction adresse via API gouv.fr"')
print("    git push")
print()
print(f"BACKUP : {backup_name}")
