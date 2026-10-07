import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

def remp(nom, ancre, nouveau):
    global src
    n = src.count(ancre)
    if n != 1:
        print("ABANDON " + nom + " : ancre trouvee " + str(n) + " fois")
        cle = ancre.strip().split("\n")[0][:45]
        for i, l in enumerate(src.split("\n")):
            if cle in l:
                print("  ligne " + str(i + 1) + " : " + l.strip()[:200])
        sys.exit(1)
    src = src.replace(ancre, nouveau)
    print("OK " + nom)

def bloc(nom, deb, fin, nouveau):
    global src
    nd, nf = src.count(deb), src.count(fin)
    if nd != 1 or nf != 1:
        print("ABANDON " + nom + " : ancre debut x" + str(nd) + ", ancre fin x" + str(nf))
        sys.exit(1)
    i, j = src.index(deb), src.index(fin)
    if j <= i:
        print("ABANDON " + nom + " : ancre de fin avant l ancre de debut")
        sys.exit(1)
    src = src[:i] + nouveau + src[j:]
    print("OK " + nom)

# 1) TEXTE STEP AVEC ACCENTS (insere juste avant le helper des nombres)
remp("texte STEP accentue",
r"""  // Nombre STEP : toujours un point decimal, jamais NaN ni Infinity""",
r"""  // Texte STEP AVEC accents, pour les noms qui doivent tomber juste dans un autre logiciel.
  // ISO 10303-21 code un caractere non-ASCII par la marque X2, son code UTF-16 sur 4 chiffres
  // hexa, puis la marque X0 : cadwork ecrit Beton sous la forme B\X2\00E9\X0\ton. Un nom de
  // materiau desaccentue ne tombe sur aucune entree de sa liste et reste donc non affecte.
  const txtAcc = (s) => {
    const br = String((s === undefined || s === null) ? "" : s).replace(/\\/g, "\\\\").replace(/'/g, "''");
    let out = "";
    let i = 0;
    while (i < br.length) {
      const c = br.charCodeAt(i);
      if (c >= 32 && c <= 126) { out += br.charAt(i); i += 1; }
      else {
        let hex = "";
        while (i < br.length) {
          const d = br.charCodeAt(i);
          if (d >= 32 && d <= 126) break;
          hex += ("000" + d.toString(16).toUpperCase()).slice(-4);
          i += 1;
        }
        out += "\\X2\\" + hex + "\\X0\\";
      }
    }
    return out;
  };
  // Nombre STEP : toujours un point decimal, jamais NaN ni Infinity""")

# 2) MATERIAUX AUX NOMS DE LA LISTE CADWORK + GROUPES AUX NOMS RELEVES
bloc("materiaux de la liste cadwork",
r"""  const ESSENCES_IFC = { sapin: "Sapin", epicea: "Epicea", douglas: "Douglas", chene: "Chene", pin: "Pin", meleze: "Meleze" };""",
r"""  console.log("[DEVIA] IFC : " + idsBois.length + " piece(s) bois et " + idsBeton.length + " element(s) beton");""",
r"""  // Les noms viennent de la LISTE DE MATERIAUX cadwork, releves dans un IFC qu il a lui-meme
  // exporte : ce sont des noms francais accentues (Sapin, Beton, Chene) et PAS des classes de
  // resistance. La classe part dans Pset_MaterialWood, a sa vraie place.
  const MATERIAU_CW = { sapin: "Sapin", epicea: "Épicéa", douglas: "Douglas", chene: "Chêne", pin: "Pin", meleze: "Mélèze" };
  const BETON_CW = "Béton";
  if (idsBois.length > 0) {
    const essCle = String((params && params.essence) || "sapin").toLowerCase();
    const nomBois = MATERIAU_CW[essCle] || "Sapin";
    const matBois = nextId(); E(matBois, "IFCMATERIAL('" + txtAcc(nomBois) + "',$,'');");
    const relB = nextId();
    E(relB, "IFCRELASSOCIATESMATERIAL('" + guid() + "',#" + owner + ",$,$,(#" + idsBois.join(",#") + "),#" + matBois + ");");
    const pEsp = nextId(); E(pEsp, "IFCPROPERTYSINGLEVALUE('Species',$,IFCLABEL('" + txtAcc(nomBois) + "'),$);");
    const pCls = nextId(); E(pCls, "IFCPROPERTYSINGLEVALUE('StrengthGrade',$,IFCLABEL('C24'),$);");
    const mpB = nextId(); E(mpB, "IFCMATERIALPROPERTIES('Pset_MaterialWood',$,(#" + pEsp + ",#" + pCls + "),#" + matBois + ");");
    console.log("[DEVIA] IFC : materiau bois = " + nomBois + " (nom de la liste cadwork), classe C24");
  }
  if (idsBeton.length > 0) {
    const matBet = nextId(); E(matBet, "IFCMATERIAL('" + txtAcc(BETON_CW) + "',$,'');");
    const relC = nextId();
    E(relC, "IFCRELASSOCIATESMATERIAL('" + guid() + "',#" + owner + ",$,$,(#" + idsBeton.join(",#") + "),#" + matBet + ");");
  }
  // --- Cadwork3dProperties : les noms de proprietes sont ceux releves dans son propre export,
  // soit Group et Sub group - avec l espace, Subgroup ne serait pas relu.
  // memberIds suit piecesBois element par element : pas besoin d un second registre.
  if (memberIds.length === piecesBois.length && memberIds.length > 0) {
    const familles = {};
    piecesBois.forEach((p, iF) => {
      const estBeton = p.matiere === "beton";
      const cle = (p.nom || "Piece") + "|" + (estBeton ? "b" : "w");
      if (familles[cle] === undefined) {
        familles[cle] = { nom: p.nom || "Piece", grp: estBeton ? "Maçonnerie" : "Charpente", ids: [] };
      }
      familles[cle].ids.push(memberIds[iF]);
    });
    const clesF = Object.keys(familles);
    clesF.forEach((cle) => {
      const f = familles[cle];
      const pG = nextId(); E(pG, "IFCPROPERTYSINGLEVALUE('Group',$,IFCLABEL('" + txtAcc(f.grp) + "'),$);");
      const pS = nextId(); E(pS, "IFCPROPERTYSINGLEVALUE('Sub group',$,IFCLABEL('" + txtAcc(f.nom) + "'),$);");
      const psF = nextId();
      E(psF, "IFCPROPERTYSET('" + guid() + "',#" + owner + ",'Cadwork3dProperties',$,(#" + pG + ",#" + pS + "));");
      const relF = nextId();
      E(relF, "IFCRELDEFINESBYPROPERTIES('" + guid() + "',#" + owner + ",$,$,(#" + f.ids.join(",#") + "),#" + psF + ");");
    });
    console.log("[DEVIA] IFC : " + clesF.length + " famille(s) rangees par Group / Sub group");
  }
""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
