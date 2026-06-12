#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable."); sys.exit(1)

content = open("devia.jsx", encoding="utf-8").read()
if "const COUVERTURES = {" in content:
    print("[INFO] Registre deja present."); sys.exit(0)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_registre"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

registre = '''  // ============================================================
  // REGISTRE DES COUVERTURES (source unique de verite)
  // ============================================================
  const COUVERTURES = {
    tuile_terre: { label: "Tuile terre cuite", couleur: 0xc87650, espChevron: 0.50, espLiteau: 0.35, penteMin: 30, poids: 45, prixM2: null },
    tuile_beton: { label: "Tuile beton", couleur: 0x8b6355, espChevron: 0.45, espLiteau: 0.32, penteMin: 25, poids: 48, prixM2: null },
    ardoise: { label: "Ardoise", couleur: 0x4a4f57, espChevron: 0.45, espLiteau: 0.33, penteMin: 22, poids: 30, prixM2: null },
    bac_acier: { label: "Bac acier", couleur: 0x3a3a3f, espChevron: 0.70, espLiteau: 0.50, penteMin: 7, poids: 10, prixM2: null },
    zinc: { label: "Zinc (joint debout)", couleur: 0x9aa0a6, espChevron: 0.60, espLiteau: 0.45, penteMin: 5, poids: 12, prixM2: null },
    shingle: { label: "Shingle / bardeau bitume", couleur: 0x5a4632, espChevron: 0.45, espLiteau: 0.32, penteMin: 18, poids: 12, prixM2: null },
    fibrociment: { label: "Fibrociment ondule", couleur: 0xb8bcc0, espChevron: 0.90, espLiteau: 0.60, penteMin: 12, poids: 18, prixM2: null },
  };
  const getCouverture = (code) => COUVERTURES[code] || COUVERTURES.tuile_terre;

'''

anchor = "  // ============================================================\n  // CHARPENTE TRADITIONNELLE (2 pans)"
idx = content.find(anchor)
if idx == -1:
    print("[ERREUR] Ancre introuvable."); sys.exit(1)

content = content[:idx] + registre + content[idx:]
open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] Registre COUVERTURES insere")
print("1 MODIFICATION APPLIQUEE")
