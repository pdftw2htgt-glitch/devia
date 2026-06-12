#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Fix IFC : orienter chaque piece selon son vrai axe long (au lieu de tout vertical)"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()

old = '''  piecesBois.forEach((p) => {
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
  });'''

new = '''  piecesBois.forEach((p) => {
    // --- Dimensions Three.js d'origine (NON triees, pour garder la direction) ---
    // sx = dim selon X three, sy = selon Y three (haut), sz = selon Z three
    const sx = Math.abs(p.dimsBrutes[0]);
    const sy = Math.abs(p.dimsBrutes[1]);
    const sz = Math.abs(p.dimsBrutes[2]);

    // --- Quel axe porte la longueur (la plus grande dimension) ? ---
    // axeLong : 0=X, 1=Y, 2=Z (dans le repere Three.js)
    let axeLong = 0, Lmax = sx;
    if (sy > Lmax) { axeLong = 1; Lmax = sy; }
    if (sz > Lmax) { axeLong = 2; Lmax = sz; }
    const L = Lmax;

    // --- Les 2 autres dimensions = section (largeur w, hauteur h du profil) ---
    let w, h;
    if (axeLong === 0) { w = sy; h = sz; }        // long selon X -> section (Y,Z)
    else if (axeLong === 1) { w = sx; h = sz; }   // long selon Y -> section (X,Z)
    else { w = sx; h = sy; }                       // long selon Z -> section (X,Y)

    // --- Position du centre, conversion Three(x,y,z) -> IFC(x,z,y) ---
    const px = p.pos[0], py = p.pos[2], pz = p.pos[1];

    // --- Direction d'extrusion en IFC selon l'axe long Three, converti en IFC ---
    // Three X -> IFC X ; Three Y(haut) -> IFC Z ; Three Z -> IFC Y
    let extrDirVec;
    if (axeLong === 0) extrDirVec = "(1.,0.,0.)";       // X three -> X ifc
    else if (axeLong === 1) extrDirVec = "(0.,0.,1.)";  // Y three (haut) -> Z ifc
    else extrDirVec = "(0.,1.,0.)";                      // Z three -> Y ifc

    // profil rectangulaire centre
    const profCtrPt = nextId(); E(profCtrPt, "IFCCARTESIANPOINT((0.,0.));");
    const profDir = nextId(); E(profDir, "IFCDIRECTION((1.,0.));");
    const profPos = nextId(); E(profPos, "IFCAXIS2PLACEMENT2D(#" + profCtrPt + ",#" + profDir + ");");
    const prof = nextId(); E(prof, "IFCRECTANGLEPROFILEDEF(.AREA.,$,#" + profPos + "," + w.toFixed(4) + "," + h.toFixed(4) + ");");

    // placement de la piece : on oriente l'axe Z LOCAL de la piece vers la direction d'extrusion
    const ptPiece = nextId(); E(ptPiece, "IFCCARTESIANPOINT((" + px.toFixed(4) + "," + py.toFixed(4) + "," + pz.toFixed(4) + "));");
    // axe Z local = direction d'extrusion ; axe X local = un axe perpendiculaire
    let axisZ, refX;
    if (axeLong === 0) { axisZ = "(1.,0.,0.)"; refX = "(0.,0.,1.)"; }
    else if (axeLong === 1) { axisZ = "(0.,0.,1.)"; refX = "(1.,0.,0.)"; }
    else { axisZ = "(0.,1.,0.)"; refX = "(1.,0.,0.)"; }
    const dirZpiece = nextId(); E(dirZpiece, "IFCDIRECTION(" + axisZ + ");");
    const dirXpiece = nextId(); E(dirXpiece, "IFCDIRECTION(" + refX + ");");
    const axPiece = nextId(); E(axPiece, "IFCAXIS2PLACEMENT3D(#" + ptPiece + ",#" + dirZpiece + ",#" + dirXpiece + ");");
    const plcPiece = nextId(); E(plcPiece, "IFCLOCALPLACEMENT(#" + storeyPlc + ",#" + axPiece + ");");

    // extrusion : dans le repere local, on extrude selon Z local, centree (-L/2)
    const extrPt = nextId(); E(extrPt, "IFCCARTESIANPOINT((0.,0.," + (-L/2).toFixed(4) + "));");
    const extrAx = nextId(); E(extrAx, "IFCAXIS2PLACEMENT3D(#" + extrPt + ",$,$);");
    const extrDir = nextId(); E(extrDir, "IFCDIRECTION((0.,0.,1.));");
    const solid = nextId(); E(solid, "IFCEXTRUDEDAREASOLID(#" + prof + ",#" + extrAx + ",#" + extrDir + "," + L.toFixed(4) + ");");

    const shapeRep = nextId(); E(shapeRep, "IFCSHAPEREPRESENTATION(#" + geomCtx + ",'Body','SweptSolid',(#" + solid + "));");
    const prodDef = nextId(); E(prodDef, "IFCPRODUCTDEFINITIONSHAPE($,$,(#" + shapeRep + "));");

    const member = nextId();
    E(member, "IFCMEMBER('" + guid() + "',$,'" + (p.nom || "Piece") + "',$,$,#" + plcPiece + ",#" + prodDef + ",$,$);");
    memberIds.push(member);
  });'''

n = content.count(old)
if n != 1:
    print(f"[ERREUR] ancre trouvee {n} fois (attendu 1) -> abandon")
    exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fix_ifc_orient"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")
content = content.replace(old, new, 1)
open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] Orientation des pieces corrigee (axe long detecte)")
print("1 MODIFICATION APPLIQUEE")
