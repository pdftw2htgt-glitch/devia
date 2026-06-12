#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D A2.2.4 : Ajout type 4 PANS (toit en croupe)
- 4 murs
- Faitage central COURT (plus court que la longueur)
- 2 grands pans trapezoidaux (avant/arriere)
- 2 croupes triangulaires (sur les cotes courts)
- Aretiers (aretes diagonales) + quelques chevrons
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_4pans"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter draw4Pans() dans buildScene3D
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
  } else if (typeProjet === "appentis") {
    drawAppentis();
  } else {
    drawCharpenteTrad();
  }'''

new_with_4pans = '''  // ============================================================
  // 4 PANS (toit en croupe)
  // ============================================================
  const draw4Pans = () => {
    const hf = lg / 2 * Math.tan((pente * Math.PI) / 180); // hauteur faitage
    // Longueur du faitage : plus court que L (recule de lg/2 de chaque cote)
    const retraitCroupe = lg / 2;
    const Lfait = Math.max(0.5, L - 2 * retraitCroupe);

    // MURS (4 cotes)
    [
      [L, Ht, 0.15, 0, Ht/2, lg/2],
      [L, Ht, 0.15, 0, Ht/2, -lg/2],
      [0.15, Ht, lg, -L/2, Ht/2, 0],
      [0.15, Ht, lg, L/2, Ht/2, 0]
    ].forEach(([sx, sy, sz, px, py, pz]) => addBox(sx, sy, sz, px, py, pz, wallMat));

    // FAITAGE (central, court)
    addBox(Lfait, 0.14, 0.14, 0, Ht + hf, 0);

    // Points cles du faitage
    const xFaitGauche = -Lfait/2;
    const xFaitDroit = Lfait/2;
    const yFait = Ht + hf;

    // ===== 2 GRANDS PANS (avant Z+ et arriere Z-) =====
    // Chaque grand pan est un trapeze. On l'approxime avec une geometrie custom.
    const angLong = Math.atan(hf / (lg/2));
    const plLong = (lg/2) / Math.cos(angLong);

    // Grand pan AVANT (Z+)
    const panAvGeo = new THREE.BufferGeometry();
    const panAvVerts = new Float32Array([
      // Trapeze : 2 points bas (eaves) + 2 points haut (faitage)
      -L/2, Ht, lg/2,        // bas gauche
       L/2, Ht, lg/2,        // bas droit
       xFaitDroit, yFait, 0, // haut droit (faitage)
      -L/2, Ht, lg/2,        // bas gauche
       xFaitDroit, yFait, 0, // haut droit
       xFaitGauche, yFait, 0,// haut gauche
    ]);
    panAvGeo.setAttribute("position", new THREE.BufferAttribute(panAvVerts, 3));
    panAvGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(panAvGeo, roofMat));

    // Grand pan ARRIERE (Z-)
    const panArGeo = new THREE.BufferGeometry();
    const panArVerts = new Float32Array([
      -L/2, Ht, -lg/2,
       xFaitGauche, yFait, 0,
       xFaitDroit, yFait, 0,
      -L/2, Ht, -lg/2,
       xFaitDroit, yFait, 0,
       L/2, Ht, -lg/2,
    ]);
    panArGeo.setAttribute("position", new THREE.BufferAttribute(panArVerts, 3));
    panArGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(panArGeo, roofMat));

    // ===== 2 CROUPES (triangles sur cotes courts) =====
    // Croupe GAUCHE (X-)
    const croupeGGeo = new THREE.BufferGeometry();
    const croupeGVerts = new Float32Array([
      -L/2, Ht, -lg/2,
      -L/2, Ht, lg/2,
      xFaitGauche, yFait, 0,
    ]);
    croupeGGeo.setAttribute("position", new THREE.BufferAttribute(croupeGVerts, 3));
    croupeGGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(croupeGGeo, roofMat));

    // Croupe DROITE (X+)
    const croupeDGeo = new THREE.BufferGeometry();
    const croupeDVerts = new Float32Array([
      L/2, Ht, -lg/2,
      xFaitDroit, yFait, 0,
      L/2, Ht, lg/2,
    ]);
    croupeDGeo.setAttribute("position", new THREE.BufferAttribute(croupeDVerts, 3));
    croupeDGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(croupeDGeo, roofMat));

    // ===== ARETIERS (4 aretes diagonales des coins vers le faitage) =====
    const aretiers = [
      [-L/2, Ht, lg/2, xFaitGauche, yFait, 0],   // coin avant-gauche -> faitage gauche
      [-L/2, Ht, -lg/2, xFaitGauche, yFait, 0],  // coin arriere-gauche -> faitage gauche
      [L/2, Ht, lg/2, xFaitDroit, yFait, 0],     // coin avant-droit -> faitage droit
      [L/2, Ht, -lg/2, xFaitDroit, yFait, 0],    // coin arriere-droit -> faitage droit
    ];
    aretiers.forEach(([x1, y1, z1, x2, y2, z2]) => {
      const dx = x2 - x1, dy = y2 - y1, dz = z2 - z1;
      const len = Math.sqrt(dx*dx + dy*dy + dz*dz);
      const cx = (x1 + x2) / 2, cy = (y1 + y2) / 2, cz = (z1 + z2) / 2;
      const aretier = new THREE.Mesh(
        new THREE.BoxGeometry(0.12, 0.12, len),
        woodMat
      );
      aretier.position.set(cx, cy, cz);
      // Orienter l'aretier le long du vecteur
      const dir = new THREE.Vector3(dx, dy, dz).normalize();
      const quaternion = new THREE.Quaternion();
      quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), dir);
      aretier.quaternion.copy(quaternion);
      scene.add(aretier);
    });

    // ===== QUELQUES PANNES sur les grands pans =====
    const nbPannes = 2;
    for (let i = 1; i <= nbPannes; i++) {
      const t = i / (nbPannes + 1);
      const yPanne = Ht + hf * t;
      const zPanne = (lg/2) * (1 - t);
      // Panne sur pan avant
      addBox(Lfait + (L - Lfait) * (1 - t), 0.1, 0.1, 0, yPanne, zPanne);
      // Panne sur pan arriere
      addBox(Lfait + (L - Lfait) * (1 - t), 0.1, 0.1, 0, yPanne, -zPanne);
    }
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
  } else if (typeProjet === "4_pans") {
    draw4Pans();
  } else {
    drawCharpenteTrad();
  }'''

if "draw4Pans" in content:
    print("[INFO] 4 pans deja en place")
elif old_switch_marker in content:
    content = content.replace(old_switch_marker, new_with_4pans, 1)
    print("[OK] draw4Pans() ajoutee + switch mis a jour")
    modifs += 1
else:
    print("[ERREUR] Switch SELON TYPE PROJET non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : yCentre pour 4_pans (comme charpente_trad)
# ================================================================

old_ycentre_block = '''  let yCentre;
  if (typeProjet === "carport" || typeProjet === "monopente" || typeProjet === "appentis") {
    yCentre = Ht + (lg * Math.tan((pente * Math.PI) / 180)) / 2;
  } else if (typeProjet === "hangar") {
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
    // charpente_trad ET 4_pans
    yCentre = Ht/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
  }'''

if "charpente_trad ET 4_pans" in content:
    print("[INFO] yCentre deja commente pour 4_pans")
elif old_ycentre_block in content:
    content = content.replace(old_ycentre_block, new_ycentre_block, 1)
    print("[OK] yCentre OK pour 4_pans (utilise le else commun)")
    modifs += 1
else:
    print("[INFO] yCentre : 4_pans utilise deja le else par defaut (OK)")

# ================================================================
# MOD 3 : Detection IA dans detectParams
# ================================================================

old_type_detect = '''    else if (/appentis|accole|contre.*mur|abri.*bois|terrasse.*couvert/i.test(text)) out.type = "appentis";'''

new_type_detect = '''    else if (/appentis|accole|contre.*mur|abri.*bois|terrasse.*couvert/i.test(text)) out.type = "appentis";
    else if (/4 pans|quatre pans|croupe|toit.*croupe|pavillon/i.test(text)) out.type = "4_pans";'''

if 'out.type = "4_pans"' in content:
    print("[INFO] Detection 4_pans deja presente")
elif old_type_detect in content:
    content = content.replace(old_type_detect, new_type_detect, 1)
    print("[OK] Detection '4 pans / croupe' ajoutee dans detectParams")
    modifs += 1
else:
    print("[WARN] Bloc detection type non trouve")

# ================================================================
# MOD 4 : Prompt IA - ajouter 4_pans dans la detection
# ================================================================

old_appentis_prompt_line = '''"'appentis' (toit 1 pan ACCOLE a un mur existant, terrasse couverte, abri a bois contre une maison), " +'''

new_with_4pans_prompt = '''"'appentis' (toit 1 pan ACCOLE a un mur existant, terrasse couverte, abri a bois contre une maison), " +
"'4_pans' (toit en croupe a 4 pentes, maison pavillon, toit avec aretiers), " +'''

if "'4_pans' (toit en croupe" in content:
    print("[INFO] Prompt IA deja a jour pour 4_pans")
elif old_appentis_prompt_line in content:
    content = content.replace(old_appentis_prompt_line, new_with_4pans_prompt, 1)
    print("[OK] Prompt IA enrichi avec 4_pans")
    modifs += 1
else:
    print("[WARN] Ligne appentis dans prompt non trouvee")

# ================================================================
# MOD 5 : Exemple JSON type_projet
# ================================================================

old_json_type = '"type_projet":"carport_OU_charpente_trad_OU_monopente_OU_hangar_OU_appentis_OU_abri_OU_autre"'
new_json_type = '"type_projet":"carport_OU_charpente_trad_OU_monopente_OU_hangar_OU_appentis_OU_4_pans_OU_abri_OU_autre"'

if "4_pans_OU_abri" in content:
    print("[INFO] Exemple JSON deja a jour")
elif old_json_type in content:
    content = content.replace(old_json_type, new_json_type, 1)
    print("[OK] Exemple JSON type_projet mis a jour")
    modifs += 1
else:
    print("[WARN] Exemple JSON non trouve")

# ================================================================
# MOD 6 : Option 4 pans dans QUESTIONS
# ================================================================

old_appentis_option = '{ val: "appentis", label: "Appentis (accole a un mur)", icon: "home" },'

new_with_4pans_option = '''{ val: "appentis", label: "Appentis (accole a un mur)", icon: "home" },
{ val: "4_pans", label: "Toit 4 pans (croupe)", icon: "home" },'''

if 'val: "4_pans"' in content:
    print("[INFO] Option 4_pans deja dans QUESTIONS")
elif old_appentis_option in content:
    content = content.replace(old_appentis_option, new_with_4pans_option, 1)
    print("[OK] Option 'Toit 4 pans' ajoutee dans QuestionsScreen")
    modifs += 1
else:
    print("[WARN] Option appentis non trouvee")

# ================================================================
# MOD 7 : Ratios temps 4_pans dans le prompt
# ================================================================

old_appentis_ratio = 'Pour un appentis (toit accole a mur existant, terrasse couverte, abri a bois) : 0.4-0.6h fabrication par m2 + 0.35-0.5h pose par m2.'

new_with_4pans_ratio = 'Pour un appentis (toit accole a mur existant, terrasse couverte, abri a bois) : 0.4-0.6h fabrication par m2 + 0.35-0.5h pose par m2. Pour un toit 4 pans / croupe (plus complexe, aretiers) : 1.0-1.4h fabrication par m2 + 0.6-0.9h pose par m2.'

if "4 pans / croupe (plus complexe" in content:
    print("[INFO] Ratio 4_pans deja present")
elif old_appentis_ratio in content:
    content = content.replace(old_appentis_ratio, new_with_4pans_ratio, 1)
    print("[OK] Ratio temps 4_pans ajoute au prompt")
    modifs += 1
else:
    print("[WARN] Ratio appentis non trouve")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. draw4Pans() ajoutee (toit en croupe)")
print("  2. yCentre OK (utilise calcul charpente_trad)")
print("  3. detectParams reconnait '4 pans', 'croupe', 'pavillon'")
print("  4. Prompt IA enrichi avec type 4_pans")
print("  5. Exemple JSON mis a jour")
print("  6. Option 'Toit 4 pans (croupe)' dans QuestionsScreen")
print("  7. Ratio temps 4_pans (plus eleve car complexe)")
print()
print("STRUCTURE 4 PANS :")
print("  - 4 murs")
print("  - Faitage central COURT")
print("  - 2 grands pans trapezoidaux (avant/arriere)")
print("  - 2 croupes triangulaires (cotes courts)")
print("  - 4 aretiers diagonaux (coins -> faitage)")
print("  - Pannes")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
