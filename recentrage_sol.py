# Viewer : recentrage de l'ensemble multi sur l'origine + sol agrandi
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''      new THREE.PlaneGeometry(30, 30),'''
NEW1 = '''      new THREE.PlaneGeometry(120, 120),'''

OLD2 = '''      const gap = 2.0;
      const metresAll = [];'''
NEW2 = '''      const gap = 2.0;
      const metresAll = [];
      const groupes = [];'''

OLD3 = '''        scene.add(grp);
        metresAll.push(...res.metre);'''
NEW3 = '''        scene.add(grp);
        groupes.push(grp);
        metresAll.push(...res.metre);'''

OLD4 = '''        console.warn("[DEVIA] Accolage : reference introuvable, ouvrage place en bout de rangee");
      });
      if (onMetreRef.current && metresAll.length) {'''
NEW4 = '''        console.warn("[DEVIA] Accolage : reference introuvable, ouvrage place en bout de rangee");
      });

      // Recentrage de l'ensemble sur l'origine (sol et camera)
      if (groupes.length > 1) {
        const boite = new THREE.Box3();
        groupes.forEach((g) => { boite.expandByObject(g); });
        if (boite.isEmpty() === false) {
          const centre = new THREE.Vector3();
          boite.getCenter(centre);
          groupes.forEach((g) => { g.position.x -= centre.x; g.position.z -= centre.z; });
        }
      }
      if (onMetreRef.current && metresAll.length) {'''

anchors = [("sol", OLD1, NEW1), ("liste groupes", OLD2, NEW2), ("suivi groupes", OLD3, NEW3), ("recentrage", OLD4, NEW4)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_recentrage_sol")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : ensemble multi recentre + sol 120x120")
