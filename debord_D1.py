import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_debord_D1_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ===== P1 : parametre debord (metres) lu par le moteur 3D =====
remplacer('''  const pente = params.pente || 35;
  const typeProjet = params.type_projet || "charpente_trad";''',
'''  const pente = params.pente || 35;
  const debord = Math.max(0, parseFloat(params.debord) || 0); // depasse de toiture (m), egouts + rives
  const typeProjet = params.type_projet || "charpente_trad";''', "P1")

# ===== P2 : faitiere prolongee en rives =====
remplacer('''    addBox(L + 0.4, pfH, pfB, 0, yFait, 0, woodMat);''',
'''    addBox(L + 0.4 + 2 * debord, pfH, pfB, 0, yFait, 0, woodMat);''', "P2")

# ===== P3 : pannes prolongees en rives (queues de panne) =====
remplacer('''      addBox(L + 0.3, pnH, pnB, 0, yP, zRef, woodMat);   // pan Z+ (droite)
      addBox(L + 0.3, pnH, pnB, 0, yP, -zRef, woodMat);  // pan Z- (droite)''',
'''      addBox(L + 0.3 + 2 * debord, pnH, pnB, 0, yP, zRef, woodMat);   // pan Z+ (droite)
      addBox(L + 0.3 + 2 * debord, pnH, pnB, 0, yP, -zRef, woodMat);  // pan Z- (droite)''', "P3")

# ===== P4 : chevrons prolonges au-dela du mur (depasse egout) =====
remplacer('''      const zE = lg/2;                              // egout (aplomb du mur)''',
'''      const zE = lg/2 + debord;                     // egout (aplomb du mur + depasse)''', "P4")

# ===== P5 : chevrons de rive au bord du depasse de pignon =====
remplacer('''    fermeXs.forEach((fx) => chevronXs.push(fx));''',
'''    fermeXs.forEach((fx) => chevronXs.push(fx));
    // Chevrons de rive : au bord du depasse de pignon (portes par les queues de panne)
    if (debord > 0.05) { chevronXs.push(-(L/2 + debord - chB/2)); chevronXs.push(L/2 + debord - chB/2); }''', "P5")

# ===== P6 : couverture prolongee (egout + rives), centre du pan recale =====
remplacer('''    const couv = getCouverture(opts && opts.couverture);
    const dPerpCouv = arH2/2 + (pnH + 0.03) * cosA + chH + 0.01;
    const ext = dPerpCouv * Math.tan(ang);
    const plCouv = pl + ext;
    const tradRoofMat = makeRoofMaterial(couv, L, plCouv);
    const rg = new THREE.PlaneGeometry(L + 0.6, plCouv);
    // centre du pan : centre rampant + dPerp perpendiculaire + ext/2 vers le haut le long du rampant
    const yR = Ht + hf/2 + dPerpCouv * cosA + (ext/2) * sinA;
    const zR = lg/4 + dPerpCouv * sinA - (ext/2) * cosA;''',
'''    const couv = getCouverture(opts && opts.couverture);
    const dPerpCouv = arH2/2 + (pnH + 0.03) * cosA + chH + 0.01;
    const ext = dPerpCouv * Math.tan(ang);
    const extBas = debord / cosA;                 // prolongement du rampant = depasse en egout
    const plCouv = pl + ext + extBas;
    const tradRoofMat = makeRoofMaterial(couv, L + 2 * debord, plCouv);
    const rg = new THREE.PlaneGeometry(L + 0.6 + 2 * debord, plCouv);
    // centre du pan : centre rampant + dPerp perpendiculaire + ext/2 vers le haut + extBas/2 vers le bas
    const yR = Ht + hf/2 + dPerpCouv * cosA + (ext/2) * sinA - (extBas/2) * sinA;
    const zR = lg/4 + dPerpCouv * sinA - (ext/2) * cosA + (extBas/2) * cosA;''', "P6")

# ===== F1 : etat formulaire (saisi en cm) =====
remplacer('''const [formPenteUnite, setFormPenteUnite] = useState("deg"); // "deg" ou "pourcent" - formPente reste TOUJOURS en degres''',
'''const [formPenteUnite, setFormPenteUnite] = useState("deg"); // "deg" ou "pourcent" - formPente reste TOUJOURS en degres
const [formDebord, setFormDebord] = useState(""); // depasse de toiture en cm (vide = 0)''', "F1")

# ===== F2 : champ debord dans les params du devis (converti en metres) =====
remplacer('''      pente: formPente ? parseFloat(formPente) : undefined,
    };''',
'''      pente: formPente ? parseFloat(formPente) : undefined,
      debord: formDebord ? parseFloat(formDebord) / 100 : undefined,
    };''', "F2")

# ===== F3 : le depasse dans la description envoyee a l'IA de generation =====
remplacer('''    if (formLongueur && formLargeur) parts.push(formLongueur + "x" + formLargeur + "m");''',
'''    if (formLongueur && formLargeur) parts.push(formLongueur + "x" + formLargeur + "m");
    if (formDebord) parts.push("depasse de toiture " + formDebord + " cm");''', "F3")

# ===== F4 : le depasse dans le prompt structure de generation =====
remplacer('''(fp.pente ? "Pente=" + fp.pente + "deg. " : "") +''',
'''(fp.pente ? "Pente=" + fp.pente + "deg. " : "") +
(fp.debord ? "DepasseToiture=" + fp.debord + "m (rallonge la couverture en egout et en rives). " : "") +''', "F4")

# ===== W1 : debord dans view3DParams (devis solo) =====
remplacer('''        murs: finalParams.murs || undefined,
        solaire: finalParams.solaire || undefined
      });''',
'''        murs: finalParams.murs || undefined,
        solaire: finalParams.solaire || undefined,
        debord: finalParams.debord || undefined
      });''', "W1")

# ===== W2 : persistance dans devis_data (rechargement) =====
remplacer('''  if (finalParams.solaire) parsed._solaire = finalParams.solaire;''',
'''  if (finalParams.solaire) parsed._solaire = finalParams.solaire;
  if (finalParams.debord) parsed._debord = finalParams.debord;''', "W2")

# ===== W3 : rechargement projet =====
remplacer('''        murs: project.devis_data._murs || undefined,
        solaire: project.devis_data._solaire || undefined,
        ouvrages: project.devis_data._ouvrages3D || undefined,
      });''',
'''        murs: project.devis_data._murs || undefined,
        solaire: project.devis_data._solaire || undefined,
        debord: project.devis_data._debord || undefined,
        ouvrages: project.devis_data._ouvrages3D || undefined,
      });''', "W3")

# ===== W4 : debord transmis aux ouvrages 3D (multi, prepare l'etape 2) =====
remplacer('''        longueur: s.longueur, largeur: s.largeur, hauteur: s.hauteur, pente: s.pente,
        couverture: s.couverture, essence: s.essence, murs: s.murs,''',
'''        longueur: s.longueur, largeur: s.largeur, hauteur: s.hauteur, pente: s.pente,
        couverture: s.couverture, essence: s.essence, murs: s.murs, debord: s.debord || undefined,''', "W4")

# ===== W5 : debord conserve quand on isole un ouvrage dans le viewer =====
remplacer(''', type_projet: view3DParams.ouvrages[ouvrageActif].type_projet, couverture: view3DParams.ouvrages[ouvrageActif].couverture || view3DParams.couverture }''',
''', type_projet: view3DParams.ouvrages[ouvrageActif].type_projet, couverture: view3DParams.ouvrages[ouvrageActif].couverture || view3DParams.couverture, debord: view3DParams.ouvrages[ouvrageActif].debord }''', "W5")

# ===== U1 : champ "Depasse de toiture" dans le formulaire (apres la pente) =====
remplacer('''              {/* Couverture */}''',
'''              {/* Depasse de toiture */}
              <div style={{ marginBottom: 18, display: ["terrasse","etage","balcon","garde_corps"].includes(typeEffectif) ? "none" : undefined }}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 10, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Depasse de toiture</label>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <input value={formDebord} onChange={e => setFormDebord(e.target.value)} type="number" placeholder="0" style={{ ...inputStyle, maxWidth: 100 }} />
                  <span style={{ color: "#545870", fontSize: 12 }}>cm (egouts et rives)</span>
                </div>
              </div>
              {/* Couverture */}''', "U1")

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : depasse de toiture dans le moteur 3D (charpente trad) + formulaire + persistance.")
