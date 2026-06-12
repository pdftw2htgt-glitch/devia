#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D A2.2.3 : Ajout type APPENTIS
- Mur arriere PLEIN et HAUT (simule un mur existant de maison)
- Toit 1 pan qui descend du mur arriere vers l'avant
- Pas de mur avant (ou tres bas)
- Cotes lateraux avec petits murs trapezoidaux
- Typique pour terrasse couverte, abri a bois accole, etc.
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_appentis"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter drawAppentis() dans buildScene3D
# AVANT le switch SELON TYPE PROJET
# ================================================================

old_switch_marker = '''  // ============================================================
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

new_with_appentis = '''  // ============================================================
  // APPENTIS (toit 1 pan accole a un mur arriere haut)
  // ============================================================
  const drawAppentis = () => {
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;            // hauteur cote avant (libre)
    const Hhaut = Ht + denivele; // hauteur mur arriere (simule mur maison)

    // MUR ARRIERE PLEIN ET HAUT (simule un mur existant)
    // On le rend opaque et un peu plus epais pour bien le distinguer
    const murArriereMat = new THREE.MeshLambertMaterial({
      color: 0xd4ccb6,
      transparent: true,
      opacity: 0.85,
      side: THREE.DoubleSide
    });
    addBox(L + 0.5, Hhaut + 0.3, 0.25, 0, (Hhaut + 0.3)/2, lg/2, murArriereMat);

    // 2 POTEAUX AVANT (pour soutenir le toit)
    const sectionPotau = 0.18;
    addBox(sectionPotau, Hbas, sectionPotau, -L/2, Hbas/2, -lg/2);
    addBox(sectionPotau, Hbas, sectionPotau, L/2, Hbas/2, -lg/2);

    // PETITS MURS LATERAUX TRAPEZOIDAUX (option : peuvent etre transparents)
    // Cote gauche
    const triGeoL = new THREE.BufferGeometry();
    const triVertL = new Float32Array([
      -L/2, 0, -lg/2,
      -L/2, Hbas, -lg/2,
      -L/2, Hhaut, lg/2,
      -L/2, 0, -lg/2,
      -L/2, Hhaut, lg/2,
      -L/2, 0, lg/2,
    ]);
    triGeoL.setAttribute("position", new THREE.BufferAttribute(triVertL, 3));
    triGeoL.computeVertexNormals();
    const triMeshL = new THREE.Mesh(triGeoL, wallMat);
    scene.add(triMeshL);

    // Cote droit
    const triGeoR = new THREE.BufferGeometry();
    const triVertR = new Float32Array([
      L/2, 0, -lg/2,
      L/2, Hbas, -lg/2,
      L/2, Hhaut, lg/2,
      L/2, 0, -lg/2,
      L/2, Hhaut, lg/2,
      L/2, 0, lg/2,
    ]);
    triGeoR.setAttribute("position", new THREE.BufferAttribute(triVertR, 3));
    triGeoR.computeVertexNormals();
    const triMeshR = new THREE.Mesh(triGeoR, wallMat);
    scene.add(triMeshR);

    // SABLIERES
    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2);   // sabliere avant (basse)
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2);   // sabliere arriere (haute, contre mur)

    // CHEVRONS en pente (du mur arriere vers l'avant)
    const nbChevrons = Math.max(3, Math.ceil(L / 1.0));
    const ang = Math.atan(denivele / lg);
    const longueurChevron = lg / Math.cos(ang);
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      const yCentre = Hbas + denivele/2;
      addBox(0.10, 0.10, longueurChevron + 0.2, x, yCentre, 0, woodMat, [ang, 0, 0]);
    }

    // 2 PANNES intermediaires
    const nbPannes = 2;
    for (let i = 0; i < nbPannes; i++) {
      const t = (i + 1) / (nbPannes + 1);
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele;
      addBox(L + 0.3, 0.12, 0.12, 0, y, z);
    }

    // TOITURE 1 pan
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
  } else if (typeProjet === "hangar") {
    drawHangar();
  } else if (typeProjet === "appentis") {
    drawAppentis();
  } else {
    drawCharpenteTrad();
  }'''

if "drawAppentis" in content:
    print("[INFO] Appentis deja en place")
elif old_switch_marker in content:
    content = content.replace(old_switch_marker, new_with_appentis, 1)
    print("[OK] drawAppentis() ajoutee + switch mis a jour")
    modifs += 1
else:
    print("[ERREUR] Switch SELON TYPE PROJET non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : yCentre pour appentis
# ================================================================

old_ycentre_block = '''  let yCentre;
  if (typeProjet === "carport" || typeProjet === "monopente") {
    yCentre = Ht + (lg * Math.tan((pente * Math.PI) / 180)) / 2;
  } else if (typeProjet === "hangar") {
    // Hangar : centre plus haut pour bien voir le toit
    yCentre = Ht * 0.7 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
  } else {
    yCentre = Ht/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
  }'''

new_ycentre_block = '''  let yCentre;
  if (typeProjet === "carport" || typeProjet === "monopente" || typeProjet === "appentis") {
    yCentre = Ht + (lg * Math.tan((pente * Math.PI) / 180)) / 2;
  } else if (typeProjet === "hangar") {
    yCentre = Ht * 0.7 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
  } else {
    yCentre = Ht/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
  }'''

if 'typeProjet === "appentis"' in content and "carport" in old_ycentre_block:
    if old_ycentre_block in content:
        content = content.replace(old_ycentre_block, new_ycentre_block, 1)
        print("[OK] yCentre adapte pour appentis")
        modifs += 1
    else:
        print("[INFO] yCentre deja a jour pour appentis")
else:
    if old_ycentre_block in content:
        content = content.replace(old_ycentre_block, new_ycentre_block, 1)
        print("[OK] yCentre adapte pour appentis")
        modifs += 1
    else:
        print("[WARN] Bloc yCentre non trouve")

# ================================================================
# MOD 3 : Detection IA dans detectParams
# ================================================================

old_type_detect = '''    else if (/hangar|grange|batiment.*agricole|grand.*portee|industriel/i.test(text)) out.type = "hangar";'''

new_type_detect = '''    else if (/hangar|grange|batiment.*agricole|grand.*portee|industriel/i.test(text)) out.type = "hangar";
    else if (/appentis|accole|contre.*mur|abri.*bois|terrasse.*couvert/i.test(text)) out.type = "appentis";'''

if 'out.type = "appentis"' in content:
    print("[INFO] Detection appentis deja presente")
elif old_type_detect in content:
    content = content.replace(old_type_detect, new_type_detect, 1)
    print("[OK] Detection 'appentis' ajoutee dans detectParams")
    modifs += 1
else:
    print("[WARN] Bloc detection type non trouve")

# ================================================================
# MOD 4 : Prompt IA avec ratios appentis
# ================================================================

old_hangar_prompt = 'Pour un hangar (batiment agricole, grande portee, poteaux + 2 pans) : 0.3-0.5h fabrication par m2 + 0.25-0.4h pose par m2.'

new_with_appentis_prompt = 'Pour un hangar (batiment agricole, grande portee, poteaux + 2 pans) : 0.3-0.5h fabrication par m2 + 0.25-0.4h pose par m2. Pour un appentis (toit accole a mur existant, terrasse couverte, abri a bois) : 0.4-0.6h fabrication par m2 + 0.35-0.5h pose par m2.'

if "appentis (toit accole" in content:
    print("[INFO] Prompt IA deja a jour pour appentis")
elif old_hangar_prompt in content:
    content = content.replace(old_hangar_prompt, new_with_appentis_prompt, 1)
    print("[OK] Prompt IA enrichi avec ratios appentis")
    modifs += 1
else:
    print("[WARN] Phrase hangar dans prompt non trouvee")

# ================================================================
# MOD 5 : Option Appentis dans QUESTIONS
# ================================================================

old_hangar_option = '{ val: "hangar", label: "Hangar / Batiment agricole", icon: "factory" },'

new_with_appentis_option = '''{ val: "hangar", label: "Hangar / Batiment agricole", icon: "factory" },
{ val: "appentis", label: "Appentis (accole a un mur)", icon: "home" },'''

if 'val: "appentis"' in content:
    print("[INFO] Option appentis deja dans QUESTIONS")
elif old_hangar_option in content:
    content = content.replace(old_hangar_option, new_with_appentis_option, 1)
    print("[OK] Option Appentis ajoutee dans QuestionsScreen")
    modifs += 1
else:
    print("[WARN] Option hangar non trouvee")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. drawAppentis() ajoutee dans buildScene3D")
print("  2. Switch type_projet inclut maintenant 'appentis'")
print("  3. yCentre adapte (centre haut pour bien voir le toit)")
print("  4. detectParams reconnait 'appentis', 'accole', 'abri a bois', 'terrasse couverte'")
print("  5. Prompt IA enrichi avec ratios appentis")
print("  6. Option 'Appentis (accole a un mur)' ajoutee dans QuestionsScreen")
print()
print("STRUCTURE APPENTIS :")
print("  - MUR ARRIERE PLEIN HAUT (couleur creme, simule mur maison)")
print("  - 2 poteaux avant (cote libre)")
print("  - Petits murs lateraux trapezoidaux (semi-transparents)")
print("  - Sablieres (avant basse + arriere haute)")
print("  - Chevrons en pente")
print("  - 2 pannes intermediaires")
print("  - Toiture 1 pan")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
