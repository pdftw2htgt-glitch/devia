# -*- coding: utf-8 -*-
import io, sys

chemin = sys.argv[1] if len(sys.argv) > 1 else "devia.jsx"
s = io.open(chemin, encoding="utf-8").read()
etapes = []

def rempl(titre, ancre, nouveau, attendu=1):
    global s
    n = s.count(ancre)
    etapes.append((titre, n, attendu))
    if n > attendu or n < attendu:
        raise SystemExit("ABANDON sur '" + titre + "' : " + str(n) + " occurrence(s), attendu " + str(attendu))
    s = s.replace(ancre, nouveau)

# ---------------------------------------------------------------- 1. le reglage
rempl("1. lecture du delardement",
"  const debord = Math.max(0, parseFloat(params.debord) || 0); // depasse de toiture (m), egouts + rives\n",
"""  const debord = Math.max(0, parseFloat(params.debord) || 0); // depasse de toiture (m), egouts + rives
  // DELARDEMENT DES PANNES (m). Une panne d aplomb ne touche le chevron que par l arete AVAL
  // de son dessus : on y coupe un plat parallele au rampant pour que le chevron porte a plat.
  // Saisi en MILLIMETRES dans le formulaire, 15 par defaut (usinage courant de charpentier).
  const delardement = Math.max(0, (params.delardement === undefined || params.delardement === null || params.delardement === "")
    ? 15 : (parseFloat(params.delardement) || 0)) / 1000;
""")

# ---------------------------------------------------------------- 2. le moteur geometrique
rempl("2. fonctions de dessin de la panne delardee",
"""  // Poutre orientee entre 2 points (touche forcement les 2 extremites)
  const addBeam = (x1, y1, z1, x2, y2, z2, thick, mat) => {""",
"""  // ===== PANNE DELARDEE =====
  // Section de la panne dans le plan (y, z), relative a son centre, une fois delardee.
  // tanP = tangente de la pente ; del = profondeur du plat a l arete aval (m).
  // signAval : +1 la pente descend vers les z croissants, -1 l inverse, 0 des deux cotes
  // (faitiere : un chevron vient mourir dessus de chaque cote, donc deux plats).
  const sectionDelardee = (h, b, tanP, signAval, del) => {
    const d = Math.max(0, Math.min(del, h * 0.6));          // jamais plus de 60 pour cent de la hauteur
    const plat = (tanP > 0.0001) ? d / tanP : 0;            // portee horizontale du plat
    let pts;
    if (d < 0.0005 || plat < 0.0005) {
      pts = [[-h/2, -b/2], [-h/2, b/2], [h/2, b/2], [h/2, -b/2]];
    } else if (signAval === 0) {
      const p2 = Math.min(plat, b/2);
      pts = (p2 >= b/2 - 0.0005)
        ? [[-h/2, -b/2], [-h/2, b/2], [h/2 - d, b/2], [h/2 - d + (b/2) * tanP, 0], [h/2 - d, -b/2]]
        : [[-h/2, -b/2], [-h/2, b/2], [h/2 - d, b/2], [h/2, b/2 - p2], [h/2, -b/2 + p2], [h/2 - d, -b/2]];
    } else {
      const p1 = Math.min(plat, b);
      pts = (p1 >= b - 0.0005)
        ? [[-h/2, -b/2], [-h/2, b/2], [h/2 - d, b/2], [h/2 - Math.max(0, d - b * tanP), -b/2]]
        : [[-h/2, -b/2], [-h/2, b/2], [h/2 - d, b/2], [h/2, b/2 - p1], [h/2, -b/2]];
      if (signAval < 0) pts = pts.map((q) => [q[0], -q[1]]);
    }
    // Sens trigonometrique impose : un profil IFC parcouru a l envers donne une aire negative.
    let aire = 0;
    for (let i = 0; i < pts.length; i++) {
      const q = pts[i], r = pts[(i + 1) % pts.length];
      aire += q[0] * r[1] - r[0] * q[1];
    }
    if (aire < 0) pts = pts.slice().reverse();
    return pts;
  };

  // Prisme de section quelconque file selon X. Remplace addBox pour les pannes delardees.
  const addPanneDelardee = (lgX, h, b, px, py, pz, tanP, signAval, del, mat, nomForce) => {
    const pts = sectionDelardee(h, b, tanP, signAval, del);
    const x1 = px - lgX / 2, x2 = px + lgX / 2;
    const S1 = pts.map((q) => [x1, py + q[0], pz + q[1]]);
    const S2 = pts.map((q) => [x2, py + q[0], pz + q[1]]);
    const pos = [];
    const tri = (a, c, e) => { pos.push(a[0],a[1],a[2], c[0],c[1],c[2], e[0],e[1],e[2]); };
    for (let i = 1; i < pts.length - 1; i++) { tri(S1[0], S1[i + 1], S1[i]); tri(S2[0], S2[i], S2[i + 1]); }
    for (let i = 0; i < pts.length; i++) {
      const j = (i + 1) % pts.length;
      tri(S1[i], S1[j], S2[j]); tri(S1[i], S2[j], S2[i]);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pos), 3));
    g.computeVertexNormals();
    const m = new THREE.Mesh(g, mat || woodMat);
    m.castShadow = true;
    scene.add(m);
    // Le metre garde la SECTION NOMINALE : le delardement est un usinage, pas une section de
    // debit. On commande bien une panne pleine. Seul l export IFC recoit le profil reel.
    logPiece(lgX, h, b, { pos: [px, py, pz], rot: null, quat: null }, nomForce);
    // Delardement nul : la section reste un rectangle, l IFC garde son profil rectangulaire.
    const plein = pts.every((q) => Math.abs(Math.abs(q[0]) - h / 2) < 0.000001);
    if (plein === false) metre[metre.length - 1].profil = { pts: pts, len: lgX, axe: "x" };
  };

  // Poutre orientee entre 2 points (touche forcement les 2 extremites)
  const addBeam = (x1, y1, z1, x2, y2, z2, thick, mat) => {""")

# ---------------------------------------------------------------- 3. charpente traditionnelle
rempl("3a. section de panne alignee (murs)",
'    const [pnB0, pnH0] = sec("Panne", 0.12, 0.12);\n',
'    const [pnB0, pnH0] = sec("Panne", 0.12, 0.24);\n')

rempl("3b. plan porteur (murs et reservations)",
"    const dPerp0 = arH0 / 2 + (pnH0 + 0.03) * cosA0;\n"
"    const hMurSousSabliere = Ht + dPerp0 / cosA0 + (sbB0 / 2) * tanA0 - sbH0;\n",
"    // Le chevron porte sur l arete AVAL du dessus de la panne, moins le delardement :\n"
"    // la largeur de la panne compte donc dans la hauteur du plan porteur.\n"
"    const dPerp0 = arH0 / 2 + (pnH0 + 0.03 - delardement) * cosA0 + pnB0 * Math.sin(ang);\n"
"    const hMurSousSabliere = Ht + dPerp0 / cosA0 - (sbB0 / 2) * tanA0 + delardement - sbH0;\n")

rempl("3c. reservation de la faitiere dans le pignon",
"    reservPignon.push({ z: 0, y: Ht + hf + dPerp0 / cosA0 - pfH0 / 2, b: pfB0, h: pfH0 });\n",
"    reservPignon.push({ z: 0, y: Ht + hf + dPerp0 / cosA0 - (pfB0 / 2) * tanA0 + delardement - pfH0 / 2, b: pfB0, h: pfH0 });\n")

rempl("3d. section de panne alignee (sablieres)",
'    const [pnBr, pnHr] = sec("Panne", 0.12, 0.12);\n',
'    const [pnBr, pnHr] = sec("Panne", 0.12, 0.24);\n')

rempl("3e. plan porteur des chevrons",
"    const dPerpSousChevron = arHr / 2 + (pnHr + 0.03) * cosR;\n",
"    const dPerpSousChevron = arHr / 2 + (pnHr + 0.03 - delardement) * cosR + pnBr * Math.sin(ang);\n")

rempl("3f. sablieres delardees",
"    const ySabl = yPlanRampant + (sbB / 2) * tanR - sbH / 2;  // coin amont de la sabliere sur ce plan\n"
"    addBox(L + 0.3, sbH, sbB, 0, ySabl, lg/2, woodMat);\n"
"    addBox(L + 0.3, sbH, sbB, 0, ySabl, -lg/2, woodMat);\n",
"    const ySabl = yPlanRampant - (sbB / 2) * tanR + delardement - sbH / 2;  // dessus delarde dans le plan des chevrons\n"
"    addPanneDelardee(L + 0.3, sbH, sbB, 0, ySabl, lg/2, tanR, 1, delardement, woodMat);\n"
"    addPanneDelardee(L + 0.3, sbH, sbB, 0, ySabl, -lg/2, tanR, -1, delardement, woodMat);\n")

rempl("3g. faitiere delardee sur ses deux aretes",
"    const yFaitPanne = yFait + dPerpSousChevron / cosR - pfH / 2;\n"
"    addBox(L + 0.4 + debLX, pfH, pfB, debCX, yFaitPanne, 0, woodMat);\n",
"    const yFaitPanne = yFait + dPerpSousChevron / cosR - (pfB / 2) * tanR + delardement - pfH / 2;\n"
"    addPanneDelardee(L + 0.4 + debLX, pfH, pfB, debCX, yFaitPanne, 0, tanR, 0, delardement, woodMat);\n")

rempl("3h. pannes delardees",
"      addBox(L + 0.3 + debLX, pnH, pnB, debCX, yP, zRef, woodMat);   // pan Z+ (droite)\n"
"      addBox(L + 0.3 + debLX, pnH, pnB, debCX, yP, -zRef, woodMat);  // pan Z- (droite)\n",
"      addPanneDelardee(L + 0.3 + debLX, pnH, pnB, debCX, yP, zRef, tanA, 1, delardement, woodMat);   // pan Z+\n"
"      addPanneDelardee(L + 0.3 + debLX, pnH, pnB, debCX, yP, -zRef, tanA, -1, delardement, woodMat); // pan Z-\n")

rempl("3i. pose des chevrons sur le delardement",
"    const dPerpChevron = arH2/2 + (pnH + 0.03) * cosA + chH/2;\n",
"    const dPerpChevron = arH2/2 + (pnH + 0.03 - delardement) * cosA + pnB * sinA + chH/2;\n")

rempl("3j. couverture calee sur les chevrons",
"    const dPerpCouv = arH2/2 + (pnH + 0.03) * cosA + chH + 0.01;\n",
"    const dPerpCouv = dPerpChevron + chH / 2 + 0.01;\n")

# ---------------------------------------------------------------- 4. export IFC
rempl("4. profil reel dans l export IFC",
"    // --- Dimensions Three.js d'origine ---\n"
"    const sx = Math.abs(p.dimsBrutes[0]);\n",
"""    // --- Piece bois usinee : on exporte son PROFIL REEL, pas un rectangle plein ---
    // profil = { pts: [[u, v], ...], len, axe:"x" } ; u suit l axe Y de la scene (hauteur),
    // v son axe Z, l extrusion suit X. Cadwork recoit ainsi le delardement des pannes.
    if (p.profil && Array.isArray(p.profil.pts) && p.profil.pts.length >= 3 && p.profil.len > 0.01) {
      const idsD = p.profil.pts.map((q) => {
        const idq = nextId();
        E(idq, "IFCCARTESIANPOINT((" + num(q[0]) + "," + num(q[1]) + "));");
        return idq;
      });
      const polyD = nextId(); E(polyD, "IFCPOLYLINE((#" + idsD.join(",#") + ",#" + idsD[0] + "));");
      const profD = nextId(); E(profD, "IFCARBITRARYCLOSEDPROFILEDEF(.AREA.,$,#" + polyD + ");");
      // Repere : Z local = X de la scene (axe long), X local = Y de la scene (hauteur).
      // Le Y local tombe alors sur le Z de la scene, comme les points du profil.
      const posD = nextId(); E(posD, "IFCCARTESIANPOINT((" + num(p.pos[0]) + "," + num(-p.pos[2]) + "," + num(p.pos[1]) + "));");
      const dzD = nextId(); E(dzD, "IFCDIRECTION((1.,0.,0.));");
      const dxD = nextId(); E(dxD, "IFCDIRECTION((0.,0.,1.));");
      const axD = nextId(); E(axD, "IFCAXIS2PLACEMENT3D(#" + posD + ",#" + dzD + ",#" + dxD + ");");
      const plcD = nextId(); E(plcD, "IFCLOCALPLACEMENT(#" + storeyPlc + ",#" + axD + ");");
      const exPtD = nextId(); E(exPtD, "IFCCARTESIANPOINT((0.,0.," + num(-p.profil.len / 2) + "));");
      const exAxD = nextId(); E(exAxD, "IFCAXIS2PLACEMENT3D(#" + exPtD + ",$,$);");
      const exDirD = nextId(); E(exDirD, "IFCDIRECTION((0.,0.,1.));");
      const solD = nextId(); E(solD, "IFCEXTRUDEDAREASOLID(#" + profD + ",#" + exAxD + ",#" + exDirD + "," + num(p.profil.len) + ");");
      const repD = nextId(); E(repD, "IFCSHAPEREPRESENTATION(#" + bodyCtx + ",'Body','SweptSolid',(#" + solD + "));");
      const pdD = nextId(); E(pdD, "IFCPRODUCTDEFINITIONSHAPE($,$,(#" + repD + "));");
      const clsD = classeDe(p);
      const memD = nextId();
      E(memD, clsD[0] + "('" + guid() + "',#" + owner + ",'" + txt(p.nom || "Piece") + "',$,$,#" + plcD + ",#" + pdD + ",'" + (iP + 1) + "'," + clsD[1] + ");");
      memberIds.push(memD);
      if (p.matiere === "beton") idsBeton.push(memD); else idsBois.push(memD);
      return;
    }
    // --- Dimensions Three.js d'origine ---
    const sx = Math.abs(p.dimsBrutes[0]);
""")

# ---------------------------------------------------------------- 5. formulaire
rempl("5a. etat du champ",
'const [formDebord, setFormDebord] = useState(""); // depasse de toiture en cm (vide = 0)\n',
'const [formDebord, setFormDebord] = useState(""); // depasse de toiture en cm (vide = 0)\n'
'const [formDelardement, setFormDelardement] = useState("15"); // delardement des pannes en mm\n')

rempl("5b. champ dans le formulaire",
"""                  <span style={{ color: "#545870", fontSize: 12 }}>cm (egouts et rives)</span>
                </div>
              </div>
""",
"""                  <span style={{ color: "#545870", fontSize: 12 }}>cm (egouts et rives)</span>
                </div>
              </div>
              {/* Delardement des pannes */}
              <div style={{ marginBottom: 18, display: ["terrasse","etage","balcon","garde_corps"].includes(typeEffectif) ? "none" : undefined }}>
                <label style={{ display: "block", color: themeMode === "light" ? "#474b5c" : cl("#9ca0b8", "#565a6c"), fontSize: 11, marginBottom: 10, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Delardement</label>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <input value={formDelardement} onChange={e => setFormDelardement(e.target.value)} type="number" placeholder="15" style={{ ...inputStyle, maxWidth: 100 }} />
                  <span style={{ color: "#545870", fontSize: 12 }}>mm (plat coupe sur le dessus des pannes)</span>
                </div>
              </div>
""")

rempl("5c. parametre de generation",
"      debord: formDebord ? parseFloat(formDebord) / 100 : undefined,\n",
"      debord: formDebord ? parseFloat(formDebord) / 100 : undefined,\n"
'      delardement: formDelardement === "" ? undefined : parseFloat(formDelardement),\n')

rempl("5d. memorisation dans le devis",
"  if (finalParams.debord) parsed._debord = finalParams.debord;\n",
"  if (finalParams.debord) parsed._debord = finalParams.debord;\n"
'  if (typeof finalParams.delardement === "number") parsed._delardement = finalParams.delardement;\n')

rempl("5e. transmission a la 3D",
"        debord: finalParams.debord || undefined,\n",
"        debord: finalParams.debord || undefined,\n"
"        delardement: finalParams.delardement,\n")

rempl("5f. rechargement d un projet",
"        debord: project.devis_data._debord || undefined,\n",
"        debord: project.devis_data._debord || undefined,\n"
"        delardement: project.devis_data._delardement,\n")

rempl("5g. projet multi-ouvrages",
"        ouvrages: ouvrages3D,\n"
"        sk: zoneInfo ? zoneInfo.sk : undefined,\n",
"        ouvrages: ouvrages3D,\n"
'        delardement: formDelardement === "" ? undefined : parseFloat(formDelardement),\n'
"        sk: zoneInfo ? zoneInfo.sk : undefined,\n")

rempl("5h. memorisation multi-ouvrages",
"      if (zoneInfo) { fusion._sk = zoneInfo.sk; fusion._dS = zoneInfo.dS; }\n",
'      if (formDelardement === "") { fusion._delardement = undefined; } else { fusion._delardement = parseFloat(formDelardement); }\n'
"      if (zoneInfo) { fusion._sk = zoneInfo.sk; fusion._dS = zoneInfo.dS; }\n")

io.open(chemin, "w", encoding="utf-8").write(s)
for t, n, a in etapes:
    print("  " + t + " : " + str(n) + "/" + str(a))
print("OK delardement pose")
