# Etape 2 (2A-2) : les volumes avec position extraite du plan sont ACCOLES en 3D
# (viewer). Volumes sans position : comportement actuel inchange.
import shutil, datetime, sys

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"

with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''      const rangee = [];
      const ancres = [];
      params.ouvrages.forEach((o, i) => {
        if (idxPorteur < 0 || i === idxPorteur) { rangee.push(o); return; }'''
NEW1 = '''      const rangee = [];
      const ancres = [];
      const accoles = [];
      params.ouvrages.forEach((o, i) => {
        if (idxPorteur < 0 || i === idxPorteur) { rangee.push(o); return; }
        if (o.pos && o.pos.contre) { accoles.push(o); return; }'''

OLD2 = '''          grp.position.z = (porteur.largeur || 6) / 2 + (o.type_projet === "appentis" ? -(o.largeur || 2) / 2 + (o.largeur || 2) + 0.1 : 0.1);
        }
      });
      if (onMetreRef.current && metresAll.length) {'''
NEW2 = '''          grp.position.z = (porteur.largeur || 6) / 2 + (o.type_projet === "appentis" ? -(o.largeur || 2) / 2 + (o.largeur || 2) + 0.1 : 0.1);
        }
      });

      // ===== ACCOLES : places selon les positions extraites du plan =====
      const places = new Map();
      rangee.forEach((o) => { places.set(o, { x: posRangee.get(o) || 0, z: 0, rot: 0 }); });
      const demiEmprise = (o, rot) => {
        const quart = Math.abs(Math.round(rot / (Math.PI / 2))) % 2;
        if (quart === 1) return { hx: (o.largeur || 6) / 2, hz: (o.longueur || 8) / 2 };
        return { hx: (o.longueur || 8) / 2, hz: (o.largeur || 6) / 2 };
      };
      let attente = accoles.slice();
      let tours = 0;
      while (attente.length > 0 && tours < 10) {
        tours += 1;
        const encore = [];
        attente.forEach((o) => {
          const ref = params.ouvrages[(o.pos.contre || 1) - 1];
          const pRef = places.get(ref);
          if (pRef === undefined || ref === o) { encore.push(o); return; }
          const rot = (o.pos.faitage === "perpendiculaire") ? pRef.rot + Math.PI / 2 : pRef.rot;
          const dR = demiEmprise(ref, pRef.rot);
          const dA = demiEmprise(o, rot);
          const dec = o.pos.decalage || 0;
          let px = pRef.x, pz = pRef.z;
          if (o.pos.cote === "pignon_droit") { px = pRef.x + dR.hx + dA.hx + 0.2; pz = pRef.z + dec; }
          else if (o.pos.cote === "pignon_gauche") { px = pRef.x - dR.hx - dA.hx - 0.2; pz = pRef.z + dec; }
          else if (o.pos.cote === "gouttereau_avant") { px = pRef.x + dec; pz = pRef.z + dR.hz + dA.hz + 0.2; }
          else { px = pRef.x + dec; pz = pRef.z - dR.hz - dA.hz - 0.2; }
          const grp = buildOuvrage(o, null);
          grp.rotation.y = rot;
          grp.position.x = px;
          grp.position.z = pz;
          places.set(o, { x: px, z: pz, rot: rot });
          console.log("[DEVIA] Accolage : " + (o.type_projet || "ouvrage") + " contre V" + o.pos.contre + " cote " + o.pos.cote + " a x=" + px.toFixed(2) + " z=" + pz.toFixed(2));
        });
        attente = encore;
      }
      attente.forEach((o) => {
        // Reference introuvable : placement de secours en bout de rangee
        let maxX = 0;
        places.forEach((p, oo) => { const d = demiEmprise(oo, p.rot); if (p.x + d.hx > maxX) maxX = p.x + d.hx; });
        const dA = demiEmprise(o, 0);
        const grp = buildOuvrage(o, null);
        grp.position.x = maxX + 2.0 + dA.hx;
        places.set(o, { x: maxX + 2.0 + dA.hx, z: 0, rot: 0 });
        console.warn("[DEVIA] Accolage : reference introuvable, ouvrage place en bout de rangee");
      });
      if (onMetreRef.current && metresAll.length) {'''

anchors = [("classement accoles", OLD1, NEW1), ("placement accoles", OLD2, NEW2)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)

shutil.copy2(F, F + ".backup_" + stamp + "_accolage_A2")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK etape 2 : accolage 3D selon les positions du plan (viewer)")
