# Etape 3, marche 1 : type sas_liaison - murailleres sur pignons (appui voisins),
# solives entre elles, platelage toit plat, parois de fermeture. + plomberie prompt/types.
import shutil, datetime, sys

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"

with open(F, "r", encoding="utf-8") as f:
    c = f.read()

edits = []

OLD1 = ''''{"type":"traditionnelle|fermette|monopente|carport|hangar|appentis|4_pans|terrasse|etage|balcon|garde_corps|null",' +'''
NEW1 = ''''{"type":"traditionnelle|fermette|monopente|carport|hangar|appentis|4_pans|terrasse|etage|balcon|garde_corps|sas|null",' +'''
edits.append(("schema enum type", OLD1, NEW1, 1))

OLD2 = '''Un sas ou une liaison a TOIT PLAT = type etage (solivage bois porteur), desc precisant toit plat.'''
NEW2 = '''Un sas ou une liaison a TOIT PLAT = type sas (liaison fermee, solivage porteur entre les deux volumes voisins) ; pour un sas, hauteur_murs = hauteur du toit plat lue sur les coupes.'''
edits.append(("aiguillage sas", OLD2, NEW2, 1))

OLD3 = '''      const TYPES_DECOMP = ["traditionnelle", "fermette", "monopente", "carport", "hangar", "appentis", "4_pans", "terrasse", "etage", "balcon", "garde_corps"];'''
NEW3 = '''      const TYPES_DECOMP = ["traditionnelle", "fermette", "monopente", "carport", "hangar", "appentis", "4_pans", "terrasse", "etage", "balcon", "garde_corps", "sas"];'''
edits.append(("types decomp", OLD3, NEW3, 1))

OLD4 = '''"4_pans": "toit 4 pans avec croupe" };'''
NEW4 = '''"4_pans": "toit 4 pans avec croupe", sas: "sas de liaison a toit plat" };'''
edits.append(("labels type (2 tables)", OLD4, NEW4, 2))

OLD5 = '''          const sansToit = ["terrasse", "etage", "balcon", "garde_corps"].includes(o.type);'''
NEW5 = '''          const sansToit = ["terrasse", "etage", "balcon", "garde_corps", "sas"].includes(o.type);'''
edits.append(("sans toit decomp", OLD5, NEW5, 1))

OLD6 = '''etage: "etage", balcon: "balcon" };'''
NEW6 = '''etage: "etage", balcon: "balcon", sas: "sas_liaison" };'''
edits.append(("type vers projet 3D", OLD6, NEW6, 1))

OLD7 = '''  } else if (typeProjet === "etage") {
    drawEtage();'''
NEW7 = '''  } else if (typeProjet === "sas_liaison") {
    drawSasLiaison();
  } else if (typeProjet === "etage") {
    drawEtage();'''
edits.append(("dispatch 3D", OLD7, NEW7, 1))

OLD8 = '''  const drawEtage = () => {'''
NEW8 = '''  const drawSasLiaison = () => {
    // Sas de liaison a toit plat : murailleres plaquees aux pignons (appui sur les
    // volumes voisins accoles), solives entre elles, platelage, parois de fermeture
    const [soB, soH] = sec("Solive", 0.08, 0.20);
    const [ppB, ppH] = sec("Muraillere", 0.12, 0.32);
    const hToit = Math.max(Ht, 2.2);
    const yMur = hToit - ppH / 2;
    const ySolive = hToit - soH / 2;
    const xMur = L / 2 - ppB / 2;

    // ===== 2 MURAILLERES (sens largeur, aux extremites X = pignons d'appui) =====
    setPiece("Muraillere");
    addBox(ppB, ppH, lg, xMur, yMur, 0, woodMat);
    addBox(ppB, ppH, lg, -xMur, yMur, 0, woodMat);

    // ===== SOLIVES (portee entre les murailleres, entraxe ~50 cm) =====
    setPiece("Solive");
    const portee = L - 2 * ppB;
    const nbSolives = Math.max(2, Math.round(lg / 0.5) + 1);
    for (let i = 0; i < nbSolives; i++) {
      const z = -lg/2 + soB/2 + (i / (nbSolives - 1)) * (lg - soB);
      addBox(portee, soH, soB, 0, ySolive, z, woodMat);
    }

    // ===== PLATELAGE TOIT PLAT (visuel) =====
    const platMat = new THREE.MeshStandardMaterial({ color: 0x8a8f9c, roughness: 0.9, transparent: true, opacity: 0.55 });
    const plat = new THREE.Mesh(new THREE.BoxGeometry(L, 0.04, lg), platMat);
    plat.position.set(0, hToit + 0.02, 0);
    scene.add(plat);

    // ===== PAROIS DE FERMETURE (gouttereaux - vitrage/menuiserie hors lot charpente) =====
    const paroiMat = new THREE.MeshStandardMaterial({ color: 0xd8d2c0, roughness: 0.9, transparent: true, opacity: 0.3 });
    const hParoi = hToit - ppH;
    for (const s of [-1, 1]) {
      const paroi = new THREE.Mesh(new THREE.BoxGeometry(L, hParoi, 0.08), paroiMat);
      paroi.position.set(0, hParoi / 2, s * (lg / 2 - 0.04));
      scene.add(paroi);
    }
  };

  const drawEtage = () => {'''
edits.append(("brique sas", OLD8, NEW8, 1))

for nom, old, new, attendu in edits:
    n = c.count(old)
    if n != attendu:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de " + str(attendu) + " - abandon, rien modifie")
        sys.exit(1)

shutil.copy2(F, F + ".backup_" + stamp + "_sas_31")
for nom, old, new, attendu in edits:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK 3-1 : type sas_liaison en place (prompt + types + 3D)")
