#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Branchement complet de la couverture (etape 2)

1) view3DParams recoit 'couverture' dans les 2 remplissages
   (+ 'type_projet' manquant dans le 2eme)
2) Viewer3D passe opts={ couverture } a buildScene3D (le fil manquant principal)
3) capture3DViews (PDF) passe couverture dans son opts
4) monopente / appentis / 4pans rebranches sur le registre COUVERTURES

Chaque modif est conditionnelle et reportee individuellement (robuste).
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

if "const COUVERTURES = {" not in open("devia.jsx", encoding="utf-8").read():
    print("ERREUR : registre COUVERTURES absent. Lance d'abord registre_couvertures.py")
    sys.exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_branchement_couverture"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

def apply(old, new, label):
    global content, modifs
    n = content.count(old)
    if n == 1:
        content = content.replace(old, new, 1)
        print(f"[OK] {label}")
        modifs += 1
    elif n == 0:
        print(f"[WARN] {label} : motif NON trouve (deja fait ?)")
    else:
        print(f"[WARN] {label} : motif trouve {n} fois (ambigu) -> ignore")

# ----------------------------------------------------------------
# 1) Remplissage #1 de view3DParams (depuis l'IA)
# ----------------------------------------------------------------
apply(
    '''        longueur: p.longueur || 10,
        largeur: p.largeur || 8,
        hauteur: p.hauteur || 3,
        pente: p.pente || 35,
        type_projet: p.type_projet || "autre"
      });''',
    '''        longueur: p.longueur || 10,
        largeur: p.largeur || 8,
        hauteur: p.hauteur || 3,
        pente: p.pente || 35,
        type_projet: p.type_projet || "autre",
        couverture: p.couverture || "tuile_terre"
      });''',
    "Remplissage #1 (IA) : + couverture"
)

# ----------------------------------------------------------------
# 2) Remplissage #2 de view3DParams (depuis projet sauve)
#    (manque aussi type_projet)
# ----------------------------------------------------------------
apply(
    '''      setView3DParams({
        longueur: p.longueur || 10,
        largeur: p.largeur || 8,
        hauteur: p.hauteur || 3,
        pente: p.pente || 35
      });''',
    '''      setView3DParams({
        longueur: p.longueur || 10,
        largeur: p.largeur || 8,
        hauteur: p.hauteur || 3,
        pente: p.pente || 35,
        type_projet: p.type_projet || "autre",
        couverture: p.couverture || "tuile_terre"
      });''',
    "Remplissage #2 (projet sauve) : + type_projet + couverture"
)

# ----------------------------------------------------------------
# 3) Viewer3D : passer opts={ couverture } a buildScene3D
# ----------------------------------------------------------------
apply(
    "const buildResultViewer = buildScene3D(scene, params);",
    "const buildResultViewer = buildScene3D(scene, params, { couverture: params.couverture });",
    "Viewer3D : opts.couverture transmis (fil manquant principal)"
)

# ----------------------------------------------------------------
# 4) capture3DViews (PDF) : ajouter couverture dans l'opts
# ----------------------------------------------------------------
apply(
    '''  const buildResult = buildScene3D(scene, view3DParams, {
    woodColor: 0xa8743a,
    roofColor: 0x6b4a3f,
    wallColor: 0xd8d2c0,
    wallOpacity: 0.25
  });''',
    '''  const buildResult = buildScene3D(scene, view3DParams, {
    woodColor: 0xa8743a,
    roofColor: 0x6b4a3f,
    wallColor: 0xd8d2c0,
    wallOpacity: 0.25,
    couverture: view3DParams.couverture
  });''',
    "capture3DViews (PDF) : + couverture"
)

# ----------------------------------------------------------------
# 5) Rebrancher MONOPENTE sur le registre
# ----------------------------------------------------------------
apply(
    '''    const typeCouv = (opts && opts.couverture) ? opts.couverture : "tuile_terre";
    let couvColor;
    if (typeCouv === "bac_acier") {
      couvColor = 0x3a3a3f;  // anthracite
    } else if (typeCouv === "tuile_beton") {
      couvColor = 0x8b6355;  // brun-gris
    } else {
      couvColor = 0xc87650;  // tuile terre cuite (defaut)
    }''',
    '''    const couv = getCouverture(opts && opts.couverture);
    const couvColor = couv.couleur;''',
    "Monopente : couleur depuis registre"
)
apply(
    "    const espChevron = 0.5;",
    "    const espChevron = couv.espChevron;",
    "Monopente : espChevron depuis registre"
)
apply(
    "    const espLiteau = 0.35;",
    "    const espLiteau = couv.espLiteau;",
    "Monopente : espLiteau depuis registre"
)

# ----------------------------------------------------------------
# 6) Rebrancher APPENTIS sur le registre
# ----------------------------------------------------------------
apply(
    '''    const typeCouv = (opts && opts.couverture) ? opts.couverture : "tuile_terre";
    let couvColor, espChevron, espLiteau;
    if (typeCouv === "bac_acier") {
      couvColor = 0x3a3a3f;  espChevron = 0.70;  espLiteau = 0.50;  // porte loin
    } else if (typeCouv === "tuile_beton") {
      couvColor = 0x8b6355;  espChevron = 0.45;  espLiteau = 0.32;  // lourde
    } else {
      couvColor = 0xc87650;  espChevron = 0.50;  espLiteau = 0.35;  // tuile terre
    }''',
    '''    const couv = getCouverture(opts && opts.couverture);
    const couvColor = couv.couleur;
    const espChevron = couv.espChevron;
    const espLiteau = couv.espLiteau;''',
    "Appentis : couleur + espacements depuis registre"
)

# ----------------------------------------------------------------
# 7) Rebrancher 4 PANS sur le registre
# ----------------------------------------------------------------
apply(
    '''    const typeCouv = (opts && opts.couverture) ? opts.couverture : "tuile_terre";
    let couvColor, espChevron, espLiteau;
    if (typeCouv === "bac_acier") {
      couvColor = 0x3a3a3f;  espChevron = 0.70;  espLiteau = 0.50;
    } else if (typeCouv === "tuile_beton") {
      couvColor = 0x8b6355;  espChevron = 0.45;  espLiteau = 0.32;
    } else {
      couvColor = 0xc87650;  espChevron = 0.50;  espLiteau = 0.35;
    }''',
    '''    const couv = getCouverture(opts && opts.couverture);
    const couvColor = couv.couleur;
    const espChevron = couv.espChevron;
    const espLiteau = couv.espLiteau;''',
    "4 pans : couleur + espacements depuis registre"
)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)")
print("=" * 60)
print()
print("La couverture est maintenant branchee de bout en bout :")
print("  formulaire -> view3DParams -> opts -> registre -> rendu 3D")
print()
print("Tu devrais voir la couleur ET la densite des chevrons changer")
print("selon la couverture choisie (tuile / ardoise / bac acier / etc.)")
print()
print("PROCHAINE ETAPE :  npm run build")
print()
print(f"BACKUP : {backup}")
