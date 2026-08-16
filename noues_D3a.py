import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_noues_D3a_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ===== A1 : debords de rive asymetriques (0 au pignon de contact) =====
remplacer('''    const yFait = Ht + hf;                                  // hauteur du faitage''',
'''    const yFait = Ht + hf;                                  // hauteur du faitage
    // Debords de RIVE asymetriques : pas de depasse au pignon de CONTACT d'un volume accole
    const smf = (opts && opts.sansMurFace) || "";
    const debG = smf === "pignon_gauche" ? 0 : debord;   // rive x = -L/2
    const debD = smf === "pignon_droit" ? 0 : debord;    // rive x = +L/2
    const debLX = debG + debD;                            // allongement total en X
    const debCX = (debD - debG) / 2;                      // recentrage X des pieces filantes''', "A1")

# ===== A2 : faitiere =====
remplacer('''    addBox(L + 0.4 + 2 * debord, pfH, pfB, 0, yFait, 0, woodMat);''',
'''    addBox(L + 0.4 + debLX, pfH, pfB, debCX, yFait, 0, woodMat);''', "A2")

# ===== A3 : pannes =====
remplacer('''      addBox(L + 0.3 + 2 * debord, pnH, pnB, 0, yP, zRef, woodMat);   // pan Z+ (droite)
      addBox(L + 0.3 + 2 * debord, pnH, pnB, 0, yP, -zRef, woodMat);  // pan Z- (droite)''',
'''      addBox(L + 0.3 + debLX, pnH, pnB, debCX, yP, zRef, woodMat);   // pan Z+ (droite)
      addBox(L + 0.3 + debLX, pnH, pnB, debCX, yP, -zRef, woodMat);  // pan Z- (droite)''', "A3")

# ===== A4 : chevrons de rive, seulement cote libre =====
remplacer('''    if (debord > 0.05) { chevronXs.push(-(L/2 + debord - chB/2)); chevronXs.push(L/2 + debord - chB/2); }''',
'''    if (debG > 0.05) chevronXs.push(-(L/2 + debG - chB/2));
    if (debD > 0.05) chevronXs.push(L/2 + debD - chB/2);''', "A4")

# ===== A5-A6 : couverture =====
remplacer('''    const tradRoofMat = makeRoofMaterial(couv, L + 2 * debord, plCouv);''',
'''    const tradRoofMat = makeRoofMaterial(couv, L + debLX, plCouv);''', "A5")
remplacer('''    const rg = new THREE.PlaneGeometry(L + 0.6 + 2 * debord, plCouv);''',
'''    const rg = new THREE.PlaneGeometry(L + 0.6 + debLX, plCouv);''', "A6")

# ===== A7-A8 : les 2 pans recentres =====
remplacer('''    r1.position.set(0, yR, zR);''',
'''    r1.position.set(debCX, yR, zR);''', "A7")
remplacer('''    r2.position.set(0, yR, -zR);''',
'''    r2.position.set(debCX, yR, -zR);''', "A8")

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : plus de depasse de toiture au pignon de contact (faitiere, pannes, chevron de rive, couverture).")
