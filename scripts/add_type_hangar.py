#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D A2.2.2 : Ajout type HANGAR
- Poteaux aux 4 coins + poteaux intermediaires
- Sablieres
- 2 pans (toit symetrique comme charpente trad)
- Pas de murs (batiment ouvert)
- Grande portee, typique agricole/industriel
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_hangar"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter drawHangar() dans buildScene3D
# AVANT le switch SELON TYPE PROJET
# ================================================================

old_switch_marker = '''  // ============================================================
  // SWITCH SELON TYPE PROJET
  // ============================================================
  if (typeProjet === "carport") {
    drawCarport();
  } else if (typeProjet === "monopente") {
    drawMonopente();
  } else {
    drawCharpenteTrad();
  }'''

new_with_hangar = '''  // ============================================================
  // HANGAR (poteaux + 2 pans, sans murs, grande portee)
  // ============================================================
  const drawHangar = () => {
    const hf = lg / 2 * Math.tan((pente * Math.PI) / 180);
    const sectionPotau = 0.22; // poteaux plus gros pour hangar

    // POTEAUX (4 coins + intermediaires selon longueur)
    const nbPoteauxLong = Math.max(2, Math.ceil(L / 4)); // 1 poteau tous les 4m max
    for (let i = 0; i <= nbPoteauxLong; i++) {
      const x = -L/2 + (i / nbPoteauxLong) * L;
      // Poteau cote Z+
      addBox(sectionPotau, Ht, sectionPotau, x, Ht/2, lg/2);
      // Poteau cote Z-
      addBox(sectionPotau, Ht, sectionPotau, x, Ht/2, -lg/2);
    }

    // SABLIERES (2 longues poutres entre les poteaux)
    addBox(L + 0.4, 0.20, 0.20, 0, Ht, lg/2);   // sabliere Z+
    addBox(L + 0.4, 0.20, 0.20, 0, Ht, -lg/2);  // sabliere Z-

    // FERMES (assemblees comme charpente trad mais sans murs)
    const nbFermes = Math.max(2, Math.ceil(L / 3)); // 1 ferme tous les 3m
    for (let i = 0; i <= nbFermes; i++) {
      const x = -L/2 + (i / nbFermes) * L;
      const ang = Math.atan(hf / (lg/2));
      const pl = (lg/2) / Math.cos(ang);
      // Arbaletriers (les 2 pans inclines)
      addBox(pl, 0.14, 0.14, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);
      addBox(pl, 0.14, 0.14, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);
      // Entrait (poutre horizontale en bas)
      addBox(0.14, 0.14, lg, x, Ht, 0);
      // Poincon (vertical central)
      addBox(0.14, hf, 0.14, x, Ht + hf/2, 0);
    }

    // FAITAGE
    addBox(L + 0.5, 0.16, 0.16, 0, Ht + hf, 0);

    // PANNES (le long de la longueur, sur les pans)
    const nbPannes = 3;
    for (let i = 1; i < nbPannes; i++) {
      const t = i / nbPannes;
      const yPanne = Ht + hf * (1 - t);
      const zPanne = (lg/2) * t;
      addBox(L + 0.4, 0.12, 0.12, 0, yPanne, zPanne);
      addBox(L + 0.4, 0.12, 0.12, 0, yPanne, -zPanne);
    }

    // TOITURE (2 pans)
    const ang = Math.atan(hf / (lg/2));
    const pl = (lg/2) / Math.cos(ang);
    const rg = new THREE.PlaneGeometry(L + 0.8, pl + 0.3);
    const r1 = new THREE.Mesh(rg, roofMat);
    r1.position.set(0, Ht + hf/2, lg/4);
    r1.rotation.x = ang - Math.PI/2;
    scene.add(r1);
    const r2 = new THREE.Mesh(rg, roofMat);
    r2.position.set(0, Ht + hf/2, -lg/4);
    r2.rotation.x = -(ang - Math.PI/2);
    scene.add(r2);
  };

  // ============================================================
  // SWITCH SELON TYPE PROJET
  // ============================================================
  if (typeProjet === "carport") {
    drawCarport();
  } else if (typeProjet === "monopente") {
    drawMonopente();
  } else if (typeProjet === "hangar") {
    drawHangar();
  } else {
    drawCharpenteTrad();
  }'''

if "drawHangar" in content:
    print("[INFO] Hangar deja en place")
elif old_switch_marker in content:
    content = content.replace(old_switch_marker, new_with_hangar, 1)
    print("[OK] drawHangar() ajoutee + switch mis a jour")
    modifs += 1
else:
    print("[ERREUR] Switch SELON TYPE PROJET non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : yCentre pour hangar (similaire a charpente_trad)
# Pas de modif necessaire si hangar utilise le meme calcul que trad
# Mais on peut affiner
# ================================================================

old_ycentre_block = '''  let yCentre;
  if (typeProjet === "carport" || typeProjet === "monopente") {
    yCentre = Ht + (lg * Math.tan((pente * Math.PI) / 180)) / 2;
  } else {
    yCentre = Ht/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
  }'''

new_ycentre_block = '''  let yCentre;
  if (typeProjet === "carport" || typeProjet === "monopente") {
    yCentre = Ht + (lg * Math.tan((pente * Math.PI) / 180)) / 2;
  } else if (typeProjet === "hangar") {
    // Hangar : centre plus haut pour bien voir le toit
    yCentre = Ht * 0.7 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
  } else {
    yCentre = Ht/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
  }'''

if "hangar : centre plus haut" in content.lower() or 'typeProjet === "hangar"' in content and "yCentre = Ht * 0.7" in content:
    print("[INFO] yCentre deja a jour pour hangar")
elif old_ycentre_block in content:
    content = content.replace(old_ycentre_block, new_ycentre_block, 1)
    print("[OK] yCentre adapte pour hangar")
    modifs += 1
else:
    print("[WARN] Bloc yCentre non trouve - peut-etre deja modifie")

# ================================================================
# MOD 3 : Detection IA dans detectParams - ajouter "hangar"
# ================================================================

old_type_detect = '''    else if (/monopente|mono.?pente|une seule pente|1 pente|1 pan/i.test(text)) out.type = "monopente";'''

new_type_detect = '''    else if (/monopente|mono.?pente|une seule pente|1 pente|1 pan/i.test(text)) out.type = "monopente";
    else if (/hangar|grange|batiment.*agricole|grand.*portee|industriel/i.test(text)) out.type = "hangar";'''

if 'out.type = "hangar"' in content:
    print("[INFO] Detection hangar deja presente")
elif old_type_detect in content:
    content = content.replace(old_type_detect, new_type_detect, 1)
    print("[OK] Detection 'hangar' ajoutee dans detectParams")
    modifs += 1
else:
    print("[WARN] Bloc detection type non trouve")

# ================================================================
# MOD 4 : Mettre a jour le prompt IA avec ratios hangar
# ================================================================

old_mono_prompt = 'Pour une monopente (atelier/garage avec 1 pente) : 0.5-0.7h fabrication par m2 + 0.4-0.6h pose par m2.'

new_with_hangar_prompt = 'Pour une monopente (atelier/garage avec 1 pente) : 0.5-0.7h fabrication par m2 + 0.4-0.6h pose par m2. Pour un hangar (batiment agricole, grande portee, poteaux + 2 pans) : 0.3-0.5h fabrication par m2 + 0.25-0.4h pose par m2.'

if "hangar (batiment agricole" in content:
    print("[INFO] Prompt IA deja a jour pour hangar")
elif old_mono_prompt in content:
    content = content.replace(old_mono_prompt, new_with_hangar_prompt, 1)
    print("[OK] Prompt IA enrichi avec ratios hangar")
    modifs += 1
else:
    print("[WARN] Phrase monopente dans prompt non trouvee")

# ================================================================
# MOD 5 : Ajouter dans QUESTIONS l'option Hangar
# ================================================================

old_mono_option = '{ val: "monopente", label: "Monopente", icon: "ruler" },'

new_with_hangar_option = '''{ val: "monopente", label: "Monopente", icon: "ruler" },
{ val: "hangar", label: "Hangar / Batiment agricole", icon: "factory" },'''

if 'val: "hangar"' in content:
    print("[INFO] Option hangar deja dans QUESTIONS")
elif old_mono_option in content:
    content = content.replace(old_mono_option, new_with_hangar_option, 1)
    print("[OK] Option Hangar ajoutee dans QuestionsScreen")
    modifs += 1
else:
    print("[WARN] Option monopente non trouvee")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. drawHangar() ajoutee dans buildScene3D")
print("  2. Switch type_projet inclut maintenant 'hangar'")
print("  3. yCentre adapte pour vue camera (centre plus haut)")
print("  4. detectParams reconnait 'hangar', 'grange', 'batiment agricole'")
print("  5. Prompt IA enrichi avec ratios de temps hangar")
print("  6. Option 'Hangar / Batiment agricole' ajoutee dans QuestionsScreen")
print()
print("STRUCTURE HANGAR :")
print("  - Poteaux aux 4 coins + intermediaires (1 tous les 4m max)")
print("  - Sablieres longues (poutres horizontales entre poteaux)")
print("  - Fermes (arbaletriers + entraits + poincons)")
print("  - Faitage")
print("  - 3 pannes longitudinales")
print("  - Toiture 2 pans")
print("  - PAS DE MURS (batiment ouvert)")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
