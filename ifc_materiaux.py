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

remp("MVD transfert de conception",
""""FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');\\n" +""",
""""FILE_DESCRIPTION(('ViewDefinition [DesignTransferView_V1.0]'),'2;1');\\n" +""")

remp("materiaux et proprietes cadwork",
"""  // Chaque famille repart avec sa vraie matiere
  if (idsBois.length > 0) {
    const matBois = nextId(); E(matBois, "IFCMATERIAL('Bois massif C24',$,'Bois');");
    const relB = nextId();
    E(relB, "IFCRELASSOCIATESMATERIAL('" + guid() + "',#" + owner + ",$,$,(#" + idsBois.join(",#") + "),#" + matBois + ");");
  }
  if (idsBeton.length > 0) {
    const matBet = nextId(); E(matBet, "IFCMATERIAL('Beton arme C25/30',$,'Beton');");
    const relC = nextId();
    E(relC, "IFCRELASSOCIATESMATERIAL('" + guid() + "',#" + owner + ",$,$,(#" + idsBeton.join(",#") + "),#" + matBet + ");");
  }
  console.log("[DEVIA] IFC : " + idsBois.length + " piece(s) bois et " + idsBeton.length + " element(s) beton");""",
"""  // Chaque famille repart avec sa vraie matiere.
  // Un logiciel de charpente rapproche le materiau d un IFC de sa propre liste PAR LE NOM :
  // on donne donc la designation normalisee SEULE (classe de resistance pour le bois, classe
  // de beton pour la maconnerie) et jamais une phrase. L essence part dans Pset_MaterialWood.
  const ESSENCES_IFC = { sapin: "Sapin", epicea: "Epicea", douglas: "Douglas", chene: "Chene", pin: "Pin", meleze: "Meleze" };
  if (idsBois.length > 0) {
    const matBois = nextId(); E(matBois, "IFCMATERIAL('C24',$,'Bois massif');");
    const relB = nextId();
    E(relB, "IFCRELASSOCIATESMATERIAL('" + guid() + "',#" + owner + ",$,$,(#" + idsBois.join(",#") + "),#" + matBois + ");");
    const essNom = ESSENCES_IFC[String((params && params.essence) || "sapin").toLowerCase()] || "Resineux";
    const pEsp = nextId(); E(pEsp, "IFCPROPERTYSINGLEVALUE('Species',$,IFCLABEL('" + txt(essNom) + "'),$);");
    const pCls = nextId(); E(pCls, "IFCPROPERTYSINGLEVALUE('StrengthGrade',$,IFCLABEL('C24'),$);");
    const mpB = nextId(); E(mpB, "IFCMATERIALPROPERTIES('Pset_MaterialWood',$,(#" + pEsp + ",#" + pCls + "),#" + matBois + ");");
  }
  if (idsBeton.length > 0) {
    const matBet = nextId(); E(matBet, "IFCMATERIAL('C25/30',$,'Beton arme');");
    const relC = nextId();
    E(relC, "IFCRELASSOCIATESMATERIAL('" + guid() + "',#" + owner + ",$,$,(#" + idsBeton.join(",#") + "),#" + matBet + ");");
  }
  // --- Cadwork3dProperties : c est le jeu de proprietes que cadwork ecrit LUI-MEME a l export,
  // donc celui qu il sait relire. Une entree par famille de pieces (toutes les pannes ensemble).
  // memberIds suit piecesBois element par element : pas besoin d un second registre.
  if (memberIds.length === piecesBois.length && memberIds.length > 0) {
    const familles = {};
    piecesBois.forEach((p, iF) => {
      const estBeton = p.matiere === "beton";
      const cle = (p.nom || "Piece") + "|" + (estBeton ? "b" : "w");
      if (familles[cle] === undefined) {
        familles[cle] = { nom: p.nom || "Piece", mat: estBeton ? "C25/30" : "C24", ids: [] };
      }
      familles[cle].ids.push(memberIds[iF]);
    });
    const clesF = Object.keys(familles);
    clesF.forEach((cle) => {
      const f = familles[cle];
      const props = [];
      const addProp = (nomP, val) => {
        const idP = nextId();
        E(idP, "IFCPROPERTYSINGLEVALUE('" + nomP + "',$,IFCLABEL('" + txt(val) + "'),$);");
        props.push(idP);
      };
      addProp("Name", f.nom);
      addProp("Group", f.nom);
      addProp("Subgroup", "DEVIA");
      addProp("Material", f.mat);
      const psF = nextId();
      E(psF, "IFCPROPERTYSET('" + guid() + "',#" + owner + ",'Cadwork3dProperties',$,(#" + props.join(",#") + "));");
      const relF = nextId();
      E(relF, "IFCRELDEFINESBYPROPERTIES('" + guid() + "',#" + owner + ",$,$,(#" + f.ids.join(",#") + "),#" + psF + ");");
    });
    console.log("[DEVIA] IFC : " + clesF.length + " famille(s) de pieces decrites dans Cadwork3dProperties");
  }
  console.log("[DEVIA] IFC : " + idsBois.length + " piece(s) bois et " + idsBeton.length + " element(s) beton");""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
