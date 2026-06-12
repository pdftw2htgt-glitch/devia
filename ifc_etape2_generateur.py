#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - IFC etape 2 : generateur de fichier IFC (STEP) depuis metre[]"""
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

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_ifc_gen"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# Generateur IFC insere juste avant agregerMetre
gen = r'''// ============================================================
// GENERATEUR IFC (ISO-10303-21 / IFC4) depuis le metre 3D
// ============================================================
// Note conventions axes : Three.js Y=haut -> IFC Z=haut. Conversion (x,y,z)->(x,z,y).
function genererIFC(metre, params) {
  const piecesBois = (metre || []).filter((p) => p.pos); // seulement pieces avec position
  let id = 0;
  const nextId = () => ++id;
  const lines = [];
  const E = (n, s) => { lines.push("#" + n + "=" + s); }; // ecrit une entite

  // --- En-tete STEP ---
  const now = new Date();
  const stamp = now.toISOString().slice(0, 19);
  const header =
"ISO-10303-21;\n" +
"HEADER;\n" +
"FILE_DESCRIPTION(('DEVIA charpente export'),'2;1');\n" +
"FILE_NAME('devia.ifc','" + stamp + "',(''),(''),'DEVIA','DEVIA','');\n" +
"FILE_SCHEMA(('IFC4'));\n" +
"ENDSEC;\n" +
"DATA;\n";

  // --- Contexte de base ---
  const dimExp = nextId(); E(dimExp, "IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);");
  const origin = nextId(); E(origin, "IFCCARTESIANPOINT((0.,0.,0.));");
  const dirZ = nextId(); E(dirZ, "IFCDIRECTION((0.,0.,1.));");
  const dirX = nextId(); E(dirX, "IFCDIRECTION((1.,0.,0.));");
  const axisPlacement = nextId(); E(axisPlacement, "IFCAXIS2PLACEMENT3D(#" + origin + ",#" + dirZ + ",#" + dirX + ");");
  const worldCoord = nextId(); E(worldCoord, "IFCAXIS2PLACEMENT3D(#" + origin + ",$,$);");

  const lenUnit = nextId(); E(lenUnit, "IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);");
  const areaUnit = nextId(); E(areaUnit, "IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);");
  const volUnit = nextId(); E(volUnit, "IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);");
  const angUnit = nextId(); E(angUnit, "IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);");
  const unitAssign = nextId(); E(unitAssign, "IFCUNITASSIGNMENT((#" + lenUnit + ",#" + areaUnit + ",#" + volUnit + ",#" + angUnit + "));");

  const geomCtx = nextId(); E(geomCtx, "IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#" + axisPlacement + ",$);");

  const guid = () => {
    const c = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$";
    let s = ""; for (let i = 0; i < 22; i++) s += c[Math.floor(Math.random() * 64)];
    return s;
  };

  const ownerHist = nextId(); E(ownerHist, "$"); // simplifie (pas d'historique)

  // --- Hierarchie spatiale ---
  const project = nextId();
  const site = nextId();
  const building = nextId();
  const storey = nextId();
  E(project, "IFCPROJECT('" + guid() + "',$,'DEVIA Charpente',$,$,$,$,(#" + geomCtx + "),#" + unitAssign + ");");
  const sitePlc = nextId(); E(sitePlc, "IFCLOCALPLACEMENT($,#" + axisPlacement + ");");
  E(site, "IFCSITE('" + guid() + "',$,'Terrain',$,$,#" + sitePlc + ",$,$,.ELEMENT.,$,$,$,$,$);");
  const bldgPlc = nextId(); E(bldgPlc, "IFCLOCALPLACEMENT(#" + sitePlc + ",#" + axisPlacement + ");");
  E(building, "IFCBUILDING('" + guid() + "',$,'Batiment',$,$,#" + bldgPlc + ",$,$,.ELEMENT.,$,$,$);");
  const storeyPlc = nextId(); E(storeyPlc, "IFCLOCALPLACEMENT(#" + bldgPlc + ",#" + axisPlacement + ");");
  E(storey, "IFCBUILDINGSTOREY('" + guid() + "',$,'Niveau 0',$,$,#" + storeyPlc + ",$,$,.ELEMENT.,0.);");

  // Relations d'agregation
  const relAggProj = nextId(); E(relAggProj, "IFCRELAGGREGATES('" + guid() + "',$,$,$,#" + project + ",(#" + site + "));");
  const relAggSite = nextId(); E(relAggSite, "IFCRELAGGREGATES('" + guid() + "',$,$,$,#" + site + ",(#" + building + "));");
  const relAggBldg = nextId(); E(relAggBldg, "IFCRELAGGREGATES('" + guid() + "',$,$,$,#" + building + ",(#" + storey + "));");

  // --- Une piece -> un IfcMember ---
  const memberIds = [];
  piecesBois.forEach((p) => {
    // conversion axes Three(x,y,z) -> IFC(x,z,y)
    const px = p.pos[0], py = p.pos[2], pz = p.pos[1];
    // dims brutes (m) : on prend section = 2 plus petites, longueur = plus grande
    const d = [...p.dimsBrutes].map(Math.abs).sort((a, b) => b - a);
    const L = d[0], w = d[1], h = d[2];

    // profil rectangulaire centre
    const profCtrPt = nextId(); E(profCtrPt, "IFCCARTESIANPOINT((0.,0.));");
    const profDir = nextId(); E(profDir, "IFCDIRECTION((1.,0.));");
    const profPos = nextId(); E(profPos, "IFCAXIS2PLACEMENT2D(#" + profCtrPt + ",#" + profDir + ");");
    const prof = nextId(); E(prof, "IFCRECTANGLEPROFILEDEF(.AREA.,$,#" + profPos + "," + w.toFixed(4) + "," + h.toFixed(4) + ");");

    // position de la piece dans le storey
    const ptPiece = nextId(); E(ptPiece, "IFCCARTESIANPOINT((" + px.toFixed(4) + "," + py.toFixed(4) + "," + pz.toFixed(4) + "));");
    const axPiece = nextId(); E(axPiece, "IFCAXIS2PLACEMENT3D(#" + ptPiece + ",$,$);");
    const plcPiece = nextId(); E(plcPiece, "IFCLOCALPLACEMENT(#" + storeyPlc + ",#" + axPiece + ");");

    // extrusion : repere local, extrude selon Z local sur longueur L, centre en -L/2
    const extrPt = nextId(); E(extrPt, "IFCCARTESIANPOINT((0.,0.," + (-L/2).toFixed(4) + "));");
    const extrAx = nextId(); E(extrAx, "IFCAXIS2PLACEMENT3D(#" + extrPt + ",$,$);");
    const extrDir = nextId(); E(extrDir, "IFCDIRECTION((0.,0.,1.));");
    const solid = nextId(); E(solid, "IFCEXTRUDEDAREASOLID(#" + prof + ",#" + extrAx + ",#" + extrDir + "," + L.toFixed(4) + ");");

    const shapeRep = nextId(); E(shapeRep, "IFCSHAPEREPRESENTATION(#" + geomCtx + ",'Body','SweptSolid',(#" + solid + "));");
    const prodDef = nextId(); E(prodDef, "IFCPRODUCTDEFINITIONSHAPE($,$,(#" + shapeRep + "));");

    const member = nextId();
    E(member, "IFCMEMBER('" + guid() + "',$,'" + (p.nom || "Piece") + "',$,$,#" + plcPiece + ",#" + prodDef + ",$,$);");
    memberIds.push(member);
  });

  // Rattacher tous les membres au storey
  if (memberIds.length) {
    const relContain = nextId();
    E(relContain, "IFCRELCONTAINEDINSPATIALSTRUCTURE('" + guid() + "',$,$,$,(#" + memberIds.join(",#") + "),#" + storey + ");");
  }

  const footer = "ENDSEC;\nEND-ISO-10303-21;\n";
  return header + lines.join("\n") + "\n" + footer;
}

'''
apply("// AGREGATION DU METRE (regroupe par type de piece + totaux)", gen + "// AGREGATION DU METRE (regroupe par type de piece + totaux)", "Generateur genererIFC insere")

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
