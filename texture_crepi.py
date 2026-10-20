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

# 1. "texture" porte desormais le nom de fichier complet, extension comprise
rempl("1. commentaire de la table",
'// "texture" = image dans public/textures/ ; si elle est renseignee elle REMPLACE le motif\n'
'//             dessine. C est ici qu on branchera les vraies photos de finition.\n',
'// "texture" = nom de fichier COMPLET dans public/textures/ (jpg ou png). Si elle est\n'
'//             renseignee elle REMPLACE le motif dessine ; le motif sert alors de repli\n'
'//             si l image manque. Une photo doit etre REPETABLE bord a bord.\n')

rempl("2. le beton garde son png",
'  "":      { label: "Beton apparent",   couleur: 0xb4b4b8, rugosite: 0.95, texture: "beton_mur", motif: null,     taille: 2.5 },\n'
'  crepi:   { label: "Crepi",            couleur: 0xe9e3d7, rugosite: 1.00, texture: null,        motif: "grain",  taille: 0.5 },\n',
'  "":      { label: "Beton apparent",   couleur: 0xb4b4b8, rugosite: 0.95, texture: "beton_mur.png", motif: null,    taille: 2.5 },\n'
'  crepi:   { label: "Crepi",            couleur: 0xe9e3d7, rugosite: 1.00, texture: "crepi.jpg",     motif: "grain", taille: 0.6 },\n')

# 3. priorite a la photo, repli sur le motif, et une finition CHOISIE s affiche partout
rempl("3. chargement de la finition",
"""    if (finMur.motif) {
      const cv = motifMurCanvas(finMur.motif, finMur.couleur);
      if (cv) {
        const tex = new THREE.CanvasTexture(cv);
        poser(tex);
        betonMat.bumpMap = tex;        // un crepi, une brique et une pierre ont du relief
        betonMat.bumpScale = 0.02;
      }
      return;
    }
    if (finMur.texture && modeB === "realiste") {
      new THREE.TextureLoader().load("/textures/" + finMur.texture + ".png", poser);
    }
""",
"""    // Hors navigateur (banc d essai, rendu serveur) il n y a ni canvas ni chargeur
    // d image : le mur garde sa couleur unie, rien ne plante.
    if (typeof document === "undefined") return;
    const dessiner = () => {
      if (finMur.motif === null) return;
      const cv = motifMurCanvas(finMur.motif, finMur.couleur);
      if (cv === null) return;
      const tex = new THREE.CanvasTexture(cv);
      poser(tex);
      betonMat.bumpMap = tex;          // un crepi, une brique et une pierre ont du relief
      betonMat.bumpScale = 0.02;
    };
    // Le beton apparent garde son comportement d origine : photo en mode realiste seulement.
    // Une finition CHOISIE s affiche dans les DEUX modes, c est tout l interet du reglage.
    const choisie = (finMur === FINITIONS_MUR[""]) ? false : true;
    if (finMur.texture && (choisie || modeB === "realiste")) {
      new THREE.TextureLoader().load("/textures/" + finMur.texture, (img) => {
        poser(img);
        if (choisie === false) return;  // pas de relief ajoute sur le rendu beton d origine
        betonMat.bumpMap = img;
        betonMat.bumpScale = 0.015;
      }, undefined, dessiner);          // image absente : on retombe sur le motif dessine
      return;
    }
    dessiner();
""")

io.open(chemin, "w", encoding="utf-8").write(s)
for t, n, a in etapes:
    print("  " + t + " : " + str(n) + "/" + str(a))
print("OK texture crepi branchee")
