#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Metre 3A : remontee du metre + agregation (pas d'affichage encore)"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()
modifs = 0
def apply(old, new, label):
    global content, modifs
    n = content.count(old)
    if n == 1:
        content = content.replace(old, new, 1); print(f"[OK] {label}"); modifs += 1
    elif n == 0: print(f"[WARN] {label} : NON trouve")
    else: print(f"[WARN] {label} : {n}x ambigu -> ignore")

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_metre_3a"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) Fonction d'agregation, inseree juste avant le composant Viewer3D
agg = '''// ============================================================
// AGREGATION DU METRE (regroupe par type de piece + totaux)
// ============================================================
function agregerMetre(metre, densiteBois) {
  if (!metre || metre.length === 0) return { groupes: [], totalVolume: 0, totalPoids: 0, nbPieces: 0 };
  const map = {};
  metre.forEach((p) => {
    // cle = nom + section (pour distinguer p.ex. chevrons de sections differentes)
    const secKey = p.section[0] + "x" + p.section[1];
    const key = p.nom + "|" + secKey;
    if (!map[key]) {
      map[key] = {
        nom: p.nom,
        section: p.section,        // [mm, mm]
        nombre: 0,
        longueurTotale: 0,         // m
        longueurUnitMax: 0,        // m (plus longue piece du groupe)
        volume: 0,                 // m3
      };
    }
    map[key].nombre += 1;
    map[key].longueurTotale += p.longueur;
    map[key].longueurUnitMax = Math.max(map[key].longueurUnitMax, p.longueur);
    map[key].volume += p.volume;
  });
  const groupes = Object.values(map).map((g) => ({
    ...g,
    longueurMoy: g.longueurTotale / g.nombre,
    poids: g.volume * densiteBois,   // kg
  })).sort((a, b) => b.volume - a.volume);
  const totalVolume = groupes.reduce((s, g) => s + g.volume, 0);
  const totalPoids = groupes.reduce((s, g) => s + g.poids, 0);
  const nbPieces = groupes.reduce((s, g) => s + g.nombre, 0);
  return { groupes, totalVolume, totalPoids, nbPieces };
}

'''
apply("function Viewer3D({ params }) {", agg + "function Viewer3D({ params }) {", "Fonction agregerMetre inseree")

# 2) Viewer3D accepte un callback onMetre
apply(
    "function Viewer3D({ params }) {\n  const mountRef = useRef(null);",
    "function Viewer3D({ params, onMetre }) {\n  const mountRef = useRef(null);",
    "Viewer3D : prop onMetre ajoutee"
)

# 3) Apres le build, remonter le metre via onMetre
apply(
    "    const buildResultViewer = buildScene3D(scene, params, { couverture: params.couverture, mode: params.mode3D });",
    '''    const buildResultViewer = buildScene3D(scene, params, { couverture: params.couverture, mode: params.mode3D });
    if (onMetre && buildResultViewer.metre) {
      onMetre(agregerMetre(buildResultViewer.metre, buildResultViewer.densiteBois || 450));
    }''',
    "Remontee du metre via onMetre"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
