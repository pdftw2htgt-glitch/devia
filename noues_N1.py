# Noues N1 : aile perpendiculaire plus basse -> 2 noues + faitiere prolongee sur le pan du porteur
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''  // ============================================================
  // SWITCH SELON TYPE PROJET
  // ============================================================'''
NEW1 = '''  const drawPenetration = () => {
    // Noues v1 : ce volume (l'aile) penetre le pan du corps principal, pan principal continu.
    // Repere local aile : faitage le long de X, mur de contact au pignon opts.sansMurFace.
    const pen = opts.penetration;
    const s = opts.sansMurFace === "pignon_droit" ? 1 : -1;
    const aRad = ((pente || 35) * Math.PI) / 180;
    const pRad = ((pen.penteRef || 35) * Math.PI) / 180;
    const hF = Ht + (lg / 2) * Math.tan(aRad);
    const hE = pen.hEgoutRef;
    if (hF <= hE + 0.05) return;
    const dR = (hF - hE) / Math.tan(pRad);
    const xw = s * L / 2;
    const zBrut = (hF - hE) / Math.tan(aRad);
    const zE = zBrut > lg / 2 ? lg / 2 : zBrut;
    const yPied = hF - zE * Math.tan(aRad);
    const dPied = (yPied - hE) / Math.tan(pRad);
    setPiece("Noue");
    for (const sz of [-1, 1]) {
      addBeam(xw + s * dPied, yPied, sz * zE, xw + s * dR, hF, 0, 0.12, woodMat);
    }
    setPiece("Panne faitiere");
    addBox(dR, 0.24, 0.12, xw + s * dR / 2, hF - 0.12, 0, woodMat);
    console.log("[DEVIA] Penetration : 2 noues + faitiere prolongee (profondeur " + dR.toFixed(2) + " m)");
  };

  // ============================================================
  // SWITCH SELON TYPE PROJET
  // ============================================================'''

OLD2 = '''  } else {
    drawCharpenteTrad();
  }'''
NEW2 = '''  } else {
    drawCharpenteTrad();
    if (opts && opts.penetration && opts.sansMurFace && opts.sansMurFace.indexOf("pignon") === 0) drawPenetration();
  }'''

OLD3 = '''              console.log("[DEVIA] Jonction : mur " + extraMur.sansMurFace + " retire sur " + (o.type_projet || "ouvrage"));
            }
          }
          const grp = buildOuvrage(o, extraMur);'''
NEW3 = '''              console.log("[DEVIA] Jonction : mur " + extraMur.sansMurFace + " retire sur " + (o.type_projet || "ouvrage"));
            }
          }
          // Penetration de toiture : aile perpendiculaire plus basse contre un gouttereau -> noues
          const coteG = o.pos.cote === "gouttereau_avant" || o.pos.cote === "gouttereau_arriere";
          if (extraMur && coteG && o.pos.faitage === "perpendiculaire" && AVEC_MURS.includes(o.type_projet) && AVEC_MURS.includes(ref.type_projet || "")) {
            const fAile = (o.hauteur || 3) + ((o.largeur || 6) / 2) * Math.tan(((o.pente || 35) * Math.PI) / 180);
            const fRef = (ref.hauteur || 3) + ((ref.largeur || 6) / 2) * Math.tan(((ref.pente || 35) * Math.PI) / 180);
            if (fAile < fRef) {
              extraMur.penetration = { hEgoutRef: ref.hauteur || 3, penteRef: ref.pente || 35 };
            }
          }
          const grp = buildOuvrage(o, extraMur);'''

anchors = [("fonction penetration", OLD1, NEW1), ("dispatch penetration", OLD2, NEW2), ("accolage penetration", OLD3, NEW3)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_noues_N1")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK N1 : noues + faitiere prolongee dans la penetration")
