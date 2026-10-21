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

# ------------------------------------------------- 1. le reglage
rempl("1. lecture du debord de panne",
"""  const delardement = Math.max(0, (params.delardement === undefined || params.delardement === null || params.delardement === "")
    ? 15 : (parseFloat(params.delardement) || 0)) / 1000;
""",
"""  const delardement = Math.max(0, (params.delardement === undefined || params.delardement === null || params.delardement === "")
    ? 15 : (parseFloat(params.delardement) || 0)) / 1000;
  // DEBORD DE PANNE (m) : la queue de panne qui ressort au pignon pour porter le chevron
  // de rive. Saisi en CENTIMETRES dans le formulaire, 50 par defaut.
  const debordPanne = Math.max(0, (params.debord_panne === undefined || params.debord_panne === null || params.debord_panne === "")
    ? 50 : (parseFloat(params.debord_panne) || 0)) / 100;
""")

# ------------------------------------------------- 2. charpente traditionnelle
rempl("2. calcul du debord par pignon",
"""    const rivG = smf === "pignon_gauche" ? 0 : 0.3;       // petit debord de rive de base, sauf cote contact
    const rivD = smf === "pignon_droit" ? 0 : 0.3;
""",
"""    const rivG = smf === "pignon_gauche" ? 0 : 0.3;       // petit debord de rive de base, sauf cote contact
    const rivD = smf === "pignon_droit" ? 0 : 0.3;
    // QUEUES DE PANNE : pannes, sabliere et faitiere ressortent au pignon pour porter le
    // chevron de rive. Au moins le debord demande, et jamais moins loin que la couverture,
    // sinon elle porterait dans le vide. Rien ne ressort du cote ou un volume vient s accoler.
    const dpG = smf === "pignon_gauche" ? 0 : Math.max(debordPanne, rivG + debG);
    const dpD = smf === "pignon_droit" ? 0 : Math.max(debordPanne, rivD + debD);
    const dpLX = dpG + dpD;                               // allongement total des pannes
    const dpCX = (dpD - dpG) / 2;                         // recentrage quand un seul cote ressort
""")

rempl("3. sablieres",
"    addPanneDelardee(L + 0.3, sbH, sbB, 0, ySabl, lg/2, tanR, 1, delardement, woodMat);\n"
"    addPanneDelardee(L + 0.3, sbH, sbB, 0, ySabl, -lg/2, tanR, -1, delardement, woodMat);\n",
"    addPanneDelardee(L + dpLX, sbH, sbB, dpCX, ySabl, lg/2, tanR, 1, delardement, woodMat);\n"
"    addPanneDelardee(L + dpLX, sbH, sbB, dpCX, ySabl, -lg/2, tanR, -1, delardement, woodMat);\n")

rempl("4. faitiere",
"    addPanneDelardee(L + 0.4 + debLX, pfH, pfB, debCX, yFaitPanne, 0, tanR, 0, delardement, woodMat);\n",
"    addPanneDelardee(L + dpLX, pfH, pfB, dpCX, yFaitPanne, 0, tanR, 0, delardement, woodMat);\n")

rempl("5. pannes",
"      addPanneDelardee(L + 0.3 + debLX, pnH, pnB, debCX, yP, zRef, tanA, 1, delardement, woodMat);   // pan Z+\n"
"      addPanneDelardee(L + 0.3 + debLX, pnH, pnB, debCX, yP, -zRef, tanA, -1, delardement, woodMat); // pan Z-\n",
"      addPanneDelardee(L + dpLX, pnH, pnB, dpCX, yP, zRef, tanA, 1, delardement, woodMat);   // pan Z+\n"
"      addPanneDelardee(L + dpLX, pnH, pnB, dpCX, yP, -zRef, tanA, -1, delardement, woodMat); // pan Z-\n")

# ------------------------------------------------- 3. formulaire
rempl("6a. etat du champ",
'const [formDelardement, setFormDelardement] = useState("15"); // delardement des pannes en mm\n',
'const [formDelardement, setFormDelardement] = useState("15"); // delardement des pannes en mm\n'
'const [formDebordPanne, setFormDebordPanne] = useState("50"); // queue de panne au pignon, en cm\n')

rempl("6b. champ dans le formulaire",
"""                  <input value={formDelardement} onChange={e => setFormDelardement(e.target.value)} type="number" placeholder="15" style={{ ...inputStyle, maxWidth: 100 }} />
                  <span style={{ color: "#545870", fontSize: 12 }}>mm (plat coupe sur le dessus des pannes)</span>
                </div>
              </div>
""",
"""                  <input value={formDelardement} onChange={e => setFormDelardement(e.target.value)} type="number" placeholder="15" style={{ ...inputStyle, maxWidth: 100 }} />
                  <span style={{ color: "#545870", fontSize: 12 }}>mm (plat coupe sur le dessus des pannes)</span>
                </div>
              </div>
              {/* Debord de panne */}
              <div style={{ marginBottom: 18, display: ["terrasse","etage","balcon","garde_corps"].includes(typeEffectif) ? "none" : undefined }}>
                <label style={{ display: "block", color: themeMode === "light" ? "#474b5c" : cl("#9ca0b8", "#565a6c"), fontSize: 11, marginBottom: 10, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Debord de panne</label>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <input value={formDebordPanne} onChange={e => setFormDebordPanne(e.target.value)} type="number" placeholder="50" style={{ ...inputStyle, maxWidth: 100 }} />
                  <span style={{ color: "#545870", fontSize: 12 }}>cm (queue de panne de chaque cote, au pignon)</span>
                </div>
              </div>
""")

rempl("6c. parametre de generation",
'      debord: formDebord ? parseFloat(formDebord) / 100 : undefined,\n      delardement: formDelardement === "" ? undefined : parseFloat(formDelardement),\n',
'      debord: formDebord ? parseFloat(formDebord) / 100 : undefined,\n      delardement: formDelardement === "" ? undefined : parseFloat(formDelardement),\n'
'      debord_panne: formDebordPanne === "" ? undefined : parseFloat(formDebordPanne),\n')

rempl("6d. memorisation dans le devis",
'  if (typeof finalParams.delardement === "number") parsed._delardement = finalParams.delardement;\n',
'  if (typeof finalParams.delardement === "number") parsed._delardement = finalParams.delardement;\n'
'  if (typeof finalParams.debord_panne === "number") parsed._debordPanne = finalParams.debord_panne;\n')

rempl("6e. transmission a la 3D",
"        delardement: finalParams.delardement,\n",
"        delardement: finalParams.delardement,\n"
"        debord_panne: finalParams.debord_panne,\n")

rempl("6f. rechargement d un projet",
"        delardement: project.devis_data._delardement,\n",
"        delardement: project.devis_data._delardement,\n"
"        debord_panne: project.devis_data._debordPanne,\n")

rempl("6g. projet multi-ouvrages",
'        finition_mur: formFinitionMur || undefined,\n        delardement: formDelardement === "" ? undefined : parseFloat(formDelardement),\n',
'        finition_mur: formFinitionMur || undefined,\n        delardement: formDelardement === "" ? undefined : parseFloat(formDelardement),\n'
'        debord_panne: formDebordPanne === "" ? undefined : parseFloat(formDebordPanne),\n')

rempl("6h. memorisation multi-ouvrages",
'      if (formDelardement === "") { fusion._delardement = undefined; } else { fusion._delardement = parseFloat(formDelardement); }\n',
'      if (formDelardement === "") { fusion._delardement = undefined; } else { fusion._delardement = parseFloat(formDelardement); }\n'
'      if (formDebordPanne === "") { fusion._debordPanne = undefined; } else { fusion._debordPanne = parseFloat(formDebordPanne); }\n')

io.open(chemin, "w", encoding="utf-8").write(s)
for t, n, a in etapes:
    print("  " + t + " : " + str(n) + "/" + str(a))
print("OK debord de panne pose")
