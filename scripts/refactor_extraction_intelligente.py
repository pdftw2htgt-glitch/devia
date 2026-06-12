#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Pre-extraction regex avant l'API gouv.fr
Strategie :
1. On extrait via regex les morceaux qui RESSEMBLENT a une adresse
   - Code postal (5 chiffres)
   - Mots avec majuscule (probables villes : Lyon, Marseille...)
   - Numero + rue/avenue/place
2. On envoie ces morceaux a l'API (precis)
3. Si rien trouve, on essaie avec tout le prompt en fallback
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_regex_preextract"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# Remplacer la fonction extractAddressFromPrompt par une version intelligente
# ================================================================

# Marqueur de debut : signature de la fonction
# Marqueur de fin : la derniere accolade fermante avec "};"

old_func = '''const extractAddressFromPrompt = async (text) => {
    if (!text || text.trim().length < 3) return null;
    try {
      // L'API gouv.fr accepte une recherche libre, elle trouvera la ville/adresse meme noyee dans du texte
      const url = "https://api-adresse.data.gouv.fr/search/?q=" + encodeURIComponent(text) + "&limit=1";
      const resp = await fetch(url);
      if (!resp.ok) return null;
      const data = await resp.json();
      if (!data.features || data.features.length === 0) {
        console.log("[DEVIA] API n'a renvoye aucune feature");
        return null;
      }
      const feat = data.features[0];
      console.log("[DEVIA] API score:", feat.properties.score, "Label:", feat.properties.label, "Ville:", feat.properties.city);
      // Score de confiance entre 0 et 1, on accepte si >= 0.1 (tres permissif pour les villes seules)
      if (!feat.properties.score || feat.properties.score < 0.1) {
        console.log("[DEVIA] Score trop bas, rejete");
        return null;
      }
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
  };'''

new_func = '''// Helper : extrait les morceaux du texte qui RESSEMBLENT a une adresse
  const extractAddressCandidates = (text) => {
    const candidates = [];

    // 1. Code postal (5 chiffres) eventuellement suivi d'une ville
    //    Ex: "75001 Paris" / "69001" / "13008"
    const cpMatch = text.match(/\\b(\\d{5})\\s*([A-ZA-zÀ-ÿ][a-zà-ÿ\\-\\s']{2,30})?/);
    if (cpMatch) {
      candidates.push(cpMatch[0].trim());
    }

    // 2. Numero + voie + reste : "12 rue Merciere Lyon" / "5 avenue Foch Paris"
    const adresseMatch = text.match(/\\b(\\d{1,4})\\s+(rue|avenue|av\\.?|boulevard|bd\\.?|place|impasse|chemin|route|allee|all\\.?|quai)\\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\\-\\s']{2,60})/i);
    if (adresseMatch) {
      candidates.push(adresseMatch[0].trim());
    }

    // 3. Noms propres : mots avec majuscule (probables villes)
    //    Ex: "Lyon", "Saint-Tropez", "La Croix-Valmer"
    //    On capture le mot + d'eventuels mots suivants commencant aussi par majuscule (Saint-Tropez, etc.)
    const mots = text.split(/[\\s,;.()\\[\\]]+/);
    const motsAvecMaj = mots.filter(m => /^[A-ZÀ-Ÿ][a-zà-ÿ\\-']{2,}/.test(m));
    // On garde les noms propres qui ne sont pas des materiaux/types connus
    const blacklist = new Set([
      "Carport", "Charpente", "Garage", "Maison", "Toiture", "Abri",
      "Sapin", "Douglas", "Chene", "Pin", "Epicea", "Ardoise",
      "Tuile", "Bardeau", "Bac", "Acier", "Zinc", "Cuivre",
      "Traditionnelle", "Fermette", "Industriel", "Metalique",
      "Neuve", "Renovation", "Combles"
    ]);
    motsAvecMaj.forEach(m => {
      if (!blacklist.has(m)) candidates.push(m);
    });

    return candidates;
  };

  const extractAddressFromPrompt = async (text) => {
    if (!text || text.trim().length < 3) return null;

    // On pre-extrait les candidats (codes postaux, noms propres, adresses)
    const candidates = extractAddressCandidates(text);
    console.log("[DEVIA] Candidats extraits:", candidates);

    // Si pas de candidats, on essaie quand meme avec tout le texte en derniere chance
    const queries = candidates.length > 0 ? candidates : [text];

    // Pour chaque candidat, on interroge l'API jusqu'a trouver un match
    for (const query of queries) {
      try {
        const url = "https://api-adresse.data.gouv.fr/search/?q=" + encodeURIComponent(query) + "&limit=1";
        const resp = await fetch(url);
        if (!resp.ok) continue;
        const data = await resp.json();
        if (!data.features || data.features.length === 0) {
          console.log("[DEVIA] Pas de feature pour:", query);
          continue;
        }
        const feat = data.features[0];
        console.log("[DEVIA] Query:", query, "-> Score:", feat.properties.score, "Label:", feat.properties.label);

        // Seuil 0.5 (plus exigeant car on cherche sur des candidats deja propres)
        if (!feat.properties.score || feat.properties.score < 0.5) {
          console.log("[DEVIA] Score trop bas pour:", query);
          continue;
        }

        return {
          label: feat.properties.label,
          ville: feat.properties.city || feat.properties.name,
          codePostal: feat.properties.postcode || "",
          lat: feat.geometry.coordinates[1],
          lng: feat.geometry.coordinates[0],
          score: feat.properties.score
        };
      } catch (e) {
        console.warn("[DEVIA] Erreur API pour", query, ":", e);
        continue;
      }
    }

    console.log("[DEVIA] Aucun candidat n'a donne un resultat exploitable");
    return null;
  };'''

if "extractAddressCandidates" in content:
    print("[INFO] Fonction deja refactorisee")
elif old_func in content:
    content = content.replace(old_func, new_func, 1)
    print("[OK] Fonction extractAddressFromPrompt refactorisee")
    print("     - Pre-extraction regex des candidats (CP, adresses, noms propres)")
    print("     - Blacklist des materiaux/types (Ardoise, Tuile, Carport, etc.)")
    print("     - Test de chaque candidat, retourne le premier OK")
    print("     - Seuil 0.5 (plus exigeant, mais sur du texte deja propre)")
else:
    print("[ERREUR] Fonction extractAddressFromPrompt non trouvee.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("EXTRACTION INTELLIGENTE EN PLACE")
print("=" * 60)
print()
print("PROCHAINE ETAPE :")
print("  Recharge la page Safari (Cmd+R)")
print("  Refais les 6 tests")
print()
print(f"BACKUP : {backup_name}")
