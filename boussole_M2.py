# Boussole M2 : placement cardinal (nord=-Z, sud=+Z, est=+X, ouest=-X),
# alignements par bords, sens de faitage cardinal par volume. Cache v7.
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''Verifie ces facades contre les noms des facades du dossier (facade nord, sud, est, ouest) quand elles existent.'''
NEW1 = '''Verifie ces facades contre les noms des facades du dossier (facade nord, sud, est, ouest) quand elles existent. Donne aussi pour CHAQUE volume le sens cardinal de son faitage : est_ouest ou nord_sud (toit plat : null).'''

OLD2 = '''"facade":"nord|sud|est|ouest|null","alignement":"nord|sud|est|ouest|centre|null",'''
NEW2 = '''"facade":"nord|sud|est|ouest|null","alignement":"nord|sud|est|ouest|centre|null","faitage_cardinal":"est_ouest|nord_sud|null",'''

OLD3 = '''          return {
            type: o.type,'''
NEW3 = '''          return {
            type: o.type,
            faitageCardinal: o.faitage_cardinal || undefined,'''

OLD4 = '''        pos: s.pos || undefined,'''
NEW4 = '''        pos: s.pos || undefined,
        faitageCardinal: s.faitageCardinal || undefined,'''

OLD5 = '''        const grp = buildOuvrage(o, extra);
        grp.position.x = cursorX + (o.longueur || 8) / 2;
        posRangee.set(o, grp.position.x);'''
NEW5 = '''        const grp = buildOuvrage(o, extra);
        if (o.faitageCardinal === "nord_sud") grp.rotation.y = Math.PI / 2;
        grp.position.x = cursorX + (o.longueur || 8) / 2;
        posRangee.set(o, grp.position.x);'''

OLD6 = '''      rangee.forEach((o) => { places.set(o, { x: posRangee.get(o) || 0, z: 0, rot: 0 }); });'''
NEW6 = '''      rangee.forEach((o) => { places.set(o, { x: posRangee.get(o) || 0, z: 0, rot: o.faitageCardinal === "nord_sud" ? Math.PI / 2 : 0 }); });'''

OLD7 = '''          const rot = (o.pos.faitage === "perpendiculaire") ? pRef.rot + Math.PI / 2 : pRef.rot;'''
NEW7 = '''          const rot = o.faitageCardinal === "nord_sud" ? Math.PI / 2 : (o.faitageCardinal === "est_ouest" ? 0 : ((o.pos.faitage === "perpendiculaire") ? pRef.rot + Math.PI / 2 : pRef.rot));'''

OLD8 = '''          const dec = o.pos.decalage || 0;
          let px = pRef.x, pz = pRef.z;
          if (o.pos.cote === "pignon_droit") { px = pRef.x + dR.hx + dA.hx + 0.2; pz = pRef.z + dec; }'''
NEW8 = '''          const dec = o.pos.decalage || 0;
          let px = pRef.x, pz = pRef.z;
          if (o.pos.facade) {
            // Placement CARDINAL : nord = -Z, sud = +Z, est = +X, ouest = -X
            const fc = o.pos.facade;
            if (fc === "est") px = pRef.x + dR.hx + dA.hx + 0.2;
            else if (fc === "ouest") px = pRef.x - dR.hx - dA.hx - 0.2;
            else if (fc === "sud") pz = pRef.z + dR.hz + dA.hz + 0.2;
            else pz = pRef.z - dR.hz - dA.hz - 0.2;
            const al = o.pos.alignement;
            if (fc === "est" || fc === "ouest") {
              if (al === "sud") pz = pRef.z + (dR.hz - dA.hz);
              else if (al === "nord") pz = pRef.z - (dR.hz - dA.hz);
              else pz = pRef.z + dec;
            } else {
              if (al === "est") px = pRef.x + (dR.hx - dA.hx);
              else if (al === "ouest") px = pRef.x - (dR.hx - dA.hx);
              else px = pRef.x + dec;
            }
          }
          else if (o.pos.cote === "pignon_droit") { px = pRef.x + dR.hx + dA.hx + 0.2; pz = pRef.z + dec; }'''

OLD9 = '''            const versRef = { pignon_droit: 2, pignon_gauche: 0, gouttereau_avant: 3, gouttereau_arriere: 1 }[o.pos.cote];'''
NEW9 = '''            const versRef = o.pos.facade ? ({ est: 2, ouest: 0, sud: 3, nord: 1 }[o.pos.facade]) : ({ pignon_droit: 2, pignon_gauche: 0, gouttereau_avant: 3, gouttereau_arriere: 1 }[o.pos.cote]);'''

OLD10 = '''const versionPrompt = vh.toString(36) + "-p3v6";'''
NEW10 = '''const versionPrompt = vh.toString(36) + "-p3v7";'''

anchors = [("prompt faitage cardinal", OLD1, NEW1), ("schema faitage cardinal", OLD2, NEW2), ("struct faitage", OLD3, NEW3), ("ouvrages3D faitage", OLD4, NEW4), ("rotation principal", OLD5, NEW5), ("places rot principal", OLD6, NEW6), ("rot accole cardinal", OLD7, NEW7), ("placement cardinal", OLD8, NEW8), ("jonction cardinale", OLD9, NEW9), ("cache v7", OLD10, NEW10)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_boussole_M2")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK M2 : placement cardinal + alignements + faitages cardinaux")
