# Mur de jonction : le volume accole a un autre corps a murs perd son mur de contact
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''  const drawMursBeton = (Lb, lgb, Hb) => {
    const ep = 0.2;'''
NEW1 = '''  const drawMursBeton = (Lb, lgb, Hb) => {
    const ep = 0.2;
    const sansFace = (opts && opts.sansMurFace) || "";'''

OLD2 = '''      bandeX(lgb/2, yBase, hEtage, ouvAv);
      bandeX(-lgb/2, yBase, hEtage, [{ cx: 0, w: 1.2, y0: y0F, y1: y1F }]);'''
NEW2 = '''      sansFace === "gouttereau_avant" ? null : bandeX(lgb/2, yBase, hEtage, ouvAv);
      sansFace === "gouttereau_arriere" ? null : bandeX(-lgb/2, yBase, hEtage, [{ cx: 0, w: 1.2, y0: y0F, y1: y1F }]);'''

OLD3 = '''    murZ(Lb/2, true);
    murZ(-Lb/2, false);'''
NEW3 = '''    sansFace === "pignon_droit" ? null : murZ(Lb/2, true);
    sansFace === "pignon_gauche" ? null : murZ(-Lb/2, false);'''

OLD4 = '''          else { px = pRef.x + dec; pz = pRef.z - dR.hz - dA.hz - 0.2; }
          const grp = buildOuvrage(o, null);'''
NEW4 = '''          else { px = pRef.x + dec; pz = pRef.z - dR.hz - dA.hz - 0.2; }
          // Mur de jonction : deux corps a murs accoles = le mur de contact de l'accole disparait
          let extraMur = null;
          if (AVEC_MURS.includes(o.type_projet) && AVEC_MURS.includes(ref.type_projet || "")) {
            const FACES = ["pignon_droit", "gouttereau_avant", "pignon_gauche", "gouttereau_arriere"];
            const versRef = { pignon_droit: 2, pignon_gauche: 0, gouttereau_avant: 3, gouttereau_arriere: 1 }[o.pos.cote];
            if (versRef === 0 || versRef > 0) {
              const q = ((Math.round(rot / (Math.PI / 2)) % 4) + 4) % 4;
              extraMur = { sansMurFace: FACES[(versRef + q) % 4] };
              console.log("[DEVIA] Jonction : mur " + extraMur.sansMurFace + " retire sur " + (o.type_projet || "ouvrage"));
            }
          }
          const grp = buildOuvrage(o, extraMur);'''

anchors = [("option sansFace", OLD1, NEW1), ("gouttereaux", OLD2, NEW2), ("pignons", OLD3, NEW3), ("accolage jonction", OLD4, NEW4)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_mur_jonction")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : mur de jonction retire entre deux corps a murs accoles")
