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

CHEVRON = "url(\\\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8' fill='none'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%237a7d92' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E\\\")"

# ------------------------------------------------- 1. table + generateur de motifs
rempl("1. table des finitions de mur",
"const EC5_LARGEUR_MINI = {\n",
'''// ====== FINITIONS DE MUR (maconnerie) ======
// Aspect des murs maconnes dans la 3D. RIEN N EST CHIFFRE : la maconnerie reste de
// l existant, la finition ne change que le rendu. Le beton apparent est le defaut.
// "taille"  = cote en metres d une tuile de motif (le dessin se repete tous les X metres).
// "texture" = image dans public/textures/ ; si elle est renseignee elle REMPLACE le motif
//             dessine. C est ici qu on branchera les vraies photos de finition.
const FINITIONS_MUR = {
  "":      { label: "Beton apparent",   couleur: 0xb4b4b8, rugosite: 0.95, texture: "beton_mur", motif: null,     taille: 2.5 },
  crepi:   { label: "Crepi",            couleur: 0xe9e3d7, rugosite: 1.00, texture: null,        motif: "grain",  taille: 0.5 },
  enduit:  { label: "Enduit lisse",     couleur: 0xe3ded3, rugosite: 0.75, texture: null,        motif: null,     taille: 1.5 },
  brique:  { label: "Brique",           couleur: 0x9e4f3a, rugosite: 0.90, texture: null,        motif: "brique", taille: 1.0 },
  pierre:  { label: "Pierre apparente", couleur: 0xb0a590, rugosite: 1.00, texture: null,        motif: "pierre", taille: 1.2 },
};

// Dessine le motif d une finition sur un canvas carre, repetable bord a bord.
// Garde en cache : la scene est reconstruite plusieurs fois par devis (pre-calcul EC5,
// rendu, PDF) et un crepi, c est vingt mille grains a poser.
const CACHE_MOTIF_MUR = {};
function motifMurCanvas(motif, couleur) {
  const cle = motif + "_" + couleur;
  if (CACHE_MOTIF_MUR[cle]) return CACHE_MOTIF_MUR[cle];
  if (typeof document === "undefined") return null;
  const N = 512;
  const cv = document.createElement("canvas");
  cv.width = N; cv.height = N;
  const c = cv.getContext("2d");
  if (c === null) return null;
  const r0 = (couleur >> 16) & 255, v0 = (couleur >> 8) & 255, b0 = couleur & 255;
  const borne = (x) => Math.max(0, Math.min(255, Math.round(x)));
  const teinte = (k) => "rgb(" + borne(r0 * k) + "," + borne(v0 * k) + "," + borne(b0 * k) + ")";
  c.fillStyle = teinte(1); c.fillRect(0, 0, N, N);

  if (motif === "grain") {
    // Crepi projete : des milliers de grains clairs et sombres, aucun motif lisible.
    for (let i = 0; i < 18000; i++) {
      c.fillStyle = teinte(0.82 + Math.random() * 0.34);
      c.beginPath();
      c.arc(Math.random() * N, Math.random() * N, 0.8 + Math.random() * 1.7, 0, 6.2832);
      c.fill();
    }
  } else if (motif === "brique") {
    // 4 briques par metre en largeur, 16 rangs : les demi-briques des bords se recollent
    // d une tuile a l autre, donc la teinte doit dependre du rang et de la colonne,
    // jamais du hasard, sinon la couture se voit.
    const cols = 4, rangs = 16;
    const lb = N / cols, hb = N / rangs, joint = Math.max(2, Math.round(hb * 0.18));
    c.fillStyle = teinte(1.5); c.fillRect(0, 0, N, N);
    for (let r = 0; r < rangs; r++) {
      const dec = (r % 2 === 0) ? 0 : lb / 2;
      for (let k = -1; k <= cols; k++) {
        const kk = ((k % cols) + cols) % cols;
        const h = ((r * 7 + kk * 13) % 11) / 11;
        c.fillStyle = teinte(0.82 + h * 0.3);
        c.fillRect(k * lb + dec + joint / 2, r * hb + joint / 2, lb - joint, hb - joint);
      }
    }
  } else if (motif === "pierre") {
    // Moellons : rangs reguliers, largeurs irregulieres. Chaque rang demarre a gauche,
    // le dernier moellon est coupe au bord : le joint vertical tombe juste a la couture.
    const rangs = 7, hp = N / rangs;
    c.fillStyle = teinte(1.18); c.fillRect(0, 0, N, N);
    for (let r = 0; r < rangs; r++) {
      const j = Math.max(2, hp * 0.1);
      let x = 0;
      while (x < N) {
        const w = hp * (0.9 + Math.random() * 1.5);
        c.fillStyle = teinte(0.78 + Math.random() * 0.36);
        c.fillRect(x + j / 2, r * hp + j / 2, w - j, hp - j);
        x += w;
      }
    }
  }
  CACHE_MOTIF_MUR[cle] = cv;
  return cv;
}

const EC5_LARGEUR_MINI = {
''')

# ------------------------------------------------- 2. materiau beton pilote par la finition
rempl("2. materiau de mur selon la finition",
"""  // Materiau BETON (murs par defaut : opaque, gris clair mat)
  const betonMat = new THREE.MeshStandardMaterial({ color: 0xb4b4b8, roughness: 0.95, metalness: 0.0 });
  (function chargeBeton() {
    const modeB = (opts && opts.mode) ? opts.mode : "technique";
    if (modeB === "realiste") {
      new THREE.TextureLoader().load("/textures/beton_mur.png", (img) => {
        img.colorSpace = THREE.SRGBColorSpace;
        img.wrapS = THREE.RepeatWrapping;
        img.wrapT = THREE.RepeatWrapping;
        betonMat.map = img;
        betonMat.color.set(0xffffff);
        betonMat.needsUpdate = true;
      });
    }
  })();
""",
"""  // Materiau BETON : son aspect suit la FINITION DE MUR choisie au formulaire
  // (voir FINITIONS_MUR en tete de fichier). Sans finition : beton apparent, comme avant.
  const finMur = FINITIONS_MUR[String((params && params.finition_mur) || "")] || FINITIONS_MUR[""];
  const betonMat = new THREE.MeshStandardMaterial({ color: finMur.couleur, roughness: finMur.rugosite, metalness: 0.0 });
  (function chargeBeton() {
    const modeB = (opts && opts.mode) ? opts.mode : "technique";
    const poser = (img) => {
      img.colorSpace = THREE.SRGBColorSpace;
      img.wrapS = THREE.RepeatWrapping;
      img.wrapT = THREE.RepeatWrapping;
      // Les UV des murs sont en METRES (voir uvEnMetres) : le motif garde donc la meme
      // taille sur un mur de 3 m et sur un mur de 12 m.
      img.repeat.set(1 / finMur.taille, 1 / finMur.taille);
      betonMat.map = img;
      betonMat.color.set(0xffffff);
      betonMat.needsUpdate = true;
    };
    if (finMur.motif) {
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
  })();
""")

# ------------------------------------------------- 3. UV des murs en metres
rempl("3. UV des murs en metres",
"""  const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), mat || woodMat);
""",
"""  // Une BoxGeometry porte des UV de 0 a 1 par face : une texture s y etire a la taille du
  // mur, donc une brique serait trois fois plus large sur un pignon que sur un refend.
  // On repasse ces UV en METRES, comme celles des murs percus (ExtrudeGeometry).
  const uvEnMetres = (geo, sx, sy, sz) => {
    const uv = geo.attributes.uv;
    if (uv === undefined) return;
    const cotes = [[sz, sy], [sz, sy], [sx, sz], [sx, sz], [sx, sy], [sx, sy]];
    for (let f = 0; f < 6; f++) {
      for (let k = 0; k < 4; k++) {
        const i = f * 4 + k;
        uv.setXY(i, uv.getX(i) * cotes[f][0], uv.getY(i) * cotes[f][1]);
      }
    }
    uv.needsUpdate = true;
  };

  const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
    const geoB = new THREE.BoxGeometry(sx, sy, sz);
    if (mat === betonMat) uvEnMetres(geoB, sx, sy, sz);
    const m = new THREE.Mesh(geoB, mat || woodMat);
""")

# ------------------------------------------------- 4. formulaire
rempl("4a. etat du champ",
'const [formMurs, setFormMurs] = useState(""); // "" = beton existant (defaut) / "ossature_bois"\n',
'const [formMurs, setFormMurs] = useState(""); // "" = beton existant (defaut) / "ossature_bois"\n'
'const [formFinitionMur, setFormFinitionMur] = useState(""); // aspect de la maconnerie (voir FINITIONS_MUR)\n')

rempl("4b. menu deroulant dans le formulaire",
"""                </div>
              </div>
              {/* Mur de pignon */}
""",
"""                </div>
                {/* Finition de la maconnerie : sans objet sur une ossature bois */}
                {formMurs === "ossature_bois" ? null : (
                  <div style={{ marginTop: 10 }}>
                    <select value={formFinitionMur} onChange={e => setFormFinitionMur(e.target.value)}
                      style={{ ...inputStyle, cursor: "pointer", appearance: "none", WebkitAppearance: "none",
                        backgroundImage: \"""" + CHEVRON + """\",
                        backgroundRepeat: "no-repeat", backgroundPosition: "right 14px center", paddingRight: 36 }}>
                      <option value="">Beton apparent (par defaut)</option>
                      <option value="crepi">Crepi</option>
                      <option value="enduit">Enduit lisse</option>
                      <option value="brique">Brique</option>
                      <option value="pierre">Pierre apparente</option>
                    </select>
                  </div>
                )}
              </div>
              {/* Mur de pignon */}
""")

rempl("4c. parametre de generation",
"      type: formType || undefined,\n      murs: formMurs || undefined,\n",
"      type: formType || undefined,\n      murs: formMurs || undefined,\n"
"      finition_mur: formFinitionMur || undefined,\n")

rempl("4d. memorisation dans le devis",
"  if (finalParams.murs) parsed._murs = finalParams.murs;\n",
"  if (finalParams.murs) parsed._murs = finalParams.murs;\n"
"  if (finalParams.finition_mur) parsed._finitionMur = finalParams.finition_mur;\n")

rempl("4e. transmission a la 3D",
"        murs: finalParams.murs || undefined,\n",
"        murs: finalParams.murs || undefined,\n"
"        finition_mur: finalParams.finition_mur || undefined,\n")

rempl("4f. rechargement d un projet",
"        murs: project.devis_data._murs || undefined,\n",
"        murs: project.devis_data._murs || undefined,\n"
"        finition_mur: project.devis_data._finitionMur || undefined,\n")

rempl("4g. projet multi-ouvrages",
"        ouvrages: ouvrages3D,\n",
"        ouvrages: ouvrages3D,\n"
"        finition_mur: formFinitionMur || undefined,\n")

rempl("4h. memorisation multi-ouvrages",
'      if (formDelardement === "") { fusion._delardement = undefined; } else { fusion._delardement = parseFloat(formDelardement); }\n',
'      if (formDelardement === "") { fusion._delardement = undefined; } else { fusion._delardement = parseFloat(formDelardement); }\n'
"      if (formFinitionMur) fusion._finitionMur = formFinitionMur;\n")

io.open(chemin, "w", encoding="utf-8").write(s)
for t, n, a in etapes:
    print("  " + t + " : " + str(n) + "/" + str(a))
print("OK finitions de mur posees")
