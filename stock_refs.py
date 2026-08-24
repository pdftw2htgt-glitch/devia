import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_stock_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ===== R1 : registre des references fournisseur (sections structure sur stock) =====
remplacer('''function buildScene3D(scene, params, opts) {''',
'''// ================================================================
// STOCK FOURNISSEUR : sections structure sur stock (autres sur demande)
// fam / classe / section b-h mm / essence / reference / longueurs (m)
// ================================================================
const REFERENCES_STOCK = [
  { fam: "contrecolle", cl: "C24", sec: "A_CONFIRMER/165", ess: "meleze", ref: "30713", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "80/200", ess: "meleze", ref: "14042", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "80/220", ess: "epicea", ref: "42634", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "100/100", ess: "epicea", ref: "14061", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "100/100", ess: "meleze", ref: "20782", lg: [6.5] },
  { fam: "contrecolle", cl: "C24", sec: "100/100", ess: "douglas", ref: "20781", lg: [6.5] },
  { fam: "contrecolle", cl: "C24", sec: "100/160", ess: "epicea", ref: "14062", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "100/200", ess: "epicea", ref: "14063", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "100/200", ess: "douglas", ref: "14028", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "100/210", ess: "meleze", ref: "14043", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "120/120", ess: "epicea", ref: "14064", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "120/120", ess: "meleze", ref: "14050", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "120/120", ess: "douglas", ref: "20641", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "120/160", ess: "epicea", ref: "14065", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "120/180", ess: "epicea", ref: "42633", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "120/200", ess: "epicea", ref: "14066", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "120/200", ess: "meleze", ref: "21623", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "120/220", ess: "epicea", ref: "14067", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "120/240", ess: "epicea", ref: "14068", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "120/240", ess: "meleze", ref: "21624", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "120/240", ess: "douglas", ref: "14029", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "140/140", ess: "epicea", ref: "14069", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "140/140", ess: "meleze", ref: "14056", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "140/140", ess: "douglas", ref: "20642", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "140/200", ess: "epicea", ref: "14070", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "140/210", ess: "meleze", ref: "20602", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "140/240", ess: "epicea", ref: "14071", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "140/240", ess: "douglas", ref: "20643", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "140/280", ess: "epicea", ref: "20567", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "160/160", ess: "epicea", ref: "14072", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "160/160", ess: "douglas", ref: "20644", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "160/240", ess: "epicea", ref: "14073", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "160/240", ess: "douglas", ref: "20645", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "180/180", ess: "epicea", ref: "14074", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "180/180", ess: "meleze", ref: "14057", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "180/180", ess: "douglas", ref: "20646", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "180/260", ess: "epicea", ref: "20568", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "200/200", ess: "epicea", ref: "14075", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "200/200", ess: "meleze", ref: "14058", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "200/200", ess: "douglas", ref: "14030", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "200/240", ess: "epicea", ref: "14076", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "200/240", ess: "meleze", ref: "22236", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "200/240", ess: "douglas", ref: "20647", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "200/280", ess: "epicea", ref: "14077", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "200/280", ess: "meleze", ref: "20569", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "240/240", ess: "epicea", ref: "14079", lg: [13] },
  { fam: "contrecolle", cl: "C24", sec: "240/240", ess: "douglas", ref: "20648", lg: [13] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "120/280", ess: "epicea", ref: "39188", lg: [12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "120/320", ess: "epicea", ref: "11371", lg: [8, 10, 12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "120/360", ess: "epicea", ref: "11372", lg: [8, 10, 12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "140/280", ess: "epicea", ref: "11373", lg: [8, 10, 12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "140/280", ess: "meleze", ref: "14160", lg: [12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "140/320", ess: "epicea", ref: "11374", lg: [8, 10, 12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "140/360", ess: "epicea", ref: "11375", lg: [8, 10, 12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "140/360", ess: "meleze", ref: "14162", lg: [12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "160/400", ess: "epicea", ref: "11376", lg: [8, 10, 12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "160/400", ess: "meleze", ref: "14163", lg: [12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "180/440", ess: "epicea", ref: "39189", lg: [12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "180/520", ess: "epicea", ref: "39190", lg: [12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "200/320", ess: "epicea", ref: "16710", lg: [10, 12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "200/360", ess: "epicea", ref: "12325", lg: [12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "200/440", ess: "epicea", ref: "11377", lg: [8, 10, 12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "200/440", ess: "meleze", ref: "14164", lg: [12.5] },
  { fam: "lamelle_colle", cl: "GL24H", sec: "200/520", ess: "epicea", ref: "14095", lg: [10, 12.5] },
  { fam: "kvh", cl: "C24", sec: "A_CONFIRMER", ess: "epicea", ref: "14194", lg: [6.5] },
  { fam: "kvh", cl: "C24", sec: "A_CONFIRMER", ess: "epicea", ref: "14191", lg: [6.5] },
  { fam: "kvh", cl: "C24", sec: "60/80", ess: "epicea", ref: "42642", lg: [6] },
  { fam: "kvh", cl: "C24", sec: "60/100", ess: "epicea", ref: "43008", lg: [6] },
  { fam: "kvh", cl: "C24", sec: "60/120", ess: "epicea", ref: "15263", lg: [13] },
  { fam: "kvh", cl: "C24", sec: "60/140", ess: "epicea", ref: "21010", lg: [6.5] },
  { fam: "kvh", cl: "C24", sec: "60/140", ess: "epicea", ref: "10239", lg: [13] },
  { fam: "kvh", cl: "C24", sec: "60/160", ess: "epicea", ref: "14087", lg: [13] },
  { fam: "kvh", cl: "C24", sec: "60/200", ess: "epicea", ref: "14340", lg: [13] },
  { fam: "kvh", cl: "C24", sec: "60/220", ess: "epicea", ref: "14088", lg: [13] },
  { fam: "kvh", cl: "C24", sec: "80/100", ess: "epicea", ref: "10244", lg: [13] },
  { fam: "kvh", cl: "C24", sec: "80/120", ess: "epicea", ref: "10246", lg: [13] },
  { fam: "kvh", cl: "C24", sec: "80/140", ess: "epicea", ref: "39191", lg: [13] },
  { fam: "kvh", cl: "C24", sec: "80/200", ess: "epicea", ref: "14090", lg: [13] },
  { fam: "kvh", cl: "C24", sec: "100/120", ess: "epicea", ref: "14084", lg: [13] },
  { fam: "kvh", cl: "C24", sec: "100/140", ess: "epicea", ref: "14085", lg: [13] },
  { fam: "kvh", cl: "C24", sec: "100/200", ess: "epicea", ref: "14086", lg: [13] },
  { fam: "ossature", cl: "C24", sec: "36/97", ess: "epicea", ref: "10210", lg: [5.1] },
  { fam: "ossature", cl: "LC", sec: "45/60", ess: "pin", ref: "18289", lg: [6] },
  { fam: "ossature", cl: "LC", sec: "45/95", ess: "pin", ref: "17177", lg: [6] },
  { fam: "ossature", cl: "C24", sec: "45/95", ess: "epicea", ref: "10211", lg: [5.1] },
  { fam: "ossature", cl: "C24", sec: "45/95", ess: "epicea", ref: "43006", lg: [6] },
  { fam: "ossature", cl: "LC", sec: "45/120", ess: "pin", ref: "16269", lg: [6] },
  { fam: "ossature", cl: "C24", sec: "45/120", ess: "epicea", ref: "10217", lg: [5.1] },
  { fam: "ossature", cl: "C24", sec: "45/120", ess: "epicea", ref: "43005", lg: [6] },
  { fam: "ossature", cl: "LC", sec: "45/145", ess: "pin", ref: "16279", lg: [6] },
  { fam: "ossature", cl: "C24", sec: "45/145", ess: "epicea", ref: "10212", lg: [5.1] },
  { fam: "ossature", cl: "C24", sec: "45/145", ess: "epicea", ref: "43007", lg: [6] },
  { fam: "ossature", cl: "LC", sec: "45/160", ess: "pin", ref: "18039", lg: [6] },
  { fam: "ossature", cl: "C24", sec: "45/160", ess: "epicea", ref: "13422", lg: [5.1] },
  { fam: "ossature", cl: "LC", sec: "45/197", ess: "pin", ref: "17176", lg: [6] },
  { fam: "ossature", cl: "C24", sec: "45/200", ess: "epicea", ref: "15274", lg: [5.1] },
  { fam: "ossature", cl: "LC", sec: "45/220", ess: "pin", ref: "18274", lg: [6] },
  { fam: "ossature", cl: "C24", sec: "45/220", ess: "epicea", ref: "10213", lg: [5.1] },
  { fam: "ossature", cl: "C24", sec: "45/240", ess: "epicea", ref: "13425", lg: [5.1] },
  { fam: "poutre_i", cl: "", sec: "47/300", ess: "", ref: "37640", lg: [13] },
  { fam: "poutre_i", cl: "", sec: "70/240", ess: "", ref: "37642", lg: [4.5, 8.5, 13] },
  { fam: "poutre_i", cl: "", sec: "70/300", ess: "", ref: "37643", lg: [4.5, 8.5, 13] },
  { fam: "poutre_i", cl: "", sec: "97/250", ess: "", ref: "37644", lg: [4.5, 8.5, 13] },
  { fam: "poutre_i", cl: "", sec: "97/300", ess: "", ref: "37645", lg: [4.5, 8.5, 13] },
  { fam: "poutre_i", cl: "", sec: "97/350", ess: "", ref: "37646", lg: [4.5, 8.5, 13] },
  { fam: "meleze_etuve", cl: "C20", sec: "100/140", ess: "meleze", ref: "18373", lg: [1.1, 6] },
  { fam: "meleze_etuve", cl: "C20", sec: "120/120", ess: "meleze", ref: "18374", lg: [1.1, 6] },
  { fam: "meleze_etuve", cl: "C20", sec: "120/200", ess: "meleze", ref: "19382", lg: [6] },
  { fam: "meleze_etuve", cl: "C20", sec: "150/150", ess: "meleze", ref: "18375", lg: [1.1, 6, 8] },
  { fam: "meleze_etuve", cl: "C20", sec: "200/200", ess: "meleze", ref: "18441", lg: [6, 8, 10] },
  { fam: "meleze_etuve", cl: "C20", sec: "200/250", ess: "meleze", ref: "18372", lg: [8, 10] },
  { fam: "meleze_etuve", cl: "C20", sec: "200/300", ess: "meleze", ref: "19383", lg: [8, 10] },
  { fam: "meleze_etuve", cl: "C20", sec: "250/250", ess: "meleze", ref: "18187", lg: [8, 10] },
  { fam: "meleze_etuve", cl: "C20", sec: "250/350", ess: "meleze", ref: "18188", lg: [8, 10] },
  { fam: "massif_brut", cl: "VAHC", sec: "100/140", ess: "epicea", ref: "10929", lg: [4, 5, 6] },
  { fam: "massif_brut", cl: "VAHC", sec: "120/120", ess: "epicea", ref: "10931", lg: [4, 5, 6] },
  { fam: "massif_brut", cl: "VAHC", sec: "130/210", ess: "epicea", ref: "10932", lg: [4, 5, 6] },
  { fam: "massif_brut", cl: "VAHC", sec: "140/180", ess: "epicea", ref: "10933", lg: [4, 5, 6] },
  { fam: "massif_brut", cl: "VAHC", sec: "150/150", ess: "epicea", ref: "10934", lg: [4, 5, 6] },
  { fam: "massif_brut", cl: "VAHC", sec: "200/200", ess: "epicea", ref: "10935", lg: [4, 5, 6] },
  { fam: "lvl", cl: "S", sec: "39/240", ess: "", ref: "37967", lg: [4.5, 9, 13.5] },
  { fam: "lvl", cl: "S", sec: "39/300", ess: "", ref: "37968", lg: [4.5, 9, 13.5] },
  { fam: "lvl", cl: "S", sec: "39/350", ess: "", ref: "37969", lg: [4.5, 9, 13.5] },
  { fam: "lvl", cl: "S", sec: "45/360", ess: "", ref: "37966", lg: [13.5] },
  { fam: "lvl", cl: "S", sec: "75/300", ess: "", ref: "20681", lg: [13.5] },
  { fam: "lvl", cl: "S", sec: "75/350", ess: "", ref: "37647", lg: [13.5] },
  { fam: "lvl", cl: "S", sec: "75/400", ess: "", ref: "37648", lg: [13.5] },
  { fam: "lvl", cl: "S", sec: "75/450", ess: "", ref: "37649", lg: [13.5] },
];

// References stock correspondant a une section (b x h en mm, dans les deux sens)
function refsStockPourSection(bMm, hMm) {
  const cle = bMm + "/" + hMm;
  const cle2 = hMm + "/" + bMm;
  return REFERENCES_STOCK.filter((r) => r.sec === cle || r.sec === cle2);
}

function buildScene3D(scene, params, opts) {''', "R1")

# ===== R2 : longueurs commerciales dans le prompt de generation =====
remplacer('''"REGLE CATEGORIES : chaque poste porte une categorie parmi Etude, Charpente, Couverture, Etancheite, Quincaillerie, Bardage, Pose. Repartis finement : ecran sous-toiture et membranes en Etancheite, sabots/connecteurs/visserie en Quincaillerie, main d'oeuvre en Pose, calculs et plans en Etude. " +''',
'''"REGLE CATEGORIES : chaque poste porte une categorie parmi Etude, Charpente, Couverture, Etancheite, Quincaillerie, Bardage, Pose. Repartis finement : ecran sous-toiture et membranes en Etancheite, sabots/connecteurs/visserie en Quincaillerie, main d'oeuvre en Pose, calculs et plans en Etude. " +
"STOCK BOIS FOURNISSEUR (longueurs commerciales) : contrecolle C24 jusqu'a 13,00 m - lamelle-colle GL24H 8,00/10,00/12,50 m - KVH C24 jusqu'a 13,00 m - ossature 5,10/6,00 m - poutre en I jusqu'a 13,00 m - poutre meleze etuve C20 jusqu'a 10,00 m - massif brut VAHC 4,00/5,00/6,00 m - LVL S jusqu'a 13,50 m. Une panne peut donc etre d'une seule piece jusqu'a 13 m en contrecolle ; au-dela, prevois un poste de raboutage. Quand le metre fournit une reference stock pour une piece, recopie-la dans la designation du poste. " +''', "R2")

# ===== R3 : le metre moteur cite les references stock =====
remplacer('''    const lignes = agg.groupes.map((g) => "- " + g.nom + " " + g.section[0] + "x" + g.section[1] + " mm : " + g.nombre + " piece(s), " + g.longueurTotale.toFixed(1) + " ml au total");''',
'''    const lignes = agg.groupes.map((g) => {
      const refs = refsStockPourSection(g.section[0], g.section[1]);
      const refTxt = refs.length > 0 ? " | ref stock : " + refs.map((r) => r.ref + " (" + r.fam + (r.ess ? " " + r.ess : "") + ", " + r.lg.join("/") + " m)").join(", ") : "";
      return "- " + g.nom + " " + g.section[0] + "x" + g.section[1] + " mm : " + g.nombre + " piece(s), " + g.longueurTotale.toFixed(1) + " ml au total" + refTxt;
    });''', "R3")

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : " + str(c.count("REFERENCES_STOCK")) + " occurrences registre ; stock fournisseur enregistre et branche a la generation.")
