#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Fix IFC : orienter les pieces inclinees (addBeam) via leur quaternion"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()

# On remplace tout le bloc de placement par une version qui gere quat (addBeam) ET axe long (addBox)
old = '''    // --- Dimensions Three.js d'origine (NON triees, pour garder la direction) ---
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
    const plcPiece = nextId(); E(plcPiece, "IFCLOCALPLACEMENT(#" + storeyPlc + ",#" + axPiece + ");");'''

new = '''    // --- Dimensions Three.js d'origine ---
    const sx = Math.abs(p.dimsBrutes[0]);
    const sy = Math.abs(p.dimsBrutes[1]);
    const sz = Math.abs(p.dimsBrutes[2]);

    // helper : convertit un vecteur Three (x,y,z) -> IFC (x, z, y) et normalise
    const toIfcDir = (vx, vy, vz) => {
      // Three Y(haut) -> IFC Z ; Three Z -> IFC Y
      let ix = vx, iy = vz, iz = vy;
      const n = Math.sqrt(ix*ix + iy*iy + iz*iz) || 1;
      ix /= n; iy /= n; iz /= n;
      return "(" + ix.toFixed(6) + "," + iy.toFixed(6) + "," + iz.toFixed(6) + ")";
    };

    // --- Determiner l'axe long (longueur) et la section (w,h), + direction longue en repere THREE ---
    let L, w, h;
    let longVecThree; // direction de la longueur dans le repere Three
    if (p.quat) {
      // Piece issue de addBeam : la longueur est selon l'axe Z LOCAL, oriente par le quaternion.
      // BoxGeometry(thick, thick, len) -> len selon z local. On applique le quat a (0,0,1).
      const [qx, qy, qz, qw] = p.quat;
      // rotation du vecteur (0,0,1) par le quaternion : formule v' = q * v * q^-1
      // pour v=(0,0,1) ca se simplifie :
      const vx = 2 * (qx*qz + qw*qy);
      const vy = 2 * (qy*qz - qw*qx);
      const vz = 1 - 2 * (qx*qx + qy*qy);
      longVecThree = [vx, vy, vz];
      // longueur = plus grande dim ; section = les 2 thick (egaux en general)
      const dimsSorted = [sx, sy, sz].sort((a,b) => b - a);
      L = dimsSorted[0]; w = dimsSorted[1]; h = dimsSorted[2];
    } else {
      // Piece issue de addBox : axe long = plus grande dimension, axes alignes au repere
      let axeLong = 0, Lmax = sx;
      if (sy > Lmax) { axeLong = 1; Lmax = sy; }
      if (sz > Lmax) { axeLong = 2; Lmax = sz; }
      L = Lmax;
      if (axeLong === 0) { w = sy; h = sz; longVecThree = [1,0,0]; }
      else if (axeLong === 1) { w = sx; h = sz; longVecThree = [0,1,0]; }
      else { w = sx; h = sy; longVecThree = [0,0,1]; }
    }

    // --- Position du centre, conversion Three(x,y,z) -> IFC(x,z,y) ---
    const px = p.pos[0], py = p.pos[2], pz = p.pos[1];

    // --- Axe Z local de la piece = direction de la longueur (en IFC) ---
    const axisZ = toIfcDir(longVecThree[0], longVecThree[1], longVecThree[2]);
    // axe X de reference : on choisit un vecteur non colineaire puis l'IFC orthogonalise
    // si la longueur est ~verticale en IFC, on prend X=(1,0,0), sinon Z_ifc=(0,0,1) comme ref
    let refX;
    // composante verticale IFC de l'axe long :
    const izComp = longVecThree[1]; // Three Y -> IFC Z
    if (Math.abs(izComp) > 0.9) { refX = "(1.,0.,0.)"; }
    else { refX = "(0.,0.,1.)"; }

    // profil rectangulaire centre
    const profCtrPt = nextId(); E(profCtrPt, "IFCCARTESIANPOINT((0.,0.));");
    const profDir = nextId(); E(profDir, "IFCDIRECTION((1.,0.));");
    const profPos = nextId(); E(profPos, "IFCAXIS2PLACEMENT2D(#" + profCtrPt + ",#" + profDir + ");");
    const prof = nextId(); E(prof, "IFCRECTANGLEPROFILEDEF(.AREA.,$,#" + profPos + "," + w.toFixed(4) + "," + h.toFixed(4) + ");");

    // placement de la piece : axe Z local = direction longue
    const ptPiece = nextId(); E(ptPiece, "IFCCARTESIANPOINT((" + px.toFixed(4) + "," + py.toFixed(4) + "," + pz.toFixed(4) + "));");
    const dirZpiece = nextId(); E(dirZpiece, "IFCDIRECTION(" + axisZ + ");");
    const dirXpiece = nextId(); E(dirXpiece, "IFCDIRECTION(" + refX + ");");
    const axPiece = nextId(); E(axPiece, "IFCAXIS2PLACEMENT3D(#" + ptPiece + ",#" + dirZpiece + ",#" + dirXpiece + ");");
    const plcPiece = nextId(); E(plcPiece, "IFCLOCALPLACEMENT(#" + storeyPlc + ",#" + axPiece + ");");'''

n = content.count(old)
if n != 1:
    print(f"[ERREUR] ancre trouvee {n} fois (attendu 1) -> abandon")
    exit(1)

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fix_ifc_quat"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")
content = content.replace(old, new, 1)
open("devia.jsx", "w", encoding="utf-8").write(content)
print("[OK] Orientation par quaternion (pieces inclinees) ajoutee")
print("1 MODIFICATION APPLIQUEE")
