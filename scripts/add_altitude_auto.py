#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Modif #6 : Auto-remplissage du champ Altitude
Quand addressData est mis a jour (= ville detectee), on appelle
l'API open-meteo avec lat/lng pour recuperer l'altitude.

A lancer depuis ~/Desktop/devia :
    python3 add_altitude_auto.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_altitude_auto"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# Ajouter un useEffect qui ecoute addressData et remplit altitude
# On le place juste apres le useEffect existant de l'extraction
# ================================================================

# Marqueur : la fin du useEffect existant (le clearTimeout)
old_marker = '''    return () => clearTimeout(timer);
  }, [prompt]);'''

new_with_altitude = '''    return () => clearTimeout(timer);
  }, [prompt]);

  // Auto-remplissage de l'altitude quand addressData est mis a jour
  useEffect(() => {
    if (!addressData || !addressData.lat || !addressData.lng) return;
    // Si l'user a deja saisi une altitude differente de la valeur par defaut 200, on ne touche pas
    if (altitude && altitude !== "200" && altitude.trim() !== "") {
      console.log("[DEVIA] Altitude deja saisie par l'user, pas de remplissage auto");
      return;
    }

    const fetchAltitude = async () => {
      try {
        console.log("[DEVIA] Recuperation altitude pour:", addressData.lat, addressData.lng);
        const url = "https://api.open-meteo.com/v1/elevation?latitude=" + addressData.lat + "&longitude=" + addressData.lng;
        const resp = await fetch(url);
        if (!resp.ok) {
          console.warn("[DEVIA] API altitude HTTP", resp.status);
          return;
        }
        const data = await resp.json();
        if (!data.elevation || !data.elevation.length) {
          console.warn("[DEVIA] API altitude pas de valeur");
          return;
        }
        const alt = Math.round(data.elevation[0]);
        console.log("[DEVIA] Altitude recuperee:", alt, "m");
        setAltitude(String(alt));
      } catch (e) {
        console.warn("[DEVIA] Erreur API altitude:", e);
      }
    };

    fetchAltitude();
  }, [addressData]);'''

if "Auto-remplissage de l'altitude quand addressData" in content:
    print("[INFO] useEffect altitude deja en place")
elif old_marker in content:
    content = content.replace(old_marker, new_with_altitude, 1)
    print("[OK] useEffect altitude ajoute (declenche quand addressData change)")
else:
    print("[ERREUR] Marqueur useEffect existant non trouve.")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("MODIF #6 APPLIQUEE - Altitude auto")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  - Nouveau useEffect declenche quand addressData change")
print("  - Appelle l'API open-meteo avec lat/lng")
print("  - Remplit auto le champ Altitude")
print("  - Ne touche pas si l'user a deja saisi une altitude personnalisee")
print()
print("COMMENT TESTER :")
print("  1. Recharge la page Safari (Cmd+R)")
print("  2. Vide les champs Localisation et Altitude (mets 200 par defaut)")
print("  3. Tape dans le prompt : 'Carport 4x6m, ardoise, Chamonix'")
print("  4. Attends 2 secondes")
print("  5. Le champ Localisation se remplit avec 'Chamonix'")
print("  6. Puis ~1s apres, le champ Altitude se remplit (vers 1035m)")
print()
print("AUTRES VILLES A TESTER :")
print("  - Bordeaux : ~10m (proche de la mer)")
print("  - Grenoble : ~210m (vallee)")
print("  - Briancon : ~1300m (montagne)")
print("  - Paris : ~35m")
print()
print(f"BACKUP : {backup_name}")
