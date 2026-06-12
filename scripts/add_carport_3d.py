#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Etape 1.2.B + 1.2.C : 3D adaptive (carport vs charpente_trad)
Modifie devia.jsx pour :
1. Restructurer Viewer3D pour switcher selon type_projet
2. Garder le rendu charpente traditionnelle existant (renomme drawCharpenteTrad)
3. Ajouter une nouvelle fonction drawCarport (1 pente + potaux)

A lancer depuis ~/Desktop/devia :
    python3 add_carport_3d.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("package.json"):
    print("ERREUR : package.json introuvable. Lance depuis ~/Desktop/devia")
    sys.exit(1)

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_carport_3d"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# Reperer le bloc Viewer3D actuel (lignes 67 a 140 environ)
# On va remplacer le contenu de la fonction Viewer3D par une version qui switch
# ================================================================

# On cherche le debut et la fin de Viewer3D
viewer_start = "function Viewer3D({ params }) {"
viewer_end_marker = "return <div ref={mountRef} style={{ width: \"100%\", height: \"100%\", borderRadius: 8 }} />;\n}"

if viewer_start not in content:
    print("ERREUR : impossible de trouver function Viewer3D.")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

if viewer_end_marker not in content:
    print("ERREUR : impossible de trouver la fin de Viewer3D.")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

# Verifier si deja modifie
if "drawCarport" in content:
    print("[INFO] drawCarport deja present, skip modification")
    print("       Le fichier semble deja avoir la 3D adaptive.")
    sys.exit(0)

# Trouver les positions exactes
start_idx = content.find(viewer_start)
end_idx = content.find(viewer_end_marker, start_idx) + len(viewer_end_marker)

old_viewer_block = content[start_idx:end_idx]
print(f"[INFO] Bloc Viewer3D detecte : {len(old_viewer_block)} caracteres")

# Nouveau bloc Viewer3D avec switching
new_viewer_block = '''function Viewer3D({ params }) {
  const mountRef = useRef(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const w = mountRef.current.clientWidth;
    const h = mountRef.current.clientHeight;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.shadowMap.enabled = true;
    mountRef.current.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 200);
    camera.position.set(12, 8, 12);

    scene.add(new THREE.AmbientLight(0xffffff, 0.4));
    const sun = new THREE.DirectionalLight(0xfff8e7, 1.2);
    sun.position.set(10, 20, 10);
    sun.castShadow = true;
    scene.add(sun);

    const L = params.longueur || 8;
    const lg = params.largeur || 6;
    const H = params.hauteur || 3;
    const pente = params.pente || 35;
    const typeProjet = params.type_projet || "charpente_trad";

    const woodMat = new THREE.MeshLambertMaterial({ color: 0xc4894a });
    const roofMat = new THREE.MeshLambertMaterial({ color: 0x8b6355, side: THREE.DoubleSide });
    const wallMat = new THREE.MeshLambertMaterial({ color: 0xf0ece0, transparent: true, opacity: 0.2, side: THREE.DoubleSide });

    const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
      const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), mat || woodMat);
      m.position.set(px, py, pz);
      if (rot) m.rotation.set(...rot);
      m.castShadow = true;
      scene.add(m);
    };

    // ============================================================
    // FONCTION : dessine une charpente traditionnelle (2 pans)
    // ============================================================
    const drawCharpenteTrad = () => {
      const hf = lg / 2 * Math.tan((pente * Math.PI) / 180);

      // Murs (4 cotes)
      [
        [L, H, 0.15, 0, H/2, lg/2],
        [L, H, 0.15, 0, H/2, -lg/2],
        [0.15, H, lg, -L/2, H/2, 0],
        [0.15, H, lg, L/2, H/2, 0]
      ].forEach(([sx, sy, sz, px, py, pz]) => addBox(sx, sy, sz, px, py, pz, wallMat));

      // Fermes
      const nb = Math.max(2, Math.ceil(L / 2.5));
      for (let i = 0; i <= nb; i++) {
        const x = -L/2 + (i/nb) * L;
        const ang = Math.atan(hf / (lg/2));
        const pl = (lg/2) / Math.cos(ang);
        addBox(pl, 0.12, 0.12, x, H + hf/2, lg/4, woodMat, [ang, 0, 0]);
        addBox(pl, 0.12, 0.12, x, H + hf/2, -lg/4, woodMat, [-ang, 0, 0]);
        addBox(0.12, hf + 0.1, 0.12, x, H + hf/2, 0);
      }

      // Faitage
      addBox(L + 0.4, 0.14, 0.14, 0, H + hf, 0);

      // Toiture (2 pans)
      const ang = Math.atan(hf / (lg/2));
      const pl = (lg/2) / Math.cos(ang);
      const rg = new THREE.PlaneGeometry(L + 0.6, pl + 0.2);
      const r1 = new THREE.Mesh(rg, roofMat);
      r1.position.set(0, H + hf/2, lg/4);
      r1.rotation.x = ang - Math.PI/2;
      scene.add(r1);
      const r2 = new THREE.Mesh(rg, roofMat);
      r2.position.set(0, H + hf/2, -lg/4);
      r2.rotation.x = -(ang - Math.PI/2);
      scene.add(r2);
    };

    // ============================================================
    // FONCTION : dessine un carport (1 pente + potaux + pas de murs)
    // ============================================================
    const drawCarport = () => {
      // Carport : la pente est sur la largeur (axe Z)
      // Cote bas a -lg/2, cote haut a +lg/2
      const denivele = lg * Math.tan((pente * Math.PI) / 180);
      const Hbas = H;
      const Hhaut = H + denivele;

      // 4 POTAUX (un a chaque coin)
      const sectionPotau = 0.18;
      // Potau bas avant gauche
      addBox(sectionPotau, Hbas, sectionPotau, -L/2, Hbas/2, -lg/2);
      // Potau bas avant droit
      addBox(sectionPotau, Hbas, sectionPotau, L/2, Hbas/2, -lg/2);
      // Potau haut arriere gauche
      addBox(sectionPotau, Hhaut, sectionPotau, -L/2, Hhaut/2, lg/2);
      // Potau haut arriere droit
      addBox(sectionPotau, Hhaut, sectionPotau, L/2, Hhaut/2, lg/2);

      // 2 SABLIERES (poutres horizontales en haut, sens longueur)
      // Sabliere cote bas (avant)
      addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2);
      // Sabliere cote haut (arriere)
      addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2);

      // PANNES (poutres horizontales perpendiculaires aux sablieres, suivent la pente)
      // On en met 3 : panne basse, intermediaire, haute
      const nbPannes = 3;
      for (let i = 0; i < nbPannes; i++) {
        const t = i / (nbPannes - 1); // 0 a 1
        const z = -lg/2 + t * lg;
        const y = Hbas + t * denivele;
        addBox(L + 0.3, 0.14, 0.14, 0, y, z);
      }

      // CHEVRONS (poses sur les pannes, sens largeur, en pente)
      const nbChevrons = Math.max(3, Math.ceil(L / 1.0));
      const ang = Math.atan(denivele / lg);
      const longueurChevron = lg / Math.cos(ang);
      for (let i = 0; i <= nbChevrons; i++) {
        const x = -L/2 + (i / nbChevrons) * L;
        // Chevron centre verticalement entre Hbas et Hhaut, position Z = 0
        const yCentre = Hbas + denivele/2;
        addBox(0.10, 0.10, longueurChevron + 0.2, x, yCentre, 0, woodMat, [ang, 0, 0]);
      }

      // TOITURE (1 seul pan)
      const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
      const roof = new THREE.Mesh(rg, roofMat);
      roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
      roof.rotation.x = ang - Math.PI/2;
      scene.add(roof);
    };

    // ============================================================
    // SWITCH : choisir la fonction selon type_projet
    // ============================================================
    if (typeProjet === "carport") {
      drawCarport();
    } else {
      drawCharpenteTrad();
    }

    // SOL (commun a tous les types)
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(30, 30),
      new THREE.MeshLambertMaterial({ color: 0x1a1f2e })
    );
    ground.rotation.x = -Math.PI/2;
    scene.add(ground);

    // ANIMATION (rotation camera)
    let angle = 0, animId;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      angle += 0.005;
      camera.position.x = Math.cos(angle) * 16;
      camera.position.z = Math.sin(angle) * 16;
      // Centre de la camera : adapter selon type
      const yCentre = typeProjet === "carport"
        ? H + (lg * Math.tan((pente * Math.PI) / 180)) / 2
        : H/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
      camera.lookAt(0, yCentre, 0);
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(animId);
      renderer.dispose();
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current)
        mountRef.current.removeChild(renderer.domElement);
    };
  }, [params]);

  return <div ref={mountRef} style={{ width: "100%", height: "100%", borderRadius: 8 }} />;
}'''

content = content[:start_idx] + new_viewer_block + content[end_idx:]
print("[OK] Viewer3D restructure avec switching carport / charpente_trad")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("ETAPE 1.2.B + 1.2.C APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Viewer3D restructure proprement avec 2 fonctions :")
print("     - drawCharpenteTrad : ancien rendu (preserve)")
print("     - drawCarport : nouveau rendu (4 potaux + 1 pente)")
print("  2. Switching automatique selon type_projet detecte par l'IA")
print()
print("PROCHAINE ETAPE :")
print("  1. Push sur GitHub :")
print("     git add devia.jsx")
print("     git commit -m '3D adaptive : carport vs charpente_trad'")
print("     git push")
print("  2. Attendre redeploiement (1-2 min)")
print("  3. Tester sur devia-iota.vercel.app :")
print("     - Generer 'Carport 6x4m 1 pente 30%' -> doit afficher CARPORT")
print("     - Generer 'Charpente trad 10x8m sapin pente 35deg' -> CHARPENTE 2 PANS")
print()
print(f"BACKUP : {backup_name}")
