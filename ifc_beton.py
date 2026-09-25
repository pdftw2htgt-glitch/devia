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

# 1) Le releve accepte une matiere : le beton entre sans se faire passer pour du bois
remp("logPiece matiere",
"""  const logPiece = (a, b, c, place) => {
    const dims = [a, b, c].sort((u, v) => v - u);
    const longueur = dims[0];
    const sx = dims[1], sy = dims[2];
    const volume = a * b * c;
    metre.push({
      nom: currentPiece,""",
"""  const logPiece = (a, b, c, place, nomForce, matiere) => {
    const dims = [a, b, c].sort((u, v) => v - u);
    const longueur = dims[0];
    const sx = dims[1], sy = dims[2];
    const volume = a * b * c;
    metre.push({
      matiere: matiere || "bois",
      nom: nomForce || currentPiece,""")

# 2) Les murs et dalles beton sont desormais consignes
remp("addBox beton",
"""    if (!mat || mat === woodMat) logPiece(sx, sy, sz, { pos: [px, py, pz], rot: rot || null, quat: null }); // bois uniquement""",
"""    if (!mat || mat === woodMat) logPiece(sx, sy, sz, { pos: [px, py, pz], rot: rot || null, quat: null }); // bois
    else if (mat === betonMat) logPiece(sx, sy, sz, { pos: [px, py, pz], rot: rot || null, quat: null }, "Mur beton", "beton");
    else if (mat === dalleMat) logPiece(sx, sy, sz, { pos: [px, py, pz], rot: rot || null, quat: null }, "Dalle beton", "beton");""")

# 3) Le chiffrage bois ignore le beton (volume, poids, sections EC5)
remp("agregerMetre sans beton",
"""  const map = {};
  metre.forEach((p) => {
    // cle = nom + section (pour distinguer p.ex. chevrons de sections differentes)""",
"""  const map = {};
  metre.forEach((p) => {
    if (p.matiere === "beton") return; // la maconnerie n est pas du bois : hors metre et hors EC5
    // cle = nom + section (pour distinguer p.ex. chevrons de sections differentes)""")

# 4) La vue rangee au sol ne range que du bois
remp("vue rangee sans beton",
"""      metreVue.forEach((p) => {
        const nomP = p.nom || "Piece";""",
"""      metreVue.forEach((p) => {
        if (p.matiere === "beton") return;
        const nomP = p.nom || "Piece";""")

# 5) IFC : classe et matiere d apres la matiere reelle de l element
remp("classeDe par piece",
"""  const classeDe = (nom) => {
    const n = String(nom || "").toLowerCase();""",
"""  const classeDe = (p) => {
    const n = String((p && p.nom) || "").toLowerCase();
    if (p && p.matiere === "beton") {
      if (n.indexOf("dalle") >= 0 || n.indexOf("plancher") >= 0) return ["IFCSLAB", ".FLOOR."];
      return ["IFCWALL", ".SOLIDWALL."];
    }""")

remp("appel classeDe",
"""    const cls = classeDe(p.nom);""",
"""    const cls = classeDe(p);""")

remp("listes par matiere",
"""  const memberIds = [];
  piecesBois.forEach((p, iP) => {""",
"""  const memberIds = [];
  const idsBois = [];
  const idsBeton = [];
  piecesBois.forEach((p, iP) => {""")

remp("rangement par matiere",
"""    memberIds.push(member);
  });""",
"""    memberIds.push(member);
    if (p.matiere === "beton") idsBeton.push(member); else idsBois.push(member);
  });""")

remp("deux matieres",
"""  // Rattacher tous les elements au niveau
  if (memberIds.length > 0) {
    const relContain = nextId();
    E(relContain, "IFCRELCONTAINEDINSPATIALSTRUCTURE('" + guid() + "',#" + owner + ",$,$,(#" + memberIds.join(",#") + "),#" + storey + ");");
    // Matiere : toute la charpente est du bois massif
    const matBois = nextId(); E(matBois, "IFCMATERIAL('Bois massif C24',$,'Bois');");
    const relMat = nextId();
    E(relMat, "IFCRELASSOCIATESMATERIAL('" + guid() + "',#" + owner + ",$,$,(#" + memberIds.join(",#") + "),#" + matBois + ");");
  }
  console.log("[DEVIA] IFC : " + memberIds.length + " element(s) exporte(s)");""",
"""  // Rattacher tous les elements au niveau
  if (memberIds.length > 0) {
    const relContain = nextId();
    E(relContain, "IFCRELCONTAINEDINSPATIALSTRUCTURE('" + guid() + "',#" + owner + ",$,$,(#" + memberIds.join(",#") + "),#" + storey + ");");
  }
  // Chaque famille repart avec sa vraie matiere
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
  console.log("[DEVIA] IFC : " + idsBois.length + " piece(s) bois et " + idsBeton.length + " element(s) beton");""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
