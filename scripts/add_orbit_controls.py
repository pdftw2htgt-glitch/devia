#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - 3D A1 : Camera interactive (OrbitControls)
- Importer OrbitControls
- Remplacer l'animation auto par drag/zoom
- Garder une rotation lente initiale qui s'arrete au premier mouvement
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_orbit_controls"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Importer OrbitControls
# ================================================================

old_three_import = 'import * as THREE from "three";'
new_three_imports = '''import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";'''

if "OrbitControls" in content:
    print("[INFO] OrbitControls deja importe")
elif old_three_import in content:
    content = content.replace(old_three_import, new_three_imports, 1)
    print("[OK] Import OrbitControls ajoute")
    modifs += 1
else:
    print("[ERREUR] Import THREE non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Remplacer l'animation auto par OrbitControls
# Cible le bloc "ANIMATION (rotation camera)"
# ================================================================

old_animation = '''    // ANIMATION (rotation camera)
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
    };'''

new_orbit_controls = '''    // ============================================================
    // CAMERA INTERACTIVE (OrbitControls)
    // ============================================================

    // Centre cible de la camera (adapte selon type)
    const yCentre = typeProjet === "carport"
      ? H + (lg * Math.tan((pente * Math.PI) / 180)) / 2
      : H/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;

    // Configuration OrbitControls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, yCentre, 0);
    controls.enableDamping = true;          // mouvement fluide
    controls.dampingFactor = 0.08;
    controls.rotateSpeed = 0.6;
    controls.zoomSpeed = 0.8;
    controls.panSpeed = 0.5;
    controls.minDistance = 5;               // limite zoom in
    controls.maxDistance = 50;              // limite zoom out
    controls.minPolarAngle = 0.1;           // empeche de passer en dessous
    controls.maxPolarAngle = Math.PI / 2.1; // empeche de passer sous le sol
    controls.autoRotate = true;             // rotation lente au demarrage
    controls.autoRotateSpeed = 0.5;
    camera.lookAt(0, yCentre, 0);
    controls.update();

    // Arreter l'auto-rotation au premier mouvement utilisateur
    const stopAutoRotate = () => { controls.autoRotate = false; };
    controls.addEventListener("start", stopAutoRotate);

    // Boucle de rendu
    let animId;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // Gestion du resize
    const handleResize = () => {
      if (!mountRef.current) return;
      const newW = mountRef.current.clientWidth;
      const newH = mountRef.current.clientHeight;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      controls.removeEventListener("start", stopAutoRotate);
      controls.dispose();
      cancelAnimationFrame(animId);
      renderer.dispose();
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current)
        mountRef.current.removeChild(renderer.domElement);
    };'''

if "OrbitControls(camera" in content:
    print("[INFO] OrbitControls deja en place dans Viewer3D")
elif old_animation in content:
    content = content.replace(old_animation, new_orbit_controls, 1)
    print("[OK] Animation auto remplacee par OrbitControls interactif")
    modifs += 1
else:
    print("[ERREUR] Bloc animation non trouve exactement")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Import OrbitControls ajoute")
print("  2. Animation auto remplacee par camera interactive")
print()
print("COMPORTEMENT :")
print("  - Au demarrage : rotation lente automatique (smooth)")
print("  - Au premier mouvement : l'auto-rotate s'arrete")
print("  - Click gauche + drag : tourner la camera")
print("  - Scroll wheel : zoomer/dezoomer")
print("  - Click droit + drag : deplacer le centre (pan)")
print("  - Damping : mouvement fluide apres relachement")
print("  - Limites : zoom 5-50m, ne passe pas sous le sol")
print("  - Resize automatique de la fenetre")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
