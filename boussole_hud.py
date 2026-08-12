# Boussole HUD : pastille en coin d'ecran qui tourne avec la camera (remplace la fleche 3D)
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''    scene.add(ground);

    // BOUSSOLE permanente : fleche doree pointee plein NORD (nord = -Z)
    const xBou = -((params.longueur || 10) / 2) - 4;
    const bouMat = new THREE.MeshStandardMaterial({ color: 0xf0c040, roughness: 0.6 });
    const bouTige = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.2, 8), bouMat);
    bouTige.rotation.x = Math.PI / 2;
    bouTige.position.set(xBou, 0.08, -0.1);
    scene.add(bouTige);
    const bouPointe = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.7, 12), bouMat);
    bouPointe.rotation.x = -Math.PI / 2;
    bouPointe.position.set(xBou, 0.08, -1.55);
    scene.add(bouPointe);
    const bouCan = document.createElement("canvas");
    bouCan.width = 64;
    bouCan.height = 64;
    const bouCtx = bouCan.getContext("2d");
    bouCtx.fillStyle = "#f0c040";
    bouCtx.font = "bold 46px Arial";
    bouCtx.textAlign = "center";
    bouCtx.textBaseline = "middle";
    bouCtx.fillText("N", 32, 34);
    const bouSpr = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(bouCan), transparent: true, depthTest: false }));
    bouSpr.scale.set(1.1, 1.1, 1);
    bouSpr.position.set(xBou, 0.9, -2.4);
    scene.add(bouSpr);'''
NEW1 = '''    scene.add(ground);'''

OLD2 = '''    mountRef.current.appendChild(renderer.domElement);'''
NEW2 = '''    mountRef.current.appendChild(renderer.domElement);
    // BOUSSOLE HUD : pastille en haut a droite, l'aiguille suit la camera (nord = -Z monde)
    mountRef.current.style.position = "relative";
    const hudBoussole = document.createElement("div");
    hudBoussole.style.cssText = "position:absolute;top:10px;right:10px;width:54px;height:54px;border-radius:50%;background:rgba(10,12,20,0.72);border:1px solid rgba(240,192,64,0.45);display:flex;align-items:center;justify-content:center;pointer-events:none;z-index:5;";
    const aiguilleBoussole = document.createElement("div");
    aiguilleBoussole.style.cssText = "display:flex;flex-direction:column;align-items:center;color:#f0c040;font-family:Arial;font-weight:700;font-size:11px;line-height:1.1;transform-origin:center;";
    aiguilleBoussole.textContent = "N";
    const flecheBoussole = document.createElement("div");
    flecheBoussole.style.cssText = "width:0;height:0;border-left:5px solid transparent;border-right:5px solid transparent;border-bottom:10px solid #f0c040;margin-bottom:2px;";
    aiguilleBoussole.prepend(flecheBoussole);
    hudBoussole.appendChild(aiguilleBoussole);
    mountRef.current.appendChild(hudBoussole);'''

OLD3 = '''    const animate = () => {
      animId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };'''
NEW3 = '''    const animate = () => {
      animId = requestAnimationFrame(animate);
      controls.update();
      const azimB = Math.atan2(camera.position.x - controls.target.x, camera.position.z - controls.target.z);
      aiguilleBoussole.style.transform = "rotate(" + (azimB * 180 / Math.PI) + "deg)";
      renderer.render(scene, camera);
    };'''

OLD4 = '''      if (mountRef.current && renderer.domElement.parentNode === mountRef.current)
        mountRef.current.removeChild(renderer.domElement);'''
NEW4 = '''      hudBoussole.remove();
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current)
        mountRef.current.removeChild(renderer.domElement);'''

anchors = [("retrait fleche 3D", OLD1, NEW1), ("creation HUD", OLD2, NEW2), ("rotation aiguille", OLD3, NEW3), ("nettoyage HUD", OLD4, NEW4)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_boussole_hud")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : boussole HUD en coin d'ecran (fleche 3D retiree)")
