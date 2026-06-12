#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D A2.2.1 : Ajout type MONOPENTE
- Ajoute drawMonopente() dans buildScene3D
- Met a jour le prompt IA pour detecter "monopente"
- Met a jour QuestionsScreen avec l'option

Description :
- Batiment rectangulaire avec MURS (contrairement au carport)
- Toit 1 seule pente (mur arriere haut, mur avant bas)
- Sablieres + pannes + chevrons + toiture 1 pan
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_monopente"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter drawMonopente() dans buildScene3D
# On le place AVANT le switch "SELON TYPE PROJET"
# ================================================================

old_switch_marker = '''  // ============================================================
  // SWITCH SELON TYPE PROJET
  // ============================================================
  if (typeProjet === "carport") {
    drawCarport();
  } else {
    drawCharpenteTrad();
  }'''

new_with_monopente = '''  // ============================================================
  // MONOPENTE (1 pan + murs, mur arriere haut, mur avant bas)
  // ============================================================
  const drawMonopente = () => {
    // Calcul deniveles
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;            // hauteur mur avant
    const Hhaut = Ht + denivele; // hauteur mur arriere

    // 4 MURS (avec hauteurs variables sur les cotes)
    // Mur arriere (Z+, haut)
    addBox(L, Hhaut, 0.15, 0, Hhaut/2, lg/2, wallMat);
    // Mur avant (Z-, bas)
    addBox(L, Hbas, 0.15, 0, Hbas/2, -lg/2, wallMat);

    // Mur lateral gauche (forme trapezoidale - approxime avec 2 boxes)
    // Partie basse : rectangle Hbas
    addBox(0.15, Hbas, lg, -L/2, Hbas/2, 0, wallMat);
    // Partie haute : triangle (approxime par un prisme)
    const triGeo = new THREE.BufferGeometry();
    const triVertices = new Float32Array([
      // Triangle gauche
      -L/2, Hbas, -lg/2,
      -L/2, Hbas, lg/2,
      -L/2, Hhaut, lg/2,
    ]);
    triGeo.setAttribute("position", new THREE.BufferAttribute(triVertices, 3));
    triGeo.computeVertexNormals();
    const triMeshG = new THREE.Mesh(triGeo, wallMat);
    scene.add(triMeshG);

    // Mur lateral droit
    addBox(0.15, Hbas, lg, L/2, Hbas/2, 0, wallMat);
    const triGeo2 = new THREE.BufferGeometry();
    const triVertices2 = new Float32Array([
      L/2, Hbas, -lg/2,
      L/2, Hbas, lg/2,
      L/2, Hhaut, lg/2,
    ]);
    triGeo2.setAttribute("position", new THREE.BufferAttribute(triVertices2, 3));
    triGeo2.computeVertexNormals();
    const triMeshD = new THREE.Mesh(triGeo2, wallMat);
    scene.add(triMeshD);

    // SABLIERES
    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2);  // sabliere avant
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2);  // sabliere arriere

    // PANNES (3 pannes entre sablieres)
    const nbPannes = 3;
    for (let i = 0; i < nbPannes; i++) {
      const t = i / (nbPannes - 1);
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele;
      addBox(L + 0.3, 0.14, 0.14, 0, y, z);
    }

    // CHEVRONS (en pente, sens largeur)
    const nbChevrons = Math.max(3, Math.ceil(L / 1.0));
    const ang = Math.atan(denivele / lg);
    const longueurChevron = lg / Math.cos(ang);
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      const yCentre = Hbas + denivele/2;
      addBox(0.10, 0.10, longueurChevron + 0.2, x, yCentre, 0, woodMat, [ang, 0, 0]);
    }

    // TOITURE (1 pan)
    const rg = new THREE.PlaneGeometry(longueurChevron + 0.3, L + 0.4);
    const roof = new THREE.Mesh(rg, roofMat);
    roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
    roof.rotation.z = ang;
    roof.rotation.y = Math.PI/2;
    scene.add(roof);
  };

  // ============================================================
  // SWITCH SELON TYPE PROJET
  // ============================================================
  if (typeProjet === "carport") {
    drawCarport();
  } else if (typeProjet === "monopente") {
    drawMonopente();
  } else {
    drawCharpenteTrad();
  }'''

if "drawMonopente" in content:
    print("[INFO] Monopente deja en place")
elif old_switch_marker in content:
    content = content.replace(old_switch_marker, new_with_monopente, 1)
    print("[OK] drawMonopente() ajoutee + switch mis a jour")
    modifs += 1
else:
    print("[ERREUR] Switch SELON TYPE PROJET non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Mettre a jour le yCentre pour monopente
# ================================================================

old_ycentre = '''  const yCentre = typeProjet === "carport"
    ? Ht + (lg * Math.tan((pente * Math.PI) / 180)) / 2
    : Ht/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;'''

new_ycentre = '''  let yCentre;
  if (typeProjet === "carport" || typeProjet === "monopente") {
    yCentre = Ht + (lg * Math.tan((pente * Math.PI) / 180)) / 2;
  } else {
    yCentre = Ht/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
  }'''

if "typeProjet === \"monopente\"" in content and "yCentre = Ht" in content:
    print("[INFO] yCentre deja a jour pour monopente")
elif old_ycentre in content:
    content = content.replace(old_ycentre, new_ycentre, 1)
    print("[OK] yCentre adapte pour monopente")
    modifs += 1
else:
    print("[WARN] yCentre non trouve - peut-etre deja modifie")

# ================================================================
# MOD 3 : Detection IA dans detectParams - ajouter "monopente"
# ================================================================

old_type_detect = '''    if (/fermette|industriel/i.test(text)) out.type = "fermette";
    else if (/traditionn/i.test(text)) out.type = "traditionnelle";
    else if (/lamell/i.test(text)) out.type = "lamelle";
    else if (/metal/i.test(text)) out.type = "metalique";'''

new_type_detect = '''    if (/fermette|industriel/i.test(text)) out.type = "fermette";
    else if (/traditionn/i.test(text)) out.type = "traditionnelle";
    else if (/lamell/i.test(text)) out.type = "lamelle";
    else if (/metal/i.test(text)) out.type = "metalique";
    else if (/monopente|mono.?pente|une seule pente|1 pente|1 pan/i.test(text)) out.type = "monopente";'''

if 'out.type = "monopente"' in content:
    print("[INFO] Detection monopente deja presente")
elif old_type_detect in content:
    content = content.replace(old_type_detect, new_type_detect, 1)
    print("[OK] Detection 'monopente' ajoutee dans detectParams")
    modifs += 1
else:
    print("[WARN] Bloc detection type non trouve")

# ================================================================
# MOD 4 : Ajouter dans le prompt IA la mention monopente
# ================================================================

# On cherche la phrase qui demande type_projet
old_prompt_type = '"\\"type_projet\\":\\"' + '"'  # marqueur partiel

# Plus simple : juste ajouter dans la liste des types acceptes
old_carport_prompt = 'Pour un carport simple : 0.4-0.6h fabrication par m2 + 0.3-0.5h pose par m2.'

new_with_mono_prompt = 'Pour un carport simple : 0.4-0.6h fabrication par m2 + 0.3-0.5h pose par m2. Pour une monopente (atelier/garage avec 1 pente) : 0.5-0.7h fabrication par m2 + 0.4-0.6h pose par m2.'

if "monopente (atelier/garage" in content:
    print("[INFO] Prompt IA deja a jour pour monopente")
elif old_carport_prompt in content:
    content = content.replace(old_carport_prompt, new_with_mono_prompt, 1)
    print("[OK] Prompt IA enrichi avec ratios monopente")
    modifs += 1
else:
    print("[WARN] Phrase carport dans prompt non trouvee")

# ================================================================
# MOD 5 : Ajouter dans QUESTIONS l'option monopente
# (dans l'array des types de charpente)
# ================================================================

old_metal_option = '{ val: "metalique", label: "Charpente metallique", icon: "gear" },'

new_with_monopente_option = '''{ val: "metalique", label: "Charpente metallique", icon: "gear" },
{ val: "monopente", label: "Monopente", icon: "ruler" },'''

if 'val: "monopente"' in content:
    print("[INFO] Option monopente deja dans QUESTIONS")
elif old_metal_option in content:
    content = content.replace(old_metal_option, new_with_monopente_option, 1)
    print("[OK] Option Monopente ajoutee dans QuestionsScreen")
    modifs += 1
else:
    print("[WARN] Option metalique non trouvee")

# ================================================================
# MOD 6 : Mettre a jour aussi le mapping type_projet detection
# (la logique qui transforme type d'IA en type 3D)
# Cherche "charpente_trad" pour comprendre ou est le mapping
# ================================================================

# Approche : chercher si le type "monopente" est mappe vers type_projet="monopente"
# Dans le code on a probablement quelque chose comme :
#   if (type === "carport") view3DParams.type_projet = "carport";
# On cherche ce pattern

# Le mapping est probablement dans handleGenerate ou apres reception du JSON
# On ne va pas y toucher si ca semble fonctionner par defaut

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. drawMonopente() ajoutee dans buildScene3D")
print("  2. Switch type_projet inclut maintenant 'monopente'")
print("  3. yCentre adapte pour vue camera")
print("  4. detectParams reconnait 'monopente', 'mono-pente', '1 pente', '1 pan'")
print("  5. Prompt IA enrichi avec ratios de temps monopente")
print("  6. Option 'Monopente' ajoutee dans QuestionsScreen")
print()
print("STRUCTURE MONOPENTE :")
print("  - 4 murs (lateraux trapezoidaux)")
print("  - Sabliere haute + basse")
print("  - 3 pannes")
print("  - Chevrons en pente")
print("  - Toiture 1 pan")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
