import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

DEB = "function genererIFC(metre, params) {"
FIN = r'  return header + lines.join("\n") + "\n" + footer;' + "\n}"

if src.count(DEB) != 1:
    print("ABANDON : debut de genererIFC trouve " + str(src.count(DEB)) + " fois")
    sys.exit(1)
d = src.find(DEB)
f = src.find(FIN, d)
if f < 0:
    print("ABANDON : fin de genererIFC introuvable")
    sys.exit(1)
print("Fonction reperee : " + str(src[d:f].count(chr(10))) + " lignes remplacees")

NOUVELLE = r'''function genererIFC(metre, params) {
  const piecesBois = (metre || []).filter((p) => p.pos); // seulement pieces avec position
  let id = 0;
  const nextId = () => ++id;
  const lines = [];
  const E = (n, s) => { lines.push("#" + n + "=" + s); }; // ecrit une entite

  // Texte STEP : ASCII strict, apostrophes doublees (un accent brut invalide le fichier)
  const txt = (s) => String((s === undefined || s === null) ? "" : s)
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^\x20-\x7E]/g, " ")
    .replace(/'/g, "''");
  // Nombre STEP : toujours un point decimal, jamais NaN ni Infinity
  const num = (v, d) => {
    const x = Number(v);
    return (isFinite(x) ? x : 0).toFixed(d === undefined ? 4 : d);
  };

  // --- En-tete STEP ---
  const now = new Date();
  const stamp = now.toISOString().slice(0, 19);
  const header =
"ISO-10303-21;\n" +
"HEADER;\n" +
"FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');\n" +
"FILE_NAME('devia.ifc','" + stamp + "',('DEVIA'),('DEVIA'),'DEVIA','DEVIA','');\n" +
"FILE_SCHEMA(('IFC4'));\n" +
"ENDSEC;\n" +
"DATA;\n";

  // --- Identifiants IFC : 22 caracteres base64 IFC, le PREMIER limite a 0-3 ---
  // (22 x 6 bits = 132 bits pour 128 bits d UUID : le premier caractere ne porte que 2 bits.
  //  Un GlobalId commencant au-dela de 3 est invalide et fait rejeter le fichier.)
  const B64 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$";
  const guid = () => {
    let s = "0123".charAt(Math.floor(Math.random() * 4));
    for (let i = 1; i < 22; i++) s += B64.charAt(Math.floor(Math.random() * 64));
    return s;
  };

  // --- Contexte de base ---
  const origin = nextId(); E(origin, "IFCCARTESIANPOINT((0.,0.,0.));");
  const dirZ = nextId(); E(dirZ, "IFCDIRECTION((0.,0.,1.));");
  const dirX = nextId(); E(dirX, "IFCDIRECTION((1.,0.,0.));");
  const axisPlacement = nextId(); E(axisPlacement, "IFCAXIS2PLACEMENT3D(#" + origin + ",#" + dirZ + ",#" + dirX + ");");

  const lenUnit = nextId(); E(lenUnit, "IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);");
  const areaUnit = nextId(); E(areaUnit, "IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);");
  const volUnit = nextId(); E(volUnit, "IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);");
  const angUnit = nextId(); E(angUnit, "IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);");
  const unitAssign = nextId(); E(unitAssign, "IFCUNITASSIGNMENT((#" + lenUnit + ",#" + areaUnit + ",#" + volUnit + ",#" + angUnit + "));");

  // --- Producteur du fichier : reclame par les importeurs stricts ---
  const person = nextId(); E(person, "IFCPERSON($,'DEVIA',$,$,$,$,$,$);");
  const orga = nextId(); E(orga, "IFCORGANIZATION($,'DEVIA',$,$,$);");
  const persOrg = nextId(); E(persOrg, "IFCPERSONANDORGANIZATION(#" + person + ",#" + orga + ",$);");
  const appli = nextId(); E(appli, "IFCAPPLICATION(#" + orga + ",'1.0','DEVIA Charpente','DEVIA');");
  const secs = Math.floor(now.getTime() / 1000);
  const owner = nextId();
  E(owner, "IFCOWNERHISTORY(#" + persOrg + ",#" + appli + ",$,.ADDED.," + secs + ",#" + persOrg + ",#" + appli + "," + secs + ");");

  const geomCtx = nextId(); E(geomCtx, "IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#" + axisPlacement + ",$);");
  // Sous-contexte 'Body' : sans lui, beaucoup d importeurs ignorent purement la geometrie
  const bodyCtx = nextId();
  E(bodyCtx, "IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Body','Model',*,*,*,*,#" + geomCtx + ",$,.MODEL_VIEW.,$);");

  // --- Hierarchie spatiale ---
  const project = nextId();
  const site = nextId();
  const building = nextId();
  const storey = nextId();
  E(project, "IFCPROJECT('" + guid() + "',#" + owner + ",'DEVIA Charpente',$,$,$,$,(#" + geomCtx + "),#" + unitAssign + ");");
  const sitePlc = nextId(); E(sitePlc, "IFCLOCALPLACEMENT($,#" + axisPlacement + ");");
  E(site, "IFCSITE('" + guid() + "',#" + owner + ",'Terrain',$,$,#" + sitePlc + ",$,$,.ELEMENT.,$,$,$,$,$);");
  const bldgPlc = nextId(); E(bldgPlc, "IFCLOCALPLACEMENT(#" + sitePlc + ",#" + axisPlacement + ");");
  E(building, "IFCBUILDING('" + guid() + "',#" + owner + ",'Batiment',$,$,#" + bldgPlc + ",$,$,.ELEMENT.,$,$,$);");
  const storeyPlc = nextId(); E(storeyPlc, "IFCLOCALPLACEMENT(#" + bldgPlc + ",#" + axisPlacement + ");");
  E(storey, "IFCBUILDINGSTOREY('" + guid() + "',#" + owner + ",'Niveau 0',$,$,#" + storeyPlc + ",$,$,.ELEMENT.,0.);");

  // Relations d'agregation
  const relAggProj = nextId(); E(relAggProj, "IFCRELAGGREGATES('" + guid() + "',#" + owner + ",$,$,#" + project + ",(#" + site + "));");
  const relAggSite = nextId(); E(relAggSite, "IFCRELAGGREGATES('" + guid() + "',#" + owner + ",$,$,#" + site + ",(#" + building + "));");
  const relAggBldg = nextId(); E(relAggBldg, "IFCRELAGGREGATES('" + guid() + "',#" + owner + ",$,$,#" + building + ",(#" + storey + "));");

  // --- Classe IFC d apres le role de la piece (un logiciel de charpente s en sert) ---
  const classeDe = (nom) => {
    const n = String(nom || "").toLowerCase();
    if (n.indexOf("poteau") >= 0 || n.indexOf("montant") >= 0 || n.indexOf("poincon") >= 0 || n.indexOf("plot") >= 0) return ["IFCCOLUMN", ".COLUMN."];
    if (n.indexOf("panneau") >= 0 || n.indexOf("lame") >= 0 || n.indexOf("planche") >= 0 || n.indexOf("bandeau") >= 0) return ["IFCPLATE", ".SHEET."];
    if (n.indexOf("panne") >= 0 || n.indexOf("solive") >= 0 || n.indexOf("poutre") >= 0 || n.indexOf("muraillere") >= 0
      || n.indexOf("sabliere") >= 0 || n.indexOf("entrait") >= 0 || n.indexOf("lisse") >= 0 || n.indexOf("porteuse") >= 0
      || n.indexOf("faitage") >= 0 || n.indexOf("faitiere") >= 0) return ["IFCBEAM", ".BEAM."];
    return ["IFCMEMBER", ".MEMBER."];
  };

  // --- Une piece -> un element IFC ---
  const memberIds = [];
  piecesBois.forEach((p, iP) => {
    // --- Dimensions Three.js d'origine ---
    const sx = Math.abs(p.dimsBrutes[0]);
    const sy = Math.abs(p.dimsBrutes[1]);
    const sz = Math.abs(p.dimsBrutes[2]);

    // --- Repere local COMPLET de la piece : axe long + roulis de section conserves ---
    // Conversion Three (x,y,z) -> IFC (x,-z,y) : Y haut -> Z haut, nord scene (-Z) -> +Y IFC.
    // (l'ancienne conversion (x,z,y) inversait la chiralite : batiment exporte en MIROIR)
    const fmtDir = (v) => {
      const nrm = Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]) || 1;
      return "(" + num(v[0]/nrm, 6) + "," + num(v[1]/nrm, 6) + "," + num(v[2]/nrm, 6) + ")";
    };
    const toIfcVec = (v) => [v[0], -v[2], v[1]];
    // Matrice de rotation de la piece (quaternion prioritaire, sinon euler XYZ Three, sinon identite)
    const mRot = new THREE.Matrix4();
    if (p.quat) {
      mRot.makeRotationFromQuaternion(new THREE.Quaternion(p.quat[0], p.quat[1], p.quat[2], p.quat[3]));
    } else if (p.rot) {
      mRot.makeRotationFromEuler(new THREE.Euler(p.rot[0] || 0, p.rot[1] || 0, p.rot[2] || 0, "XYZ"));
    }
    const elm = mRot.elements; // colonne-major
    const axesLoc = [
      [elm[0], elm[1], elm[2]],   // axe X local exprime dans le repere Three
      [elm[4], elm[5], elm[6]],   // axe Y local
      [elm[8], elm[9], elm[10]],  // axe Z local
    ];
    // Axe long = plus grande dimension ; les 2 autres = la section
    const dims3 = [sx, sy, sz];
    let iLong = 0;
    if (dims3[1] > dims3[iLong]) iLong = 1;
    if (dims3[2] > dims3[iLong]) iLong = 2;
    const iX = (iLong + 1) % 3;
    const iY = (iLong + 2) % 3;
    const L = dims3[iLong];
    const w = dims3[iX];
    const h = dims3[iY];
    if ((L > 0.001 && w > 0.001 && h > 0.001) === false) return; // piece degeneree : jamais exportee
    // Placement IFC : Z local = axe long REEL de la piece, X local = axe de section REEL (roulis conserve)
    const axisZ = fmtDir(toIfcVec(axesLoc[iLong]));
    const refX = fmtDir(toIfcVec(axesLoc[iX]));
    // Position du centre, Three (x,y,z) -> IFC (x,-z,y)
    const px = p.pos[0], py = -p.pos[2], pz = p.pos[1];

    // profil rectangulaire centre
    const profCtrPt = nextId(); E(profCtrPt, "IFCCARTESIANPOINT((0.,0.));");
    const profDir = nextId(); E(profDir, "IFCDIRECTION((1.,0.));");
    const profPos = nextId(); E(profPos, "IFCAXIS2PLACEMENT2D(#" + profCtrPt + ",#" + profDir + ");");
    const prof = nextId(); E(prof, "IFCRECTANGLEPROFILEDEF(.AREA.,$,#" + profPos + "," + num(w) + "," + num(h) + ");");

    // placement de la piece : axe Z local = direction longue
    const ptPiece = nextId(); E(ptPiece, "IFCCARTESIANPOINT((" + num(px) + "," + num(py) + "," + num(pz) + "));");
    const dirZpiece = nextId(); E(dirZpiece, "IFCDIRECTION(" + axisZ + ");");
    const dirXpiece = nextId(); E(dirXpiece, "IFCDIRECTION(" + refX + ");");
    const axPiece = nextId(); E(axPiece, "IFCAXIS2PLACEMENT3D(#" + ptPiece + ",#" + dirZpiece + ",#" + dirXpiece + ");");
    const plcPiece = nextId(); E(plcPiece, "IFCLOCALPLACEMENT(#" + storeyPlc + ",#" + axPiece + ");");

    // extrusion : dans le repere local, on extrude selon Z local, centree (-L/2)
    const extrPt = nextId(); E(extrPt, "IFCCARTESIANPOINT((0.,0.," + num(-L/2) + "));");
    const extrAx = nextId(); E(extrAx, "IFCAXIS2PLACEMENT3D(#" + extrPt + ",$,$);");
    const extrDir = nextId(); E(extrDir, "IFCDIRECTION((0.,0.,1.));");
    const solid = nextId(); E(solid, "IFCEXTRUDEDAREASOLID(#" + prof + ",#" + extrAx + ",#" + extrDir + "," + num(L) + ");");

    const shapeRep = nextId(); E(shapeRep, "IFCSHAPEREPRESENTATION(#" + bodyCtx + ",'Body','SweptSolid',(#" + solid + "));");
    const prodDef = nextId(); E(prodDef, "IFCPRODUCTDEFINITIONSHAPE($,$,(#" + shapeRep + "));");

    const cls = classeDe(p.nom);
    const member = nextId();
    E(member, cls[0] + "('" + guid() + "',#" + owner + ",'" + txt(p.nom || "Piece") + "',$,$,#" + plcPiece + ",#" + prodDef + ",'" + (iP + 1) + "'," + cls[1] + ");");
    memberIds.push(member);
  });

  // Rattacher tous les elements au niveau
  if (memberIds.length > 0) {
    const relContain = nextId();
    E(relContain, "IFCRELCONTAINEDINSPATIALSTRUCTURE('" + guid() + "',#" + owner + ",$,$,(#" + memberIds.join(",#") + "),#" + storey + ");");
    // Matiere : toute la charpente est du bois massif
    const matBois = nextId(); E(matBois, "IFCMATERIAL('Bois massif C24',$,'Bois');");
    const relMat = nextId();
    E(relMat, "IFCRELASSOCIATESMATERIAL('" + guid() + "',#" + owner + ",$,$,(#" + memberIds.join(",#") + "),#" + matBois + ");");
  }
  console.log("[DEVIA] IFC : " + memberIds.length + " element(s) exporte(s)");

  const footer = "ENDSEC;\nEND-ISO-10303-21;\n";
  return header + lines.join("\n") + "\n" + footer;
}'''

src = src[:d] + NOUVELLE + src[f + len(FIN):]
open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit : generateur IFC remplace ---")
