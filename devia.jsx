import { useState, useRef, useEffect } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
// ===== MOTEUR EC5 (deplace avant buildScene3D pour init) =====

// ============================================================
// MOTEUR DE DIMENSIONNEMENT EC5 (cours TCB Gojon)
// !!! Valeurs de descente de charge A VALIDER PAR LE PROF !!!
// ============================================================
const EC5_BOIS = { C18:{fmk:18,E:9000}, C24:{fmk:24,E:11000}, C30:{fmk:30,E:12000} };
const EC5_GAMMA_M = 1.3; // bois massif
const EC5_KMOD = {
  1:{permanent:0.6,long:0.7,moyen:0.8,court:0.9,instant:1.1},
  2:{permanent:0.6,long:0.7,moyen:0.8,court:0.9,instant:0.9},
  3:{permanent:0.5,long:0.55,moyen:0.65,court:0.7,instant:0.9},
};
const EC5_KDEF = {1:0.6,2:0.8,3:2.0};
const EC5_FLECHE_ADM = { courant:{winst:300,wnetfin:200}, agricole:{winst:200,wnetfin:150} };

// Sections standard FR (b x h mm)
const EC5_SECTIONS = [
  [38,100],[38,120],[38,150],[38,175],[38,200],[38,225],
  [50,150],[50,175],[50,200],[50,225],[50,250],
  [63,150],[63,175],[63,200],[63,225],[63,250],
  [75,175],[75,200],[75,225],[75,250],[75,300],
  [100,200],[100,225],[100,250],[100,300],
  [150,300],[150,350],[150,400],
];
const EC5_LARGEUR_MINI = {
  Chevron:60, Panne:75, Sabliere:75, Arbaletrier:75, "Panne faitiere":75,
  Ferme:75, Poteau:100, Entrait:60, Aretier:75, Empannon:60, "Empannon de croupe":60,
  Liteau:0, Echantignole:0, Defaut:60,
};
const EC5_RATIO_MAX = 3;

// Poids couvertures (kg/m2) -> recuperes du registre COUVERTURES
const EC5_COUV_POIDS = {
  tuile_terre:45, tuile_beton:48, ardoise:30, bac_acier:10, zinc:12, shingle:12, fibrociment:18,
};
// --- CONSTANTES DESCENTE DE CHARGE (A VALIDER PROF) ---
const EC5_POIDS_CHARPENTE = 0.15; // kN/m2 (A VALIDER)
const EC5_MU_NEIGE = 0.8;         // coef forme toiture (A VALIDER, depend pente)
const EC5_Q_TOITURE = 0.0;        // kN/m2 exploitation toiture (A VALIDER)
const EC5_G_TO_KN = 0.0098;       // kg/m2 -> kN/m2

function ec5DescenteCharge(couverture, sk) {
  const poidsCouv = (EC5_COUV_POIDS[couverture] || 45) * EC5_G_TO_KN;
  const G = poidsCouv + EC5_POIDS_CHARPENTE;
  const S = (sk || 0.45) * EC5_MU_NEIGE;
  const Q = EC5_Q_TOITURE;
  return { G, Q, S };
}

function ec5VerifierFlexion(o) {
  const mat = EC5_BOIS[o.classe];
  const L = o.portee * 1000;
  const IGz = (o.b * Math.pow(o.h, 3)) / 12;
  let qELU = 1.35*o.G + 1.5*o.Q; if (o.S>0) qELU += 0.5*o.S;
  const Mfz = (qELU*o.entraxe*L*L)/8;
  const sigmaMax = Mfz/(IGz/(0.5*o.h));
  const kmod = EC5_KMOD[o.classeService][o.dureeVariable] || EC5_KMOD[o.classeService].moyen;
  const Fmd = mat.fmk*kmod/EC5_GAMMA_M;
  const tauxELU = (sigmaMax/Fmd)*100;
  const qInst = Math.max(o.Q, o.S||0);
  const Winst = (5*qInst*o.entraxe*Math.pow(L,4))/(384*mat.E*IGz);
  const tauxWinst = (Winst/(L/EC5_FLECHE_ADM[o.typeBatiment].winst))*100;
  const kdef = EC5_KDEF[o.classeService];
  const qNetFin = o.G*(1+1*kdef) + o.Q*(1+0.3*kdef);
  const WnetFin = (5*qNetFin*o.entraxe*Math.pow(L,4))/(384*mat.E*IGz);
  const tauxWnetFin = (WnetFin/(L/EC5_FLECHE_ADM[o.typeBatiment].wnetfin))*100;
  return { tauxELU, tauxWinst, tauxWnetFin, tauxMax: Math.max(tauxELU,tauxWinst,tauxWnetFin) };
}

// Dimensionne UNE piece -> { mini, conseillee } ou null
function dimensionnerPiece(typePiece, charge) {
  const wMini = EC5_LARGEUR_MINI[typePiece] != null ? EC5_LARGEUR_MINI[typePiece] : EC5_LARGEUR_MINI.Defaut;
  if (wMini === 0) return null; // pieces non structurelles (liteau, echantignole)
  const ordreClasse = { C18:0, C24:1, C30:2 };
  const candidats = [];
  for (const classe of ["C18","C24","C30"]) {
    for (const [b,h] of EC5_SECTIONS) {
      if (b < wMini) continue;
      if (h/b > EC5_RATIO_MAX) continue;
      const r = ec5VerifierFlexion({ ...charge, b, h, classe });
      if (r.tauxMax <= 100) candidats.push({ b,h,classe,...r, aire:b*h });
    }
  }
  if (!candidats.length) return null;
  const mini = [...candidats].sort((a,b)=> a.aire-b.aire || ordreClasse[a.classe]-ordreClasse[b.classe])[0];
  const conseillee = [...candidats].sort((a,b)=> Math.abs(a.tauxMax-70)-Math.abs(b.tauxMax-70))[0];
  return { mini, conseillee };
}

// ============================================================
// CALCUL CENTRAL DES SECTIONS PAR TYPE DE PIECE (reutilisable 3D + tableau)
// Retourne { "Panne": {mini:{b,h,classe,tauxMax}, conseillee:{...}}, ... }
// !!! Hypotheses portee/entraxe/charge A VALIDER PROF !!!
// ============================================================
function calculerSectionsCharpente(metreAgrege, params, sk) {
  if (!metreAgrege || !metreAgrege.groupes) return {};
  const ch = ec5DescenteCharge((params && params.couverture) || "tuile_terre", sk || 0.45);
  const ENTRAXE_FERMES = 3.5;
  const PORTEE_MAX = 8;
  const result = {};

  metreAgrege.groupes.forEach((g) => {
    if (result[g.nom]) return; // un seul calcul par type (le 1er groupe du type)
    // portee realiste selon type
    let porteeCalc;
    if (g.nom === "Panne" || g.nom === "Panne faitiere" || g.nom === "Sabliere") {
      porteeCalc = ENTRAXE_FERMES;
    } else {
      porteeCalc = g.longueurUnitMax;
    }
    porteeCalc = Math.min(porteeCalc, PORTEE_MAX);
    const entraxe = (g.nom === "Chevron" || g.nom === "Empannon" || g.nom === "Empannon de croupe") ? 0.6
                  : (g.nom === "Panne" || g.nom === "Panne faitiere") ? 1.5
                  : (g.nom === "Sabliere" || g.nom === "Aretier") ? 1.0
                  : 1.0;
    const charge = {
      portee: porteeCalc, entraxe,
      G: ch.G, Q: ch.Q, S: ch.S,
      classeService: 2, typeBatiment: "courant", dureeVariable: "court",
    };
    const dim = dimensionnerPiece(g.nom, charge);
    if (dim) result[g.nom] = dim;
  });
  return result;
}


// ================================================================
// BUILD SCENE 3D - Construit la geometrie selon type de projet
// Utilisee par Viewer3D (interactif) et capture3DViews (PDF)
// ================================================================
function buildScene3D(scene, params, opts) {
  const L = params.longueur || 8;
  const lg = params.largeur || 6;
  const Ht = params.hauteur || 3;
  const pente = params.pente || 35;
  const typeProjet = params.type_projet || "charpente_trad";

  // Helper sections EC5 : si opts.sections[nom] existe, l'utilise (mm->m), sinon fallback
  // sectionMode choisit mini ou conseillee
  const secMode = (opts && opts.sectionMode) || "conseillee";
  const sec = (nom, wDef, hDef) => {
    const dim = opts && opts.sections && opts.sections[nom];
    if (dim && dim[secMode]) return [dim[secMode].b / 1000, dim[secMode].h / 1000];
    return [wDef, hDef];
  };

  // Options : couleurs (peuvent varier pour le PDF vs interactif)
  const woodColor = opts && opts.woodColor ? opts.woodColor : 0xc4894a;
  const roofColor = opts && opts.roofColor ? opts.roofColor : 0x8b6355;
  const wallColor = opts && opts.wallColor ? opts.wallColor : 0xf0ece0;
  const wallOpacity = opts && opts.wallOpacity !== undefined ? opts.wallOpacity : 0.2;

  // ===== METRE : capture des pieces dessinees =====
  const DENSITES_BOIS = { sapin: 450, epicea: 450, douglas: 520, chene: 700, pin: 510 };
  const essence = (params && params.essence) ? params.essence : "sapin";
  const densiteBois = DENSITES_BOIS[essence] || 450;
  const metre = [];
  let currentPiece = "Divers";
  const setPiece = (nom) => { currentPiece = nom; };
  // longueur estimee = plus grande dimension de la piece
  const logPiece = (a, b, c, place) => {
    const dims = [a, b, c].sort((u, v) => v - u);
    const longueur = dims[0];
    const sx = dims[1], sy = dims[2];
    const volume = a * b * c;
    metre.push({
      nom: currentPiece,
      section: [Math.round(sx*1000), Math.round(sy*1000)], // mm
      longueur: longueur,                                   // m
      volume: volume,                                       // m3
      // placement 3D pour export IFC (optionnel)
      dimsBrutes: [a, b, c],          // sx, sy, sz d'origine (m)
      pos: place ? place.pos : null,  // [x, y, z] centre (m)
      rot: place ? place.rot : null,  // [rx, ry, rz] euler (rad) ou null
      quat: place ? place.quat : null,// [x, y, z, w] quaternion ou null
    });
  };

  const woodMat = new THREE.MeshLambertMaterial({ color: woodColor });
  const roofMat = new THREE.MeshLambertMaterial({ color: roofColor, side: THREE.DoubleSide });
  const wallMat = new THREE.MeshLambertMaterial({ color: wallColor, transparent: true, opacity: wallOpacity, side: THREE.DoubleSide });

  const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), mat || woodMat);
    m.position.set(px, py, pz);
    if (rot) m.rotation.set(...rot);
    m.castShadow = true;
    scene.add(m);
    if (!mat || mat === woodMat) logPiece(sx, sy, sz, { pos: [px, py, pz], rot: rot || null, quat: null }); // bois uniquement
  };

  // Poutre orientee entre 2 points (touche forcement les 2 extremites)
  const addBeam = (x1, y1, z1, x2, y2, z2, thick, mat) => {
    const dx = x2 - x1, dy = y2 - y1, dz = z2 - z1;
    const len = Math.sqrt(dx*dx + dy*dy + dz*dz);
    const m = new THREE.Mesh(new THREE.BoxGeometry(thick, thick, len), mat || woodMat);
    m.position.set((x1+x2)/2, (y1+y2)/2, (z1+z2)/2);
    const dir = new THREE.Vector3(dx, dy, dz).normalize();
    const q = new THREE.Quaternion();
    q.setFromUnitVectors(new THREE.Vector3(0, 0, 1), dir);
    m.quaternion.copy(q);
    m.castShadow = true;
    scene.add(m);
    if (!mat || mat === woodMat) logPiece(thick, thick, len, { pos: [(x1+x2)/2, (y1+y2)/2, (z1+z2)/2], rot: null, quat: [q.x, q.y, q.z, q.w] });
  };

  // ============================================================
  // REGISTRE DES COUVERTURES (source unique de verite)
  // ============================================================
  const COUVERTURES = {
    tuile_terre: { label: "Tuile terre cuite", couleur: 0xc87650, espChevron: 0.50, espLiteau: 0.35, penteMin: 30, poids: 45, prixM2: null },
    tuile_beton: { label: "Tuile beton", couleur: 0x8b6355, espChevron: 0.45, espLiteau: 0.32, penteMin: 25, poids: 48, prixM2: null },
    ardoise: { label: "Ardoise", couleur: 0x4a4f57, espChevron: 0.45, espLiteau: 0.33, penteMin: 22, poids: 30, prixM2: null },
    bac_acier: { label: "Bac acier", couleur: 0x3a3a3f, espChevron: 0.70, espLiteau: 0.50, penteMin: 7, poids: 10, prixM2: null },
    zinc: { label: "Zinc (joint debout)", couleur: 0x9aa0a6, espChevron: 0.60, espLiteau: 0.45, penteMin: 5, poids: 12, prixM2: null },
    shingle: { label: "Shingle / bardeau bitume", couleur: 0x5a4632, espChevron: 0.45, espLiteau: 0.32, penteMin: 18, poids: 12, prixM2: null },
    fibrociment: { label: "Fibrociment ondule", couleur: 0xb8bcc0, espChevron: 0.90, espLiteau: 0.60, penteMin: 12, poids: 18, prixM2: null },
  };
  const getCouverture = (code) => {
    const c = COUVERTURES[code] || COUVERTURES.tuile_terre;
    const key = COUVERTURES[code] ? code : "tuile_terre";
    return { ...c, code: key };
  };

  // ============================================================
  // TEXTURES PROCEDURALES DE COUVERTURE (mode realiste)
  // ============================================================
  const makeCouvTexture = (couv) => {
    const S = 512;
    const c = document.createElement("canvas");
    c.width = S; c.height = S;
    const x = c.getContext("2d");
    const r = (couv.couleur >> 16) & 255, g = (couv.couleur >> 8) & 255, b = couv.couleur & 255;
    const shade = (f) => `rgb(${Math.min(255,Math.max(0,Math.round(r*f)))},${Math.min(255,Math.max(0,Math.round(g*f)))},${Math.min(255,Math.max(0,Math.round(b*f)))})`;
    const lab = couv.label || "";

    const rr = (px, py, pw, ph, rad, col) => {
      x.fillStyle = col;
      x.beginPath();
      x.moveTo(px+rad, py);
      x.arcTo(px+pw, py, px+pw, py+ph, rad);
      x.arcTo(px+pw, py+ph, px, py+ph, rad);
      x.arcTo(px, py+ph, px, py, rad);
      x.arcTo(px, py, px+pw, py, rad);
      x.closePath(); x.fill();
    };

    if (lab.indexOf("Bac") >= 0 || lab.indexOf("Zinc") >= 0) {
      x.fillStyle = shade(1); x.fillRect(0, 0, S, S);
      const step = 46;
      for (let i = 0; i < S; i += step) {
        x.fillStyle = shade(0.6); x.fillRect(i, 0, 5, S);
        x.fillStyle = shade(1.28); x.fillRect(i + step/2, 0, 3, S);
      }
    } else if (lab.indexOf("Fibrociment") >= 0) {
      const step = 50;
      for (let i = 0; i < S; i += step) {
        const grad = x.createLinearGradient(i, 0, i + step, 0);
        grad.addColorStop(0, shade(0.65)); grad.addColorStop(0.5, shade(1.2)); grad.addColorStop(1, shade(0.65));
        x.fillStyle = grad; x.fillRect(i, 0, step, S);
      }
    } else {
      // TUILES / ARDOISE / SHINGLE : ecailles bombees avec relief
      x.fillStyle = shade(0.5); x.fillRect(0, 0, S, S);
      const w = 74, h = 58;
      const rows = Math.ceil(S / (h * 0.62)) + 2;
      for (let row = 0; row < rows; row++) {
        const py = Math.round(row * h * 0.62);
        const off = (row % 2) * (w / 2);
        const cols = Math.ceil(S / w) + 2;
        for (let col = -1; col < cols; col++) {
          const px = Math.round(col * w + off);
          const v = 0.82 + ((row * 5 + col * 7) % 6) * 0.06;
          rr(px + 2, py, w - 4, h, Math.round(w * 0.42), shade(v));         // corps
          rr(px + 4, py + 2, w - 8, Math.round(h * 0.4), Math.round(w * 0.3), shade(v * 1.18)); // lumiere haut
          x.strokeStyle = shade(0.45); x.lineWidth = 4;                      // ombre bas
          x.beginPath();
          x.arc(px + w/2, py + h * 0.62, w/2, 0.35, Math.PI - 0.35, false);
          x.stroke();
        }
      }
    }
    const tex = new THREE.CanvasTexture(c);
    tex.wrapS = THREE.RepeatWrapping; tex.wrapT = THREE.RepeatWrapping;
    tex.needsUpdate = true;
    return tex;
  };

  // Materiau de couverture selon le mode (technique = transparent / realiste = texture opaque)
  const makeRoofMaterial = (couv, surfX, surfY) => {
    const mode = (opts && opts.mode) ? opts.mode : "technique";
    if (mode !== "realiste") {
      // Vue technique : couleur transparente
      return new THREE.MeshLambertMaterial({
        color: couv.couleur, transparent: true, opacity: 0.4, side: THREE.DoubleSide
      });
    }
    // Vue realiste : on tente l'image, fallback procedural
    const code = couv.code || "";
    const rx = Math.max(1, (surfX || 4) / 2.4);
    const ry = Math.max(1, (surfY || 4) / 2.4);

    // Materiau procedural par defaut (s'affiche immediatement)
    const ptex = makeCouvTexture(couv);
    ptex.repeat.set(rx, ry);
    const mat = new THREE.MeshLambertMaterial({ map: ptex, side: THREE.DoubleSide });

    // Tentative de chargement de l'image reelle (async, remplace si trouvee)
    if (code) {
      const loader = new THREE.TextureLoader();
      const tryLoad = (ext, onFail) => {
        loader.load(
          "/textures/" + code + "." + ext,
          (img) => {
            img.wrapS = THREE.RepeatWrapping;
            img.wrapT = THREE.RepeatWrapping;
            img.repeat.set(rx, ry);
            mat.map = img;
            mat.needsUpdate = true;
          },
          undefined,
          () => { if (onFail) onFail(); }
        );
      };
      // essaie .png puis .jpg
      tryLoad("png", () => tryLoad("jpg", null));
    }
    return mat;
  };


  // ============================================================
  // CHARPENTE TRADITIONNELLE (2 pans)
  // ============================================================
  const drawCharpenteTrad = () => {
    const hf = lg / 2 * Math.tan((pente * Math.PI) / 180); // hauteur faitage
    const ang = Math.atan(hf / (lg/2));                    // angle de pente
    const pl = (lg/2) / Math.cos(ang);                     // longueur d'un arbaletrier
    const yFait = Ht + hf;                                  // hauteur du faitage

    // ===== MURS (4 cotes) =====
    [
      [L, Ht, 0.15, 0, Ht/2, lg/2],
      [L, Ht, 0.15, 0, Ht/2, -lg/2],
      [0.15, Ht, lg, -L/2, Ht/2, 0],
      [0.15, Ht, lg, L/2, Ht/2, 0]
    ].forEach(([sx, sy, sz, px, py, pz]) => addBox(sx, sy, sz, px, py, pz, wallMat));

setPiece("Ferme");
    // ===== FERMES (tous les ~3.5m) =====
    // Chaque ferme = entrait + 2 arbaletriers + poincon + 2 contrefiches
    const nbFermes = Math.max(2, Math.ceil(L / 3.5));
    const fermeXs = [];
    for (let i = 0; i <= nbFermes; i++) {
      const x = -L/2 + (i / nbFermes) * L;
      fermeXs.push(x);

      // ENTRAIT (poutre horizontale basse, sur toute la largeur)
      const [enB, enH] = sec("Ferme", 0.16, 0.16);
      addBox(enB, enH, lg, x, Ht, 0, woodMat);

      // ARBALETRIERS (les 2 pans inclines, section forte)
      const [arB, arH] = sec("Ferme", 0.16, 0.16);
      addBox(arB, arH, pl, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);
      addBox(arB, arH, pl, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);

      // POINCON (poteau vertical central, du faitage a l'entrait)
      addBox(0.14, hf, 0.14, x, Ht + hf/2, 0, woodMat);

      // CONTREFICHES (jambes de force du bas du poincon vers les arbaletriers)
      // Dessinees point-a-point : touchent forcement les 2 extremites
      const cfBaseY = Ht + hf * 0.15;           // depart : bas du poincon
      const cfT = 0.55;                          // arrivee : 55% le long de l'arbaletrier
      const cfEndY = Ht + cfT * hf;
      const cfEndZ = (lg/2) * (1 - cfT);
      addBeam(x, cfBaseY, 0, x, cfEndY, cfEndZ, 0.10, woodMat);   // vers pan Z+
      addBeam(x, cfBaseY, 0, x, cfEndY, -cfEndZ, 0.10, woodMat);  // vers pan Z-
    }

setPiece("Sabliere");
    // ===== SABLIERES (poutres basses sur les murs longs) =====
    const [sbB, sbH] = sec("Sabliere", 0.14, 0.14);
    addBox(L + 0.3, sbH, sbB, 0, Ht, lg/2, woodMat);
    addBox(L + 0.3, sbH, sbB, 0, Ht, -lg/2, woodMat);

setPiece("Panne faitiere");
    // ===== PANNE FAITIERE =====
    const [pfB, pfH] = sec("Panne faitiere", 0.14, 0.14);
    addBox(L + 0.4, pfH, pfB, 0, yFait, 0, woodMat);

setPiece("Panne");
    // ===== PANNES INTERMEDIAIRES (le long du toit, sur les 2 pans) =====
    const nbPannesParPan = 2;
    for (let p = 1; p <= nbPannesParPan; p++) {
      const t = p / (nbPannesParPan + 1); // position le long de l'arbaletrier
      const yPanne = Ht + hf * t;
      const zPanne = (lg/2) * (1 - t);
      const [pnB, pnH] = sec("Panne", 0.12, 0.12);
      addBox(L + 0.3, pnH, pnB, 0, yPanne, zPanne, woodMat);
      addBox(L + 0.3, pnH, pnB, 0, yPanne, -zPanne, woodMat);
    }

setPiece("Chevron");
    // ===== CHEVRONS RAPPROCHES (tous les ~0.5m, sur les pannes) =====
    const espChevron = 0.5;
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      // Chevron pan Z+ (section fine)
      const [chB, chH] = sec("Chevron", 0.07, 0.07);
      addBox(chB, chH, pl, x, Ht + hf/2 + 0.08, lg/4, woodMat, [ang, 0, 0]);
      // Chevron pan Z-
      addBox(chB, chH, pl, x, Ht + hf/2 + 0.08, -lg/4, woodMat, [-ang, 0, 0]);
    }

    // ===== COUVERTURE (2 pans, semi-transparente pour voir l'ossature) =====
    const roofTransMat = new THREE.MeshLambertMaterial({
      color: roofColor, transparent: true, opacity: 0.45, side: THREE.DoubleSide
    });
    const rg = new THREE.PlaneGeometry(L + 0.6, pl + 0.2);
    const r1 = new THREE.Mesh(rg, roofTransMat);
    r1.position.set(0, Ht + hf/2 + 0.12, lg/4);
    r1.rotation.x = ang - Math.PI/2;
    scene.add(r1);
    const r2 = new THREE.Mesh(rg, roofTransMat);
    r2.position.set(0, Ht + hf/2 + 0.12, -lg/4);
    r2.rotation.x = -(ang - Math.PI/2);
    scene.add(r2);
  };

  // ============================================================
  // CARPORT (1 pente, pas de murs)
  // ============================================================
  const drawCarport = () => {
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;
    const Hhaut = Ht + denivele;
    const sectionPotau = 0.18;
    const ang = Math.atan(denivele / lg);
    const longueurChevron = lg / Math.cos(ang);

setPiece("Poteau");
    // ===== POTEAUX (specificite carport) =====
    // Poteaux intermediaires aussi si carport long
    const nbPoteauxLong = Math.max(1, Math.ceil(L / 4));
    for (let i = 0; i <= nbPoteauxLong; i++) {
      const x = -L/2 + (i / nbPoteauxLong) * L;
      addBox(sectionPotau, Hbas, sectionPotau, x, Hbas/2, -lg/2);   // avant (bas)
      addBox(sectionPotau, Hhaut, sectionPotau, x, Hhaut/2, lg/2);  // arriere (haut)
    }

    // ===== SABLIERES (basse avant + haute arriere) =====
    addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2, woodMat);
    addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2, woodMat);

setPiece("Panne");
    // ===== PANNES INTERMEDIAIRES (suivent la pente) =====
    const nbPannes = 3;
    for (let i = 0; i < nbPannes; i++) {
      const t = i / (nbPannes - 1);
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele;
      addBox(L + 0.3, 0.12, 0.12, 0, y, z, woodMat);
    }

setPiece("Chevron");
    // ===== CHEVRONS RAPPROCHES (~tous les 0.6m) =====
    const espChevron = 0.6;
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    const yCentre = Hbas + denivele/2;
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      addBox(0.08, 0.08, longueurChevron + 0.2, x, yCentre + 0.06, 0, woodMat, [-ang, 0, 0]);
    }

    // ===== COUVERTURE (1 pan, semi-transparente) =====
    const roofTransMat = new THREE.MeshLambertMaterial({
      color: roofColor, transparent: true, opacity: 0.45, side: THREE.DoubleSide
    });
    const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
    const roof = new THREE.Mesh(rg, roofTransMat);
    roof.position.set(0, yCentre + 0.16, 0);
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);
  };

  // ============================================================
  // MONOPENTE (1 pan + murs, mur arriere haut, mur avant bas)
  // ============================================================
  const drawMonopente = () => {
    // ============================================================
    // MONOPENTE REALISTE - charpente complete
    // ============================================================
    // Calcul deniveles
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;             // hauteur mur avant
    const Hhaut = Ht + denivele; // hauteur mur arriere
    const ang = Math.atan(denivele / lg);
    const longueurChevron = lg / Math.cos(ang);
    const yCentre = Hbas + denivele/2;

    // ===== CHOIX COUVERTURE (bac acier / tuiles) =====
    const couv = getCouverture(opts && opts.couverture);
    const couvColor = couv.couleur;
    const monopenteRoofMat = makeRoofMaterial(couv, L, longueurChevron);

    // ===== 4 MURS (hauteurs variables sur les cotes) =====
    // Mur arriere (Z+, haut)
    addBox(L, Hhaut, 0.15, 0, Hhaut/2, lg/2, wallMat);
    // Mur avant (Z-, bas)
    addBox(L, Hbas, 0.15, 0, Hbas/2, -lg/2, wallMat);

    // Mur lateral gauche (partie basse + triangle haut)
    addBox(0.15, Hbas, lg, -L/2, Hbas/2, 0, wallMat);
    const triGeo = new THREE.BufferGeometry();
    const triVertices = new Float32Array([
      -L/2, Hbas, -lg/2,
      -L/2, Hbas, lg/2,
      -L/2, Hhaut, lg/2,
    ]);
    triGeo.setAttribute("position", new THREE.BufferAttribute(triVertices, 3));
    triGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(triGeo, wallMat));

    // Mur lateral droit (partie basse + triangle haut)
    addBox(0.15, Hbas, lg, L/2, Hbas/2, 0, wallMat);
    const triGeo2 = new THREE.BufferGeometry();
    const triVertices2 = new Float32Array([
      L/2, Hbas, -lg/2,
      L/2, Hbas, lg/2,
      L/2, Hhaut, lg/2,
    ]);
    triGeo2.setAttribute("position", new THREE.BufferAttribute(triVertices2, 3));
    triGeo2.computeVertexNormals();
    scene.add(new THREE.Mesh(triGeo2, wallMat));

    setPiece("Sabliere");
    // ===== SABLIERES (basse avant + haute arriere) =====
    const [sbB, sbH] = sec("Sabliere", 0.16, 0.16);
    addBox(L + 0.3, sbH, sbB, 0, Hbas, -lg/2, woodMat);
    addBox(L + 0.3, sbH, sbB, 0, Hhaut, lg/2, woodMat);

    setPiece("Panne");
    // ===== PANNES INTERMEDIAIRES (4, bien reparties entre sablieres) =====
    const nbPannes = 4;
    const pannePositions = [];
    for (let i = 0; i < nbPannes; i++) {
      const t = (i + 1) / (nbPannes + 1);  // evite superposition aux sablieres
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele;
      const [pnB, pnH] = sec("Panne", 0.14, 0.14);
      addBox(L + 0.3, pnH, pnB, 0, y, z, woodMat);
      pannePositions.push({ y, z, t });
    }

setPiece("Chevron");
    // ===== CHEVRONS RAPPROCHES (espacement selon couverture) =====
    const espChevron = couv.espChevron;
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      const [chB, chH] = sec("Chevron", 0.08, 0.08);
      addBox(chB, chH, longueurChevron + 0.2, x, yCentre + 0.07, 0, woodMat, [-ang, 0, 0]);
    }

setPiece("Liteau");
    // ===== LITEAUX (perpendiculaires aux chevrons, ~tous les 0.35m) =====
    // Petites planchettes paralleles aux sablieres, sur toute la longueur
    const espLiteau = couv.espLiteau;
    const nbLiteaux = Math.max(4, Math.floor(longueurChevron / espLiteau));
    for (let i = 0; i <= nbLiteaux; i++) {
      const t = i / nbLiteaux;
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele + 0.15;  // au-dessus des chevrons
      addBox(L + 0.4, 0.025, 0.04, 0, y, z, woodMat);
    }

    // ===== AISSELIERS (jambes de force obliques aux pignons) =====
    // Sur chaque mur lateral, 2 jambes obliques qui soutiennent les pannes
    // Partent du mur en haut (Hbas + 0.3) vers une panne intermediaire
    const aisselierAngles = [];  // aisseliers desactives (rendu plus propre)  // 2eme et 3eme panne
    [-1, 1].forEach((cote) => {
      const xMur = cote * (L/2 - 0.08);
      aisselierAngles.forEach((p) => {
        // Point bas : sur le mur lateral, a 80% de Hbas, decale vers z=0
        const xb = xMur;
        const yb = Hbas * 0.7;
        const zb = -lg/2 + 0.3;  // decale vers la sabliere basse
        // Point haut : sous la panne, a la position de la panne
        const xh = xMur;
        const yh = p.y - 0.08;
        const zh = p.z;
        // Calculs de la jambe oblique (centre + longueur + rotation autour de X)
        const dy = yh - yb;
        const dz = zh - zb;
        const longueur = Math.sqrt(dy*dy + dz*dz);
        const rotX = -Math.atan2(dy, dz);  // rotation autour de X
        const xc = (xb + xh) / 2;
        const yc = (yb + yh) / 2;
        const zc = (zb + zh) / 2;
        addBox(0.10, 0.10, longueur, xc, yc, zc, woodMat, [rotX, 0, 0]);
      });
    });

    // ===== COUVERTURE (1 pan, semi-transparente, couleur selon type) =====
    const rg = new THREE.PlaneGeometry(L + 0.4, longueurChevron + 0.3);
    const roof = new THREE.Mesh(rg, monopenteRoofMat);
    roof.position.set(0, yCentre + 0.20, 0);  // plus haut a cause des liteaux
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);
  };

  // ============================================================
  // HANGAR (poteaux + 2 pans, sans murs, grande portee)
  // ============================================================
  const drawHangar = () => {
    const hf = lg / 2 * Math.tan((pente * Math.PI) / 180);
    const ang = Math.atan(hf / (lg/2));
    const pl = (lg/2) / Math.cos(ang);
    const yFait = Ht + hf;
    const sectionPotau = 0.22; // poteaux plus gros pour hangar

setPiece("Poteau");
    // ===== POTEAUX (specificite hangar : 4 coins + intermediaires) =====
    const nbPoteauxLong = Math.max(2, Math.ceil(L / 4));
    for (let i = 0; i <= nbPoteauxLong; i++) {
      const x = -L/2 + (i / nbPoteauxLong) * L;
      addBox(sectionPotau, Ht, sectionPotau, x, Ht/2, lg/2);   // cote Z+
      addBox(sectionPotau, Ht, sectionPotau, x, Ht/2, -lg/2);  // cote Z-
    }

setPiece("Sabliere");
    // ===== SABLIERES (longues poutres sur les poteaux) =====
    const [sbB, sbH] = sec("Sabliere", 0.20, 0.20);
    addBox(L + 0.4, sbH, sbB, 0, Ht, lg/2, woodMat);
    addBox(L + 0.4, sbH, sbB, 0, Ht, -lg/2, woodMat);

setPiece("Ferme");
    // ===== FERMES COMPLETES (tous les ~3m) =====
    const nbFermes = Math.max(2, Math.ceil(L / 3));
    for (let i = 0; i <= nbFermes; i++) {
      const x = -L/2 + (i / nbFermes) * L;

      // Entrait (poutre horizontale basse)
      const [enB, enH] = sec("Ferme", 0.16, 0.16);
      addBox(enB, enH, lg, x, Ht, 0, woodMat);
      // Arbaletriers (pans inclines, section forte)
      const [arB, arH] = sec("Ferme", 0.16, 0.16);
      addBox(arB, arH, pl, x, Ht + hf/2, lg/4, woodMat, [ang, 0, 0]);
      addBox(arB, arH, pl, x, Ht + hf/2, -lg/4, woodMat, [-ang, 0, 0]);
      // Poincon (vertical central)
      addBox(0.14, hf, 0.14, x, Ht + hf/2, 0, woodMat);
      // Contrefiches (jambes de force, point-a-point)
      const cfBaseY = Ht + hf * 0.15;
      const cfT = 0.55;
      const cfEndY = Ht + cfT * hf;
      const cfEndZ = (lg/2) * (1 - cfT);
      addBeam(x, cfBaseY, 0, x, cfEndY, cfEndZ, 0.10, woodMat);
      addBeam(x, cfBaseY, 0, x, cfEndY, -cfEndZ, 0.10, woodMat);
    }

setPiece("Panne");
    // ===== PANNE FAITIERE + INTERMEDIAIRES =====
    const [pfw, pfh] = sec("Panne faitiere", 0.16, 0.16);
    addBox(L + 0.5, pfw, pfh, 0, yFait, 0, woodMat);
    const nbPannesParPan = 2;
    const [pw, ph] = sec("Panne", 0.12, 0.12);
    for (let p = 1; p <= nbPannesParPan; p++) {
      const t = p / (nbPannesParPan + 1);
      const yPanne = Ht + hf * t;
      const zPanne = (lg/2) * (1 - t);
      addBox(L + 0.4, pw, ph, 0, yPanne, zPanne, woodMat);
      addBox(L + 0.4, pw, ph, 0, yPanne, -zPanne, woodMat);
    }

    setPiece("Chevron");
    // ===== CHEVRONS RAPPROCHES (~tous les 0.6m) =====
    const espChevron = 0.6;
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      const [chB, chH] = sec("Chevron", 0.07, 0.07);
      addBox(chB, chH, pl, x, Ht + hf/2 + 0.08, lg/4, woodMat, [ang, 0, 0]);
      addBox(chB, chH, pl, x, Ht + hf/2 + 0.08, -lg/4, woodMat, [-ang, 0, 0]);
    }

    // ===== COUVERTURE (2 pans, semi-transparente) =====
    const roofTransMat = new THREE.MeshLambertMaterial({
      color: roofColor, transparent: true, opacity: 0.45, side: THREE.DoubleSide
    });
    const rg = new THREE.PlaneGeometry(L + 0.8, pl + 0.3);
    const r1 = new THREE.Mesh(rg, roofTransMat);
    r1.position.set(0, Ht + hf/2 + 0.12, lg/4);
    r1.rotation.x = ang - Math.PI/2;
    scene.add(r1);
    const r2 = new THREE.Mesh(rg, roofTransMat);
    r2.position.set(0, Ht + hf/2 + 0.12, -lg/4);
    r2.rotation.x = -(ang - Math.PI/2);
    scene.add(r2);
  };

  // ============================================================
  // APPENTIS (toit 1 pan accole a un mur arriere haut)
  // ============================================================
  const drawAppentis = () => {
    // ============================================================
    // APPENTIS PARAMETRIQUE - charpente complete adaptative
    // S'adapte aux dimensions et a la couverture demandees.
    // (sections indicatives - calcul structurel = phase 2.B)
    // ============================================================
    const denivele = lg * Math.tan((pente * Math.PI) / 180);
    const Hbas = Ht;             // hauteur cote avant (libre)
    const Hhaut = Ht + denivele; // hauteur mur arriere (mur maison)
    const ang = Math.atan(denivele / lg);
    const longueurRampant = lg / Math.cos(ang);  // longueur du pan incline
    const yCentre = Hbas + denivele/2;

    // ===== REGLES METIER ADAPTATIVES =====
    // 1) Couverture -> couleur + espacement chevrons + espacement liteaux
    const couv = getCouverture(opts && opts.couverture);
    const couvColor = couv.couleur;
    const espChevron = couv.espChevron;
    const espLiteau = couv.espLiteau;
    const appentisRoofMat = makeRoofMaterial(couv, L, longueurRampant);

    // 2) Nb de pannes : un chevron ne franchit pas plus de ~2.2 m sans appui
    const porteeMaxChevron = 2.2;
    const nbPannes = Math.max(1, Math.ceil(longueurRampant / porteeMaxChevron) - 1);

    // 3) Section chevrons : grossit avec la longueur du rampant
    const secChevron = longueurRampant > 4.5 ? 0.10 : (longueurRampant > 3 ? 0.09 : 0.08);

    // 4) Poteaux avant : 1 tous les ~3.5 m
    const nbPoteauxLong = Math.max(1, Math.ceil(L / 3.5));

    // 5) Section pannes : grossit avec la portee entre poteaux
    const porteePanne = L / nbPoteauxLong;
    const secPanne = porteePanne > 3.5 ? 0.18 : (porteePanne > 2 ? 0.15 : 0.13);

    // 6) Section sablieres : un peu plus fortes que les pannes
    const secSabliere = Math.min(0.20, secPanne + 0.02);

    // ===== MUR ARRIERE D'ADOSSEMENT (mur existant maison) =====
    const murArriereMat = new THREE.MeshLambertMaterial({
      color: 0xd4ccb6, transparent: true, opacity: 0.85, side: THREE.DoubleSide
    });
    addBox(L + 0.5, Hhaut + 0.3, 0.25, 0, (Hhaut + 0.3)/2, lg/2, murArriereMat);

setPiece("Poteau");
    // ===== POTEAUX AVANT (cote ouvert, nb adaptatif) =====
    const secPoteau = 0.18;
    for (let i = 0; i <= nbPoteauxLong; i++) {
      const x = -L/2 + (i / nbPoteauxLong) * L;
      addBox(secPoteau, Hbas, secPoteau, x, Hbas/2, -lg/2, woodMat);
    }

    // ===== MURS LATERAUX TRAPEZOIDAUX (translucides) =====
    const triGeoL = new THREE.BufferGeometry();
    const triVertL = new Float32Array([
      -L/2, 0, -lg/2,  -L/2, Hbas, -lg/2,  -L/2, Hhaut, lg/2,
      -L/2, 0, -lg/2,  -L/2, Hhaut, lg/2,  -L/2, 0, lg/2,
    ]);
    triGeoL.setAttribute("position", new THREE.BufferAttribute(triVertL, 3));
    triGeoL.computeVertexNormals();
    scene.add(new THREE.Mesh(triGeoL, wallMat));

    const triGeoR = new THREE.BufferGeometry();
    const triVertR = new Float32Array([
      L/2, 0, -lg/2,  L/2, Hbas, -lg/2,  L/2, Hhaut, lg/2,
      L/2, 0, -lg/2,  L/2, Hhaut, lg/2,  L/2, 0, lg/2,
    ]);
    triGeoR.setAttribute("position", new THREE.BufferAttribute(triVertR, 3));
    triGeoR.computeVertexNormals();
    scene.add(new THREE.Mesh(triGeoR, wallMat));

setPiece("Sabliere");
    // ===== SABLIERES (basse avant + haute arriere contre mur) =====
    const [sbB, sbH] = sec("Sabliere", secSabliere, secSabliere);
    addBox(L + 0.3, sbH, sbB, 0, Hbas, -lg/2, woodMat);
    addBox(L + 0.3, sbH, sbB, 0, Hhaut, lg/2, woodMat);

setPiece("Panne");
    // ===== PANNES INTERMEDIAIRES (nb adaptatif, bien reparties) =====
    const pannePositions = [];
    for (let i = 0; i < nbPannes; i++) {
      const t = (i + 1) / (nbPannes + 1);
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele;
      const [pnB, pnH] = sec("Panne", secPanne, secPanne);
      addBox(L + 0.3, pnH, pnB, 0, y, z, woodMat);
      pannePositions.push({ y, z });
    }

setPiece("Chevron");
    // ===== CHEVRONS (espacement + section adaptatifs) =====
    const nbChevrons = Math.max(2, Math.floor(L / espChevron));
    const chevronXs = [];
    for (let i = 0; i <= nbChevrons; i++) {
      const x = -L/2 + (i / nbChevrons) * L;
      chevronXs.push(x);
      const [chB, chH] = sec("Chevron", secChevron, secChevron);
      addBox(chB, chH, longueurRampant + 0.2, x, yCentre + secChevron*0.8, 0, woodMat, [-ang, 0, 0]);
    }

setPiece("Liteau");
    // ===== LITEAUX (perpendiculaires aux chevrons, espacement adaptatif) =====
    const nbLiteaux = Math.max(4, Math.floor(longueurRampant / espLiteau));
    for (let i = 0; i <= nbLiteaux; i++) {
      const t = i / nbLiteaux;
      const z = -lg/2 + t * lg;
      const y = Hbas + t * denivele + secChevron + 0.07;
      addBox(L + 0.4, 0.025, 0.04, 0, y, z, woodMat);
    }

setPiece("Echantignole");
    // ===== ECHANTIGNOLES (cale a chaque croisement chevron x panne) =====
    // Petits taquets qui calent le chevron sur chaque panne (cote aval)
    chevronXs.forEach((x) => {
      pannePositions.forEach((p) => {
        const yEch = p.y + secPanne/2 + 0.03;
        const zEch = p.z - 0.07;
        addBox(secChevron * 0.9, 0.06, 0.10, x, yEch, zEch, woodMat);
      });
    });

    // ===== COUVERTURE (1 pan, semi-transparente, couleur selon type) =====
    const rg = new THREE.PlaneGeometry(L + 0.4, longueurRampant + 0.3);
    const roof = new THREE.Mesh(rg, appentisRoofMat);
    roof.position.set(0, yCentre + secChevron + 0.12, 0);
    roof.rotation.x = Math.PI/2 - ang;
    scene.add(roof);
  };

  // ============================================================
  // 4 PANS (toit en croupe)
  // ============================================================
  const draw4Pans = () => {
    // ============================================================
    // TOIT 4 PANS / CROUPE PARAMETRIQUE - charpente complete
    // S'adapte aux dimensions et a la couverture demandees.
    // (sections indicatives - calcul structurel = phase 2.B)
    // ============================================================
    const hf = (lg / 2) * Math.tan((pente * Math.PI) / 180); // hauteur faitage
    const yFait = Ht + hf;

    // Recul de croupe = profondeur horizontale du pan de croupe.
    // Par convention on prend la meme pente que les grands pans -> recul = lg/2.
    // Mais on borne pour garder un faitage visible meme si L est court.
    const reculCroupe = Math.min(lg / 2, (L - 0.6) / 2);
    const Lfait = Math.max(0.4, L - 2 * reculCroupe);
    const xFaitGauche = -Lfait / 2;
    const xFaitDroit = Lfait / 2;

    // ===== REGLES METIER ADAPTATIVES =====
    const couv = getCouverture(opts && opts.couverture);
    const couvColor = couv.couleur;
    const espChevron = couv.espChevron;
    const espLiteau = couv.espLiteau;
    const roof4Mat = makeRoofMaterial(couv, L, plLong);

    // Geometrie des grands pans
    const angLong = Math.atan(hf / (lg / 2));
    const plLong = (lg / 2) / Math.cos(angLong);   // longueur rampant grand pan
    const secChevron = plLong > 4.5 ? 0.10 : (plLong > 3 ? 0.09 : 0.08);

    // Nb de pannes par pan (un chevron ne franchit pas > ~2.2 m)
    const nbPannes = Math.max(1, Math.ceil(plLong / 2.2) - 1);

    // ===== MURS (4 cotes) =====
    [
      [L, Ht, 0.15, 0, Ht/2, lg/2],
      [L, Ht, 0.15, 0, Ht/2, -lg/2],
      [0.15, Ht, lg, -L/2, Ht/2, 0],
      [0.15, Ht, lg, L/2, Ht/2, 0]
    ].forEach(([sx, sy, sz, px, py, pz]) => addBox(sx, sy, sz, px, py, pz, wallMat));

setPiece("Sabliere");
    // ===== SABLIERES DE CHAINAGE (haut des 4 murs) =====
    const [sbB, sbH] = sec("Sabliere", 0.16, 0.16);
    addBox(L + 0.2, sbH, sbB, 0, Ht, lg/2, woodMat);
    addBox(L + 0.2, sbH, sbB, 0, Ht, -lg/2, woodMat);
    addBox(sbB, sbH, lg, -L/2, Ht, 0, woodMat);
    addBox(sbB, sbH, lg, L/2, Ht, 0, woodMat);

setPiece("Faitage");
    // ===== FAITAGE (central) =====
    addBox(Lfait, 0.15, 0.15, 0, yFait, 0, woodMat);

setPiece("Aretier");
    // ===== ARETIERS (faitage -> 4 coins) =====
    const coins = [
      [xFaitGauche, [-L/2, Ht, lg/2]],
      [xFaitGauche, [-L/2, Ht, -lg/2]],
      [xFaitDroit,  [L/2, Ht, lg/2]],
      [xFaitDroit,  [L/2, Ht, -lg/2]],
    ];
    coins.forEach(([xf, [cxp, cyp, czp]]) => {
      addBeam(cxp, cyp, czp, xf, yFait, 0, 0.12, woodMat);
    });

setPiece("Panne");
    // ===== PANNES sur les 2 grands pans (nb adaptatif) =====
    // Longueur de la panne diminue en montant (les pans se rapprochent du faitage)
    for (let i = 1; i <= nbPannes; i++) {
      const t = i / (nbPannes + 1);
      const yPanne = Ht + hf * t;
      const zPanne = (lg / 2) * (1 - t);
      const lenPanne = Lfait + (L - Lfait) * (1 - t);
      addBox(lenPanne, 0.12, 0.12, 0, yPanne, zPanne, woodMat);   // pan avant
      addBox(lenPanne, 0.12, 0.12, 0, yPanne, -zPanne, woodMat);  // pan arriere
    }

setPiece("Chevron");
    // ===== CHEVRONS sur les 2 grands pans (entre les aretiers) =====
    // Uniquement dans la zone du faitage (au-dela, ce sont les empannons)
    const nbChevGrandPan = Math.max(2, Math.floor(Lfait / espChevron));
    for (let i = 0; i <= nbChevGrandPan; i++) {
      const x = xFaitGauche + (i / nbChevGrandPan) * Lfait;
      // pan avant (Z+)
      addBeam(x, Ht, lg/2, x, yFait, 0, secChevron, woodMat);
      // pan arriere (Z-)
      addBeam(x, Ht, -lg/2, x, yFait, 0, secChevron, woodMat);
    }

setPiece("Empannon");
    // ===== EMPANNONS (chevrons courts s'appuyant sur les aretiers) =====
    // Signature de la croupe : sur chaque pan, des chevrons de longueur
    // decroissante qui butent sur l'aretier au lieu d'atteindre le faitage.
    const empannonsParCote = Math.max(2, Math.floor(reculCroupe / espChevron));

    // Helper local : projette un point du bas de pan vers l'aretier correspondant
    const drawEmpannonsGrandPan = (signZ) => {
      // Cote gauche (vers aretier gauche) et droit (vers aretier droit)
      [[-1, xFaitGauche, -L/2], [1, xFaitDroit, L/2]].forEach(([signX, xf, xCoin]) => {
        for (let i = 1; i <= empannonsParCote; i++) {
          const f = i / (empannonsParCote + 1);
          // point bas : sur la sabliere, entre le coin et le debut du faitage
          const xb = xCoin + (xf - xCoin) * f;
          const zb = signZ * (lg/2);
          // point haut : sur l'aretier, a la meme fraction
          const xh = xCoin + (xf - xCoin) * f;
          const yh = Ht + hf * f;
          const zh = signZ * (lg/2) * (1 - f);
          addBeam(xb, Ht, zb, xh, yh, zh, secChevron * 0.9, woodMat);
        }
      });
    };
    drawEmpannonsGrandPan(1);   // grand pan avant
    drawEmpannonsGrandPan(-1);  // grand pan arriere

setPiece("Empannon de croupe");
    // ===== EMPANNONS DE CROUPE (sur les 2 triangles de bout) =====
    const drawEmpannonsCroupe = (signX) => {
      const xCoinAv = signX * (L/2);
      const xf = signX * (Lfait/2);
      const nbEmp = Math.max(2, Math.floor((lg/2) / espChevron));
      for (let i = 1; i <= nbEmp; i++) {
        const f = i / (nbEmp + 1);
        // point bas sur la sabliere de pignon (varie en Z)
        const zb = -lg/2 + f * lg;
        const xb = signX * (L/2);
        // point haut : sur l'aretier le plus proche
        // aretier avant si zb>0, arriere si zb<0
        const signZ = zb >= 0 ? 1 : -1;
        const fAr = 1 - Math.abs(zb) / (lg/2);  // fraction le long de l'aretier
        const xh = xCoinAv + (xf - xCoinAv) * fAr;
        const yh = Ht + hf * fAr;
        const zh = signZ * (lg/2) * (1 - fAr);
        addBeam(xb, Ht, zb, xh, yh, zh, secChevron * 0.85, woodMat);
      }
    };
    drawEmpannonsCroupe(-1);  // croupe gauche
    drawEmpannonsCroupe(1);   // croupe droite

    // ===== COUVERTURE 4 PANS (semi-transparente) =====
    // Grand pan avant
    const panAvGeo = new THREE.BufferGeometry();
    panAvGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array([
      -L/2, Ht, lg/2,   L/2, Ht, lg/2,   xFaitDroit, yFait, 0,
      -L/2, Ht, lg/2,   xFaitDroit, yFait, 0,   xFaitGauche, yFait, 0,
    ]), 3));
    panAvGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(panAvGeo, roof4Mat));

    // Grand pan arriere
    const panArGeo = new THREE.BufferGeometry();
    panArGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array([
      -L/2, Ht, -lg/2,   xFaitGauche, yFait, 0,   xFaitDroit, yFait, 0,
      -L/2, Ht, -lg/2,   xFaitDroit, yFait, 0,   L/2, Ht, -lg/2,
    ]), 3));
    panArGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(panArGeo, roof4Mat));

    // Croupe gauche
    const croupeGGeo = new THREE.BufferGeometry();
    croupeGGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array([
      -L/2, Ht, -lg/2,   -L/2, Ht, lg/2,   xFaitGauche, yFait, 0,
    ]), 3));
    croupeGGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(croupeGGeo, roof4Mat));

    // Croupe droite
    const croupeDGeo = new THREE.BufferGeometry();
    croupeDGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array([
      L/2, Ht, -lg/2,   xFaitDroit, yFait, 0,   L/2, Ht, lg/2,
    ]), 3));
    croupeDGeo.computeVertexNormals();
    scene.add(new THREE.Mesh(croupeDGeo, roof4Mat));
  };

  // ============================================================
  // SWITCH SELON TYPE PROJET
  // ============================================================
  if (typeProjet === "carport") {
    drawCarport();
  } else if (typeProjet === "monopente") {
    drawMonopente();
  } else if (typeProjet === "hangar") {
    drawHangar();
  } else if (typeProjet === "appentis") {
    drawAppentis();
  } else if (typeProjet === "4_pans") {
    draw4Pans();
  } else {
    drawCharpenteTrad();
  }

  // Retourne le centre Y pour la camera
  let yCentre;
  if (typeProjet === "carport" || typeProjet === "monopente" || typeProjet === "appentis") {
    yCentre = Ht + (lg * Math.tan((pente * Math.PI) / 180)) / 2;
  } else if (typeProjet === "hangar") {
    yCentre = Ht * 0.7 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
  } else {
    // charpente_trad ET 4_pans
    yCentre = Ht/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
  }

  return { yCentre, metre, densiteBois, essence };
}
import { useAuth } from "./src/hooks/useAuth.js";
import Login from "./src/components/Login.jsx";
import { signOut } from "./src/lib/auth.js";
import { supabase } from "./src/lib/supabase.js";
import { useLicense } from "./src/hooks/useLicense.js";
import ActivateLicense from "./src/components/ActivateLicense.jsx";
import SubscriptionBanner from "./src/components/SubscriptionBanner.jsx";
import UserMenu from "./src/components/UserMenu.jsx";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

const T = {
bg: "#08090c", surface: "#0f1117", card: "#13161f", border: "#1e2231",
accent: "#f0c040", accentLo: "#f0c04018", text: "#e8eaf2", muted: "#545870",
dim: "#2a2e40", ok: "#3ecf8e", blue: "#60a5fa", red: "#ef4444",
purple: "#a78bfa", orange: "#f97316",
};

// ================================================================
// CAPTURE 3D - Genere 3 vues PNG en base64 pour le PDF
// ================================================================
function capture3DViews(view3DParams) {
  const W = 800;
  const H = 600;

  // Renderer offscreen avec fond transparent
  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    preserveDrawingBuffer: true
  });
  renderer.setSize(W, H);
  renderer.setClearColor(0xffffff, 0); // transparent

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, W / H, 0.1, 200);

  // Lumieres
  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const sun = new THREE.DirectionalLight(0xfff8e7, 1.2);
  sun.position.set(10, 20, 10);
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0xc4d4e8, 0.4);
  fill.position.set(-10, 10, -5);
  scene.add(fill);

  // Params
  const L = view3DParams.longueur || 8;
  const lg = view3DParams.largeur || 6;
  const Ht = view3DParams.hauteur || 3;
  const pente = view3DParams.pente || 35;
  const typeProjet = view3DParams.type_projet || "charpente_trad";

  // Construction de la scene via fonction commune
  // Couleurs adaptees pour le PDF (plus contrastees sur fond blanc)
  const buildResult = buildScene3D(scene, view3DParams, {
    woodColor: 0xa8743a,
    roofColor: 0x6b4a3f,
    wallColor: 0xd8d2c0,
    wallOpacity: 0.25,
    couverture: view3DParams.couverture
  });
  const yCentre = buildResult.yCentre;

  // Pas de sol (sinon ca pollue les vues sur fond blanc)

  // Distance camera proportionnelle a la taille
  const maxDim = Math.max(L, lg, Ht * 2);
  const dist = maxDim * 1.8;

  // ============ CAPTURE 3 VUES ============
  const views = {};

  // 1. FACE (regard depuis Z positif vers Z negatif)
  camera.position.set(0, yCentre, dist);
  camera.lookAt(0, yCentre, 0);
  renderer.render(scene, camera);
  views.face = renderer.domElement.toDataURL("image/png");

  // 2. COTE (regard depuis X positif vers X negatif)
  camera.position.set(dist, yCentre, 0);
  camera.lookAt(0, yCentre, 0);
  renderer.render(scene, camera);
  views.cote = renderer.domElement.toDataURL("image/png");

  // 3. PERSPECTIVE (3/4 classique)
  camera.position.set(dist * 0.7, yCentre + dist * 0.4, dist * 0.7);
  camera.lookAt(0, yCentre, 0);
  renderer.render(scene, camera);
  views.perspective = renderer.domElement.toDataURL("image/png");

  // Nettoyage
  renderer.dispose();

  return views;
}

// ================================================================
// GENERATEUR PDF PRO
// ================================================================
function generatePDF(result, params, zoneInfo, nomProjet, view3DParams) {
  const doc = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4"
  });

  const pageW = 210; // largeur A4 mm
  const pageH = 297; // hauteur A4 mm
  const margin = 15;
  let y = 0; // position verticale courante

  // Couleurs
  const C_OR = [240, 192, 64];        // or DEVIA
  const C_NOIR = [25, 28, 38];        // noir profond
  const C_TEXTE = [44, 44, 44];       // texte principal
  const C_GRIS = [120, 120, 130];     // gris secondaire
  const C_GRIS_LIGHT = [220, 220, 225]; // gris clair (separateurs)

  // ============ EN-TETE BANDEAU NOIR ============
  doc.setFillColor(...C_NOIR);
  doc.rect(0, 0, pageW, 45, "F");

  // Logo DEVIA (texte stylise)
  doc.setTextColor(...C_OR);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  doc.text("DEVIA", margin, 18);
  doc.setFontSize(8);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(180, 180, 190);
  doc.text("Devis charpente IA", margin, 23);

  // Bloc droit : numero devis + date
  const numDevis = "DEV-" + new Date().getFullYear() + "-" + String(Date.now()).slice(-4);
  const dateDevis = new Date().toLocaleDateString("fr-FR");
  const dateValid = new Date(Date.now() + 30 * 24 * 3600 * 1000).toLocaleDateString("fr-FR");

  doc.setTextColor(255, 255, 255);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.text("DEVIS " + numDevis, pageW - margin, 14, { align: "right" });
  doc.setFontSize(8);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(200, 200, 210);
  doc.text("Date : " + dateDevis, pageW - margin, 22, { align: "right" });
  doc.text("Valide jusqu'au : " + dateValid, pageW - margin, 28, { align: "right" });

  // Ligne or sous bandeau
  doc.setDrawColor(...C_OR);
  doc.setLineWidth(0.8);
  doc.line(0, 45, pageW, 45);

  y = 55;

  // ============ INFOS ENTREPRISE (gauche) + CLIENT (droite) ============
  doc.setTextColor(...C_GRIS);
  doc.setFontSize(7);
  doc.setFont("helvetica", "bold");
  doc.text("ENTREPRISE", margin, y);
  doc.text("CLIENT / PROJET", pageW / 2 + 5, y);

  doc.setLineWidth(0.3);
  doc.setDrawColor(...C_OR);
  doc.line(margin, y + 1.5, margin + 22, y + 1.5);
  doc.line(pageW / 2 + 5, y + 1.5, pageW / 2 + 5 + 30, y + 1.5);

  y += 8;
  doc.setTextColor(...C_TEXTE);
  doc.setFontSize(10);
  doc.setFont("helvetica", "bold");
  doc.text(params.entreprise || "Non renseigne", margin, y);

  doc.setFontSize(9);
  doc.setFont("helvetica", "bold");
  const projetDesc = result.projet && result.projet.description ? result.projet.description : (nomProjet || "Devis charpente");
  const projetLines = doc.splitTextToSize(projetDesc, 80);
  doc.text(projetLines, pageW / 2 + 5, y);

  y += 6;
  doc.setFontSize(8);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...C_GRIS);

  if (params.adresse) {
    const adrLines = doc.splitTextToSize(params.adresse, 80);
    doc.text(adrLines, margin, y);
    y += adrLines.length * 4;
  }
  if (params.siret) {
    doc.text("SIRET : " + params.siret, margin, y);
    y += 4;
  }

  // Bloc client : infos projet
  let yClient = y - (params.siret ? 4 : 0) - (params.adresse ? 4 : 0);
  doc.setFontSize(8);
  doc.setTextColor(...C_GRIS);
  if (result.projet) {
    if (result.projet.commune) {
      doc.text("Chantier : " + result.projet.commune, pageW / 2 + 5, yClient);
      yClient += 4;
    }
    if (result.projet.longueur && result.projet.largeur) {
      doc.text("Dimensions : " + result.projet.longueur + " x " + result.projet.largeur + " m", pageW / 2 + 5, yClient);
      yClient += 4;
    }
    if (result.projet.surface) {
      doc.text("Surface : " + result.projet.surface + " m²", pageW / 2 + 5, yClient);
      yClient += 4;
    }
    if (result.projet.pente) {
      doc.text("Pente : " + result.projet.pente + "°", pageW / 2 + 5, yClient);
      yClient += 4;
    }
  }

  y = Math.max(y, yClient) + 8;

  // ============ VUES 3D ============
  if (view3DParams) {
    try {
      const views = capture3DViews(view3DParams);

      // Verifier qu'on a la place sur la page
      if (y > pageH - 90) { doc.addPage(); y = 20; }

      // Titre section
      doc.setTextColor(...C_GRIS);
      doc.setFontSize(7);
      doc.setFont("helvetica", "bold");
      doc.text("VUES DU PROJET", margin, y);
      doc.setLineWidth(0.3);
      doc.setDrawColor(...C_OR);
      doc.line(margin, y + 1.5, margin + 25, y + 1.5);

      y += 6;

      // 3 vues alignees horizontalement
      const viewW = (pageW - 2 * margin - 8) / 3; // 3 colonnes + 2 gaps de 4
      const viewH = viewW * 0.65; // ratio 800x600 -> 4:3

      // FACE
      try {
        doc.addImage(views.face, "PNG", margin, y, viewW, viewH);
      } catch(e) { console.warn("Erreur vue face :", e); }

      // COTE
      try {
        doc.addImage(views.cote, "PNG", margin + viewW + 4, y, viewW, viewH);
      } catch(e) { console.warn("Erreur vue cote :", e); }

      // PERSPECTIVE
      try {
        doc.addImage(views.perspective, "PNG", margin + 2 * (viewW + 4), y, viewW, viewH);
      } catch(e) { console.warn("Erreur vue perspective :", e); }

      // Labels sous chaque vue
      y += viewH + 4;
      doc.setFontSize(7);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(...C_GRIS);
      doc.text("Vue de face", margin + viewW/2, y, { align: "center" });
      doc.text("Vue de cote", margin + viewW + 4 + viewW/2, y, { align: "center" });
      doc.text("Perspective", margin + 2 * (viewW + 4) + viewW/2, y, { align: "center" });

      y += 8;
    } catch (e) {
      console.error("Erreur capture 3D :", e);
    }
  }

  // ============ TABLEAU DES POSTES ============
  const postes = result.postes || [];
  const tableBody = postes.map(p => [
    p.designation || "",
    p.quantite ? String(p.quantite) : "—",
    p.unite || "—",
    p.prixUnitaireHT ? Number(p.prixUnitaireHT).toFixed(2) + " EUR" : "—",
    p.totalHT ? Number(p.totalHT).toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " EUR" : "—"
  ]);

  autoTable(doc, {
    startY: y,
    head: [["Designation", "Qte", "Unite", "PU HT", "Total HT"]],
    body: tableBody,
    theme: "striped",
    styles: {
      font: "helvetica",
      fontSize: 9,
      cellPadding: 3,
      textColor: C_TEXTE,
      lineColor: C_GRIS_LIGHT,
      lineWidth: 0.1
    },
    headStyles: {
      fillColor: C_NOIR,
      textColor: C_OR,
      fontStyle: "bold",
      fontSize: 9,
      cellPadding: 4
    },
    alternateRowStyles: {
      fillColor: [248, 248, 250]
    },
    columnStyles: {
      0: { cellWidth: 80 },
      1: { cellWidth: 18, halign: "right" },
      2: { cellWidth: 18, halign: "center" },
      3: { cellWidth: 30, halign: "right" },
      4: { cellWidth: 34, halign: "right", fontStyle: "bold" }
    },
    margin: { left: margin, right: margin }
  });

  y = doc.lastAutoTable.finalY + 6;

  // ============ ESTIMATION TEMPS (si presente) ============
  if (result.temps_fabrication_h !== undefined || result.temps_pose_h !== undefined) {
    const fab = Number(result.temps_fabrication_h) || 0;
    const pose = Number(result.temps_pose_h) || 0;
    const totalH = fab + pose;
    const jours = Math.ceil(totalH / 8);

    // Verifier si on a la place sur la page
    if (y > pageH - 60) { doc.addPage(); y = 20; }

    doc.setFillColor(248, 248, 250);
    doc.setDrawColor(...C_GRIS_LIGHT);
    doc.setLineWidth(0.2);
    doc.roundedRect(margin, y, pageW - 2 * margin, 22, 2, 2, "FD");

    doc.setTextColor(...C_TEXTE);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9);
    doc.text("Estimation temps", margin + 4, y + 6);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(...C_GRIS);
    doc.text("Fabrication atelier : ", margin + 4, y + 13);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...C_TEXTE);
    doc.text(fab + " h", margin + 38, y + 13);

    doc.setFont("helvetica", "normal");
    doc.setTextColor(...C_GRIS);
    doc.text("Pose chantier : ", margin + 60, y + 13);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...C_TEXTE);
    doc.text(pose + " h", margin + 88, y + 13);

    doc.setFont("helvetica", "normal");
    doc.setTextColor(...C_GRIS);
    doc.text("Total : ", margin + 110, y + 13);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...C_OR);
    doc.text(totalH + " h (" + jours + " jour" + (jours > 1 ? "s" : "") + ")", margin + 122, y + 13);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(7);
    doc.setTextColor(...C_GRIS);
    doc.text("Estimation basee sur ratios standards charpente. Sur 8h/jour.", margin + 4, y + 19);

    y += 28;
  }

  // ============ TOTAUX (bloc droit aligne) ============
  if (y > pageH - 50) { doc.addPage(); y = 20; }

  const totaux = result.totaux || {};
  const xTotaux = pageW - margin - 70;

  doc.setDrawColor(...C_GRIS_LIGHT);
  doc.setLineWidth(0.2);
  doc.line(xTotaux, y, pageW - margin, y);

  y += 6;
  doc.setTextColor(...C_TEXTE);
  doc.setFontSize(10);
  doc.setFont("helvetica", "normal");
  doc.text("Total HT", xTotaux, y);
  doc.setFont("helvetica", "bold");
  const totalHTstr = (totaux.totalHT || 0).toLocaleString("fr-FR", { minimumFractionDigits: 2 }) + " EUR";
  doc.text(totalHTstr, pageW - margin, y, { align: "right" });

  y += 6;
  doc.setFont("helvetica", "normal");
  doc.text("TVA " + (params.tva || 20) + "%", xTotaux, y);
  doc.setFont("helvetica", "bold");
  const tvaStr = (totaux.tva || 0).toLocaleString("fr-FR", { minimumFractionDigits: 2 }) + " EUR";
  doc.text(tvaStr, pageW - margin, y, { align: "right" });

  y += 4;
  doc.setDrawColor(...C_OR);
  doc.setLineWidth(0.5);
  doc.line(xTotaux, y, pageW - margin, y);

  y += 8;
  doc.setFillColor(...C_OR);
  doc.rect(xTotaux, y - 5, pageW - margin - xTotaux, 9, "F");
  doc.setTextColor(...C_NOIR);
  doc.setFontSize(11);
  doc.setFont("helvetica", "bold");
  doc.text("TOTAL TTC", xTotaux + 2, y + 1);
  const totalTTCstr = (totaux.totalTTC || 0).toLocaleString("fr-FR", { minimumFractionDigits: 2 }) + " EUR";
  doc.text(totalTTCstr, pageW - margin - 2, y + 1, { align: "right" });

  y += 12;

  // ============ NOTES ============
  if (result.notes && result.notes.length > 0) {
    if (y > pageH - 40) { doc.addPage(); y = 20; }

    doc.setTextColor(...C_GRIS);
    doc.setFontSize(7);
    doc.setFont("helvetica", "bold");
    doc.text("NOTES", margin, y);
    doc.setLineWidth(0.3);
    doc.setDrawColor(...C_OR);
    doc.line(margin, y + 1.5, margin + 12, y + 1.5);

    y += 7;
    doc.setFontSize(9);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...C_TEXTE);
    result.notes.forEach(note => {
      if (y > pageH - 25) { doc.addPage(); y = 20; }
      const lines = doc.splitTextToSize("- " + note, pageW - 2 * margin);
      doc.text(lines, margin, y);
      y += lines.length * 4 + 1;
    });
  }

  // ============ PIED DE PAGE (sur chaque page) ============
  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setDrawColor(...C_GRIS_LIGHT);
    doc.setLineWidth(0.2);
    doc.line(margin, pageH - 15, pageW - margin, pageH - 15);

    doc.setFontSize(7);
    doc.setTextColor(...C_GRIS);
    doc.setFont("helvetica", "normal");
    doc.text("Genere par DEVIA - " + dateDevis, margin, pageH - 10);
    doc.text(params.mentions || "Devis valable 30 jours", pageW / 2, pageH - 10, { align: "center" });
    doc.text("Page " + i + "/" + totalPages, pageW - margin, pageH - 10, { align: "right" });
  }

  // ============ TELECHARGER ============
  const fileName = "Devis_" + (params.entreprise || "DEVIA").replace(/\s+/g, "_") + "_" + numDevis + ".pdf";
  doc.save(fileName);
}

const ZONES_DB = {
"paris": { neige: "A1", vent: "2", sismique: "1" },
"lyon": { neige: "A2", vent: "2", sismique: "1" },
"marseille": { neige: "A1", vent: "3", sismique: "2" },
"bordeaux": { neige: "A1", vent: "2", sismique: "2" },
"toulouse": { neige: "A2", vent: "2", sismique: "3" },
"nantes": { neige: "A1", vent: "2", sismique: "1" },
"strasbourg": { neige: "B1", vent: "1", sismique: "3" },
"lille": { neige: "A1", vent: "3", sismique: "1" },
"nice": { neige: "A2", vent: "3", sismique: "3" },
"grenoble": { neige: "B2", vent: "1", sismique: "4" },
"rennes": { neige: "A1", vent: "2", sismique: "1" },
"rouen": { neige: "A1", vent: "3", sismique: "1" },
"dijon": { neige: "B1", vent: "1", sismique: "2" },
"nancy": { neige: "B1", vent: "1", sismique: "2" },
"reims": { neige: "A2", vent: "2", sismique: "1" },
"toulon": { neige: "A1", vent: "3", sismique: "2" },
"brest": { neige: "A1", vent: "4", sismique: "1" },
"montpellier": { neige: "A1", vent: "3", sismique: "3" },
"bayonne": { neige: "A3", vent: "2", sismique: "3" },
"pau": { neige: "B1", vent: "2", sismique: "4" },
"chamonix": { neige: "C1", vent: "2", sismique: "4" },
"annecy": { neige: "C1", vent: "2", sismique: "4" },
"bruxelles": { neige: "A1", vent: "2", sismique: "0" },
"lausanne": { neige: "C1", vent: "2", sismique: "2" },
"geneve": { neige: "B2", vent: "2", sismique: "2" },
"luxembourg": { neige: "A2", vent: "2", sismique: "1" },
};

// ====== Palettes Theme (Mode Clair / Sombre) ======
// Placees AU DEBUT du fichier pour etre disponibles partout
const themes = {
  dark: {
    bgRoot: "radial-gradient(ellipse at top, rgba(30, 35, 50, 0.4) 0%, #08090c 50%), #08090c",
    bgPage: "transparent",
    headerBg: "rgba(8, 9, 12, 0.7)",
    headerBorder: "rgba(255, 255, 255, 0.05)",
    cardBg: "rgba(22, 25, 35, 0.55)",
    cardBorder: "rgba(255, 255, 255, 0.06)",
    cardShadow: "0 1px 0 rgba(255,255,255,0.03) inset, 0 8px 32px rgba(0,0,0,0.25)",
    inputBg: "rgba(255, 255, 255, 0.03)",
    inputBorder: "rgba(255, 255, 255, 0.08)",
    btnSecBg: "rgba(255, 255, 255, 0.04)",
    btnSecBorder: "rgba(255, 255, 255, 0.08)",
    navBg: "rgba(255,255,255,0.03)",
    navBorder: "rgba(255,255,255,0.06)",
    navTabActive: "rgba(255,255,255,0.08)",
    navTabActiveText: "#ffffff",
    navTabText: "#7a7d92",
    navTabHover: "#d0d2dc",
    textPrimary: "#e8eaf2",
    textSecondary: "#9ca0b8",
    textMuted: "#7a7d92",
    textFaint: "#545870",
    gold: "#f0c040",
    goldDark: "#e0a020",
  },
  light: {
    bgRoot: "radial-gradient(ellipse at top, rgba(240, 192, 64, 0.05) 0%, #f5f6fa 50%), #f5f6fa",
    bgPage: "transparent",
    headerBg: "rgba(255, 255, 255, 0.85)",
    headerBorder: "rgba(0, 0, 0, 0.06)",
    cardBg: "rgba(255, 255, 255, 0.7)",
    cardBorder: "rgba(0, 0, 0, 0.06)",
    cardShadow: "0 1px 0 rgba(255,255,255,0.8) inset, 0 8px 24px rgba(0,0,0,0.04)",
    inputBg: "rgba(255, 255, 255, 0.8)",
    inputBorder: "rgba(0, 0, 0, 0.08)",
    btnSecBg: "rgba(0, 0, 0, 0.03)",
    btnSecBorder: "rgba(0, 0, 0, 0.08)",
    navBg: "rgba(255,255,255,0.7)",
    navBorder: "rgba(0,0,0,0.06)",
    navTabActive: "#1a1d2a",
    navTabActiveText: "#ffffff",
    navTabText: "#5a5e72",
    navTabHover: "#1a1d2a",
    textPrimary: "#1a1d2a",
    textSecondary: "#5a5e72",
    textMuted: "#8a8d9c",
    textFaint: "#a8abb8",
    gold: "#b8860b",
    goldDark: "#9c7000",
  }
};
// ====================================================

function getZone(commune, altitude) {
const key = commune.toLowerCase().trim();
let zone = null;
for (const k of Object.keys(ZONES_DB)) {
if (key.includes(k) || k.includes(key)) { zone = ZONES_DB[k]; break; }
}
if (!zone) zone = { neige: "A2", vent: "2", sismique: "1" };
const nl = zone.neige.match(/([A-D])(\d?)/);
const nL = nl ? nl[1] : "A";
const nC = nl ? parseInt(nl[2] || "1") : 1;
const altNum = parseInt(altitude) || 200;
const neigeBase = { A: { 1: 0.45, 2: 0.45, 3: 0.55 }, B: { 1: 0.65, 2: 0.90 }, C: { 1: 1.40, 2: 1.70 }, D: { 0: 2.30 } };
let sk = (neigeBase[nL] || {})[nC] || 0.65;
if (altNum > 200) sk = sk * (1 + ((altNum - 200) / 800) * 1.5);
const vb0 = { "1": 22, "2": 25, "3": 28, "4": 32 }[zone.vent] || 25;
const qb = (1.25 * vb0 * vb0) / 2000;
const ag = { "0": 0, "1": 0.07, "2": 0.10, "3": 0.15, "4": 0.20 }[zone.sismique] || 0.07;
return { ...zone, sk: Math.round(sk * 100) / 100, qb: Math.round(qb * 100) / 100, ag };
}

// ============================================================
// ============================================================
// GENERATEUR IFC (ISO-10303-21 / IFC4) depuis le metre 3D
// ============================================================
// Note conventions axes : Three.js Y=haut -> IFC Z=haut. Conversion (x,y,z)->(x,z,y).
function genererIFC(metre, params) {
  const piecesBois = (metre || []).filter((p) => p.pos); // seulement pieces avec position
  let id = 0;
  const nextId = () => ++id;
  const lines = [];
  const E = (n, s) => { lines.push("#" + n + "=" + s); }; // ecrit une entite

  // --- En-tete STEP ---
  const now = new Date();
  const stamp = now.toISOString().slice(0, 19);
  const header =
"ISO-10303-21;\n" +
"HEADER;\n" +
"FILE_DESCRIPTION(('DEVIA charpente export'),'2;1');\n" +
"FILE_NAME('devia.ifc','" + stamp + "',(''),(''),'DEVIA','DEVIA','');\n" +
"FILE_SCHEMA(('IFC4'));\n" +
"ENDSEC;\n" +
"DATA;\n";

  // --- Contexte de base ---
  const dimExp = nextId(); E(dimExp, "IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);");
  const origin = nextId(); E(origin, "IFCCARTESIANPOINT((0.,0.,0.));");
  const dirZ = nextId(); E(dirZ, "IFCDIRECTION((0.,0.,1.));");
  const dirX = nextId(); E(dirX, "IFCDIRECTION((1.,0.,0.));");
  const axisPlacement = nextId(); E(axisPlacement, "IFCAXIS2PLACEMENT3D(#" + origin + ",#" + dirZ + ",#" + dirX + ");");
  const worldCoord = nextId(); E(worldCoord, "IFCAXIS2PLACEMENT3D(#" + origin + ",$,$);");

  const lenUnit = nextId(); E(lenUnit, "IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);");
  const areaUnit = nextId(); E(areaUnit, "IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);");
  const volUnit = nextId(); E(volUnit, "IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);");
  const angUnit = nextId(); E(angUnit, "IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);");
  const unitAssign = nextId(); E(unitAssign, "IFCUNITASSIGNMENT((#" + lenUnit + ",#" + areaUnit + ",#" + volUnit + ",#" + angUnit + "));");

  const geomCtx = nextId(); E(geomCtx, "IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#" + axisPlacement + ",$);");

  const guid = () => {
    const c = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$";
    let s = ""; for (let i = 0; i < 22; i++) s += c[Math.floor(Math.random() * 64)];
    return s;
  };

  // --- Hierarchie spatiale ---
  const project = nextId();
  const site = nextId();
  const building = nextId();
  const storey = nextId();
  E(project, "IFCPROJECT('" + guid() + "',$,'DEVIA Charpente',$,$,$,$,(#" + geomCtx + "),#" + unitAssign + ");");
  const sitePlc = nextId(); E(sitePlc, "IFCLOCALPLACEMENT($,#" + axisPlacement + ");");
  E(site, "IFCSITE('" + guid() + "',$,'Terrain',$,$,#" + sitePlc + ",$,$,.ELEMENT.,$,$,$,$,$);");
  const bldgPlc = nextId(); E(bldgPlc, "IFCLOCALPLACEMENT(#" + sitePlc + ",#" + axisPlacement + ");");
  E(building, "IFCBUILDING('" + guid() + "',$,'Batiment',$,$,#" + bldgPlc + ",$,$,.ELEMENT.,$,$,$);");
  const storeyPlc = nextId(); E(storeyPlc, "IFCLOCALPLACEMENT(#" + bldgPlc + ",#" + axisPlacement + ");");
  E(storey, "IFCBUILDINGSTOREY('" + guid() + "',$,'Niveau 0',$,$,#" + storeyPlc + ",$,$,.ELEMENT.,0.);");

  // Relations d'agregation
  const relAggProj = nextId(); E(relAggProj, "IFCRELAGGREGATES('" + guid() + "',$,$,$,#" + project + ",(#" + site + "));");
  const relAggSite = nextId(); E(relAggSite, "IFCRELAGGREGATES('" + guid() + "',$,$,$,#" + site + ",(#" + building + "));");
  const relAggBldg = nextId(); E(relAggBldg, "IFCRELAGGREGATES('" + guid() + "',$,$,$,#" + building + ",(#" + storey + "));");

  // --- Une piece -> un IfcMember ---
  const memberIds = [];
  piecesBois.forEach((p) => {
    // --- Dimensions Three.js d'origine ---
    const sx = Math.abs(p.dimsBrutes[0]);
    const sy = Math.abs(p.dimsBrutes[1]);
    const sz = Math.abs(p.dimsBrutes[2]);

    // helper : convertit un vecteur Three (x,y,z) -> IFC (x, z, y) et normalise
    const toIfcDir = (vx, vy, vz) => {
      // Three Y(haut) -> IFC Z ; Three Z -> IFC Y
      let ix = vx, iy = vz, iz = vy;
      const n = Math.sqrt(ix*ix + iy*iy + iz*iz) || 1;
      ix /= n; iy /= n; iz /= n;
      return "(" + ix.toFixed(6) + "," + iy.toFixed(6) + "," + iz.toFixed(6) + ")";
    };

    // --- helper : rotation d'un vecteur par angles d'Euler Three (ordre XYZ) ---
    const rotEuler = (v, rx, ry, rz) => {
      let [x, y, z] = v;
      // rotation X
      let cy = Math.cos(rx), sy2 = Math.sin(rx);
      [y, z] = [y * cy - z * sy2, y * sy2 + z * cy];
      // rotation Y
      let cyy = Math.cos(ry), syy = Math.sin(ry);
      [x, z] = [x * cyy + z * syy, -x * syy + z * cyy];
      // rotation Z
      let cz = Math.cos(rz), sz2 = Math.sin(rz);
      [x, y] = [x * cz - y * sz2, x * sz2 + y * cz];
      return [x, y, z];
    };

    // --- Determiner l'axe long (longueur) et la section (w,h), + direction longue en repere THREE ---
    let L, w, h;
    let longVecThree; // direction de la longueur dans le repere Three
    if (p.quat) {
      // Piece issue de addBeam : longueur selon Z LOCAL oriente par le quaternion (applique a (0,0,1))
      const [qx, qy, qz, qw] = p.quat;
      const vx = 2 * (qx*qz + qw*qy);
      const vy = 2 * (qy*qz - qw*qx);
      const vz = 1 - 2 * (qx*qx + qy*qy);
      longVecThree = [vx, vy, vz];
      const dimsSorted = [sx, sy, sz].sort((a,b) => b - a);
      L = dimsSorted[0]; w = dimsSorted[1]; h = dimsSorted[2];
    } else {
      // Piece issue de addBox : axe long = plus grande dimension
      let axeLong = 0, Lmax = sx;
      if (sy > Lmax) { axeLong = 1; Lmax = sy; }
      if (sz > Lmax) { axeLong = 2; Lmax = sz; }
      L = Lmax;
      let baseVec;
      if (axeLong === 0) { w = sy; h = sz; baseVec = [1,0,0]; }
      else if (axeLong === 1) { w = sx; h = sz; baseVec = [0,1,0]; }
      else { w = sx; h = sy; baseVec = [0,0,1]; }
      // appliquer la rotation Euler si presente (ex chevrons : [ang,0,0])
      if (p.rot) {
        longVecThree = rotEuler(baseVec, p.rot[0] || 0, p.rot[1] || 0, p.rot[2] || 0);
      } else {
        longVecThree = baseVec;
      }
    }

    // --- Position du centre, conversion Three(x,y,z) -> IFC(x,z,y) ---
    const px = p.pos[0], py = p.pos[2], pz = p.pos[1];

    // --- Axe Z local de la piece = direction de la longueur (en IFC) ---
    const axisZ = toIfcDir(longVecThree[0], longVecThree[1], longVecThree[2]);
    // axe X de reference : on choisit un vecteur non colineaire puis l'IFC orthogonalise
    // si la longueur est ~verticale en IFC, on prend X=(1,0,0), sinon Z_ifc=(0,0,1) comme ref
    let refX;
    // composante verticale IFC de l'axe long :
    const izComp = longVecThree[1]; // Three Y -> IFC Z
    if (Math.abs(izComp) > 0.9) { refX = "(1.,0.,0.)"; }
    else { refX = "(0.,0.,1.)"; }

    // profil rectangulaire centre
    const profCtrPt = nextId(); E(profCtrPt, "IFCCARTESIANPOINT((0.,0.));");
    const profDir = nextId(); E(profDir, "IFCDIRECTION((1.,0.));");
    const profPos = nextId(); E(profPos, "IFCAXIS2PLACEMENT2D(#" + profCtrPt + ",#" + profDir + ");");
    const prof = nextId(); E(prof, "IFCRECTANGLEPROFILEDEF(.AREA.,$,#" + profPos + "," + w.toFixed(4) + "," + h.toFixed(4) + ");");

    // placement de la piece : axe Z local = direction longue
    const ptPiece = nextId(); E(ptPiece, "IFCCARTESIANPOINT((" + px.toFixed(4) + "," + py.toFixed(4) + "," + pz.toFixed(4) + "));");
    const dirZpiece = nextId(); E(dirZpiece, "IFCDIRECTION(" + axisZ + ");");
    const dirXpiece = nextId(); E(dirXpiece, "IFCDIRECTION(" + refX + ");");
    const axPiece = nextId(); E(axPiece, "IFCAXIS2PLACEMENT3D(#" + ptPiece + ",#" + dirZpiece + ",#" + dirXpiece + ");");
    const plcPiece = nextId(); E(plcPiece, "IFCLOCALPLACEMENT(#" + storeyPlc + ",#" + axPiece + ");");

    // extrusion : dans le repere local, on extrude selon Z local, centree (-L/2)
    const extrPt = nextId(); E(extrPt, "IFCCARTESIANPOINT((0.,0.," + (-L/2).toFixed(4) + "));");
    const extrAx = nextId(); E(extrAx, "IFCAXIS2PLACEMENT3D(#" + extrPt + ",$,$);");
    const extrDir = nextId(); E(extrDir, "IFCDIRECTION((0.,0.,1.));");
    const solid = nextId(); E(solid, "IFCEXTRUDEDAREASOLID(#" + prof + ",#" + extrAx + ",#" + extrDir + "," + L.toFixed(4) + ");");

    const shapeRep = nextId(); E(shapeRep, "IFCSHAPEREPRESENTATION(#" + geomCtx + ",'Body','SweptSolid',(#" + solid + "));");
    const prodDef = nextId(); E(prodDef, "IFCPRODUCTDEFINITIONSHAPE($,$,(#" + shapeRep + "));");

    const member = nextId();
    E(member, "IFCMEMBER('" + guid() + "',$,'" + (p.nom || "Piece") + "',$,$,#" + plcPiece + ",#" + prodDef + ",$,$);");
    memberIds.push(member);
  });

  // Rattacher tous les membres au storey
  if (memberIds.length) {
    const relContain = nextId();
    E(relContain, "IFCRELCONTAINEDINSPATIALSTRUCTURE('" + guid() + "',$,$,$,(#" + memberIds.join(",#") + "),#" + storey + ");");
  }

  const footer = "ENDSEC;\nEND-ISO-10303-21;\n";
  return header + lines.join("\n") + "\n" + footer;
}


// AGREGATION DU METRE (regroupe par type de piece + totaux)
// ============================================================
function agregerMetre(metre, densiteBois) {
  if (!metre || metre.length === 0) return { groupes: [], totalVolume: 0, totalPoids: 0, nbPieces: 0 };
  const map = {};
  metre.forEach((p) => {
    // cle = nom + section (pour distinguer p.ex. chevrons de sections differentes)
    const secKey = p.section[0] + "x" + p.section[1];
    const key = p.nom + "|" + secKey;
    if (!map[key]) {
      map[key] = {
        nom: p.nom,
        section: p.section,        // [mm, mm]
        nombre: 0,
        longueurTotale: 0,         // m
        longueurUnitMax: 0,        // m (plus longue piece du groupe)
        volume: 0,                 // m3
      };
    }
    map[key].nombre += 1;
    map[key].longueurTotale += p.longueur;
    map[key].longueurUnitMax = Math.max(map[key].longueurUnitMax, p.longueur);
    map[key].volume += p.volume;
  });
  const groupes = Object.values(map).map((g) => ({
    ...g,
    longueurMoy: g.longueurTotale / g.nombre,
    poids: g.volume * densiteBois,   // kg
  })).sort((a, b) => b.volume - a.volume);
  const totalVolume = groupes.reduce((s, g) => s + g.volume, 0);
  const totalPoids = groupes.reduce((s, g) => s + g.poids, 0);
  const nbPieces = groupes.reduce((s, g) => s + g.nombre, 0);
  return { groupes, totalVolume, totalPoids, nbPieces };
}

// ============================================================
// PANNEAU TECHNIQUE (metre + entraxes + assemblages) sous la 3D
// ============================================================
// Assemblages recommandes par type de piece (regles TYPES, a valider)
const ASSEMBLAGES = {
  "Panne": "Posee sur arbaletriers/poteaux. Assemblage par entaille (about) + echantignole de calage. Fixation tire-fond ou equerre.",
  "Chevron": "Cloue/visse sur pannes et sabliere. Entaille a mi-bois sur sabliere possible. Echantignole sur panne intermediaire.",
  "Sabliere": "Scellee/chevillee sur arase du mur. Assemblage d'angle a mi-bois ou tenon-mortaise. Ancrage par scellement chimique.",
  "Poteau": "Pied : sabot metallique sur platine chevillee. Tete : tenon-mortaise ou ferrure sur sabliere/panne.",
  "Faitage": "Assemblage des arbaletriers en tete : tenon-mortaise ou moise. Liaison par boulons traversants.",
  "Aretier": "Piece maitresse de croupe. Assemblage en tete sur faitage/poincon. Empannons rapportes par entaille sur l'aretier.",
  "Empannon": "Chevron court entaille sur l'aretier (coupe biaise) cote bas + sur sabliere. Cloue/visse.",
  "Empannon de croupe": "Identique empannon, sur le pan de croupe. Coupe d'onglet contre l'aretier.",
  "Liteau": "Cloue/agrafe perpendiculairement sur les chevrons. Entraxe selon pureau de la couverture.",
  "Echantignole": "Petit taquet cloue sur la panne, cale le chevron a la bonne pente.",
  "Divers": "Assemblage selon piece (voir plan d'execution).",
};

function PanneauTechnique({ data, params, zoneInfo, sectionMode = "conseillee" }) {
  if (!data || !data.groupes || data.groupes.length === 0) {
    return null;
  }
  const card = { background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 12, padding: 16, marginTop: 12 };
  const stat = { flex: 1, minWidth: 120, background: "rgba(240,192,64,0.06)", border: "1px solid rgba(240,192,64,0.18)", borderRadius: 10, padding: "12px 14px" };
  const statVal = { fontSize: 22, fontWeight: 700, color: "#f0c040", fontVariantNumeric: "tabular-nums" };
  const statLbl = { fontSize: 11, color: "#7a7d92", marginTop: 2, textTransform: "uppercase", letterSpacing: "0.04em" };
  const th = { textAlign: "left", padding: "8px 10px", fontSize: 11, color: "#7a7d92", textTransform: "uppercase", letterSpacing: "0.03em", borderBottom: "1px solid rgba(255,255,255,0.08)" };
  const td = { padding: "9px 10px", fontSize: 13, color: "#d0d2dc", borderBottom: "1px solid rgba(255,255,255,0.04)", fontVariantNumeric: "tabular-nums" };

  const fmt = (n, d) => Number(n).toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d });

  return (
    <div>
      {/* Etiquettes / stats */}
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 12 }}>
        <div style={stat}><div style={statVal}>{fmt(data.totalVolume, 3)} m3</div><div style={statLbl}>Volume bois</div></div>
        <div style={stat}><div style={statVal}>{fmt(data.totalPoids, 0)} kg</div><div style={statLbl}>Poids estime</div></div>
        <div style={stat}><div style={statVal}>{data.nbPieces}</div><div style={statLbl}>Pieces</div></div>
        <div style={stat}><div style={statVal}>{data.groupes.length}</div><div style={statLbl}>Types differents</div></div>
      </div>

      {/* Tableau de metre */}
      <div style={card}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#e8eaf2", marginBottom: 10 }}>Metre detaille</div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Piece</th>
                <th style={th}>Section (mm)</th>
                <th style={{ ...th, textAlign: "right" }}>Nb</th>
                <th style={{ ...th, textAlign: "right" }}>Long. unit. (m)</th>
                <th style={{ ...th, textAlign: "right" }}>Long. tot. (m)</th>
                <th style={{ ...th, textAlign: "right" }}>Volume (m3)</th>
                <th style={{ ...th, textAlign: "right" }}>Poids (kg)</th>
                <th style={{ ...th, textAlign: "right" }}>Section EC5 (mini / conseillee)</th>
              </tr>
            </thead>
            <tbody>
              {data.groupes.map((g, i) => (
                <tr key={i}>
                  <td style={{ ...td, color: "#e8eaf2", fontWeight: 500 }}>{g.nom}</td>
                  <td style={td}>{g.section[0]} x {g.section[1]}</td>
                  <td style={{ ...td, textAlign: "right" }}>{g.nombre}</td>
                  <td style={{ ...td, textAlign: "right" }}>{fmt(g.longueurUnitMax, 2)}</td>
                  <td style={{ ...td, textAlign: "right" }}>{fmt(g.longueurTotale, 2)}</td>
                  <td style={{ ...td, textAlign: "right" }}>{fmt(g.volume, 3)}</td>
                  <td style={{ ...td, textAlign: "right", color: "#f0c040" }}>{fmt(g.poids, 0)}</td>
                  <td style={{ ...td, textAlign: "right", fontSize: 12 }}>{(() => {
                    const sk = zoneInfo ? zoneInfo.sk : 0.45;
                    const ch = ec5DescenteCharge(params.couverture || "tuile_terre", sk);
                    // --- Portee de calcul realiste selon le type de piece (plafond 8m) ---
                    // Pannes/sablieres : reposent sur les fermes -> portee = entre-axe fermes (~3.5m)
                    // Chevrons/fermes/arbaletriers : longueur reelle
                    const ENTRAXE_FERMES = 3.5; // m (cours : fermes tous les ~3.5m)
                    const PORTEE_MAX = 8;        // plafond securite
                    let porteeCalc;
                    if (g.nom === "Panne" || g.nom === "Panne faitiere" || g.nom === "Sabliere") {
                      porteeCalc = ENTRAXE_FERMES; // appuis sur chaque ferme
                    } else {
                      porteeCalc = g.longueurUnitMax; // chevrons, fermes, arbaletriers : longueur reelle
                    }
                    porteeCalc = Math.min(porteeCalc, PORTEE_MAX);
                    const charge = {
                      portee: porteeCalc,
                      entraxe: (g.nom === "Chevron" || g.nom === "Empannon" || g.nom === "Empannon de croupe") ? 0.6
                             : (g.nom === "Panne" || g.nom === "Panne faitiere") ? 1.5
                             : (g.nom === "Sabliere" || g.nom === "Aretier") ? 1.0
                             : 1.0,
                      G: ch.G, Q: ch.Q, S: ch.S,
                      classeService: 2, typeBatiment: "courant", dureeVariable: "court",
                    };
                    const dim = dimensionnerPiece(g.nom, charge);
                    if (!dim) return <span style={{ color: "#545870" }}>-</span>;
                    const miniSel = sectionMode === "mini";
                    return (
                      <span>
                        <span style={{ color: miniSel ? "#60a5fa" : "#7a7d92", fontWeight: miniSel ? 700 : 400 }}>{dim.mini.b}x{dim.mini.h} {dim.mini.classe}</span>
                        <span style={{ color: "#545870" }}> / </span>
                        <span style={{ color: !miniSel ? "#60a5fa" : "#7a7d92", fontWeight: !miniSel ? 700 : 400 }}>{dim.conseillee.b}x{dim.conseillee.h} {dim.conseillee.classe}</span>
                      </span>
                    );
                  })()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div style={{ fontSize: 11, color: "#545870", marginTop: 8, fontStyle: "italic" }}>
          Essence : {data.essence || params.essence || "sapin"} - sections indicatives, a valider (DTU / Eurocode 5).<br/>
          Dimensionnement EC5 (flexion) : portee = longueur piece, entraxe et descente de charge selon hypotheses - <b>valeurs a valider par un professionnel</b>.
        </div>
      </div>

      {/* Assemblages recommandes */}
      <div style={card}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#e8eaf2", marginBottom: 10 }}>Assemblages recommandes (types)</div>
        {data.groupes.map((g, i) => (
          <div key={i} style={{ display: "flex", gap: 12, padding: "8px 0", borderBottom: i < data.groupes.length - 1 ? "1px solid rgba(255,255,255,0.04)" : "none" }}>
            <div style={{ minWidth: 130, fontSize: 13, fontWeight: 600, color: "#f0c040" }}>{g.nom}</div>
            <div style={{ fontSize: 12.5, color: "#a8abbd", lineHeight: 1.5 }}>{ASSEMBLAGES[g.nom] || ASSEMBLAGES["Divers"]}</div>
          </div>
        ))}
        <div style={{ fontSize: 11, color: "#545870", marginTop: 10, fontStyle: "italic" }}>
          Recommandations types a adapter au projet. A faire valider par un professionnel.
        </div>
      </div>
    </div>
  );
}

function Viewer3D({ params, onMetre }) {
  const mountRef = useRef(null);
  const onMetreRef = useRef(onMetre);
  onMetreRef.current = onMetre;

  useEffect(() => {
    if (!mountRef.current) return;

    const w = mountRef.current.clientWidth;
    const h = mountRef.current.clientHeight;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.shadowMap.enabled = true;
    mountRef.current.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 200);
    camera.position.set(12, 8, 12);

    scene.add(new THREE.AmbientLight(0xffffff, 0.4));
    const sun = new THREE.DirectionalLight(0xfff8e7, 1.2);
    sun.position.set(10, 20, 10);
    sun.castShadow = true;
    scene.add(sun);

    // Construction de la scene via fonction commune
    // 1er passage : sans sections (pour obtenir le metre)
    const preBuild = buildScene3D(scene, params, { couverture: params.couverture, mode: params.mode3D });
    // calcul des sections EC5 a partir du metre obtenu
    let sectionsEC5 = {};
    try {
      const agg = agregerMetre(preBuild.metre, preBuild.densiteBois || 450);
      sectionsEC5 = calculerSectionsCharpente(agg, params, params.sk);
    } catch (e) { sectionsEC5 = {}; }
    // 2e passage : on vide la scene des meshes et on redessine avec les sections
    // (simple : on retire tous les Mesh ajoutes par le 1er passage)
    const toRemove = [];
    scene.traverse((o) => { if (o.isMesh) toRemove.push(o); });
    toRemove.forEach((o) => { scene.remove(o); if (o.geometry) o.geometry.dispose(); });
    const buildResultViewer = buildScene3D(scene, params, {
      couverture: params.couverture, mode: params.mode3D,
      sections: sectionsEC5, sectionMode: params.sectionMode || "conseillee",
    });
    if (onMetreRef.current && buildResultViewer.metre) {
      onMetreRef.current(agregerMetre(buildResultViewer.metre, buildResultViewer.densiteBois || 450), buildResultViewer.metre);
    }
    const H = params.hauteur || 3;
    const lg = params.largeur || 6;
    const pente = params.pente || 35;
    const typeProjet = params.type_projet || "charpente_trad";

        // SOL (commun à tous les types)
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(30, 30),
      new THREE.MeshLambertMaterial({ color: 0x1a1f2e })
    );
    ground.rotation.x = -Math.PI/2;
    scene.add(ground);

    // ============================================================
    // CAMERA INTERACTIVE (OrbitControls)
    // ============================================================

    // Centre cible de la camera (adapte selon type)
    const yCentre = typeProjet === "carport"
      ? H + (lg * Math.tan((pente * Math.PI) / 180)) / 2
      : H/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;

    // Configuration OrbitControls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, yCentre, 0);
    controls.enableDamping = true;          // mouvement fluide
    controls.dampingFactor = 0.08;
    controls.rotateSpeed = 0.6;
    controls.zoomSpeed = 0.8;
    controls.panSpeed = 0.5;
    controls.minDistance = 5;               // limite zoom in
    controls.maxDistance = 50;              // limite zoom out
    controls.minPolarAngle = 0.1;           // empeche de passer en dessous
    controls.maxPolarAngle = Math.PI / 2.1; // empeche de passer sous le sol
    controls.autoRotate = true;             // rotation lente au demarrage
    controls.autoRotateSpeed = 0.5;
    camera.lookAt(0, yCentre, 0);
    controls.update();

    // Arreter l'auto-rotation au premier mouvement utilisateur
    const stopAutoRotate = () => { controls.autoRotate = false; };
    controls.addEventListener("start", stopAutoRotate);

    // Boucle de rendu
    let animId;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // Gestion du resize
    const handleResize = () => {
      if (!mountRef.current) return;
      const newW = mountRef.current.clientWidth;
      const newH = mountRef.current.clientHeight;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      controls.removeEventListener("start", stopAutoRotate);
      controls.dispose();
      cancelAnimationFrame(animId);
      renderer.dispose();
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current)
        mountRef.current.removeChild(renderer.domElement);
    };
  }, [params.longueur, params.largeur, params.hauteur, params.pente, params.type_projet, params.couverture, params.mode3D, params.sectionMode]);

  return <div ref={mountRef} style={{ width: "100%", height: "100%", borderRadius: 8 }} />;
}

const QUESTIONS = {
type: {
label: "Type de charpente",
options: [
{ val: "fermette", label: "Fermette industrielle", icon: "factory" },
{ val: "traditionnelle", label: "Charpente traditionnelle", icon: "tree-log" },
{ val: "lamelle", label: "Lamellé-collé", icon: "sparkles" },
{ val: "metalique", label: "Charpente metallique", icon: "gear" },
{ val: "monopente", label: "Monopente", icon: "ruler" },
{ val: "hangar", label: "Hangar / Batiment agricole", icon: "factory" },
{ val: "appentis", label: "Appentis (accole a un mur)", icon: "home" },
{ val: "4_pans", label: "Toit 4 pans (croupe)", icon: "home" },
],
},
couverture: {
label: "Type de couverture",
options: [
{ val: "tuile_terre", label: "Tuile terre cuite", icon: "circle-brown" },
{ val: "tuile_beton", label: "Tuile béton", icon: "square" },
{ val: "ardoise", label: "Ardoise naturelle", icon: "square" },
{ val: "bac_acier", label: "Bac acier", icon: "ruler" },
],
},
essence: {
label: "Essence du bois",
options: [
{ val: "sapin", label: "Sapin / Épicéa", icon: "tree-conifer" },
{ val: "pin", label: "Pin Maritime", icon: "tree-leaf" },
{ val: "douglas", label: "Douglas", icon: "tree-conifer" },
{ val: "chene", label: "Chene", icon: "tree-leaf" },
],
},
combles: {
label: "Utilisation des combles",
options: [
{ val: "perdus", label: "Combles perdus", icon: "box" },
{ val: "amenageables", label: "Amenageables", icon: "home" },
{ val: "amenages", label: "Amenages", icon: "sofa" },
],
},
};

// Mapping des identifiants vers des SVG (style line icons, stroke 2px)
function renderIcon(name, size = 20, color = "#e8eaf2") {
  const stroke = color;
  const sw = "2";
  const svgs = {
    "factory": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M2 20a2 2 0 002 2h16a2 2 0 002-2V8l-7 5V8l-7 5V4a2 2 0 00-2-2H4a2 2 0 00-2 2z"/></svg>,
    "sparkles": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z"/><path d="M5 18l.75 2.25L8 21l-2.25.75L5 24l-.75-2.25L2 21l2.25-.75L5 18z"/></svg>,
    "gear": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>,
    "circle-brown": <svg width={size} height={size} viewBox="0 0 24 24" fill="#a8841f" stroke="#a8841f" strokeWidth={sw}><circle cx="12" cy="12" r="9"/></svg>,
    "square": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/></svg>,
    "ruler": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M16 2l6 6L8 22l-6-6L16 2z"/><path d="M7.5 10.5l2 2"/><path d="M10.5 7.5l2 2"/><path d="M13.5 4.5l2 2"/></svg>,
    "tree-log": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="6" rx="9" ry="3"/><path d="M3 6v12c0 1.66 4.03 3 9 3s9-1.34 9-3V6"/><line x1="12" y1="9" x2="12" y2="9.01"/><line x1="9" y1="8.5" x2="9" y2="8.51"/><line x1="15" y1="8.5" x2="15" y2="8.51"/></svg>,
    "tree-conifer": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M12 2l4 6h-2l3 5h-2l3 5H6l3-5H7l3-5H8l4-6z"/><line x1="12" y1="18" x2="12" y2="22"/></svg>,
    "tree-leaf": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M12 22V12"/><path d="M12 12c-3 0-7-2-7-7 0 0 4-1 7 4 3-5 7-4 7-4 0 5-4 7-7 7z"/></svg>,
    "box": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>,
    "home": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>,
    "sofa": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M20 9V7a2 2 0 00-2-2H6a2 2 0 00-2 2v2"/><path d="M2 11v5a2 2 0 002 2h16a2 2 0 002-2v-5a2 2 0 00-4 0v3H6v-3a2 2 0 00-4 0z"/><line x1="6" y1="18" x2="6" y2="20"/><line x1="18" y1="18" x2="18" y2="20"/></svg>,
    "help-circle": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
    "paperclip": <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>,
  };
  return svgs[name] || null;
}

function QuestionsScreen({ detected, onValidate }) {
const [answers, setAnswers] = useState({});
const missing = Object.keys(QUESTIONS).filter(k => !detected[k]);
const allAnswered = missing.every(k => answers[k]);
return (
<div style={{ padding: 24, maxWidth: 600, margin: "0 auto" }}>
<div style={{ textAlign: "center", marginBottom: 28 }}>
<div style={{ marginBottom: 8, display: "flex", justifyContent: "center" }}>{renderIcon("help-circle", 40, "#f0c040")}</div>
<div style={{ fontSize: 20, fontWeight: 700, color: "#e8eaf2" }}>Quelques precisions</div>
<div style={{ color: "#545870", fontSize: 14, marginTop: 4 }}>Pour un devis precis, quelques informations manquantes</div>
</div>
{missing.map(key => (
<div key={key} style={{ marginBottom: 20 }}>
<div style={{ color: "#545870", fontSize: 13, marginBottom: 10, textTransform: "uppercase", letterSpacing: 1 }}>{QUESTIONS[key].label}</div>
<div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
{QUESTIONS[key].options.map(opt => (
<button key={opt.val} onClick={() => setAnswers(prev => ({ ...prev, [key]: opt.val }))}
style={{
background: answers[key] === opt.val ? "#f0c04018" : "#13161f",
border: answers[key] === opt.val ? "1px solid #f0c040" : "1px solid #1e2231",
borderRadius: 8, padding: "12px 10px", cursor: "pointer",
color: answers[key] === opt.val ? "#f0c040" : "#e8eaf2",
textAlign: "left", display: "flex", alignItems: "center", gap: 8, fontSize: 14,
}}>
<span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 20, height: 20 }}>{renderIcon(opt.icon, 18, "#e8eaf2")}</span>{opt.label}
</button>
))}
</div>
</div>
))}
<button onClick={() => onValidate({ ...detected, ...answers })} disabled={!allAnswered}
style={{
width: "100%", padding: 14, borderRadius: 8, border: "none",
background: allAnswered ? "#f0c040" : "#2a2e40",
color: allAnswered ? "#000" : "#545870",
fontWeight: 700, fontSize: 15, cursor: allAnswered ? "pointer" : "not-allowed", marginTop: 8,
}}>
Générer le devis
</button>
</div>
);
}

function FeuilleCalcTable({ devisData, zoneData }) {
const largeur = devisData.largeur || 6;
const sk = zoneData ? zoneData.sk : 0.65;
const qb = zoneData ? zoneData.qb : 0.39;
const ag = zoneData ? zoneData.ag : 0.07;
const q_neige = sk * 0.8;
const q_vent = qb * 1.5 * 0.8;
const q_totale = q_neige + q_vent * 0.6 + 0.35 + 0.15;
const portee = largeur / 2;
const moment = (q_totale * portee * portee) / 8;
const section_requise = Math.sqrt((moment * 1000000 * 6) / 24) / 10;
const section_choisie = Math.ceil(section_requise / 25) * 25;
const rows = [
{ cat: "Charges permanentes", item: "Couverture", val: "0.35 kN/m2", ok: true },
{ cat: "Charges permanentes", item: "Charpente propre", val: "0.15 kN/m2", ok: true },
{ cat: "Charges climatiques", item: "Neige sk", val: sk.toFixed(2) + " kN/m2", ok: true },
{ cat: "Charges climatiques", item: "Neige appliquee", val: q_neige.toFixed(2) + " kN/m2", ok: true },
{ cat: "Charges climatiques", item: "Vent qb", val: qb.toFixed(2) + " kN/m2", ok: true },
{ cat: "Charges climatiques", item: "Vent applique", val: q_vent.toFixed(2) + " kN/m2", ok: true },
{ cat: "Combinaisons ELU", item: "Charge totale", val: q_totale.toFixed(2) + " kN/m2", ok: true },
{ cat: "Verification EC5", item: "Portee de calcul", val: portee.toFixed(2) + " m", ok: true },
{ cat: "Verification EC5", item: "Moment flechissant", val: moment.toFixed(2) + " kN.m", ok: true },
{ cat: "Verification EC5", item: "Section requise", val: section_requise.toFixed(0) + " mm", ok: true },
{ cat: "Verification EC5", item: "Section choisie", val: section_choisie + "x" + section_choisie + " mm", ok: section_choisie >= section_requise },
{ cat: "Sismique", item: "Acceleration ag", val: ag + " g", ok: ag < 0.15 },
{ cat: "Assemblages", item: "Connecteurs", val: "Simpson Strong-Tie", ok: true },
{ cat: "Assemblages", item: "Visserie inox A4", val: "8x120 mm / 300 mm", ok: true },
];
let lastCat = "";
return (
<div style={{ fontFamily: "monospace", fontSize: 13 }}>
<div style={{ marginBottom: 16, padding: 12, background: "#f0c04018", borderRadius: 8, border: "1px solid #f0c040" }}>
<span style={{ color: "#f0c040", fontWeight: 700 }}>Note : </span>
<span style={{ color: "#545870" }}>Calculs preliminaires EN 1990/1991/1995. A valider par un bureau d etudes.</span>
</div>
<table style={{ width: "100%", borderCollapse: "collapse" }}>
<thead>
<tr style={{ background: "#2a2e40" }}>
{["Categorie", "Parametre", "Valeur", "Statut"].map(h => (
<th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "#545870", fontSize: 11, textTransform: "uppercase" }}>{h}</th>
))}
</tr>
</thead>
<tbody>
{rows.map((r, i) => {
const showCat = r.cat !== lastCat;
lastCat = r.cat;
return (
<tr key={i} style={{ borderBottom: "1px solid #1e2231", background: i % 2 === 0 ? "transparent" : "#0f1117" }}>
<td style={{ padding: "7px 12px", color: showCat ? "#60a5fa" : "transparent", fontSize: 12, fontWeight: 600 }}>{r.cat}</td>
<td style={{ padding: "7px 12px", color: "#e8eaf2" }}>{r.item}</td>
<td style={{ padding: "7px 12px", color: "#f0c040" }}>{r.val}</td>
<td style={{ padding: "7px 12px", color: r.ok ? "#3ecf8e" : "#ef4444", fontSize: 16 }}>{r.ok ? "OK" : "!!"}</td>
</tr>
);
})}
</tbody>
</table>
<div style={{ marginTop: 16, padding: 12, background: "#13161f", borderRadius: 8, border: "1px solid #3ecf8e" }}>
<span style={{ color: "#3ecf8e", fontWeight: 700 }}>Conclusion : </span>
<span style={{ color: "#e8eaf2" }}>Section {section_choisie}x{section_choisie} mm en C24 - espacement fermes 2.0 m.</span>
</div>
</div>
);
}

function Badge({ children, color }) {
return (
<span style={{ background: color + "22", color: color, border: "1px solid " + color + "44", borderRadius: 4, padding: "2px 8px", fontSize: 12, fontWeight: 600 }}>
{children}
</span>
);
}

// ====== Détection intelligente du type de materiau ======
const MATERIAL_TYPES = {
  bois_structure: {
    label: "Bois structure",
    color: "#a78bfa",
    keywords: ["panne", "chevron", "sabliere", "poteau", "ferme", "arbalétrier", "lambourde", "solive", "poutre", "muraille", "entrait", "blochet", "jambette", "contrefiche", "echantignole"],
    showDimensions: true,
    suggestedUnits: ["ml", "m3", "u"],
    defaultUnit: "ml",
    placeholder: "Ex: 75x175 mm"
  },
  bois_ossature: {
    label: "Bois ossature",
    color: "#a78bfa",
    keywords: ["ossature", "montant", "traverse", "osb", "lamellé-collé", "lamellecolle", "kvh", "bois lamelle", "agglomere", "contreplaque"],
    showDimensions: true,
    suggestedUnits: ["ml", "m2", "u"],
    defaultUnit: "ml",
    placeholder: "Ex: 45x95 mm"
  },
  couverture: {
    label: "Couverture",
    color: "#60a5fa",
    keywords: ["tuile", "ardoise", "volige", "liteau", "fait", "ecran sous-toiture", "ecran sous toiture", "membrane", "bac acier", "shingle", "zinc", "cuivre", "noue", "rive", "gouttiere", "descente"],
    showDimensions: false,
    suggestedUnits: ["m2", "u", "ml"],
    defaultUnit: "m2",
    placeholder: ""
  },
  visserie: {
    label: "Visserie / fixations",
    color: "#fcd34d",
    keywords: ["vis", "clou", "boulon", "ecrou", "rondelle", "equerre", "sabot", "etrier", "tirefond", "agrafe", "cheville", "scellement", "broche", "pointe"],
    showDimensions: true,
    suggestedUnits: ["u", "kg", "forfait"],
    defaultUnit: "u",
    placeholder: "Ex: 5x80 mm"
  },
  outillage: {
    label: "Outillage",
    color: "#fb923c",
    keywords: ["marteau", "scie", "perceuse", "visseuse", "niveau", "metre", "decametre", "rabot", "ciseau", "burin", "pied de biche", "echelle", "echafaudage", "tronconneuse", "ponceuse", "meuleuse", "cordeau", "outils"],
    showDimensions: false,
    suggestedUnits: ["u", "forfait"],
    defaultUnit: "u",
    placeholder: ""
  },
  isolation: {
    label: "Isolation",
    color: "#3ecf8e",
    keywords: ["laine", "isolant", "ouate", "polystyrene", "panneau isolant", "chanvre", "lin", "fibre de bois", "fibralith", "knauf", "rockwool", "isover", "soufflage"],
    showDimensions: true,
    suggestedUnits: ["m2", "m3", "u"],
    defaultUnit: "m2",
    placeholder: "Ex: 200mm ep, R=5"
  },
  quincaillerie: {
    label: "Quincaillerie",
    color: "#94a3b8",
    keywords: ["charniere", "gond", "poignee", "serrure", "verrou", "cremone", "fermeture", "loquet", "espagnolette"],
    showDimensions: false,
    suggestedUnits: ["u", "forfait"],
    defaultUnit: "u",
    placeholder: ""
  },
  epi: {
    label: "EPI / Sécurité",
    color: "#ef4444",
    keywords: ["casque", "harnais", "gants", "chaussures securite", "lunettes", "masque", "protection", "antichute", "longe", "baudrier", "epi"],
    showDimensions: false,
    suggestedUnits: ["u", "forfait"],
    defaultUnit: "u",
    placeholder: ""
  },
  autre: {
    label: "Autre",
    color: "#7a7d92",
    keywords: [],
    showDimensions: true,
    suggestedUnits: ["u", "ml", "m2", "m3", "kg", "h", "forfait"],
    defaultUnit: "u",
    placeholder: ""
  }
};

function detectMateriauType(designation) {
  if (!designation || designation.trim().length < 2) return "autre";
  const text = designation.toLowerCase().trim();
  let bestMatch = { type: "autre", score: 0 };
  for (const [type, config] of Object.entries(MATERIAL_TYPES)) {
    if (type === "autre") continue;
    let score = 0;
    for (const keyword of config.keywords) {
      if (text.includes(keyword)) {
        score += keyword.length > 4 ? 2 : 1;
      }
    }
    if (score > bestMatch.score) {
      bestMatch = { type, score };
    }
  }
  return bestMatch.type;
}

// Mapping : type détecté -> categorie sauvegardee en BDD
function typeToCategorie(type) {
  const mapping = {
    bois_structure: "Charpente",
    bois_ossature: "Charpente",
    couverture: "Couverture",
    isolation: "Isolation",
    visserie: "Quincaillerie",
    quincaillerie: "Quincaillerie",
    outillage: "Outillage",
    epi: "Outillage",
    autre: "Autre"
  };
  return mapping[type] || "Autre";
}

// Mapping inverse : categorie BDD -> type (pour le mode edition)
function categorieToType(categorie) {
  const reverseMap = {
    "Charpente": "bois_structure",
    "Bardage": "bois_ossature",
    "Couverture": "couverture",
    "Isolation": "isolation",
    "Quincaillerie": "quincaillerie",
    "Outillage": "outillage"
  };
  return reverseMap[categorie] || null;
}
// ====================================================

function DeviaMain() {
  const { user } = useAuth();
  const { license } = useLicense();

const [activeTab, setActiveTab] = useState("devis");
const [prompt, setPrompt] = useState("");
const [nomProjet, setNomProjet] = useState("");
const [commune, setCommune] = useState("");
  const [typeTravaux, setTypeTravaux] = useState("neuf");
  const [addressData, setAddressData] = useState(null); // lat/lng/nom officiel pour modif #6
  const [searchProjects, setSearchProjects] = useState("");
  const [groupes, setGroupes] = useState([]);
  const [selectedGroupe, setSelectedGroupe] = useState("all"); // "all" ou un UUID de groupe
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");
  const [savingGroup, setSavingGroup] = useState(false);
  const [groupError, setGroupError] = useState(null);
  const [editingGroupId, setEditingGroupId] = useState(null); // null = creation, sinon UUID
  const [openMenuGroupId, setOpenMenuGroupId] = useState(null); // pour le menu '...'
  const [deleteConfirmGroup, setDeleteConfirmGroup] = useState(null); // objet groupe ou null
  const [deletingGroup, setDeletingGroup] = useState(false);
  const [openProjectGroupDropdown, setOpenProjectGroupDropdown] = useState(null); // id du projet dont le dropdown est ouvert
  const [pendingAssignProjectId, setPendingAssignProjectId] = useState(null); // si on créé un groupe depuis une card, on assigne apres
  const [openProjectMenuId, setOpenProjectMenuId] = useState(null);
  const [renameProjectModal, setRenameProjectModal] = useState(null);
  const [renameProjectName, setRenameProjectName] = useState("");
  const [savingRename, setSavingRename] = useState(false);
  const [renameError, setRenameError] = useState(null);
  const [showInfosEntreprise, setShowInfosEntreprise] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState(null);
  const [avatarHover, setAvatarHover] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const avatarFileInputRef = useRef(null);
  const [usageLogs, setUsageLogs] = useState([]);
  const [themeMode, setThemeMode] = useState(() => {
    try {
      return localStorage.getItem("devia_theme") || "dark";
    } catch (e) {
      return "dark";
    }
  });

  // Persistance du theme
  useEffect(() => {
    try {
      localStorage.setItem("devia_theme", themeMode);
    } catch (e) {}
  }, [themeMode]);

  // Styles dynamiques selon le theme
  const t = themes[themeMode] || themes.dark;
  const cardStyle = {
    background: t.cardBg,
    backdropFilter: "blur(24px) saturate(140%)",
    WebkitBackdropFilter: "blur(24px) saturate(140%)",
    border: "1px solid " + t.cardBorder,
    borderRadius: 16,
    padding: 24,
    marginBottom: 16,
    boxShadow: t.cardShadow
  };
  const inputStyle = {
    width: "100%",
    background: t.inputBg,
    border: "1px solid " + t.inputBorder,
    borderRadius: 10,
    padding: "12px 16px",
    color: t.textPrimary,
    fontSize: 14,
    outline: "none",
    boxSizing: "border-box",
    fontFamily: "inherit",
    transition: "border-color 0.15s, background 0.15s"
  };
  const btnPrimary = {
    background: t.gold,
    color: themeMode === "light" ? "#ffffff" : "#0a0a0a",
    border: "1px solid " + t.gold,
    borderRadius: 999,
    padding: "11px 24px",
    cursor: "pointer",
    fontSize: 14,
    fontWeight: 600,
    letterSpacing: "0.01em",
    boxShadow: "0 4px 14px rgba(240, 192, 64, 0.18)",
    transition: "transform 0.1s, box-shadow 0.15s"
  };
  const btnSecondary = {
    background: t.btnSecBg,
    backdropFilter: "blur(16px)",
    WebkitBackdropFilter: "blur(16px)",
    color: t.textPrimary,
    border: "1px solid " + t.btnSecBorder,
    borderRadius: 999,
    padding: "11px 24px",
    cursor: "pointer",
    fontSize: 14,
    fontWeight: 500,
    letterSpacing: "0.01em",
    transition: "background 0.15s, border-color 0.15s"
  };
  const [extractingAddress, setExtractingAddress] = useState(false); // indicateur visuel
const [altitude, setAltitude] = useState("200");
const [files, setFiles] = useState([]);
const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [loadingProgress, setLoadingProgress] = useState(0);
const [result, setResult] = useState(null);
const [error, setError] = useState(null);
const [view3DParams, setView3DParams] = useState({ longueur: 8, largeur: 6, hauteur: 3, pente: 35 });
const [activeResultTab, setActiveResultTab] = useState("devis");
  const [mode3D, setMode3D] = useState("technique"); // "technique" | "realiste"
  const [metreData, setMetreData] = useState(null);
  const [metreBrut, setMetreBrut] = useState(null);
  const [sectionMode, setSectionMode] = useState("conseillee"); // "mini" | "conseillee"
const [showQuestions, setShowQuestions] = useState(false);
const [detectedParams, setDetectedParams] = useState({});
const [projects, setProjects] = useState([]);
  const [marchePrix, setMarchePrix] = useState([]);
  const [catalogueEntreprise, setCatalogueEntreprise] = useState([]);
  const [activeCatalogTab, setActiveCatalogTab] = useState("marche");
  const [loadingCatalogues, setLoadingCatalogues] = useState(false);
  const [showAddCatalogModal, setShowAddCatalogModal] = useState(false);
  const [catalogForm, setCatalogForm] = useState({
    categorie: "Charpente",
    categorieAutre: "",
    designation: "",
    dimensions: "",
    unite: "ml",
    prix_ht: "",
    notes: "",
  });
  const [detectedType, setDetectedType] = useState("autre");
  const [typeOverride, setTypeOverride] = useState(null);
  const [showTypeMenu, setShowTypeMenu] = useState(false);
  const [catalogFormError, setCatalogFormError] = useState(null);
  const [savingCatalog, setSavingCatalog] = useState(false);
  const [editingCatalogId, setEditingCatalogId] = useState(null);
  const [catalogChoice, setCatalogChoice] = useState("marche");
  const [completeWithMarket, setCompleteWithMarket] = useState(true);

  // Charge les projets de l'utilisateur depuis Supabase au demarrage
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;
        const { data, error } = await supabase
          .from("projects")
          .select("*")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false });
        if (error) {
          console.error("Erreur chargement projets:", error);
          return;
        }
        if (data) {
          const formatted = data.map(p => ({
            id: p.id,
            nom: p.nom,
            commune: p.commune || "",
            date: p.created_at ? p.created_at.split("T")[0] : "",
            ttc: p.total_ttc || 0,
            dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m",
            devis_data: p.devis_data,
            zone_data: p.zone_data,
            groupe_id: p.groupe_id || null,
            tokens_in: p.tokens_in || 0,
            tokens_out: p.tokens_out || 0,
            created_at: p.created_at,
          }));
          setProjects(formatted);
        }
      } catch (e) {
        console.error("Erreur loadProjects:", e);
      }
    };
    loadProjects();

    // Chargement des groupes
    const loadGroupes = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;
        const { data, error } = await supabase
          .from("groupes_projets")
          .select("*")
          .eq("user_id", user.id)
          .order("nom", { ascending: true });
        if (error) {
          console.error("Erreur chargement groupes:", error);
          return;
        }
        if (data) setGroupes(data);
      } catch (e) {
        console.error("Erreur loadGroupes:", e);
      }
    };
    loadGroupes();

    // Chargement de l'historique de consommation
    const loadUsageLogs = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;
        const { data, error } = await supabase
          .from("usage_logs")
          .select("*")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false });
        if (error) {
          console.error("Erreur chargement usage_logs:", error);
          return;
        }
        if (data) setUsageLogs(data);
      } catch (e) {
        console.error("Erreur loadUsageLogs:", e);
      }
    };
    loadUsageLogs();

    // Chargement du profil (avatar)
    const loadProfile = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;
        const { data, error } = await supabase
          .from("profiles")
          .select("avatar_url")
          .eq("user_id", user.id)
          .maybeSingle();
        if (error) {
          console.error("Erreur chargement profile:", error);
          return;
        }
        if (data && data.avatar_url) setAvatarUrl(data.avatar_url);
      } catch (e) {
        console.error("Erreur loadProfile:", e);
      }
    };
    loadProfile();
  }, []);

  // Ferme le menu '...' au clic externe
  useEffect(() => {
    if (!openMenuGroupId) return;
    const handleClickOutside = () => setOpenMenuGroupId(null);
    const timer = setTimeout(() => {
      document.addEventListener("click", handleClickOutside);
    }, 50);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("click", handleClickOutside);
    };
  }, [openMenuGroupId]);

  // Ferme le dropdown 'groupe du projet' au clic externe
  useEffect(() => {
    if (!openProjectGroupDropdown) return;
    const handleClickOutside = () => setOpenProjectGroupDropdown(null);
    const timer = setTimeout(() => {
      document.addEventListener("click", handleClickOutside);
    }, 50);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("click", handleClickOutside);
    };
  }, [openProjectGroupDropdown]);

  // Ferme le menu '...' projet au clic externe
  useEffect(() => {
    if (!openProjectMenuId) return;
    const handleClickOutside = () => setOpenProjectMenuId(null);
    const timer = setTimeout(() => {
      document.addEventListener("click", handleClickOutside);
    }, 50);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("click", handleClickOutside);
    };
  }, [openProjectMenuId]);

  // Charge les 2 catalogues depuis Supabase
  useEffect(() => {
    const loadCatalogues = async () => {
      setLoadingCatalogues(true);
      try {
        // Catalogue marché DEVIA (lecture seule, accessible à tous)
        const { data: marcheData, error: marcheError } = await supabase
          .from("marche_prix")
          .select("*")
          .eq("actif", true)
          .order("categorie")
          .order("designation");
        if (marcheError) {
          console.error("Erreur chargement marche_prix:", marcheError);
        } else if (marcheData) {
          setMarchePrix(marcheData);
        }

        // Catalogue entreprise (perso a l'utilisateur)
        const { data: { user } } = await supabase.auth.getUser();
        if (user) {
          const { data: persoData, error: persoError } = await supabase
            .from("catalogue_entreprise")
            .select("*")
            .eq("user_id", user.id)
            .eq("actif", true)
            .order("categorie")
            .order("designation");
          if (persoError) {
            console.error("Erreur chargement catalogue_entreprise:", persoError);
          } else if (persoData) {
            setCatalogueEntreprise(persoData);
          }
        }
      } catch (e) {
        console.error("Erreur loadCatalogues:", e);
      } finally {
        setLoadingCatalogues(false);
      }
    };
    loadCatalogues();
  }, []);

const [params, setParams] = useState({
entreprise: "", siret: "", adresse: "",
tauxHoraire: 55, tva: 20, marge: 25,
mentions: "Devis valable 30 jours.",
});
const [paramsLoaded, setParamsLoaded] = useState(false);
const [paramsSaving, setParamsSaving] = useState(false);
const [paramsSavedAt, setParamsSavedAt] = useState(null);
const paramsSaveTimerRef = useRef(null);
const fileInputRef = useRef(null);

// Charger les params depuis Supabase au demarrage
useEffect(() => {
  const loadParams = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) { setParamsLoaded(true); return; }
      const { data, error } = await supabase
        .from("profiles")
        .select("params")
        .eq("user_id", user.id)
        .maybeSingle();
      if (error) {
        console.error("Erreur chargement params :", error);
        setParamsLoaded(true);
        return;
      }
      if (data && data.params && Object.keys(data.params).length > 0) {
        setParams(prev => ({ ...prev, ...data.params }));
      }
      setParamsLoaded(true);
    } catch (e) {
      console.error("Erreur loadParams :", e);
      setParamsLoaded(true);
    }
  };
  loadParams();
}, []);

// Sauvegarde automatique des params dans Supabase avec debounce
useEffect(() => {
  if (!paramsLoaded) return; // Ne pas sauvegarder pendant le chargement initial
  if (paramsSaveTimerRef.current) clearTimeout(paramsSaveTimerRef.current);
  paramsSaveTimerRef.current = setTimeout(async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      setParamsSaving(true);
      const { error } = await supabase
        .from("profiles")
        .upsert({
          user_id: user.id,
          params: params,
          updated_at: new Date().toISOString()
        }, { onConflict: "user_id" });
      if (error) {
        console.error("Erreur sauvegarde params :", error);
        setParamsSaving(false);
        return;
      }
      setParamsSavedAt(new Date());
      setTimeout(() => setParamsSaving(false), 300);
    } catch (e) {
      console.error("Erreur saveParams :", e);
      setParamsSaving(false);
    }
  }, 800); // Debounce 800ms
  return () => {
    if (paramsSaveTimerRef.current) clearTimeout(paramsSaveTimerRef.current);
  };
}, [params, paramsLoaded]);

const detectParams = (text) => {
const out = {};
if (/fermette|industriel/i.test(text)) out.type = "fermette";
else if (/traditionn/i.test(text)) out.type = "traditionnelle";
else if (/lamell/i.test(text)) out.type = "lamelle";
else if (/metal/i.test(text)) out.type = "metalique";
if (/tuile.*terre|terre.*cuite/i.test(text)) out.couverture = "tuile_terre";
else if (/tuile.*beton/i.test(text)) out.couverture = "tuile_beton";
else if (/ardoise/i.test(text)) out.couverture = "ardoise";
else if (/bac.*acier/i.test(text)) out.couverture = "bac_acier";
if (/sapin|épicéa/i.test(text)) out.essence = "sapin";
else if (/douglas/i.test(text)) out.essence = "douglas";
else if (/chene/i.test(text)) out.essence = "chene";
else if (/pin/i.test(text)) out.essence = "pin";
if (/perdus/i.test(text)) out.combles = "perdus";
else if (/amenages/i.test(text)) out.combles = "amenages";
else if (/amenageable/i.test(text)) out.combles = "amenageables";
const dims = text.match(/(\d+)[x](\d+)/);
if (dims) { out.longueur = parseInt(dims[1]); out.largeur = parseInt(dims[2]); }
const surf = text.match(/(\d+)\s*m2/);
if (surf) out.surface = parseInt(surf[1]);
const pt = text.match(/(\d+)\s*deg/);
if (pt) out.pente = parseInt(pt[1]);
return out;
};

// Extraction d'adresse via API gouv.fr (limite 50 req/sec, gratuit, pas de cle)
  // Auto-extraction de l'adresse depuis le prompt (debounce 1s)
  useEffect(() => {
    if (!prompt || prompt.trim().length < 10) {
      console.log("[DEVIA] Prompt trop court, pas d'extraction");
      return;
    }
    if (commune && commune.trim() !== "") {
      console.log("[DEVIA] Localisation déjà remplie, pas d'extraction");
      return;
    }

    console.log("[DEVIA] Debounce demarre, attente 1s avant extraction...");
    const timer = setTimeout(async () => {
      console.log("[DEVIA] Lancement extraction adresse pour:", prompt);
      setExtractingAddress(true);
      const extracted = await extractAddressFromPrompt(prompt);
      console.log("[DEVIA] Resultat extraction:", extracted);
      if (extracted && (!commune || commune.trim() === "")) {
        // On utilise le label complet (adresse complete si l'user en a tape une, sinon juste la ville)
        const valeurChamp = extracted.label || extracted.ville;
        console.log("[DEVIA] Remplissage du champ Localisation avec:", valeurChamp);
        setCommune(valeurChamp);
        setAddressData(extracted);
      }
      setExtractingAddress(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, [prompt]);

  // Auto-remplissage de l'altitude quand addressData est mis a jour
  useEffect(() => {
    if (!addressData || !addressData.lat || !addressData.lng) return;
    // Si l'user a déjà saisi une altitude differente de la valeur par defaut 200, on ne touche pas
    if (altitude && altitude !== "200" && altitude.trim() !== "") {
      console.log("[DEVIA] Altitude déjà saisie par l'user, pas de remplissage auto");
      return;
    }

    const fetchAltitude = async () => {
      try {
        console.log("[DEVIA] Recuperation altitude pour:", addressData.lat, addressData.lng);
        const url = "https://api.open-meteo.com/v1/elevation?latitude=" + addressData.lat + "&longitude=" + addressData.lng;
        const resp = await fetch(url);
        if (!resp.ok) {
          console.warn("[DEVIA] API altitude HTTP", resp.status);
          return;
        }
        const data = await resp.json();
        if (!data.elevation || !data.elevation.length) {
          console.warn("[DEVIA] API altitude pas de valeur");
          return;
        }
        const alt = Math.round(data.elevation[0]);
        console.log("[DEVIA] Altitude recuperee:", alt, "m");
        setAltitude(String(alt));
      } catch (e) {
        console.warn("[DEVIA] Erreur API altitude:", e);
      }
    };

    fetchAltitude();
  }, [addressData]);

  // Helper : extrait les morceaux du texte qui RESSEMBLENT à une adresse
  const extractAddressCandidates = (text) => {
    const candidates = [];

    // 1. Code postal (5 chiffres) eventuellement suivi d'une ville
    //    Ex: "75001 Paris" / "69001" / "13008"
    const cpMatch = text.match(/\b(\d{5})\s*([A-ZA-zÀ-ÿ][a-zà-ÿ\-\s']{2,30})?/);
    if (cpMatch) {
      candidates.push(cpMatch[0].trim());
    }

    // 2. Numéro + voie + reste : "12 rue Merciere Lyon" / "5 avenue Foch Paris"
    const adresseMatch = text.match(/\b(\d{1,4})\s+(rue|avenue|av\.?|boulevard|bd\.?|place|impasse|chemin|route|allee|all\.?|quai)\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-\s']{2,60})/i);
    if (adresseMatch) {
      candidates.push(adresseMatch[0].trim());
    }

    // 3. Noms propres : mots avec majuscule (probables villes)
    //    Ex: "Lyon", "Saint-Tropez", "La Croix-Valmer"
    //    On capture le mot + d'eventuels mots suivants commencant aussi par majuscule (Saint-Tropez, etc.)
    const mots = text.split(/[\s,;.()\[\]]+/);
    const motsAvecMaj = mots.filter(m => /^[A-ZÀ-Ÿ][a-zà-ÿ\-']{2,}/.test(m));
    // On garde les noms propres qui ne sont pas des matériaux/types connus
    const blacklist = new Set([
      // Types de constructions
      "Carport", "Charpente", "Garage", "Maison", "Toiture", "Abri", "Pergola",
      "Hangar", "Veranda", "Extension", "Ossature", "Cabanon", "Atelier",
      // Matériaux
      "Sapin", "Douglas", "Chene", "Pin", "Épicéa", "Melèze", "Mélèze",
      "Ardoise", "Tuile", "Bardeau", "Bac", "Acier", "Zinc", "Cuivre", "Plomb",
      "Beton", "Terre", "Cuite", "Lauze", "Shingle",
      // Types de charpente
      "Traditionnelle", "Fermette", "Industriel", "Industrielle", "Metalique", "Metallique",
      "Lamelle", "Lamellee", "Colle", "Massif", "Bois",
      // Etat travaux
      "Neuve", "Neuf", "Rénovation", "Refection", "Combles", "Perdus",
      "Amenagees", "Amenageables",
      // Adjectifs courants (faux positifs)
      "Petit", "Petite", "Grand", "Grande", "Nouveau", "Nouvelle",
      "Vieux", "Vieille", "Ancien", "Ancienne", "Beau", "Belle", "Bel",
      "Premier", "Premiere", "Second", "Seconde",
      // Autres
      "Pente", "Pentes", "Toit", "Faite", "Faitage", "Pignon", "Pignons",
      "Sablieres", "Sabliere", "Chevrons", "Chevron", "Pannes", "Panne",
      "Liteaux", "Liteau", "Arbalétriers", "Arbalétrier"
    ]);
    motsAvecMaj.forEach(m => {
      if (!blacklist.has(m)) candidates.push(m);
    });

    return candidates;
  };

  const extractAddressFromPrompt = async (text) => {
    if (!text || text.trim().length < 3) return null;

    // On pre-extrait les candidats (codes postaux, noms propres, adresses)
    const candidates = extractAddressCandidates(text);
    console.log("[DEVIA] Candidats extraits:", candidates);

    // Si pas de candidats, on essaie quand meme avec tout le texte en derniere chance
    const queries = candidates.length > 0 ? candidates : [text];

    // Pour chaque candidat, on interroge l'API jusqu'a trouver un match
    for (const query of queries) {
      try {
        const url = "https://api-adresse.data.gouv.fr/search/?q=" + encodeURIComponent(query) + "&limit=1";
        const resp = await fetch(url);
        if (!resp.ok) continue;
        const data = await resp.json();
        if (!data.features || data.features.length === 0) {
          console.log("[DEVIA] Pas de feature pour:", query);
          continue;
        }
        const feat = data.features[0];
        console.log("[DEVIA] Query:", query, "-> Score:", feat.properties.score, "Label:", feat.properties.label);

        // Seuil adaptatif : 0.85 pour 1 mot seul, 0.5 pour plusieurs mots
        const motsCandidat = query.trim().split(/\s+/).length;
        const seuilMin = motsCandidat === 1 ? 0.85 : 0.5;
        if (!feat.properties.score || feat.properties.score < seuilMin) {
          console.log("[DEVIA] Score", feat.properties.score, "<", seuilMin, "pour:", query, "(", motsCandidat, "mot(s)) -> rejete");
          continue;
        }

        return {
          label: feat.properties.label,
          ville: feat.properties.city || feat.properties.name,
          codePostal: feat.properties.postcode || "",
          lat: feat.geometry.coordinates[1],
          lng: feat.geometry.coordinates[0],
          score: feat.properties.score
        };
      } catch (e) {
        console.warn("[DEVIA] Erreur API pour", query, ":", e);
        continue;
      }
    }

    console.log("[DEVIA] Aucun candidat n'a donne un resultat exploitable");
    return null;
  };

  const handleCreateGroup = async () => {
    const nom = newGroupName.trim();
    if (!nom) {
      setGroupError("Le nom est obligatoire");
      return;
    }
    if (nom.length > 50) {
      setGroupError("Le nom est trop long (50 caracteres maximum)");
      return;
    }
    setSavingGroup(true);
    setGroupError(null);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        setGroupError("Vous devez etre connecte");
        setSavingGroup(false);
        return;
      }

      if (editingGroupId) {
        // Mode EDITION
        const { error } = await supabase
          .from("groupes_projets")
          .update({ nom, updated_at: new Date().toISOString() })
          .eq("id", editingGroupId)
          .eq("user_id", user.id);
        if (error) {
          console.error("Erreur edition groupe:", error);
          setGroupError("Erreur : " + (error.message || "echec de la modification"));
          setSavingGroup(false);
          return;
        }
        // Met a jour le groupe dans la liste
        setGroupes(prev => prev.map(g => g.id === editingGroupId ? { ...g, nom } : g).sort((a, b) => a.nom.localeCompare(b.nom)));
      } else {
        // Mode CREATION
        const { data, error } = await supabase
          .from("groupes_projets")
          .insert([{ user_id: user.id, nom }])
          .select()
          .single();
        if (error) {
          console.error("Erreur creation groupe:", error);
          setGroupError("Erreur : " + (error.message || "echec de la creation"));
          setSavingGroup(false);
          return;
        }
        setGroupes(prev => [...prev, data].sort((a, b) => a.nom.localeCompare(b.nom)));
        setSelectedGroupe(data.id);
        // Si on creait depuis une card projet, on assigne le projet à ce nouveau groupe
        if (pendingAssignProjectId) {
          await assignProjectToGroup(pendingAssignProjectId, data.id);
          setPendingAssignProjectId(null);
        }
      }

      // Reset modale
      setShowGroupModal(false);
      setNewGroupName("");
      setEditingGroupId(null);
      setSavingGroup(false);
    } catch (e) {
      console.error("Erreur handleCreateGroup:", e);
      setGroupError("Erreur inattendue");
      setSavingGroup(false);
    }
  };

  // Suppression d'un groupe (les projets reviennent a 'Sans groupe')
  const handleRenameProject = async () => {
    if (!renameProjectModal) return;
    const newName = renameProjectName.trim();
    if (!newName) { setRenameError("Le nom est obligatoire"); return; }
    if (newName.length > 120) { setRenameError("Le nom est trop long (120 caracteres maximum)"); return; }
    setSavingRename(true);
    setRenameError(null);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) { setRenameError("Vous devez etre connecte"); setSavingRename(false); return; }
      const { error } = await supabase
        .from("projects")
        .update({ nom: newName, updated_at: new Date().toISOString() })
        .eq("id", renameProjectModal.id)
        .eq("user_id", user.id);
      if (error) {
        console.error("Erreur renommage projet:", error);
        setRenameError("Erreur : " + (error.message || "echec du renommage"));
        setSavingRename(false);
        return;
      }
      setProjects(prev => prev.map(p => p.id === renameProjectModal.id ? { ...p, nom: newName } : p));
      setRenameProjectModal(null);
      setRenameProjectName("");
      setSavingRename(false);
    } catch (e) {
      console.error("Erreur handleRenameProject:", e);
      setRenameError("Erreur inattendue");
      setSavingRename(false);
    }
  };

  const handleAvatarUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validation
    if (!file.type.startsWith("image/")) {
      alert("Veuillez selectionner une image");
      return;
    }
    if (file.size > 2097152) {
      alert("L'image est trop grande (2 Mo maximum)");
      return;
    }

    setUploadingAvatar(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        alert("Vous devez etre connecte");
        setUploadingAvatar(false);
        return;
      }

      // Supprimer les anciens avatars de l'utilisateur
      const { data: existingFiles } = await supabase.storage
        .from("avatars")
        .list(user.id + "/");
      if (existingFiles && existingFiles.length > 0) {
        const pathsToRemove = existingFiles.map(f => user.id + "/" + f.name);
        await supabase.storage.from("avatars").remove(pathsToRemove);
      }

      // Upload nouveau fichier
      const ext = file.name.split(".").pop().toLowerCase();
      const filePath = user.id + "/avatar." + ext;
      const { error: uploadError } = await supabase.storage
        .from("avatars")
        .upload(filePath, file, { upsert: true, cacheControl: "0" });

      if (uploadError) {
        console.error("Erreur upload avatar:", uploadError);
        alert("Erreur lors de l'upload");
        setUploadingAvatar(false);
        return;
      }

      // Recuperer l'URL publique
      const { data: { publicUrl } } = supabase.storage
        .from("avatars")
        .getPublicUrl(filePath);

      // Ajouter cachebuster pour forcer le refresh
      const publicUrlWithBuster = publicUrl + "?t=" + Date.now();

      // Update profile
      const { error: updateError } = await supabase
        .from("profiles")
        .upsert({ user_id: user.id, avatar_url: publicUrlWithBuster, updated_at: new Date().toISOString() }, { onConflict: "user_id" });

      if (updateError) {
        console.error("Erreur update profile:", updateError);
        alert("Photo uploadee mais erreur de sauvegarde");
        setUploadingAvatar(false);
        return;
      }

      setAvatarUrl(publicUrlWithBuster);
      setUploadingAvatar(false);
    } catch (e) {
      console.error("Erreur handleAvatarUpload:", e);
      alert("Erreur inattendue");
      setUploadingAvatar(false);
    }
  };

  const handleAvatarDelete = async () => {
    if (!confirm("Supprimer la photo de profil ?")) return;
    setUploadingAvatar(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // Supprimer du Storage
      const { data: existingFiles } = await supabase.storage
        .from("avatars")
        .list(user.id + "/");
      if (existingFiles && existingFiles.length > 0) {
        const pathsToRemove = existingFiles.map(f => user.id + "/" + f.name);
        await supabase.storage.from("avatars").remove(pathsToRemove);
      }

      // Update profile (avatar_url = null)
      await supabase
        .from("profiles")
        .upsert({ user_id: user.id, avatar_url: null, updated_at: new Date().toISOString() }, { onConflict: "user_id" });

      setAvatarUrl(null);
      setUploadingAvatar(false);
    } catch (e) {
      console.error("Erreur handleAvatarDelete:", e);
      setUploadingAvatar(false);
    }
  };

  const assignProjectToGroup = async (projectId, groupeId) => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      const { error } = await supabase
        .from("projects")
        .update({ groupe_id: groupeId, updated_at: new Date().toISOString() })
        .eq("id", projectId)
        .eq("user_id", user.id);
      if (error) {
        console.error("Erreur assignation groupe:", error);
        return;
      }
      // Met a jour l'etat local
      setProjects(prev => prev.map(p => p.id === projectId ? { ...p, groupe_id: groupeId } : p));
      setOpenProjectGroupDropdown(null);
    } catch (e) {
      console.error("Erreur assignProjectToGroup:", e);
    }
  };

  const handleDeleteGroup = async () => {
    if (!deleteConfirmGroup) return;
    setDeletingGroup(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        setDeletingGroup(false);
        return;
      }
      const { error } = await supabase
        .from("groupes_projets")
        .delete()
        .eq("id", deleteConfirmGroup.id)
        .eq("user_id", user.id);
      if (error) {
        console.error("Erreur suppression groupe:", error);
        alert("Erreur lors de la suppression du groupe");
        setDeletingGroup(false);
        return;
      }
      // Retire le groupe de la liste
      setGroupes(prev => prev.filter(g => g.id !== deleteConfirmGroup.id));
      // Si c'etait le groupe selectionne, retour a 'Tous'
      if (selectedGroupe === deleteConfirmGroup.id) setSelectedGroupe("all");
      // Met a jour les projets : ceux qui etaient dans ce groupe -> groupe_id null
      setProjects(prev => prev.map(p => p.groupe_id === deleteConfirmGroup.id ? { ...p, groupe_id: null } : p));
      setDeleteConfirmGroup(null);
      setDeletingGroup(false);
    } catch (e) {
      console.error("Erreur handleDeleteGroup:", e);
      setDeletingGroup(false);
    }
  };

  const handleGenerate = async (finalParams) => {
setShowQuestions(false);
setLoading(true);
setLoadingStep(0);
setLoadingProgress(0);
setError(null);

// Simulation de progression par etapes
// Etape 0: Analyse de la demande (0-1.5s)
// Etape 1: Calcul de la zone climatique (1.5-3s)
// Etape 2: Génération du modele 3D (3-5s)
// Etape 3: Création du devis IA (5-7s)
// Etape 4: Finalisation (7s+ jusqu'a la fin de l'API)
const stepTimers = [];
stepTimers.push(setTimeout(() => { setLoadingStep(1); setLoadingProgress(20); }, 1500));
stepTimers.push(setTimeout(() => { setLoadingStep(2); setLoadingProgress(40); }, 3000));
stepTimers.push(setTimeout(() => { setLoadingStep(3); setLoadingProgress(65); }, 5000));
stepTimers.push(setTimeout(() => { setLoadingStep(4); setLoadingProgress(85); }, 7000));
// Garde une référence pour nettoyer si necessaire
window._deviaStepTimers = stepTimers;
setLoadingProgress(5);
const zoneInfo = getZone(commune, altitude);
// Construction de la liste de prix selon le choix utilisateur
    let prixList = [];
    let catalogSource = "marche";
    if (catalogChoice === "marche") {
      prixList = marchePrix;
      catalogSource = "marche";
    } else if (catalogChoice === "perso") {
      if (completeWithMarket) {
        // Catalogue perso prioritaire, complete par marche pour les manquants
        prixList = [...catalogueEntreprise];
        const designationsPerso = new Set(catalogueEntreprise.map(p => (p.designation + "|" + (p.dimensions || "")).toLowerCase()));
        marchePrix.forEach(m => {
          const key = (m.designation + "|" + (m.dimensions || "")).toLowerCase();
          if (!designationsPerso.has(key)) {
            prixList.push(m);
          }
        });
        catalogSource = "perso+marche";
      } else {
        prixList = catalogueEntreprise;
        catalogSource = "perso";
      }
    }

    // Format compact pour le prompt (economiser les tokens)
    const prixListText = prixList.length > 0
      ? prixList.map(p => `- ${p.categorie} | ${p.designation} | ${p.dimensions || "-"} | ${p.unite} | ${Number(p.prix_ht).toFixed(2)} EUR`).join("\n")
      : "Aucun catalogue fourni - estimé les prix toi-meme.";

    const systemPrompt = "Tu es DEVIA, expert charpente bois. Genere un devis professionnel EN FRANCAIS. " +
"DETECTION DU TYPE DE PROJET : analyse la description et choisis 1 valeur pour type_projet : " +
"'carport' (carport, abri voiture, auvent ouvert sans murs, structure sur poteaux, toit 1 pan), " +
"'charpente_trad' (charpente traditionnelle de maison, toit 2 pans avec murs), " +
"'monopente' (batiment ferme avec murs et toit a 1 SEULE pente, atelier, garage), " +
"'hangar' (hangar agricole, batiment industriel, grand volume couvert, poteaux + 2 pans sans murs), " +
"'appentis' (toit 1 pan ACCOLE a un mur existant, terrasse couverte, abri a bois contre une maison), " +
"'4_pans' (toit en croupe a 4 pentes, maison pavillon, toit avec aretiers), " +
"'abri' (abri jardin, abri petit volume), " +
"'autre' (si rien ne correspond clairement). " +
"IMPORTANT : si la description mentionne 'monopente' ou '1 seule pente' avec des murs, utilise 'monopente'. Si elle mentionne 'accole', 'contre un mur', 'contre la maison', utilise 'appentis'. " +
"\n\nCATALOGUE DE PRIX A UTILISER (source: " + catalogSource + ") :\n" + prixListText + "\n\n" +
(catalogSource === "perso" ?
  // MODE STRICT : que le catalogue perso, pas d'invention
  "REGLES PRIX (MODE STRICT - CATALOGUE PERSO UNIQUEMENT) : " +
  "1) INTERDICTION ABSOLUE d'inventer un prix ou de creer un poste pour un matériau qui n'est PAS dans le catalogue ci-dessus. " +
  "2) Tu DOIS uniquement creer des postes correspondant aux materiaux LISTES dans le catalogue. " +
  "3) Le prix unitaire HT doit correspondre EXACTEMENT au prix du catalogue. " +
  "4) Si tu n'as pas assez de materiaux pour faire un devis complet (par exemple, pas de tuiles, pas de fixations), ne genere QUE les postes pour lesquels tu as un matériau dans le catalogue. " +
  "5) Le devis sera donc PARTIEL. C'est ok et voulu. " +
  "6) Adapte les quantites au projet decrit. " +
  "7) Dans le tableau 'notes' du JSON, AJOUTE en premiere note : 'Devis partiel : seuls les materiaux de votre catalogue sont inclus. Les postes manquants doivent etre completes manuellement ou en activant l option Compléter avec marche.' " +
  "8) Genere entre 3 et 8 postes (selon le nombre de materiaux disponibles). "
  :
  // MODE NORMAL : avec complement marche
  "REGLES PRIX : 1) Pour chaque poste de devis, utilise EN PRIORITE un matériau du catalogue ci-dessus si disponible. " +
  "2) Le prix unitaire HT doit correspondre exactement au prix du catalogue. " +
  "3) Si un matériau necessaire n'existe pas dans le catalogue, estimé le prix au mieux mais signale-le dans les notes. " +
  "4) Adapte les quantites au projet decrit. "
) +
"Type=" + (finalParams.type || "traditionnelle") + ", Couverture=" + (finalParams.couverture || "tuile_terre") + ", Essence=" + (finalParams.essence || "sapin") + ", Combles=" + (finalParams.combles || "perdus") + ". " +
"Commune=" + commune + ", Altitude=" + altitude + "m, Zone neige=" + zoneInfo.neige + " sk=" + zoneInfo.sk + "kN/m2, Vent=" + zoneInfo.vent + " qb=" + zoneInfo.qb + "kN/m2. " +
(finalParams.longueur ? "Dimensions=" + finalParams.longueur + "x" + finalParams.largeur + "m. " : "") +
(finalParams.pente ? "Pente=" + finalParams.pente + "deg. " : "") +
"Reponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans backticks, sans texte avant ou apres. Format exact : " +
'{"projet":{"description":"texte","commune":"' + commune + '","longueur":10,"largeur":8,"hauteur":3,"pente":35,"surface":80,' +
'"type":"' + (finalParams.type || "traditionnelle") + '","couverture":"' + (finalParams.couverture || "tuile_terre") + '",' +
'"essence":"' + (finalParams.essence || "sapin") + '","combles":"' + (finalParams.combles || "perdus") + '",' +
'"type_projet":"carport_OU_charpente_trad_OU_monopente_OU_hangar_OU_appentis_OU_4_pans_OU_abri_OU_autre"},' +
'"postes":[{"categorie":"Charpente","designation":"Exemple","unite":"ml","quantite":10,"prixUnitaireHT":45,"totalHT":450}],' +
'"totaux":{"totalHT":12000,"tva":2400,"totalTTC":14400},"temps_fabrication_h":24,"temps_pose_h":16,"notes":["Note 1"]}. ' +
"Genere 12 a 18 postes realistes avec prix marche francais 2024. " +
"ESTIMATION TEMPS : Tu DOIS aussi estimer le temps de fabrication en atelier (debit, assemblage des pieces) et le temps de pose sur chantier (montage de la charpente) en HEURES. " +
"Base tes estimations sur la complexite du projet, la surface, le type de charpente, le nombre de pieces. " +
"Pour une charpente traditionnelle standard : compter environ 0.8-1.2h de fabrication par m2 + 0.5-0.8h de pose par m2. " +
"Pour un carport simple : 0.4-0.6h fabrication par m2 + 0.3-0.5h pose par m2. Pour une monopente (atelier/garage avec 1 pente) : 0.5-0.7h fabrication par m2 + 0.4-0.6h pose par m2. Pour un hangar (batiment agricole, grande portee, poteaux + 2 pans) : 0.3-0.5h fabrication par m2 + 0.25-0.4h pose par m2. Pour un appentis (toit accole a mur existant, terrasse couverte, abri a bois) : 0.4-0.6h fabrication par m2 + 0.35-0.5h pose par m2. Pour un toit 4 pans / croupe (plus complexe, aretiers) : 1.0-1.4h fabrication par m2 + 0.6-0.9h pose par m2. " +
"Ajuste selon les specificites (pente forte, combles amenages, essence difficile = +20%). " +
"AJOUTE ces 2 valeurs dans le JSON apres totaux : \"temps_fabrication_h\":XX, \"temps_pose_h\":XX (entiers). " +
"IMPORTANT: Reponds UNIQUEMENT avec le JSON, rien d autre.";
try {
const response = await fetch("/api/chat", {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({
model: "claude-sonnet-4-20250514",
max_tokens: 4000,
system: systemPrompt,
messages: [{ role: "user", content: prompt }],
}),
});

  if (!response.ok) {
    const errText = await response.text();
    throw new Error("Erreur serveur " + response.status + " : " + errText.substring(0, 150));
  }

  const data = await response.json();

  // Extraction robuste du texte
  const text = (data.content && data.content[0] && data.content[0].text)
    ? data.content[0].text
    : "";

  if (!text) {
    throw new Error("Reponse vide du serveur. Vérifié la cle API dans Vercel.");
  }

  // Nettoyage : supprime les backticks markdown si presents
  const clean = text.replace(/\x60\x60\x60json|\x60\x60\x60/g, "").trim();

  // Extraction du JSON
  const jsonMatch = clean.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    throw new Error("Reponse inattendue : " + clean.substring(0, 120));
  }

  const parsed = JSON.parse(jsonMatch[0]);

  setResult({ ...parsed, _catalogSource: catalogSource });
  if (parsed.projet) {
    const p = parsed.projet;
    setView3DParams({
        longueur: p.longueur || 10,
        largeur: p.largeur || 8,
        hauteur: p.hauteur || 3,
        pente: p.pente || 35,
        type_projet: p.type_projet || "autre",
        couverture: p.couverture || "tuile_terre"
      });
      console.log("[DEVIA] Type de projet détecté par l'IA :", p.type_projet || "non specifie");
    (async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        const totalTTC = parsed.totaux ? parsed.totaux.totalTTC : 0;
        const totalHT = parsed.totaux ? parsed.totaux.totalHT : 0;
        if (user) {
          const newProject = {
            user_id: user.id,
            nom: nomProjet.trim() || p.description || "Nouveau projet",
            commune: p.commune || commune,
            longueur: p.longueur || null,
            largeur: p.largeur || null,
            hauteur: p.hauteur || null,
            pente: p.pente || null,
            surface: p.surface || null,
            type_charpente: p.type || null,
            total_ttc: totalTTC,
            total_ht: totalHT,
            devis_data: parsed,
            tokens_in: (data.usage && data.usage.input_tokens) || 0,
            tokens_out: (data.usage && data.usage.output_tokens) || 0,
          };
          const tokensIn = (data.usage && data.usage.input_tokens) || 0;
          const tokensOut = (data.usage && data.usage.output_tokens) || 0;

          const { data: inserted, error: insertError } = await supabase
            .from("projects")
            .insert(newProject)
            .select()
            .single();
          if (insertError) {
            console.error("Erreur sauvegarde projet:", insertError);
            setProjects(prev => [{ id: Date.now(), nom: nomProjet.trim() || p.description || "Nouveau projet", commune: p.commune || commune, date: new Date().toISOString().split("T")[0], ttc: totalTTC, dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m" }, ...prev]);
          } else if (inserted) {
            // Insert usage_logs : historique de consommation (survit à la suppression du projet)
            (async () => {
              try {
                const { data: logData, error: logError } = await supabase
                  .from("usage_logs")
                  .insert({
                    user_id: user.id,
                    tokens_in: tokensIn,
                    tokens_out: tokensOut,
                    model: "claude-sonnet-4-20250514",
                    project_id: inserted.id,
                  })
                  .select()
                  .single();
                if (logError) {
                  console.error("Erreur insert usage_logs:", logError);
                } else if (logData) {
                  // Maj du state local immediatement (pas besoin de refresh)
                  setUsageLogs(prev => [logData, ...prev]);
                }
              } catch (e) {
                console.error("Erreur usage_logs async:", e);
              }
            })();
            setProjects(prev => [{
              id: inserted.id,
              nom: inserted.nom,
              commune: inserted.commune || "",
              date: inserted.created_at ? inserted.created_at.split("T")[0] : "",
              ttc: inserted.total_ttc || 0,
              dims: (inserted.longueur || "?") + "x" + (inserted.largeur || "?") + "m",
              devis_data: inserted.devis_data,
            }, ...prev]);
          }
        } else {
          setProjects(prev => [{ id: Date.now(), nom: nomProjet.trim() || p.description || "Nouveau projet", commune: p.commune || commune, date: new Date().toISOString().split("T")[0], ttc: totalTTC, dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m" }, ...prev]);
        }
      } catch (e) {
        console.error("Erreur sauvegarde:", e);
      }
    })();
  }
  setActiveResultTab("devis");
} catch (e) {
  setError("Erreur : " + e.message);
} finally {
  setLoading(false);
}

};

const loadProjectDetails = (project) => {
    if (!project.devis_data) {
      setError("Donnees du devis non disponibles pour ce projet.");
      return;
    }
    setResult(project.devis_data);
    if (project.devis_data.projet) {
      const p = project.devis_data.projet;
      setView3DParams({
        longueur: p.longueur || 10,
        largeur: p.largeur || 8,
        hauteur: p.hauteur || 3,
        pente: p.pente || 35,
        type_projet: p.type_projet || "autre",
        couverture: p.couverture || "tuile_terre"
      });
    }
    setActiveResultTab("devis");
    setActiveTab("devis");
    setError(null);
  };

  const deleteProject = async (projectId, projectNom) => {
    const confirmed = window.confirm("Supprimer le projet \"" + projectNom + "\" ? Cette action est irreversible.");
    if (!confirmed) return;
    try {
      const { error } = await supabase.from("projects").delete().eq("id", projectId);
      if (error) {
        console.error("Erreur suppression:", error);
        alert("Erreur lors de la suppression : " + error.message);
        return;
      }
      setProjects(prev => prev.filter(p => p.id !== projectId));
    } catch (e) {
      console.error("Erreur deleteProject:", e);
      alert("Erreur lors de la suppression");
    }
  };

  const resetCatalogForm = () => {
    setCatalogForm({
      categorie: "Charpente",
      categorieAutre: "",
      designation: "",
      dimensions: "",
      unite: "ml",
      prix_ht: "",
      notes: "",
    });
    setCatalogFormError(null);
    setEditingCatalogId(null);
    setDetectedType("autre");
    setTypeOverride(null);
    setShowTypeMenu(false);
  };

  // Re-detection du type quand designation change (utile en mode edition)
  useEffect(() => {
    if (catalogForm.designation && catalogForm.designation.trim().length >= 2) {
      setDetectedType(detectMateriauType(catalogForm.designation));
    }
  }, [catalogForm.designation]);

  // Auto-suggestion de l'unite selon le type detecte
  useEffect(() => {
    const activeType = typeOverride || detectedType;
    const config = MATERIAL_TYPES[activeType];
    if (!config) return;
    if (!editingCatalogId && !config.suggestedUnits.includes(catalogForm.unite)) {
      setCatalogForm(prev => ({ ...prev, unite: config.defaultUnit }));
    }
  }, [detectedType, typeOverride]);

  // Fermeture du menu type au clic externe
  useEffect(() => {
    if (!showTypeMenu) return;
    const handleClickOutside = () => setShowTypeMenu(false);
    const timer = setTimeout(() => {
      document.addEventListener("click", handleClickOutside);
    }, 50);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("click", handleClickOutside);
    };
  }, [showTypeMenu]);

  const openEditCatalogModal = (material) => {
    const isStandardCat = ["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie", "Outillage"].includes(material.categorie);
    // Pre-remplir le typeOverride depuis la categorie BDD
    const typeFromCat = categorieToType(material.categorie);
    if (typeFromCat) {
      setTypeOverride(typeFromCat);
    }
    setCatalogForm({
      categorie: isStandardCat ? material.categorie : "Autre",
      categorieAutre: isStandardCat ? "" : material.categorie,
      designation: material.designation || "",
      dimensions: material.dimensions || "",
      unite: material.unite || "ml",
      prix_ht: material.prix_ht ? String(material.prix_ht) : "",
      notes: material.notes || "",
    });
    setEditingCatalogId(material.id);
    setCatalogFormError(null);
    setShowAddCatalogModal(true);
  };

  const handleDeleteMaterial = async (material) => {
    const confirmed = window.confirm("Supprimer le matériau \"" + material.designation + "\" ? Cette action est irreversible.");
    if (!confirmed) return;
    try {
      const { error } = await supabase
        .from("catalogue_entreprise")
        .delete()
        .eq("id", material.id);
      if (error) {
        console.error("Erreur suppression catalogue:", error);
        alert("Erreur lors de la suppression : " + error.message);
        return;
      }
      setCatalogueEntreprise(prev => prev.filter(m => m.id !== material.id));
    } catch (e) {
      console.error("Erreur handleDeleteMaterial:", e);
      alert("Erreur inattendue lors de la suppression.");
    }
  };

  const handleAddMaterial = async () => {
    setCatalogFormError(null);

    // Validations
    // Categorie calculee automatiquement depuis le type détecté (ou override)
    const activeType = typeOverride || detectedType;
    const categorieFinal = typeToCategorie(activeType);
    if (!categorieFinal) {
      setCatalogFormError("La categorie est obligatoire.");
      return;
    }
    if (!catalogForm.designation.trim()) {
      setCatalogFormError("La designation est obligatoire.");
      return;
    }
    const prixHt = parseFloat(catalogForm.prix_ht);
    if (isNaN(prixHt) || prixHt < 0) {
      setCatalogFormError("Le prix HT doit etre un nombre positif.");
      return;
    }
    if (!catalogForm.unite) {
      setCatalogFormError("L'unite est obligatoire.");
      return;
    }

    setSavingCatalog(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        setCatalogFormError("Vous devez etre connecte.");
        setSavingCatalog(false);
        return;
      }
      const newRow = {
        user_id: user.id,
        categorie: categorieFinal,
        designation: catalogForm.designation.trim(),
        dimensions: catalogForm.dimensions.trim() || null,
        unite: catalogForm.unite,
        prix_ht: prixHt,
        notes: catalogForm.notes.trim() || null,
      };
      if (editingCatalogId) {
        // MODE MODIFICATION
        const { data: updated, error } = await supabase
          .from("catalogue_entreprise")
          .update(newRow)
          .eq("id", editingCatalogId)
          .select()
          .single();
        if (error) {
          console.error("Erreur update catalogue:", error);
          setCatalogFormError("Erreur : " + error.message);
          setSavingCatalog(false);
          return;
        }
        // Mise a jour locale
        setCatalogueEntreprise(prev => prev.map(m => m.id === editingCatalogId ? updated : m));
      } else {
        // MODE AJOUT
        const { data: inserted, error } = await supabase
          .from("catalogue_entreprise")
          .insert(newRow)
          .select()
          .single();
        if (error) {
          console.error("Erreur insertion catalogue:", error);
          setCatalogFormError("Erreur : " + error.message);
          setSavingCatalog(false);
          return;
        }
        setCatalogueEntreprise(prev => [inserted, ...prev]);
      }
      setShowAddCatalogModal(false);
      resetCatalogForm();
    } catch (e) {
      console.error("Erreur handleAddMaterial:", e);
      setCatalogFormError("Erreur inattendue : " + e.message);
    } finally {
      setSavingCatalog(false);
    }
  };

  const handleSubmit = () => {
if (!prompt.trim()) return;
const detected = detectParams(prompt);
const missingKeys = Object.keys(QUESTIONS).filter(k => !detected[k]);
if (missingKeys.length > 0) { setDetectedParams(detected); setShowQuestions(true); }
else handleGenerate(detected);
};

const zoneInfo = commune ? getZone(commune, altitude) : null;
// === DEVIA Design System v2 - Liquid Glass ===
// Cards translucides avec backdrop-filter, bordures ultra-fines, plus d'espace
// Les styles cardStyle/inputStyle/btnPrimary/btnSecondary
// sont definis dynamiquement DANS DeviaMain selon themeMode (voir themes plus haut)

return (
<div style={{ minHeight: "100vh", background: t.bgRoot, color: t.textPrimary, fontFamily: "Inter, sans-serif", transition: "background 0.3s, color 0.3s" }}>
<style>{`
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-feature-settings: "ss01", "cv11"; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; letter-spacing: -0.005em; }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }
    input:focus, select:focus, textarea:focus { border-color: rgba(240,192,64,0.4) !important; background: rgba(255,255,255,0.05) !important; }
    button:active { transform: scale(0.97); }
    .devia-page { animation: fadeInUp 0.35s ease-out; }
    .devia-bg-noise { background-image: radial-gradient(at 0% 0%, rgba(240, 192, 64, 0.04) 0px, transparent 40%), radial-gradient(at 100% 100%, rgba(96, 165, 250, 0.03) 0px, transparent 40%); }
  `}</style>

  <header style={{
    background: t.headerBg,
    backdropFilter: "blur(20px) saturate(180%)",
    WebkitBackdropFilter: "blur(20px) saturate(180%)",
    borderBottom: "1px solid " + t.headerBorder,
    padding: "0 28px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    height: 64,
    position: "sticky",
    top: 0,
    zIndex: 100,
    transition: "background 0.3s, border-color 0.3s"
  }}>
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <img
        src="/logo-devia.jpeg"
        alt="DEVIA"
        style={{
          width: 32,
          height: 32,
          borderRadius: 9,
          objectFit: "cover",
          boxShadow: "0 2px 8px rgba(0,0,0,0.3)"
        }}
      />
      <span style={{ fontWeight: 700, fontSize: 15, letterSpacing: "-0.01em" }}>DEVIA</span>
      <span style={{ color: "#545870", fontSize: 11, fontWeight: 500, marginLeft: 4, paddingLeft: 12, borderLeft: "1px solid rgba(255,255,255,0.08)" }}>Devis charpente IA</span>
    </div>
    <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
    <nav style={{
      display: "flex",
      gap: 2,
      background: t.navBg,
      border: "1px solid " + t.navBorder,
      borderRadius: 999,
      padding: 4
    }}>
      {[{ id: "devis", label: "Devis" }, { id: "projets", label: "Projets" }, { id: "catalogue", label: "Catalogue" }, { id: "parametres", label: "Paramètres" }, { id: "compte", label: "Compte" }].map(tab => (
        <button key={tab.id} onClick={() => setActiveTab(tab.id)}
          style={{
            background: activeTab === tab.id ? t.navTabActive : "transparent",
            border: "none",
            color: activeTab === tab.id ? t.navTabActiveText : t.navTabText,
            borderRadius: 999,
            padding: "7px 16px",
            cursor: "pointer",
            fontSize: 13,
            fontWeight: activeTab === tab.id ? 600 : 500,
            letterSpacing: "-0.005em",
            transition: "all 0.15s",
            boxShadow: activeTab === tab.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
          }}
          onMouseEnter={(e) => { if (activeTab !== tab.id) e.currentTarget.style.color = t.navTabHover; }}
          onMouseLeave={(e) => { if (activeTab !== tab.id) e.currentTarget.style.color = t.navTabText; }}>
          {tab.label}
        </button>
      ))}
    </nav>
    {user && <UserMenu user={user} license={license} avatarUrl={avatarUrl} />}
    </div>
  </header>

  <main className="devia-page devia-bg-noise" style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 20px" }}>

    {activeTab === "devis" && (
      <div>
        {showQuestions ? (
          <div style={cardStyle}><QuestionsScreen detected={detectedParams} onValidate={handleGenerate} /></div>
        ) : !result ? (
          <div>
            <div style={{ marginBottom: 20, paddingTop: 4 }}>
              <p style={{ color: "#7a7d92", fontSize: 14, lineHeight: 1.55 }}>Décrivez votre projet en langage naturel. DEVIA génère un devis professionnel et une visualisation 3D.</p>
            </div>

            {/* Toggle Neuf / Rénovation */}
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 20,
              padding: "14px 18px",
              background: "rgba(255, 255, 255, 0.02)",
              border: "1px solid rgba(255, 255, 255, 0.05)",
              borderRadius: 12
            }}>
              <div>
                <div style={{ color: "#9ca0b8", fontSize: 11, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>
                  Type de travaux
                </div>
                <div style={{ color: "#e8eaf2", fontSize: 13, fontWeight: 500 }}>
                  {typeTravaux === "neuf" ? "Construction neuve" : "Rénovation"}
                </div>
              </div>
              <div style={{
                display: "inline-flex",
                gap: 2,
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 999,
                padding: 4
              }}>
                {[
                  { id: "neuf", label: "Neuf", color: "#f0c040" },
                  { id: "renovation", label: "Rénovation", color: "#3ecf8e" }
                ].map(t => (
                  <button key={t.id} type="button" onClick={() => setTypeTravaux(t.id)}
                    style={{
                      background: typeTravaux === t.id ? "rgba(255,255,255,0.08)" : "transparent",
                      border: "none",
                      color: typeTravaux === t.id ? "#ffffff" : "#7a7d92",
                      borderRadius: 999,
                      padding: "7px 16px",
                      cursor: "pointer",
                      fontSize: 13,
                      fontWeight: typeTravaux === t.id ? 600 : 500,
                      letterSpacing: "-0.005em",
                      transition: "all 0.15s",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 7,
                      boxShadow: typeTravaux === t.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
                    }}
                    onMouseEnter={(e) => { if (typeTravaux !== t.id) e.currentTarget.style.color = "#d0d2dc"; }}
                    onMouseLeave={(e) => { if (typeTravaux !== t.id) e.currentTarget.style.color = "#7a7d92"; }}>
                    <span style={{
                      width: 6, height: 6, borderRadius: "50%",
                      background: typeTravaux === t.id ? t.color : "#3a3d4f",
                      transition: "background 0.15s"
                    }}></span>
                    {t.label}
                  </button>
                ))}
              </div>
            </div>
            <div style={cardStyle}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>
                  Nom du projet <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>(optionnel)</span>
                </label>
                <input
                  type="text"
                  value={nomProjet}
                  onChange={e => setNomProjet(e.target.value)}
                  placeholder="Ex: Maison Dupont, Chantier Lyon - M. Martin..."
                  maxLength={120}
                  style={inputStyle}
                />
              </div>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Description du projet</label>
                <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
                  placeholder="Ex: Charpente traditionnelle en sapin pour maison de 10x8m, tuile terre cuite, pente 35°, combles aménageables..."
                  rows={4} style={{ ...inputStyle, resize: "vertical", lineHeight: 1.6 }} />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
                <div>
                  <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Localisation</label>
                  <input value={commune} onChange={e => setCommune(e.target.value)} placeholder="Ville, code postal ou adresse complète" style={inputStyle} />
                </div>
                <div>
                  <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Altitude (m)</label>
                  <input value={altitude} onChange={e => setAltitude(e.target.value)} type="number" placeholder="200" style={inputStyle} />
                </div>
              </div>
              {zoneInfo && (
                <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
                  <Badge color="#60a5fa">Neige {zoneInfo.neige} - {zoneInfo.sk} kN/m2</Badge>
                  <Badge color="#a78bfa">Vent {zoneInfo.vent} - {zoneInfo.qb} kN/m2</Badge>
                  <Badge color="#f97316">Sismique {zoneInfo.sismique} - {zoneInfo.ag}g</Badge>
                </div>
              )}
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Documents <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>(max 5)</span></label>
                <div onClick={() => fileInputRef.current && fileInputRef.current.click()}
                  style={{ border: "2px dashed #1e2231", borderRadius: 8, padding: 20, textAlign: "center", cursor: "pointer", color: "#545870" }}>
                  <div style={{ marginBottom: 6, display: "flex", justifyContent: "center" }}>{renderIcon("paperclip", 24, "#7a7d92")}</div>
                  <div style={{ fontSize: 13 }}>Cliquez pour ajouter des fichiers</div>
                  {files.length > 0 && (
                    <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "center" }}>
                      {files.map((f, i) => <Badge key={i} color="#60a5fa">{f.name}</Badge>)}
                    </div>
                  )}
                </div>
                <input ref={fileInputRef} type="file" multiple accept="image/*,.pdf"
                  onChange={e => setFiles(prev => [...prev, ...Array.from(e.target.files || [])].slice(0, 5))}
                  style={{ display: "none" }} />
              </div>
              {error && (
                <div style={{ background: "#ef444420", border: "1px solid #ef4444", borderRadius: 8, padding: 12, marginBottom: 16, color: "#ef4444", fontSize: 14 }}>
                  {error}
                </div>
              )}
              {/* Selecteur de catalogue - v2 cards elegantes */}
              <div style={{ marginBottom: 20 }}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 12, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Catalogue a utiliser pour ce devis</label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  {/* Card MARCHE */}
                  <div onClick={() => setCatalogChoice("marche")}
                    style={{
                      position: "relative",
                      padding: 16,
                      borderRadius: 12,
                      background: catalogChoice === "marche" ? "rgba(240, 192, 64, 0.06)" : "rgba(255, 255, 255, 0.02)",
                      border: catalogChoice === "marche" ? "1px solid rgba(240, 192, 64, 0.45)" : "1px solid rgba(255, 255, 255, 0.06)",
                      cursor: "pointer",
                      transition: "all 0.18s",
                      boxShadow: catalogChoice === "marche" ? "0 0 0 3px rgba(240, 192, 64, 0.08), inset 0 0 0 1px rgba(240, 192, 64, 0.1)" : "none"
                    }}
                    onMouseEnter={(e) => { if (catalogChoice !== "marche") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.035)"; } }}
                    onMouseLeave={(e) => { if (catalogChoice !== "marche") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)"; } }}>
                    <div style={{ display: "flex", alignItems: "start", gap: 10, marginBottom: 6 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: 8,
                        background: catalogChoice === "marche" ? "linear-gradient(135deg, rgba(240, 192, 64, 0.25), rgba(240, 192, 64, 0.1))" : "rgba(255, 255, 255, 0.04)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        flexShrink: 0,
                        transition: "background 0.18s"
                      }}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={catalogChoice === "marche" ? "#f0c040" : "#7a7d92"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <div style={{ fontSize: 13, fontWeight: 600, color: catalogChoice === "marche" ? "#f5f6fa" : "#d0d2dc" }}>Marché DEVIA</div>
                          {catalogChoice === "marche" && (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: "auto" }}>
                              <path d="M20 6L9 17l-5-5"/>
                            </svg>
                          )}
                        </div>
                        <div style={{ fontSize: 11, color: "#7a7d92", marginTop: 2 }}>{marchePrix.length} materiaux du marche</div>
                      </div>
                    </div>
                  </div>
                  {/* Card PERSO */}
                  <div onClick={() => setCatalogChoice("perso")}
                    style={{
                      position: "relative",
                      padding: 16,
                      borderRadius: 12,
                      background: catalogChoice === "perso" ? "rgba(62, 207, 142, 0.06)" : "rgba(255, 255, 255, 0.02)",
                      border: catalogChoice === "perso" ? "1px solid rgba(62, 207, 142, 0.45)" : "1px solid rgba(255, 255, 255, 0.06)",
                      cursor: "pointer",
                      transition: "all 0.18s",
                      boxShadow: catalogChoice === "perso" ? "0 0 0 3px rgba(62, 207, 142, 0.08), inset 0 0 0 1px rgba(62, 207, 142, 0.1)" : "none"
                    }}
                    onMouseEnter={(e) => { if (catalogChoice !== "perso") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.035)"; } }}
                    onMouseLeave={(e) => { if (catalogChoice !== "perso") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)"; } }}>
                    <div style={{ display: "flex", alignItems: "start", gap: 10, marginBottom: 6 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: 8,
                        background: catalogChoice === "perso" ? "linear-gradient(135deg, rgba(62, 207, 142, 0.25), rgba(62, 207, 142, 0.1))" : "rgba(255, 255, 255, 0.04)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        flexShrink: 0,
                        transition: "background 0.18s"
                      }}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={catalogChoice === "perso" ? "#3ecf8e" : "#7a7d92"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                          <circle cx="12" cy="7" r="4" />
                        </svg>
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <div style={{ fontSize: 13, fontWeight: 600, color: catalogChoice === "perso" ? "#f5f6fa" : "#d0d2dc" }}>Mon catalogue</div>
                          {catalogChoice === "perso" && (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: "auto" }}>
                              <path d="M20 6L9 17l-5-5"/>
                            </svg>
                          )}
                        </div>
                        <div style={{ fontSize: 11, color: "#7a7d92", marginTop: 2 }}>{catalogueEntreprise.length} materiaux personnels</div>
                      </div>
                    </div>
                  </div>
                </div>
                {catalogChoice === "perso" && (
                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "10px 14px",
                    marginTop: 10,
                    fontSize: 13,
                    cursor: "pointer",
                    background: "rgba(240, 192, 64, 0.04)",
                    border: "1px solid rgba(240, 192, 64, 0.18)",
                    borderRadius: 10,
                    color: completeWithMarket ? "#e8eaf2" : "#9ca0b8",
                    transition: "all 0.15s"
                  }}>
                    <input type="checkbox" checked={completeWithMarket}
                      onChange={(e) => setCompleteWithMarket(e.target.checked)}
                      style={{ accentColor: "#f0c040", width: 16, height: 16, cursor: "pointer" }} />
                    <span>Completer les materiaux manquants avec les prix marche DEVIA</span>
                  </label>
                )}
              </div>

              <button onClick={handleSubmit} disabled={loading || !prompt.trim() || !commune.trim()}
                style={{
                  ...btnPrimary,
                  width: "100%",
                  padding: "16px 24px",
                  fontSize: 15,
                  fontWeight: 700,
                  letterSpacing: "0.01em",
                  marginTop: 8,
                  opacity: loading || !prompt.trim() || !commune.trim() ? 0.45 : 1,
                  cursor: loading || !prompt.trim() || !commune.trim() ? "not-allowed" : "pointer",
                  boxShadow: loading || !prompt.trim() || !commune.trim() ? "none" : "0 8px 24px rgba(240, 192, 64, 0.28), 0 2px 6px rgba(240, 192, 64, 0.15)",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 10
                }}
                onMouseEnter={(e) => { if (!loading && prompt.trim() && commune.trim()) { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 12px 32px rgba(240, 192, 64, 0.35), 0 4px 8px rgba(240, 192, 64, 0.2)"; } }}
                onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = loading || !prompt.trim() || !commune.trim() ? "none" : "0 8px 24px rgba(240, 192, 64, 0.28), 0 2px 6px rgba(240, 192, 64, 0.15)"; }}>
                {loading ? (
                  <>
                    <span style={{ display: "inline-block", width: 14, height: 14, border: "2px solid rgba(10,10,10,0.25)", borderTopColor: "#0a0a0a", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                    <span>Analyse en cours...</span>
                  </>
                ) : (
                  <>
                    <span>Générer le devis</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M5 12h14M13 5l7 7-7 7"/>
                    </svg>
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div style={{ marginBottom: 24 }}>
              <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between", gap: 16, marginBottom: 14, flexWrap: "wrap" }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6, flexWrap: "wrap" }}>
                    <h2 style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-0.015em", lineHeight: 1.2 }}>{result.projet ? result.projet.description : "Devis charpente"}</h2>
                    {result._catalogSource && (
                      <span style={{
                        fontSize: 10,
                        fontWeight: 600,
                        padding: "3px 9px",
                        borderRadius: 999,
                        letterSpacing: "0.02em",
                        textTransform: "uppercase",
                        background: result._catalogSource === "perso" ? "rgba(62, 207, 142, 0.1)" : (result._catalogSource === "perso+marche" ? "rgba(167, 139, 250, 0.1)" : "rgba(240, 192, 64, 0.1)"),
                        color: result._catalogSource === "perso" ? "#3ecf8e" : (result._catalogSource === "perso+marche" ? "#a78bfa" : "#f0c040"),
                        border: "1px solid " + (result._catalogSource === "perso" ? "rgba(62, 207, 142, 0.3)" : (result._catalogSource === "perso+marche" ? "rgba(167, 139, 250, 0.3)" : "rgba(240, 192, 64, 0.3)")),
                        display: "inline-flex", alignItems: "center", gap: 5
                      }}>
                        <span style={{ width: 5, height: 5, borderRadius: "50%", background: result._catalogSource === "perso" ? "#3ecf8e" : (result._catalogSource === "perso+marche" ? "#a78bfa" : "#f0c040") }}></span>
                        {result._catalogSource === "perso" ? "Catalogue perso" : (result._catalogSource === "perso+marche" ? "Perso + marche" : "Marché DEVIA")}
                      </span>
                    )}
                  </div>
                  <div style={{ color: "#7a7d92", fontSize: 13, display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                    {result.projet && result.projet.commune && (<>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
                      </svg>
                      <span>{result.projet.commune}</span>
                      <span style={{ opacity: 0.4 }}>&bull;</span>
                    </>)}
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                    <span>{new Date().toLocaleDateString("fr-FR")}</span>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
                  <button style={btnSecondary} onClick={() => { setResult(null); setPrompt(""); setNomProjet(""); }}>Nouveau</button>
                  <button style={btnPrimary} onClick={() => generatePDF(result, params, zoneInfo, nomProjet, view3DParams)}>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                      </svg>
                      PDF
                    </span>
                  </button>
                </div>
              </div>
              {result._catalogSource === "perso" && (
                <div style={{ padding: 14, background: "rgba(249, 115, 22, 0.06)", border: "1px solid rgba(249, 115, 22, 0.25)", borderRadius: 12, display: "flex", alignItems: "start", gap: 12 }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 2 }}>
                    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "#fb923c", marginBottom: 3 }}>Devis partiel</div>
                    <div style={{ fontSize: 12, color: "#fdba74", lineHeight: 1.5 }}>
                      Ce devis ne contient que les materiaux presents dans votre catalogue d&apos;entreprise.
                      Pour un devis complet, cochez &quot;Compléter avec marche&quot; lors de la prochaine generation.
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div style={{ display: "inline-flex", gap: 2, marginBottom: 20, background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 999, padding: 4 }}>
              {[{ id: "devis", label: "Devis" }, { id: "3d", label: "Vue 3D" }, { id: "calcul", label: "Calcul" }].map(t => (
                <button key={t.id} onClick={() => setActiveResultTab(t.id)}
                  style={{
                    background: activeResultTab === t.id ? "rgba(255,255,255,0.08)" : "transparent",
                    border: "none",
                    color: activeResultTab === t.id ? "#ffffff" : "#7a7d92",
                    borderRadius: 999,
                    padding: "7px 18px",
                    cursor: "pointer",
                    fontSize: 13,
                    fontWeight: activeResultTab === t.id ? 600 : 500,
                    letterSpacing: "-0.005em",
                    transition: "all 0.15s",
                    boxShadow: activeResultTab === t.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
                  }}
                  onMouseEnter={(e) => { if (activeResultTab !== t.id) e.currentTarget.style.color = "#d0d2dc"; }}
                  onMouseLeave={(e) => { if (activeResultTab !== t.id) e.currentTarget.style.color = "#7a7d92"; }}>
                  {t.label}
                </button>
              ))}
            </div>

            {activeResultTab === "devis" && result.projet && (
              <div style={cardStyle}>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 24 }}>
                  {[
                    { label: "Surface", val: (result.projet.surface || "?") + "m²" },
                    { label: "Dimensions", val: (result.projet.longueur || "?") + "×" + (result.projet.largeur || "?") + "m" },
                    { label: "Pente", val: (result.projet.pente || "?") + "°" },
                    { label: "Type", val: result.projet.type || "?" }
                  ].map(info => (
                    <div key={info.label} style={{
                      background: "rgba(255, 255, 255, 0.02)",
                      borderRadius: 12,
                      padding: "14px 16px",
                      border: "1px solid rgba(255, 255, 255, 0.05)",
                      transition: "border-color 0.15s"
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.05)"; }}>
                      <div style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 6 }}>{info.label}</div>
                      <div style={{ color: "#f5f6fa", fontWeight: 700, fontSize: 18, letterSpacing: "-0.01em" }}>{info.val}</div>
                    </div>
                  ))}
                </div>
                <div style={{ borderRadius: 12, overflow: "hidden", border: "1px solid rgba(255, 255, 255, 0.05)", marginBottom: 20 }}>
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ background: "rgba(255, 255, 255, 0.025)", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                        {[
                          { label: "Categorie", align: "left" },
                          { label: "Designation", align: "left" },
                          { label: "U", align: "left" },
                          { label: "Qte", align: "right" },
                          { label: "PU HT", align: "right" },
                          { label: "Total HT", align: "right" }
                        ].map(h => (
                          <th key={h.label} style={{ padding: "12px 16px", textAlign: h.align, color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>{h.label}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(result.postes || []).map((p, i) => (
                        <tr key={i} style={{ borderBottom: i < (result.postes || []).length - 1 ? "1px solid rgba(255, 255, 255, 0.04)" : "none", transition: "background 0.12s" }}
                          onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.025)"; }}
                          onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                          <td style={{ padding: "12px 16px", fontSize: 13 }}>
                            <span style={{ color: "#60a5fa", fontSize: 11, fontWeight: 600, padding: "3px 8px", background: "rgba(96, 165, 250, 0.08)", borderRadius: 999, letterSpacing: "0.02em" }}>{p.categorie}</span>
                          </td>
                          <td style={{ padding: "12px 16px", color: "#e8eaf2", fontSize: 13, fontWeight: 500 }}>{p.designation}</td>
                          <td style={{ padding: "12px 16px", color: "#7a7d92", fontSize: 13 }}>{p.unite}</td>
                          <td style={{ padding: "12px 16px", color: "#d0d2dc", fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{p.quantite}</td>
                          <td style={{ padding: "12px 16px", color: "#d0d2dc", fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{p.prixUnitaireHT ? p.prixUnitaireHT.toLocaleString("fr-FR") : 0} <span style={{ color: "#545870", fontSize: 11 }}>EUR</span></td>
                          <td style={{ padding: "12px 16px", color: "#f0c040", fontWeight: 600, fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{p.totalHT ? p.totalHT.toLocaleString("fr-FR") : 0} <span style={{ color: "#a8841f", fontSize: 11 }}>EUR</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <div style={{
                    background: "linear-gradient(135deg, rgba(240, 192, 64, 0.04) 0%, rgba(255, 255, 255, 0.02) 100%)",
                    border: "1px solid rgba(240, 192, 64, 0.15)",
                    borderRadius: 14,
                    padding: "18px 22px",
                    minWidth: 280,
                    boxShadow: "0 4px 16px rgba(0, 0, 0, 0.2)"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                      <span style={{ color: "#7a7d92", fontSize: 12, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Total HT</span>
                      <span style={{ color: "#e8eaf2", fontSize: 14, fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>{result.totaux ? result.totaux.totalHT.toLocaleString("fr-FR") : 0} <span style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500 }}>EUR</span></span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, paddingBottom: 14, borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                      <span style={{ color: "#7a7d92", fontSize: 12, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>TVA</span>
                      <span style={{ color: "#e8eaf2", fontSize: 14, fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>{result.totaux ? result.totaux.tva.toLocaleString("fr-FR") : 0} <span style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500 }}>EUR</span></span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                      <span style={{ color: "#f0c040", fontSize: 13, fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase" }}>Total TTC</span>
                      <span style={{
                        color: "#f0c040",
                        fontWeight: 700,
                        fontSize: 24,
                        fontVariantNumeric: "tabular-nums",
                        letterSpacing: "-0.02em",
                        textShadow: "0 0 24px rgba(240, 192, 64, 0.25)"
                      }}>{result.totaux ? result.totaux.totalTTC.toLocaleString("fr-FR") : 0} <span style={{ fontSize: 14, fontWeight: 600 }}>EUR</span></span>
                    </div>
                  </div>
                </div>
                {result.notes && result.notes.length > 0 && (
                  <div style={{ marginTop: 20, padding: 18, background: "rgba(255, 255, 255, 0.02)", borderRadius: 12, border: "1px solid rgba(255, 255, 255, 0.05)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca0b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
                      </svg>
                      <div style={{ color: "#9ca0b8", fontSize: 11, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Notes techniques</div>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                      {result.notes.map((n, i) => (
                        <div key={i} style={{ color: "#d0d2dc", fontSize: 13, lineHeight: 1.55, paddingLeft: 14, position: "relative" }}>
                          <span style={{ position: "absolute", left: 0, top: 8, width: 4, height: 4, borderRadius: "50%", background: "#7a7d92" }}></span>
                          {n}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeResultTab === "3d" && (
              <div>
                <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
                  {[{ id: "technique", label: "Vue technique" }, { id: "realiste", label: "Vue realiste" }].map(m => (
                    <button key={m.id} onClick={() => setMode3D(m.id)}
                      style={{
                        padding: "7px 16px", borderRadius: 8, cursor: "pointer",
                        fontSize: 13, fontWeight: mode3D === m.id ? 600 : 500,
                        border: "1px solid " + (mode3D === m.id ? "rgba(240,192,64,0.5)" : "rgba(255,255,255,0.08)"),
                        background: mode3D === m.id ? "rgba(240,192,64,0.12)" : "transparent",
                        color: mode3D === m.id ? "#f0c040" : "#7a7d92",
                        transition: "all 0.12s"
                      }}>
                      {m.label}
                    </button>
                  ))}
                  <button
                    onClick={() => {
                      if (!metreBrut || metreBrut.length === 0) { alert("Genere d'abord un devis avec une charpente."); return; }
                      const ifc = genererIFC(metreBrut, view3DParams);
                      const blob = new Blob([ifc], { type: "application/x-step" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = "devia_charpente.ifc";
                      document.body.appendChild(a); a.click(); document.body.removeChild(a);
                      URL.revokeObjectURL(url);
                    }}
                    style={{
                      marginLeft: "auto", padding: "7px 16px", borderRadius: 8, cursor: "pointer",
                      fontSize: 13, fontWeight: 600,
                      border: "1px solid rgba(240,192,64,0.5)",
                      background: "rgba(240,192,64,0.12)", color: "#f0c040",
                      transition: "all 0.12s"
                    }}>
                    Exporter IFC
                  </button>
                  {[{ id: "mini", label: "Section mini" }, { id: "conseillee", label: "Section conseillee" }].map(m => (
                    <button key={m.id} onClick={() => setSectionMode(m.id)}
                      style={{
                        padding: "7px 14px", borderRadius: 8, cursor: "pointer",
                        fontSize: 12.5, fontWeight: sectionMode === m.id ? 600 : 500,
                        border: "1px solid " + (sectionMode === m.id ? "rgba(96,165,250,0.5)" : "rgba(255,255,255,0.08)"),
                        background: sectionMode === m.id ? "rgba(96,165,250,0.12)" : "transparent",
                        color: sectionMode === m.id ? "#60a5fa" : "#7a7d92",
                        transition: "all 0.12s"
                      }}>
                      {m.label}
                    </button>
                  ))}
                </div>
                <div style={{ ...cardStyle, height: 420, padding: 0, overflow: "hidden" }}>
                  <Viewer3D params={{ ...view3DParams, mode3D, sectionMode, sk: zoneInfo ? zoneInfo.sk : 0.45 }} onMetre={(agg, brut) => { setMetreData(agg); setMetreBrut(brut); }} />
                </div>
                <PanneauTechnique data={metreData} params={view3DParams} zoneInfo={zoneInfo} sectionMode={sectionMode} />
              </div>
            )}

            {activeResultTab === "calcul" && (
              <div style={cardStyle}>
                {/* Card Estimation temps fabrication + pose */}
                {(result.temps_fabrication_h !== undefined || result.temps_pose_h !== undefined) && (() => {
                  const fab = Number(result.temps_fabrication_h) || 0;
                  const pose = Number(result.temps_pose_h) || 0;
                  const total = fab + pose;
                  return (
                    <div style={{
                      background: "linear-gradient(135deg, rgba(96, 165, 250, 0.08), rgba(167, 139, 250, 0.04))",
                      border: "1px solid rgba(96, 165, 250, 0.18)",
                      borderRadius: 16,
                      padding: 20,
                      marginBottom: 16,
                      backdropFilter: "blur(24px) saturate(140%)",
                      WebkitBackdropFilter: "blur(24px) saturate(140%)"
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                        <div style={{
                          width: 32, height: 32, borderRadius: 8,
                          background: "rgba(96, 165, 250, 0.12)",
                          border: "1px solid rgba(96, 165, 250, 0.2)",
                          display: "flex", alignItems: "center", justifyContent: "center"
                        }}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                          </svg>
                        </div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 14, color: "#e8eaf2" }}>Estimation temps</div>
                          <div style={{ color: "#7a7d92", fontSize: 12 }}>Fabrication atelier + pose chantier</div>
                        </div>
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
                        <div style={{
                          background: "rgba(255, 255, 255, 0.025)",
                          border: "1px solid rgba(255, 255, 255, 0.05)",
                          borderRadius: 12,
                          padding: 14
                        }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 8 }}>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#fb923c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/>
                            </svg>
                            <span style={{ color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase" }}>Fabrication</span>
                          </div>
                          <div style={{ fontSize: 22, fontWeight: 700, color: "#e8eaf2", letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums" }}>
                            {fab}<span style={{ fontSize: 13, color: "#7a7d92", fontWeight: 500, marginLeft: 4 }}>h</span>
                          </div>
                          <div style={{ color: "#545870", fontSize: 11, marginTop: 4 }}>Atelier</div>
                        </div>
                        <div style={{
                          background: "rgba(255, 255, 255, 0.025)",
                          border: "1px solid rgba(255, 255, 255, 0.05)",
                          borderRadius: 12,
                          padding: 14
                        }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 8 }}>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                            </svg>
                            <span style={{ color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase" }}>Pose</span>
                          </div>
                          <div style={{ fontSize: 22, fontWeight: 700, color: "#e8eaf2", letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums" }}>
                            {pose}<span style={{ fontSize: 13, color: "#7a7d92", fontWeight: 500, marginLeft: 4 }}>h</span>
                          </div>
                          <div style={{ color: "#545870", fontSize: 11, marginTop: 4 }}>Chantier</div>
                        </div>
                        <div style={{
                          background: "linear-gradient(135deg, rgba(240, 192, 64, 0.1), rgba(240, 192, 64, 0.03))",
                          border: "1px solid rgba(240, 192, 64, 0.25)",
                          borderRadius: 12,
                          padding: 14
                        }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 8 }}>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                            </svg>
                            <span style={{ color: "#f0c040", fontSize: 10, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase" }}>Total</span>
                          </div>
                          <div style={{ fontSize: 22, fontWeight: 700, color: "#f0c040", letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums" }}>
                            {total}<span style={{ fontSize: 13, color: "#a8841f", fontWeight: 500, marginLeft: 4 }}>h</span>
                          </div>
                          <div style={{ color: "#a8841f", fontSize: 11, marginTop: 4 }}>{Math.ceil(total / 8)} jour(s) - 8h</div>
                        </div>
                      </div>
                    </div>
                  );
                })()}

                <FeuilleCalcTable devisData={result.projet || {}} zoneData={zoneInfo} />
              </div>
            )}
          </div>
        )}
      </div>
    )}

    {activeTab === "projets" && (
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Mes projets</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>Retrouvez tous vos devis sauvegardés</div>
          </div>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 6,
            background: "rgba(96, 165, 250, 0.08)",
            border: "1px solid rgba(96, 165, 250, 0.2)",
            borderRadius: 999,
            padding: "6px 14px",
            fontSize: 12,
            fontWeight: 600,
            color: "#60a5fa"
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#60a5fa" }}></span>
            {projects.length} devis
          </div>
        </div>

        {/* Pills de filtre par groupe */}
        {(groupes.length > 0 || true) && (
          <div style={{
            display: "flex",
            gap: 6,
            marginBottom: 16,
            flexWrap: "wrap"
          }}>
            {/* Pill Tous */}
            <button
              onClick={() => setSelectedGroupe("all")}
              style={{
                background: selectedGroupe === "all" ? "rgba(240, 192, 64, 0.12)" : "rgba(255, 255, 255, 0.03)",
                border: "1px solid " + (selectedGroupe === "all" ? "rgba(240, 192, 64, 0.35)" : "rgba(255, 255, 255, 0.06)"),
                color: selectedGroupe === "all" ? "#f0c040" : "#9ca0b8",
                borderRadius: 999,
                padding: "7px 14px",
                fontSize: 12,
                fontWeight: selectedGroupe === "all" ? 600 : 500,
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: 7,
                transition: "all 0.15s",
                letterSpacing: "0.005em"
              }}
              onMouseEnter={(e) => { if (selectedGroupe !== "all") { e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)"; e.currentTarget.style.color = "#d0d2dc"; } }}
              onMouseLeave={(e) => { if (selectedGroupe !== "all") { e.currentTarget.style.background = "rgba(255, 255, 255, 0.03)"; e.currentTarget.style.color = "#9ca0b8"; } }}>
              <span style={{ width: 5, height: 5, borderRadius: "50%", background: selectedGroupe === "all" ? "#f0c040" : "#545870" }}></span>
              Tous
              <span style={{ color: selectedGroupe === "all" ? "#a8841f" : "#545870", fontWeight: 500 }}>{projects.length}</span>
            </button>
            {/* Pills par groupe */}
            {groupes.map(g => {
              const count = projects.filter(p => p.groupe_id === g.id).length;
              const isActive = selectedGroupe === g.id;
              const menuOpen = openMenuGroupId === g.id;
              return (
                <div key={g.id} style={{ position: "relative", display: "inline-flex" }}>
                  <div
                    style={{
                      background: isActive ? "rgba(240, 192, 64, 0.12)" : "rgba(255, 255, 255, 0.03)",
                      border: "1px solid " + (isActive ? "rgba(240, 192, 64, 0.35)" : "rgba(255, 255, 255, 0.06)"),
                      borderRadius: 999,
                      padding: "0 4px 0 14px",
                      fontSize: 12,
                      fontWeight: isActive ? 600 : 500,
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 7,
                      transition: "all 0.15s",
                      letterSpacing: "0.005em",
                      color: isActive ? "#f0c040" : "#9ca0b8",
                      cursor: "pointer"
                    }}
                    onMouseEnter={(e) => { if (!isActive) { e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)"; e.currentTarget.style.color = "#d0d2dc"; } }}
                    onMouseLeave={(e) => { if (!isActive) { e.currentTarget.style.background = "rgba(255, 255, 255, 0.03)"; e.currentTarget.style.color = "#9ca0b8"; } }}>
                    <span onClick={() => setSelectedGroupe(g.id)} style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "7px 4px 7px 0" }}>
                      <span style={{ width: 5, height: 5, borderRadius: "50%", background: isActive ? "#f0c040" : "#545870" }}></span>
                      {g.nom}
                      <span style={{ color: isActive ? "#a8841f" : "#545870", fontWeight: 500 }}>{count}</span>
                    </span>
                    <button
                      onClick={(e) => { e.stopPropagation(); setOpenMenuGroupId(menuOpen ? null : g.id); }}
                      title="Options"
                      style={{
                        background: menuOpen ? "rgba(255, 255, 255, 0.08)" : "transparent",
                        border: "none",
                        color: "inherit",
                        cursor: "pointer",
                        padding: "4px 6px",
                        borderRadius: 999,
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        opacity: menuOpen ? 1 : 0.55,
                        transition: "opacity 0.15s, background 0.15s"
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.opacity = "1"; }}
                      onMouseLeave={(e) => { e.currentTarget.style.opacity = menuOpen ? "1" : "0.55"; }}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/>
                      </svg>
                    </button>
                  </div>
                  {menuOpen && (
                    <div style={{
                      position: "absolute",
                      top: "calc(100% + 4px)",
                      right: 0,
                      background: "rgba(22, 25, 35, 0.98)",
                      backdropFilter: "blur(20px) saturate(140%)",
                      WebkitBackdropFilter: "blur(20px) saturate(140%)",
                      border: "1px solid rgba(255, 255, 255, 0.08)",
                      borderRadius: 10,
                      padding: 4,
                      minWidth: 140,
                      boxShadow: "0 8px 24px rgba(0, 0, 0, 0.35)",
                      zIndex: 10
                    }}>
                      <button onClick={() => {
                        setEditingGroupId(g.id);
                        setNewGroupName(g.nom);
                        setGroupError(null);
                        setShowGroupModal(true);
                        setOpenMenuGroupId(null);
                      }}
                        style={{
                          width: "100%", background: "transparent", border: "none",
                          color: "#e8eaf2", textAlign: "left", padding: "8px 12px",
                          fontSize: 13, cursor: "pointer", borderRadius: 7,
                          display: "flex", alignItems: "center", gap: 8, transition: "background 0.12s"
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; }}
                        onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                        Renommer
                      </button>
                      <button onClick={() => {
                        setDeleteConfirmGroup(g);
                        setOpenMenuGroupId(null);
                      }}
                        style={{
                          width: "100%", background: "transparent", border: "none",
                          color: "#fca5a5", textAlign: "left", padding: "8px 12px",
                          fontSize: 13, cursor: "pointer", borderRadius: 7,
                          display: "flex", alignItems: "center", gap: 8, transition: "background 0.12s"
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)"; e.currentTarget.style.color = "#ef4444"; }}
                        onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "#fca5a5"; }}>
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                        </svg>
                        Supprimer
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
            {/* Pill ghost : creer un nouveau groupe */}
            <button
              onClick={() => { setNewGroupName(""); setGroupError(null); setShowGroupModal(true); }}
              style={{
                background: "transparent",
                border: "1px dashed rgba(255, 255, 255, 0.12)",
                color: "#7a7d92",
                borderRadius: 999,
                padding: "7px 14px",
                fontSize: 12,
                fontWeight: 500,
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                transition: "all 0.15s"
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "rgba(240, 192, 64, 0.4)";
                e.currentTarget.style.color = "#f0c040";
                e.currentTarget.style.background = "rgba(240, 192, 64, 0.04)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)";
                e.currentTarget.style.color = "#7a7d92";
                e.currentTarget.style.background = "transparent";
              }}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              Nouveau groupe
            </button>
          </div>
        )}

        {/* Barre de recherche */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 20 }}>
          <div style={{ position: "relative", width: "100%", maxWidth: 360, display: "flex", alignItems: "center" }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
              style={{ position: "absolute", left: 14, pointerEvents: "none" }}>
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              type="text"
              value={searchProjects}
              onChange={(e) => setSearchProjects(e.target.value)}
              placeholder="Rechercher un projet..."
              style={{
                width: "100%",
                background: "rgba(255, 255, 255, 0.025)",
                border: "1px solid rgba(255, 255, 255, 0.06)",
                borderRadius: 999,
                padding: "10px 38px 10px 40px",
                color: "#e8eaf2",
                fontSize: 13,
                outline: "none",
                transition: "border-color 0.15s, background 0.15s"
              }}
              onFocus={(e) => { e.target.style.borderColor = "rgba(240, 192, 64, 0.3)"; e.target.style.background = "rgba(255, 255, 255, 0.04)"; }}
              onBlur={(e) => { e.target.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.target.style.background = "rgba(255, 255, 255, 0.025)"; }}
            />
            {searchProjects && (
              <button
                onClick={() => setSearchProjects("")}
                title="Effacer"
                style={{
                  position: "absolute", right: 8,
                  background: "transparent", border: "none", color: "#7a7d92",
                  cursor: "pointer", borderRadius: 999, padding: 6,
                  display: "inline-flex", alignItems: "center", justifyContent: "center",
                  transition: "color 0.15s"
                }}
                onMouseEnter={(e) => { e.currentTarget.style.color = "#e8eaf2"; }}
                onMouseLeave={(e) => { e.currentTarget.style.color = "#7a7d92"; }}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            )}
          </div>
        </div>

        {projects.length === 0 ? (
          <div style={{ ...cardStyle, textAlign: "center", padding: "48px 24px" }}>
            <div style={{
              width: 56, height: 56, borderRadius: 14,
              background: "rgba(255, 255, 255, 0.03)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              display: "inline-flex", alignItems: "center", justifyContent: "center",
              marginBottom: 16
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
              </svg>
            </div>
            <div style={{ color: "#e8eaf2", fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Aucun projet pour l&apos;instant</div>
            <div style={{ color: "#7a7d92", fontSize: 13, maxWidth: 360, margin: "0 auto", lineHeight: 1.5 }}>Generez votre premier devis depuis l&apos;onglet Devis et il apparaitra ici.</div>
          </div>
        ) : (
          <div style={{ display: "grid", gap: 10 }}>
            {projects.filter(p => {
              // Filtre par groupe
              if (selectedGroupe !== "all" && p.groupe_id !== selectedGroupe) return false;
              // Filtre par recherche
              const s = searchProjects.trim().toLowerCase();
              if (s === "") return true;
              const nom = (p.nom || "").toLowerCase();
              const commune = (p.commune || "").toLowerCase();
              const dims = (p.dims || "").toLowerCase();
              return nom.includes(s) || commune.includes(s) || dims.includes(s);
            }).length === 0 ? (
              <div style={{ ...cardStyle, textAlign: "center", padding: "48px 24px", marginBottom: 0 }}>
                <div style={{
                  width: 56, height: 56, borderRadius: 14,
                  background: "rgba(255, 255, 255, 0.03)",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                  display: "inline-flex", alignItems: "center", justifyContent: "center",
                  marginBottom: 16
                }}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                  </svg>
                </div>
                <div style={{ color: "#e8eaf2", fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Aucun resultat</div>
                <div style={{ color: "#7a7d92", fontSize: 13, maxWidth: 360, margin: "0 auto", lineHeight: 1.5 }}>
                  {selectedGroupe !== "all" && searchProjects.trim() !== ""
                    ? "Aucun projet ne correspond à votre recherche dans ce groupe."
                    : selectedGroupe !== "all"
                    ? "Aucun projet dans ce groupe."
                    : "Aucun projet ne correspond à votre recherche."}
                </div>
              </div>
            ) : projects.filter(p => {
              // Filtre par groupe
              if (selectedGroupe !== "all" && p.groupe_id !== selectedGroupe) return false;
              // Filtre par recherche
              const s = searchProjects.trim().toLowerCase();
              if (s === "") return true;
              const nom = (p.nom || "").toLowerCase();
              const commune = (p.commune || "").toLowerCase();
              const dims = (p.dims || "").toLowerCase();
              return nom.includes(s) || commune.includes(s) || dims.includes(s);
            }).map(p => (
              <div key={p.id} style={{
                ...cardStyle,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: "pointer",
                marginBottom: 0,
                padding: 18,
                transition: "all 0.18s",
                gap: 14,
                position: "relative",
                zIndex: (openProjectGroupDropdown === p.id || openProjectMenuId === p.id) ? 50 : 1
              }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = "rgba(240, 192, 64, 0.4)";
                  e.currentTarget.style.background = "rgba(240, 192, 64, 0.025)";
                  const deleteBtn = e.currentTarget.querySelector(".devia-delete-btn");
                  if (deleteBtn) deleteBtn.style.opacity = "1";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)";
                  e.currentTarget.style.background = "rgba(22, 25, 35, 0.55)";
                  const deleteBtn = e.currentTarget.querySelector(".devia-delete-btn");
                  if (deleteBtn) deleteBtn.style.opacity = "0.4";
                }}
                onClick={() => loadProjectDetails(p)}>
                <div style={{ display: "flex", alignItems: "center", gap: 14, flex: 1, minWidth: 0 }}>
                  <div style={{
                    width: 44, height: 44,
                    background: "linear-gradient(135deg, rgba(240, 192, 64, 0.18), rgba(240, 192, 64, 0.06))",
                    border: "1px solid rgba(240, 192, 64, 0.15)",
                    borderRadius: 11,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0
                  }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                    </svg>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: 15, color: "#e8eaf2", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", marginBottom: 3 }}>{p.nom}</div>
                    <div style={{ color: "#7a7d92", fontSize: 12, display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
                        </svg>
                        {p.commune || "?"}
                      </span>
                      <span style={{ opacity: 0.4 }}>&bull;</span>
                      <span>{p.dims}</span>
                      <span style={{ opacity: 0.4 }}>&bull;</span>
                      <span>{new Date(p.date).toLocaleDateString("fr-FR")}</span>
                    </div>
                    {/* Badge groupe */}
                    <div style={{ position: "relative", marginTop: 8, display: "inline-block" }} onClick={(e) => e.stopPropagation()}>
                      {(() => {
                        const groupeCourant = groupes.find(g => g.id === p.groupe_id);
                        const isOpen = openProjectGroupDropdown === p.id;
                        return (
                          <>
                            <button
                              onClick={(e) => { e.stopPropagation(); setOpenProjectGroupDropdown(isOpen ? null : p.id); }}
                              style={{
                                background: groupeCourant ? "rgba(96, 165, 250, 0.08)" : "transparent",
                                border: "1px " + (groupeCourant ? "solid rgba(96, 165, 250, 0.25)" : "dashed rgba(255, 255, 255, 0.12)"),
                                color: groupeCourant ? "#60a5fa" : "#7a7d92",
                                borderRadius: 999,
                                padding: "3px 10px",
                                fontSize: 11,
                                fontWeight: 500,
                                cursor: "pointer",
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 5,
                                transition: "all 0.15s",
                                letterSpacing: "0.01em"
                              }}
                              onMouseEnter={(e) => {
                                if (groupeCourant) { e.currentTarget.style.background = "rgba(96, 165, 250, 0.14)"; }
                                else { e.currentTarget.style.borderColor = "rgba(240, 192, 64, 0.4)"; e.currentTarget.style.color = "#f0c040"; }
                              }}
                              onMouseLeave={(e) => {
                                if (groupeCourant) { e.currentTarget.style.background = "rgba(96, 165, 250, 0.08)"; }
                                else { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)"; e.currentTarget.style.color = "#7a7d92"; }
                              }}>
                              {groupeCourant ? (
                                <>
                                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
                                  </svg>
                                  {groupeCourant.nom}
                                </>
                              ) : (
                                <>
                                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                                    <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                                  </svg>
                                  Ajouter à un groupe
                                </>
                              )}
                              <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.7 }}>
                                <polyline points="6 9 12 15 18 9"/>
                              </svg>
                            </button>
                            {isOpen && (
                              <div style={{
                                position: "absolute",
                                top: "calc(100% + 4px)",
                                left: 0,
                                background: "rgba(22, 25, 35, 0.98)",
                                backdropFilter: "blur(20px) saturate(140%)",
                                WebkitBackdropFilter: "blur(20px) saturate(140%)",
                                border: "1px solid rgba(255, 255, 255, 0.08)",
                                borderRadius: 10,
                                padding: 4,
                                minWidth: 200,
                                maxHeight: 280,
                                overflowY: "auto",
                                boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
                                zIndex: 20
                              }}>
                                {/* Option Sans groupe */}
                                <button
                                  onClick={(e) => { e.stopPropagation(); assignProjectToGroup(p.id, null); }}
                                  style={{
                                    width: "100%", background: "transparent", border: "none",
                                    color: !p.groupe_id ? "#f0c040" : "#9ca0b8", textAlign: "left",
                                    padding: "8px 12px", fontSize: 13, cursor: "pointer", borderRadius: 7,
                                    display: "flex", alignItems: "center", gap: 8, transition: "background 0.12s",
                                    fontWeight: !p.groupe_id ? 600 : 500
                                  }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                                  <span style={{ width: 14, display: "inline-flex" }}>
                                    {!p.groupe_id && (
                                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                        <polyline points="20 6 9 17 4 12"/>
                                      </svg>
                                    )}
                                  </span>
                                  Sans groupe
                                </button>
                                {/* Liste des groupes */}
                                {groupes.map(g => (
                                  <button
                                    key={g.id}
                                    onClick={(e) => { e.stopPropagation(); assignProjectToGroup(p.id, g.id); }}
                                    style={{
                                      width: "100%", background: "transparent", border: "none",
                                      color: p.groupe_id === g.id ? "#f0c040" : "#e8eaf2", textAlign: "left",
                                      padding: "8px 12px", fontSize: 13, cursor: "pointer", borderRadius: 7,
                                      display: "flex", alignItems: "center", gap: 8, transition: "background 0.12s",
                                      fontWeight: p.groupe_id === g.id ? 600 : 500
                                    }}
                                    onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; }}
                                    onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                                    <span style={{ width: 14, display: "inline-flex" }}>
                                      {p.groupe_id === g.id && (
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                          <polyline points="20 6 9 17 4 12"/>
                                        </svg>
                                      )}
                                    </span>
                                    {g.nom}
                                  </button>
                                ))}
                                <div style={{ height: 1, background: "rgba(255, 255, 255, 0.06)", margin: "4px 0" }}></div>
                                {/* Nouveau groupe */}
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setPendingAssignProjectId(p.id); // memorise le projet pour l'assigner ensuite
                                    setOpenProjectGroupDropdown(null);
                                    setNewGroupName(""); setGroupError(null); setEditingGroupId(null);
                                    setShowGroupModal(true);
                                  }}
                                  style={{
                                    width: "100%", background: "transparent", border: "none",
                                    color: "#7a7d92", textAlign: "left",
                                    padding: "8px 12px", fontSize: 13, cursor: "pointer", borderRadius: 7,
                                    display: "flex", alignItems: "center", gap: 8, transition: "background 0.12s"
                                  }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(240, 192, 64, 0.08)"; e.currentTarget.style.color = "#f0c040"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "#7a7d92"; }}>
                                  <span style={{ width: 14, display: "inline-flex", alignItems: "center" }}>
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                                      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                                    </svg>
                                  </span>
                                  Nouveau groupe
                                </button>
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </div>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 12, flexShrink: 0 }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: "#f0c040", fontWeight: 700, fontSize: 17, fontVariantNumeric: "tabular-nums", letterSpacing: "-0.01em" }}>
                      {p.ttc.toLocaleString("fr-FR")} <span style={{ fontSize: 12, fontWeight: 600 }}>EUR</span>
                    </div>
                    <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase" }}>TTC</div>
                  </div>
                  <div style={{ position: "relative", display: "inline-block" }} onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={(e) => { e.stopPropagation(); setOpenProjectMenuId(openProjectMenuId === p.id ? null : p.id); }}
                      title="Plus d'options"
                      style={{
                        background: openProjectMenuId === p.id ? "rgba(255, 255, 255, 0.08)" : "transparent",
                        border: "1px solid rgba(255, 255, 255, 0.06)",
                        color: "#7a7d92",
                        cursor: "pointer",
                        borderRadius: 8,
                        padding: "6px 8px",
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        transition: "all 0.15s"
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.color = "#d0d2dc"; }}
                      onMouseLeave={(e) => { e.currentTarget.style.background = openProjectMenuId === p.id ? "rgba(255, 255, 255, 0.08)" : "transparent"; e.currentTarget.style.color = "#7a7d92"; }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/>
                      </svg>
                    </button>
                    {openProjectMenuId === p.id && (
                      <div style={{
                        position: "absolute",
                        top: "calc(100% + 4px)",
                        right: 0,
                        background: "rgba(22, 25, 35, 0.98)",
                        backdropFilter: "blur(20px) saturate(140%)",
                        WebkitBackdropFilter: "blur(20px) saturate(140%)",
                        border: "1px solid rgba(255, 255, 255, 0.08)",
                        borderRadius: 10,
                        padding: 4,
                        minWidth: 160,
                        boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
                        zIndex: 100
                      }}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setRenameProjectModal(p);
                            setRenameProjectName(p.nom || "");
                            setRenameError(null);
                            setOpenProjectMenuId(null);
                          }}
                          style={{
                            width: "100%", background: "transparent", border: "none",
                            color: "#e8eaf2", textAlign: "left", padding: "8px 12px",
                            fontSize: 13, cursor: "pointer", borderRadius: 7,
                            display: "flex", alignItems: "center", gap: 8, transition: "background 0.12s"
                          }}
                          onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; }}
                          onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                          </svg>
                          Renommer
                        </button>
                      </div>
                    )}
                  </div>
                  <button
                    className="devia-delete-btn"
                    onClick={(e) => { e.stopPropagation(); deleteProject(p.id, p.nom); }}
                    title="Supprimer ce projet"
                    style={{
                      background: "transparent",
                      border: "1px solid rgba(255, 255, 255, 0.06)",
                      color: "#7a7d92",
                      borderRadius: 8,
                      padding: "6px 8px",
                      cursor: "pointer",
                      transition: "all 0.15s",
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      opacity: 0.4
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)"; e.currentTarget.style.borderColor = "rgba(239, 68, 68, 0.4)"; e.currentTarget.style.color = "#ef4444"; e.currentTarget.style.opacity = "1"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.color = "#7a7d92"; }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    )}

    {activeTab === "catalogue" && (
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Catalogue</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>Gérez les prix de référence utilisés pour vos devis</div>
          </div>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 6,
            background: "rgba(96, 165, 250, 0.08)",
            border: "1px solid rgba(96, 165, 250, 0.2)",
            borderRadius: 999,
            padding: "6px 14px",
            fontSize: 12,
            fontWeight: 600,
            color: "#60a5fa"
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#60a5fa" }}></span>
            {activeCatalogTab === "marche" ? marchePrix.length + " materiaux" : catalogueEntreprise.length + " materiaux"}
          </div>
        </div>

        {/* Onglets internes - style pills */}
        <div style={{ display: "inline-flex", gap: 2, marginBottom: 24, background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 999, padding: 4 }}>
          {[
            { id: "marche", label: "Marché DEVIA", color: "#f0c040" },
            { id: "perso", label: "Mon catalogue", color: "#3ecf8e" }
          ].map(t => (
            <button key={t.id} onClick={() => setActiveCatalogTab(t.id)}
              style={{
                background: activeCatalogTab === t.id ? "rgba(255,255,255,0.08)" : "transparent",
                border: "none",
                color: activeCatalogTab === t.id ? "#ffffff" : "#7a7d92",
                borderRadius: 999,
                padding: "8px 18px",
                cursor: "pointer",
                fontSize: 13,
                fontWeight: activeCatalogTab === t.id ? 600 : 500,
                letterSpacing: "-0.005em",
                transition: "all 0.15s",
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                boxShadow: activeCatalogTab === t.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
              }}
              onMouseEnter={(e) => { if (activeCatalogTab !== t.id) e.currentTarget.style.color = "#d0d2dc"; }}
              onMouseLeave={(e) => { if (activeCatalogTab !== t.id) e.currentTarget.style.color = "#7a7d92"; }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: activeCatalogTab === t.id ? t.color : "#3a3d4f", transition: "background 0.15s" }}></span>
              {t.label}
            </button>
          ))}
        </div>

        {loadingCatalogues ? (
          <div style={{ ...cardStyle, textAlign: "center", padding: 40, color: "#545870" }}>
            Chargement du catalogue...
          </div>
        ) : (
          <>
            {/* TAB MARCHE DEVIA */}
            {activeCatalogTab === "marche" && (
              <>
                <div style={{
                  padding: 16,
                  marginBottom: 16,
                  background: "rgba(96, 165, 250, 0.04)",
                  border: "1px solid rgba(96, 165, 250, 0.18)",
                  borderRadius: 12,
                  display: "flex",
                  alignItems: "start",
                  gap: 12
                }}>
                  <div style={{
                    width: 32, height: 32, borderRadius: 8,
                    background: "rgba(96, 165, 250, 0.12)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0
                  }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
                    </svg>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4, color: "#e8eaf2" }}>Catalogue marché DEVIA</div>
                    <div style={{ color: "#9ca0b8", fontSize: 13, lineHeight: 1.55 }}>
                      Prix moyens du marché français 2026, mis à jour régulièrement par DEVIA.
                      Vos prix dans &quot;Mon catalogue&quot; ont la priorité sur ces références.
                    </div>
                  </div>
                </div>
                {(() => {
                  const grouped = marchePrix.reduce((acc, m) => {
                    if (!acc[m.categorie]) acc[m.categorie] = [];
                    acc[m.categorie].push(m);
                    return acc;
                  }, {});
                  const orderedCats = ["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie", "Outillage"];
                  const catColors = {
                    "Charpente": "#a78bfa",
                    "Bardage": "#fb923c",
                    "Couverture": "#60a5fa",
                    "Isolation": "#3ecf8e",
                    "Quincaillerie": "#fcd34d",
                    "Outillage": "#f0c040"
                  };
                  const renderCatIcon = (cat) => {
                    const c = catColors[cat] || "#7a7d92";
                    const sw = "2";
                    switch(cat) {
                      case "Charpente":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M12 2l4 6h-2l3 5h-2l3 5H6l3-5H7l3-5H8l4-6z"/><line x1="12" y1="18" x2="12" y2="22"/></svg>;
                      case "Bardage":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>;
                      case "Couverture":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M2 12l10-9 10 9"/><path d="M5 10v10h14V10"/></svg>;
                      case "Isolation":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20"/><path d="M2 6l10 6 10-6"/><path d="M2 12l10 6 10-6"/><path d="M2 18l10 6 10-6"/></svg>;
                      case "Quincaillerie":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4M5 5l3 3M16 16l3 3M5 19l3-3M16 8l3-3"/></svg>;
                      case "Outillage":
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>;
                      default:
                        return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9"/></svg>;
                    }
                  };
                  return orderedCats.map(cat => {
                    const items = grouped[cat] || [];
                    if (items.length === 0) return null;
                    return (
                      <div key={cat} style={{ marginBottom: 24 }}>
                        <h3 style={{ fontSize: 15, fontWeight: 700, color: "#f0c040", marginBottom: 10, display: "flex", alignItems: "center", gap: 8 }}>
                          <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 22, height: 22 }}>{renderCatIcon(cat)}</span>
                          {cat} <span style={{ color: "#545870", fontWeight: 400, fontSize: 13 }}>({items.length})</span>
                        </h3>
                        <div style={{ borderRadius: 12, overflow: "hidden", border: "1px solid rgba(255, 255, 255, 0.05)", background: "rgba(255, 255, 255, 0.015)" }}>
                          <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                              <tr style={{ background: "rgba(255, 255, 255, 0.025)", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                                <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Designation</th>
                                <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Dimensions</th>
                                <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Unite</th>
                                <th style={{ padding: "12px 16px", textAlign: "right", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Prix HT</th>
                              </tr>
                            </thead>
                            <tbody>
                              {items.map((m, i) => (
                                <tr key={m.id} style={{ borderBottom: i < items.length - 1 ? "1px solid rgba(255, 255, 255, 0.04)" : "none", transition: "background 0.12s" }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.025)"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                                  <td style={{ padding: "12px 16px", fontSize: 13, color: "#e8eaf2", fontWeight: 500 }}>{m.designation}</td>
                                  <td style={{ padding: "12px 16px", fontSize: 13, color: "#9ca0b8" }}>{m.dimensions || "—"}</td>
                                  <td style={{ padding: "12px 16px", fontSize: 13, color: "#7a7d92" }}>{m.unite}</td>
                                  <td style={{ padding: "12px 16px", textAlign: "right", fontSize: 13, color: "#f0c040", fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>
                                    {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} <span style={{ color: "#a8841f", fontSize: 11 }}>EUR</span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    );
                  });
                })()}
              </>
            )}

            {/* TAB MON CATALOGUE */}
            {activeCatalogTab === "perso" && (
              <>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, gap: 12 }}>
                  <div style={{
                    padding: 16,
                    background: "rgba(62, 207, 142, 0.04)",
                    border: "1px solid rgba(62, 207, 142, 0.18)",
                    borderRadius: 12,
                    flex: 1,
                    display: "flex",
                    alignItems: "start",
                    gap: 12
                  }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: 8,
                      background: "rgba(62, 207, 142, 0.12)",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      flexShrink: 0
                    }}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 21h6"/><path d="M12 17v4"/><path d="M12 3a6 6 0 016 6c0 3-2 4-3 6H9c-1-2-3-3-3-6a6 6 0 016-6z"/>
                      </svg>
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4, color: "#e8eaf2" }}>Mon catalogue d&apos;entreprise</div>
                      <div style={{ color: "#9ca0b8", fontSize: 13, lineHeight: 1.55 }}>
                        Vos prix personnels, prioritaires sur le catalogue marche.
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => { resetCatalogForm(); setShowAddCatalogModal(true); }}
                    style={{
                      background: "#f0c040",
                      color: "#0a0a0a",
                      border: "1px solid #f0c040",
                      borderRadius: 999,
                      padding: "11px 20px",
                      cursor: "pointer",
                      fontSize: 13,
                      fontWeight: 700,
                      letterSpacing: "0.01em",
                      whiteSpace: "nowrap",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 8,
                      boxShadow: "0 4px 14px rgba(240, 192, 64, 0.22)",
                      transition: "transform 0.1s, box-shadow 0.15s"
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 8px 20px rgba(240, 192, 64, 0.3)"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 4px 14px rgba(240, 192, 64, 0.22)"; }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    Ajouter un matériau
                  </button>
                </div>
                {catalogueEntreprise.length === 0 ? (
                  <div style={{ ...cardStyle, textAlign: "center", padding: "48px 24px" }}>
                    <div style={{
                      width: 56, height: 56, borderRadius: 14,
                      background: "rgba(255, 255, 255, 0.03)",
                      border: "1px solid rgba(255, 255, 255, 0.06)",
                      display: "inline-flex", alignItems: "center", justifyContent: "center",
                      marginBottom: 16
                    }}>
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/>
                      </svg>
                    </div>
                    <div style={{ color: "#e8eaf2", fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Aucun matériau dans votre catalogue</div>
                    <div style={{ color: "#7a7d92", fontSize: 13, maxWidth: 360, margin: "0 auto", lineHeight: 1.5 }}>Cliquez sur &quot;Ajouter un matériau&quot; pour creer votre premier prix personnalise.</div>
                  </div>
                ) : (
                  <div style={{ ...cardStyle, padding: 0, overflow: "hidden" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead>
                        <tr style={{ background: "rgba(255, 255, 255, 0.025)", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Categorie</th>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Designation</th>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Dimensions</th>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Unite</th>
                          <th style={{ padding: "12px 16px", textAlign: "right", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Prix HT</th>
                          <th style={{ padding: "12px 16px", textAlign: "right", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {catalogueEntreprise.map((m, i) => (
                          <tr key={m.id} style={{ borderBottom: i < catalogueEntreprise.length - 1 ? "1px solid rgba(255, 255, 255, 0.04)" : "none", transition: "background 0.12s" }}
                            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.025)"; }}
                            onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                            <td style={{ padding: "12px 16px", fontSize: 13 }}>
                              <span style={{ color: "#60a5fa", fontSize: 11, fontWeight: 600, padding: "3px 8px", background: "rgba(96, 165, 250, 0.08)", borderRadius: 999, letterSpacing: "0.02em" }}>{m.categorie}</span>
                            </td>
                            <td style={{ padding: "12px 16px", fontSize: 13, color: "#e8eaf2", fontWeight: 500 }}>{m.designation}</td>
                            <td style={{ padding: "12px 16px", fontSize: 13, color: "#9ca0b8" }}>{m.dimensions || "—"}</td>
                            <td style={{ padding: "12px 16px", fontSize: 13, color: "#7a7d92" }}>{m.unite}</td>
                            <td style={{ padding: "12px 16px", textAlign: "right", fontSize: 13, color: "#3ecf8e", fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>
                              {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} <span style={{ color: "#1f7a4c", fontSize: 11 }}>EUR</span>
                            </td>
                            <td style={{ padding: "8px 12px", textAlign: "right" }}>
                              <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                                <button
                                  onClick={() => openEditCatalogModal(m)}
                                  title="Modifier"
                                  style={{
                                    background: "transparent",
                                    border: "1px solid rgba(255, 255, 255, 0.06)",
                                    color: "#7a7d92",
                                    borderRadius: 8,
                                    padding: "6px 8px",
                                    cursor: "pointer",
                                    transition: "all 0.15s",
                                    display: "inline-flex",
                                    alignItems: "center",
                                    justifyContent: "center"
                                  }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(96, 165, 250, 0.1)"; e.currentTarget.style.borderColor = "rgba(96, 165, 250, 0.4)"; e.currentTarget.style.color = "#60a5fa"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.color = "#7a7d92"; }}>
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                  </svg>
                                </button>
                                <button
                                  onClick={() => handleDeleteMaterial(m)}
                                  title="Supprimer"
                                  style={{
                                    background: "transparent",
                                    border: "1px solid rgba(255, 255, 255, 0.06)",
                                    color: "#7a7d92",
                                    borderRadius: 8,
                                    padding: "6px 8px",
                                    cursor: "pointer",
                                    transition: "all 0.15s",
                                    display: "inline-flex",
                                    alignItems: "center",
                                    justifyContent: "center"
                                  }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)"; e.currentTarget.style.borderColor = "rgba(239, 68, 68, 0.4)"; e.currentTarget.style.color = "#ef4444"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.color = "#7a7d92"; }}>
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                                  </svg>
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    )}

    {activeTab === "parametres" && (
      <div>
        {/* Toggle Theme Sombre/Clair */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(167, 139, 250, 0.1)",
              border: "1px solid rgba(167, 139, 250, 0.2)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
              </svg>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: t.textPrimary }}>Apparence</div>
              <div style={{ color: t.textMuted, fontSize: 12 }}>Choisissez le thème de l&apos;application</div>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            {[
              { id: "dark", label: "Sombre", desc: "Noir profond, accents dorés", isActive: themeMode === "dark" },
              { id: "light", label: "Clair", desc: "Blanc pur, design épuré", isActive: themeMode === "light" }
            ].map(opt => (
              <button key={opt.id} onClick={() => setThemeMode(opt.id)}
                style={{
                  background: opt.isActive ? (opt.id === "dark" ? "linear-gradient(135deg, rgba(240, 192, 64, 0.12), rgba(240, 192, 64, 0.04))" : "linear-gradient(135deg, rgba(167, 139, 250, 0.12), rgba(167, 139, 250, 0.04))") : t.cardBg,
                  border: "1px solid " + (opt.isActive ? (opt.id === "dark" ? "rgba(240, 192, 64, 0.35)" : "rgba(167, 139, 250, 0.35)") : t.cardBorder),
                  borderRadius: 12,
                  padding: 16,
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.18s",
                  display: "flex",
                  alignItems: "center",
                  gap: 12
                }}>
                <div style={{
                  width: 40, height: 40, borderRadius: 10,
                  background: opt.id === "dark" ? "#08090c" : "#f5f6fa",
                  border: "1px solid " + (opt.id === "dark" ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.08)"),
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0
                }}>
                  {opt.id === "dark" ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
                    </svg>
                  ) : (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#b8860b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                    </svg>
                  )}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 14, fontWeight: 600, color: t.textPrimary }}>{opt.label}</span>
                    {opt.isActive && (
                      <span style={{
                        display: "inline-flex", alignItems: "center", justifyContent: "center",
                        width: 16, height: 16, borderRadius: "50%",
                        background: opt.id === "dark" ? "#f0c040" : "#b8860b"
                      }}>
                        <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke={opt.id === "dark" ? "#0a0a0a" : "#ffffff"} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                      </span>
                    )}
                  </div>
                  <div style={{ color: t.textMuted, fontSize: 11, marginTop: 2 }}>{opt.desc}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Paramètres</h2>
          <div style={{ color: "#7a7d92", fontSize: 13, display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            <span>Configurez votre entreprise et vos tarifs par défaut</span>
            {paramsSaving && (
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "#f0c040", fontSize: 12 }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ animation: "spin 1s linear infinite" }}>
                  <path d="M21 12a9 9 0 11-6.219-8.56"/>
                </svg>
                Sauvegarde...
              </span>
            )}
            {!paramsSaving && paramsSavedAt && (
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "#3ecf8e", fontSize: 12 }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                Enregistré
              </span>
            )}
          </div>
        </div>

        {/* Section Informations entreprise */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(240, 192, 64, 0.1)",
              border: "1px solid rgba(240, 192, 64, 0.2)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 21h18M5 21V7l8-4v18M19 21V11l-6-4"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="9" y1="12" x2="9.01" y2="12"/><line x1="9" y1="15" x2="9.01" y2="15"/><line x1="9" y1="18" x2="9.01" y2="18"/>
              </svg>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: "#e8eaf2" }}>Informations entreprise</div>
              <div style={{ color: "#7a7d92", fontSize: 12 }}>Ces informations apparaîtront sur vos devis</div>
            </div>
          </div>
          {[{ label: "Nom de l'entreprise", key: "entreprise" }, { label: "SIRET", key: "siret" }, { label: "Adresse", key: "adresse" }].map(f => (
            <div key={f.key} style={{ marginBottom: 14 }}>
              <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>{f.label}</label>
              <input value={params[f.key]} onChange={e => setParams(prev => ({ ...prev, [f.key]: e.target.value }))} style={inputStyle} />
            </div>
          ))}
        </div>

        {/* Section Tarification */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(62, 207, 142, 0.1)",
              border: "1px solid rgba(62, 207, 142, 0.2)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 10h12"/><path d="M4 14h9"/><path d="M19 6.41A6.93 6.93 0 0015.89 5C12 5 9 8.13 9 12s3 7 6.89 7c1.18 0 2.29-.29 3.25-.81"/>
              </svg>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: "#e8eaf2" }}>Tarification par defaut</div>
              <div style={{ color: "#7a7d92", fontSize: 12 }}>Ces valeurs s&apos;appliquent automatiquement à vos devis</div>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
            {[
              { label: "Taux horaire", key: "tauxHoraire", suffix: "EUR/h" },
              { label: "TVA", key: "tva", suffix: "%" },
              { label: "Marge", key: "marge", suffix: "%" }
            ].map(f => (
              <div key={f.key}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>{f.label} <span style={{ color: "#7a7d92", fontWeight: 400, textTransform: "none" }}>({f.suffix})</span></label>
                <input type="number" value={params[f.key]} onChange={e => setParams(prev => ({ ...prev, [f.key]: parseFloat(e.target.value) }))} style={inputStyle} />
              </div>
            ))}
          </div>
        </div>

        {/* Section Mentions legales */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(96, 165, 250, 0.1)",
              border: "1px solid rgba(96, 165, 250, 0.2)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
              </svg>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: "#e8eaf2" }}>Mentions legales</div>
              <div style={{ color: "#7a7d92", fontSize: 12 }}>Texte affiche en bas de vos devis</div>
            </div>
          </div>
          <textarea value={params.mentions} onChange={e => setParams(prev => ({ ...prev, mentions: e.target.value }))} rows={3} style={{ ...inputStyle, resize: "vertical", lineHeight: 1.6 }} />
        </div>

        {/* Bouton Sauvegardér */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
          <button style={{
            ...btnPrimary,
            padding: "12px 28px",
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            boxShadow: "0 4px 14px rgba(240, 192, 64, 0.22)",
            transition: "transform 0.1s, box-shadow 0.15s"
          }}
          onMouseEnter={(e) => { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 8px 20px rgba(240, 192, 64, 0.3)"; }}
          onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 4px 14px rgba(240, 192, 64, 0.22)"; }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>
            </svg>
            Sauvegardér
          </button>
        </div>
      </div>
    )}

    {activeTab === "compte" && (
      <div>
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Mon compte</h2>
          <div style={{ color: "#7a7d92", fontSize: 13 }}>Aperçu de votre activité DEVIA</div>
        </div>

        {/* Card Identite + Plan */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
            <div
              style={{
                position: "relative",
                width: 56, height: 56,
                flexShrink: 0,
                cursor: uploadingAvatar ? "wait" : "pointer"
              }}
              onMouseEnter={() => setAvatarHover(true)}
              onMouseLeave={() => setAvatarHover(false)}
              onClick={() => { if (!uploadingAvatar && avatarFileInputRef.current) avatarFileInputRef.current.click(); }}>
              {avatarUrl ? (
                <img src={avatarUrl} alt="Avatar"
                  style={{
                    width: 56, height: 56,
                    borderRadius: 14,
                    objectFit: "cover",
                    boxShadow: "0 4px 14px rgba(240, 192, 64, 0.25)",
                    border: "2px solid rgba(240, 192, 64, 0.4)"
                  }}
                  onError={(e) => { e.target.style.display = "none"; }}
                />
              ) : (
                <div style={{
                  width: 56, height: 56,
                  background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)",
                  borderRadius: 14,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 22,
                  fontWeight: 700,
                  color: "#0a0a0a",
                  boxShadow: "0 4px 14px rgba(240, 192, 64, 0.25)"
                }}>
                  {(params.entreprise || "M E").split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase()}
                </div>
              )}
              {/* Overlay au hover */}
              {(avatarHover || uploadingAvatar) && (
                <div style={{
                  position: "absolute",
                  inset: 0,
                  background: "rgba(0, 0, 0, 0.55)",
                  borderRadius: 14,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  backdropFilter: "blur(2px)",
                  transition: "opacity 0.18s"
                }}>
                  {uploadingAvatar ? (
                    <span style={{ display: "inline-block", width: 18, height: 18, border: "2px solid rgba(255,255,255,0.25)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                  ) : (
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
                      <circle cx="12" cy="13" r="4"/>
                    </svg>
                  )}
                </div>
              )}
              {/* Input file cache */}
              <input
                ref={avatarFileInputRef}
                type="file"
                accept="image/*"
                onChange={handleAvatarUpload}
                style={{ display: "none" }}
              />
              {/* Bouton supprimer (si photo et hover) */}
              {avatarUrl && avatarHover && !uploadingAvatar && (
                <button onClick={(e) => { e.stopPropagation(); handleAvatarDelete(); }}
                  title="Supprimer la photo"
                  style={{
                    position: "absolute",
                    top: -6, right: -6,
                    width: 22, height: 22, borderRadius: "50%",
                    background: "#ef4444",
                    border: "2px solid #0a0a0a",
                    color: "#fff",
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    padding: 0,
                    boxShadow: "0 2px 6px rgba(0, 0, 0, 0.3)"
                  }}>
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              )}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: 700, fontSize: 18, color: "#e8eaf2", marginBottom: 6, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {params.entreprise || "Mon entreprise"}
              </div>
              <div style={{
                display: "inline-flex", alignItems: "center", gap: 6,
                background: "rgba(62, 207, 142, 0.1)",
                border: "1px solid rgba(62, 207, 142, 0.25)",
                borderRadius: 999,
                padding: "4px 11px",
                fontSize: 11,
                fontWeight: 600,
                color: "#3ecf8e",
                letterSpacing: "0.02em",
                textTransform: "uppercase"
              }}>
                <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#3ecf8e" }}></span>
                Plan Pro
              </div>
            </div>
          </div>

          {/* Accordeon Infos entreprise */}
          <div style={{
            background: "rgba(255, 255, 255, 0.02)",
            border: "1px solid rgba(255, 255, 255, 0.05)",
            borderRadius: 12,
            marginBottom: 16,
            overflow: "hidden",
            transition: "border-color 0.15s"
          }}>
            <button
              onClick={() => setShowInfosEntreprise(!showInfosEntreprise)}
              style={{
                width: "100%",
                background: "transparent",
                border: "none",
                padding: "14px 16px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 12,
                color: "#e8eaf2",
                transition: "background 0.15s"
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{
                  width: 28, height: 28, borderRadius: 7,
                  background: "rgba(240, 192, 64, 0.1)",
                  border: "1px solid rgba(240, 192, 64, 0.2)",
                  display: "inline-flex", alignItems: "center", justifyContent: "center"
                }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M3 21h18M3 7h18M3 14h18M5 21V3h14v18"/>
                  </svg>
                </div>
                <div style={{ textAlign: "left" }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "#e8eaf2", marginBottom: 1 }}>Infos entreprise</div>
                  <div style={{ fontSize: 11, color: "#7a7d92" }}>{showInfosEntreprise ? "Cliquez pour replier" : "Cliquez pour déplier"}</div>
                </div>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"
                style={{ transform: showInfosEntreprise ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.2s" }}>
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </button>
            {showInfosEntreprise && (
              <div style={{
                padding: "0 16px 16px 16px",
                borderTop: "1px solid rgba(255, 255, 255, 0.04)",
                animation: "fadeInUp 0.2s ease-out"
              }}>
                {/* Bloc 1 - Identite legale */}
                <div style={{ marginTop: 16, marginBottom: 14 }}>
                  <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 10 }}>Identite</div>
                  <div style={{ display: "grid", gap: 10 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 12px", background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8 }}>
                      <span style={{ color: "#9ca0b8", fontSize: 12 }}>Nom de l'entreprise</span>
                      <span style={{ color: "#e8eaf2", fontSize: 13, fontWeight: 500, textAlign: "right" }}>{params.entreprise || <span style={{ color: "#545870", fontStyle: "italic" }}>Non renseigne</span>}</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 12px", background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8 }}>
                      <span style={{ color: "#9ca0b8", fontSize: 12 }}>SIRET</span>
                      <span style={{ color: "#e8eaf2", fontSize: 13, fontWeight: 500, fontVariantNumeric: "tabular-nums", textAlign: "right" }}>{params.siret || <span style={{ color: "#545870", fontStyle: "italic" }}>Non renseigne</span>}</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", padding: "10px 12px", background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8, gap: 12 }}>
                      <span style={{ color: "#9ca0b8", fontSize: 12, flexShrink: 0 }}>Adresse</span>
                      <span style={{ color: "#e8eaf2", fontSize: 13, fontWeight: 500, textAlign: "right" }}>{params.adresse || <span style={{ color: "#545870", fontStyle: "italic" }}>Non renseignee</span>}</span>
                    </div>
                  </div>
                </div>

                {/* Bloc 2 - Parametres financiers */}
                <div style={{ marginBottom: 6 }}>
                  <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 10 }}>Paramètres financiers</div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>
                    <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8, padding: 12, textAlign: "center" }}>
                      <div style={{ color: "#7a7d92", fontSize: 10, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.04em" }}>Taux horaire</div>
                      <div style={{ color: "#e8eaf2", fontSize: 18, fontWeight: 700, letterSpacing: "-0.01em" }}>{params.tauxHoraire}<span style={{ color: "#7a7d92", fontSize: 12, marginLeft: 2 }}>EUR/h</span></div>
                    </div>
                    <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8, padding: 12, textAlign: "center" }}>
                      <div style={{ color: "#7a7d92", fontSize: 10, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.04em" }}>TVA</div>
                      <div style={{ color: "#e8eaf2", fontSize: 18, fontWeight: 700, letterSpacing: "-0.01em" }}>{params.tva}<span style={{ color: "#7a7d92", fontSize: 12, marginLeft: 2 }}>%</span></div>
                    </div>
                    <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 255, 255, 0.04)", borderRadius: 8, padding: 12, textAlign: "center" }}>
                      <div style={{ color: "#7a7d92", fontSize: 10, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.04em" }}>Marge</div>
                      <div style={{ color: "#e8eaf2", fontSize: 18, fontWeight: 700, letterSpacing: "-0.01em" }}>{params.marge}<span style={{ color: "#7a7d92", fontSize: 12, marginLeft: 2 }}>%</span></div>
                    </div>
                  </div>
                </div>

                {/* Lien vers Parametres */}
                <div style={{ marginTop: 14, paddingTop: 12, borderTop: "1px solid rgba(255, 255, 255, 0.04)", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
                  <div style={{ color: "#545870", fontSize: 11, lineHeight: 1.4 }}>
                    Pour modifier ces informations,<br/>rendez-vous dans <span style={{ color: "#9ca0b8" }}>Paramètres</span>.
                  </div>
                  <button onClick={() => setActiveTab("parametres")}
                    style={{
                      background: "rgba(240, 192, 64, 0.08)",
                      border: "1px solid rgba(240, 192, 64, 0.25)",
                      color: "#f0c040",
                      borderRadius: 8,
                      padding: "7px 13px",
                      fontSize: 12,
                      fontWeight: 600,
                      cursor: "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 6,
                      transition: "all 0.15s",
                      flexShrink: 0
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(240, 192, 64, 0.14)"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(240, 192, 64, 0.08)"; }}>
                    Modifier
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
                    </svg>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* 5 stats responsive */}
          {(() => {
            // Calculs
            const now = new Date();
            const thisMonth = now.getMonth();
            const thisYear = now.getFullYear();
            const projetsThisMonth = projects.filter(p => {
              if (!p.created_at) return false;
              const d = new Date(p.created_at);
              return d.getMonth() === thisMonth && d.getFullYear() === thisYear;
            });
            // Tokens calcules depuis usage_logs (survit à la suppression de projets)
            const tokensTotal = usageLogs.reduce((sum, l) => sum + (l.tokens_in || 0) + (l.tokens_out || 0), 0);
            const logsThisMonth = usageLogs.filter(l => {
              if (!l.created_at) return false;
              const d = new Date(l.created_at);
              return d.getMonth() === thisMonth && d.getFullYear() === thisYear;
            });
            const tokensMonth = logsThisMonth.reduce((sum, l) => sum + (l.tokens_in || 0) + (l.tokens_out || 0), 0);
            // CO2 : approximation Anthropic ~ 0.000175 g par token (cumul in+out)
            const co2TotalG = tokensTotal * 0.000175;
            const co2MonthG = tokensMonth * 0.000175;
            const formatTokens = (n) => n >= 1000000 ? (n / 1000000).toFixed(1) + "M" : n >= 1000 ? (n / 1000).toFixed(1) + "k" : String(n);
            const formatCO2 = (g) => g >= 1000 ? (g / 1000).toFixed(2) + " kg" : g.toFixed(1) + " g";

            const stats = [
              {
                label: "Devis ce mois",
                val: projetsThisMonth.length,
                sub: null,
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 11H7v8h2v-8zm6 0h-2v8h2v-8zM11 11v8h2v-8h-2zM4 7h16M5 7v14h14V7M9 4h6v3H9z"/></svg>,
                color: "#60a5fa"
              },
              {
                label: "Total devis",
                val: projects.length,
                sub: null,
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>,
                color: "#3ecf8e"
              },
              {
                label: "Jours abo",
                val: "23",
                sub: null,
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>,
                color: "#a78bfa"
              },
              {
                label: "Tokens IA",
                val: formatTokens(tokensTotal),
                sub: tokensMonth > 0 ? formatTokens(tokensMonth) + " ce mois" : "0 ce mois",
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
                color: "#f0c040"
              },
              {
                label: "Empreinte CO2",
                val: formatCO2(co2TotalG),
                sub: co2MonthG > 0 ? formatCO2(co2MonthG) + " ce mois" : "0 g ce mois",
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C7 8 17 8 17 8z"/></svg>,
                color: "#3ecf8e"
              }
            ];

            return (
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
                gap: 10
              }}>
                {stats.map(s => (
                  <div key={s.label} style={{
                    background: "rgba(255, 255, 255, 0.02)",
                    borderRadius: 12,
                    padding: 14,
                    border: "1px solid rgba(255, 255, 255, 0.05)",
                    transition: "border-color 0.15s",
                    display: "flex",
                    flexDirection: "column"
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)"; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.05)"; }}>
                    <div style={{
                      width: 28, height: 28, borderRadius: 7,
                      background: "rgba(255, 255, 255, 0.04)",
                      border: "1px solid rgba(255, 255, 255, 0.06)",
                      display: "inline-flex", alignItems: "center", justifyContent: "center",
                      marginBottom: 10
                    }}>
                      {s.icon}
                    </div>
                    <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: 4 }}>{s.label}</div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: "#f5f6fa", letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums", lineHeight: 1.1 }}>{s.val}</div>
                    {s.sub && (
                      <div style={{ marginTop: 6, color: "#545870", fontSize: 10, fontVariantNumeric: "tabular-nums" }}>{s.sub}</div>
                    )}
                  </div>
                ))}
              </div>
            );
          })()}
        </div>

        {/* Section Plans d'abonnement */}
        <div style={{ marginTop: 20 }}>
          <div style={{ marginBottom: 14 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, letterSpacing: "-0.01em", marginBottom: 2 }}>Votre abonnement</h3>
            <div style={{ color: "#7a7d92", fontSize: 12 }}>Plan actuel et offres à venir</div>
          </div>

          {/* PLAN ACTUEL : DEVIA Charpente */}
          <div style={{
            background: "linear-gradient(135deg, rgba(240, 192, 64, 0.06) 0%, rgba(240, 192, 64, 0.02) 100%)",
            border: "1px solid rgba(240, 192, 64, 0.25)",
            borderRadius: 14,
            padding: 20,
            marginBottom: 14,
            boxShadow: "0 0 0 1px rgba(255,255,255,0.02) inset"
          }}>
            <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between", gap: 14, marginBottom: 16, flexWrap: "wrap" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, flex: "1 1 auto", minWidth: 0 }}>
                <div style={{
                  width: 44, height: 44,
                  background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)",
                  borderRadius: 11,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0,
                  boxShadow: "0 4px 14px rgba(240, 192, 64, 0.25)"
                }}>
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0a0a0a" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
                  </svg>
                </div>
                <div style={{ minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3, flexWrap: "wrap" }}>
                    <span style={{ fontSize: 17, fontWeight: 700, color: "#f5f6fa", letterSpacing: "-0.01em" }}>DEVIA Charpente</span>
                    <span style={{
                      display: "inline-flex", alignItems: "center", gap: 5,
                      background: "rgba(62, 207, 142, 0.12)",
                      border: "1px solid rgba(62, 207, 142, 0.3)",
                      borderRadius: 999,
                      padding: "2px 9px",
                      fontSize: 10,
                      fontWeight: 600,
                      color: "#3ecf8e",
                      letterSpacing: "0.04em",
                      textTransform: "uppercase"
                    }}>
                      <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#3ecf8e" }}></span>
                      Plan actuel
                    </span>
                  </div>
                  <div style={{ color: "#9ca0b8", fontSize: 12 }}>Devis de charpente assistés par intelligence artificielle</div>
                </div>
              </div>
              <div style={{ textAlign: "right", flexShrink: 0 }}>
                <div style={{ fontSize: 11, color: "#7a7d92", marginBottom: 2 }}>Installation</div>
                <div style={{ fontSize: 16, fontWeight: 700, color: "#f5f6fa", fontVariantNumeric: "tabular-nums" }}>2 000 <span style={{ fontSize: 11, color: "#7a7d92", fontWeight: 500 }}>EUR</span></div>
                <div style={{ fontSize: 11, color: "#7a7d92", marginTop: 4 }}>puis</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "#f0c040", fontVariantNumeric: "tabular-nums" }}>35 <span style={{ fontSize: 11, color: "#7a7d92", fontWeight: 500 }}>EUR/mois</span></div>
              </div>
            </div>

            {/* Features */}
            <div style={{
              background: "rgba(0, 0, 0, 0.15)",
              border: "1px solid rgba(255, 255, 255, 0.04)",
              borderRadius: 10,
              padding: 14,
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: 8
            }}>
              {[
                "Devis IA illimites",
                "Visualisation 3D",
                "Catalogue personnalise",
                "Calculs Eurocode",
                "Export PDF"
              ].map(f => (
                <div key={f} style={{ display: "flex", alignItems: "center", gap: 8, color: "#e8eaf2", fontSize: 12 }}>
                  <div style={{
                    width: 18, height: 18, borderRadius: "50%",
                    background: "rgba(62, 207, 142, 0.12)",
                    border: "1px solid rgba(62, 207, 142, 0.3)",
                    display: "inline-flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0
                  }}>
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  </div>
                  <span>{f}</span>
                </div>
              ))}
            </div>
          </div>

          {/* AUTRES PLANS DEVIA : Coming soon */}
          <div style={{ marginTop: 18, marginBottom: 8 }}>
            <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 10 }}>Autres plans DEVIA</div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
            {[
              {
                nom: "DEVIA Menuiserie",
                desc: "Devis fenetres, portes, escaliers",
                color1: "#60a5fa",
                color2: "#3b82f6",
                icon: (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="1"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="12" y1="3" x2="12" y2="21"/>
                  </svg>
                )
              },
              {
                nom: "DEVIA Maçonnerie",
                desc: "Devis gros oeuvre, fondations, murs",
                color1: "#a78bfa",
                color2: "#8b5cf6",
                icon: (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="14" width="6" height="6" rx="0.5"/><rect x="9" y="14" width="6" height="6" rx="0.5"/><rect x="16" y="14" width="6" height="6" rx="0.5"/><rect x="5" y="7" width="6" height="6" rx="0.5"/><rect x="12" y="7" width="6" height="6" rx="0.5"/>
                  </svg>
                )
              }
            ].map(plan => (
              <div key={plan.nom} style={{
                background: "rgba(255, 255, 255, 0.02)",
                border: "1px solid rgba(255, 255, 255, 0.05)",
                borderRadius: 12,
                padding: 16,
                transition: "all 0.18s",
                position: "relative",
                overflow: "hidden"
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.03)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.05)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)"; }}>
                {/* Halo decoratif */}
                <div style={{
                  position: "absolute",
                  top: -30, right: -30,
                  width: 100, height: 100,
                  background: "radial-gradient(circle, " + plan.color1 + "15 0%, transparent 70%)",
                  pointerEvents: "none"
                }}></div>
                <div style={{ display: "flex", alignItems: "center", gap: 11, marginBottom: 10, position: "relative" }}>
                  <div style={{
                    width: 38, height: 38,
                    background: "linear-gradient(135deg, " + plan.color1 + "30 0%, " + plan.color2 + "15 100%)",
                    border: "1px solid " + plan.color1 + "40",
                    borderRadius: 10,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    color: plan.color1,
                    flexShrink: 0
                  }}>
                    {plan.icon}
                  </div>
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div style={{ fontSize: 14, fontWeight: 700, color: "#e8eaf2", letterSpacing: "-0.005em", marginBottom: 2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{plan.nom}</div>
                    <div style={{ fontSize: 11, color: "#7a7d92", lineHeight: 1.4 }}>{plan.desc}</div>
                  </div>
                </div>
                <div style={{
                  display: "inline-flex", alignItems: "center", gap: 6,
                  background: "rgba(255, 255, 255, 0.04)",
                  border: "1px dashed rgba(255, 255, 255, 0.1)",
                  borderRadius: 999,
                  padding: "5px 12px",
                  fontSize: 11,
                  fontWeight: 500,
                  color: "#9ca0b8",
                  letterSpacing: "0.02em"
                }}>
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                  </svg>
                  Disponible bientot
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )}

  </main>

  {renameProjectModal && (
    <div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0, 0, 0, 0.55)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 1000, padding: 16,
        animation: "fadeInUp 0.18s ease-out"
      }}
      onClick={(e) => { if (e.target === e.currentTarget && !savingRename) { setRenameProjectModal(null); setRenameProjectName(""); setRenameError(null); } }}>
      <div style={{
        background: "rgba(22, 25, 35, 0.95)",
        backdropFilter: "blur(24px) saturate(140%)",
        WebkitBackdropFilter: "blur(24px) saturate(140%)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: 20,
        padding: 28,
        maxWidth: 480,
        width: "100%",
        boxShadow: "0 24px 64px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,0.04) inset"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: 24, gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>Renommer le projet</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>Modifiez le nom de ce projet</div>
          </div>
          <button onClick={() => { if (!savingRename) { setRenameProjectModal(null); setRenameProjectName(""); setRenameError(null); } }}
            style={{
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              color: "#7a7d92",
              cursor: savingRename ? "not-allowed" : "pointer",
              borderRadius: 10,
              padding: 8,
              flexShrink: 0,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.15s",
              opacity: savingRename ? 0.5 : 1
            }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Nom du projet <span style={{ color: "#f0c040" }}>*</span></label>
          <input
            type="text"
            value={renameProjectName}
            onChange={(e) => setRenameProjectName(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !savingRename) handleRenameProject(); }}
            placeholder="Ex: Maison Dupont, Chantier Lyon - M. Martin..."
            autoFocus
            disabled={savingRename}
            style={inputStyle}
            maxLength={120}
          />
        </div>

        {renameError && (
          <div style={{
            background: "rgba(239, 68, 68, 0.08)",
            border: "1px solid rgba(239, 68, 68, 0.25)",
            borderRadius: 10,
            padding: 14,
            color: "#fca5a5",
            fontSize: 13,
            display: "flex",
            alignItems: "start",
            gap: 10,
            marginBottom: 16
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <div>{renameError}</div>
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12, paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <button onClick={() => { setRenameProjectModal(null); setRenameProjectName(""); setRenameError(null); }}
            disabled={savingRename}
            style={{ ...btnSecondary, opacity: savingRename ? 0.5 : 1 }}>
            Annuler
          </button>
          <button onClick={handleRenameProject}
            disabled={savingRename || !renameProjectName.trim()}
            style={{
              ...btnPrimary,
              padding: "11px 22px",
              opacity: (savingRename || !renameProjectName.trim()) ? 0.5 : 1,
              cursor: (savingRename || !renameProjectName.trim()) ? "not-allowed" : "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              boxShadow: savingRename ? "none" : "0 4px 14px rgba(240, 192, 64, 0.25)"
            }}>
            {savingRename ? (
              <>
                <span style={{ display: "inline-block", width: 13, height: 13, border: "2px solid rgba(10,10,10,0.25)", borderTopColor: "#0a0a0a", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                <span>Sauvegardé...</span>
              </>
            ) : (
              <>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                Enregistrer
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )}

  {deleteConfirmGroup && (
    <div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0, 0, 0, 0.55)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 1001, padding: 16,
        animation: "fadeInUp 0.18s ease-out"
      }}
      onClick={(e) => { if (e.target === e.currentTarget && !deletingGroup) setDeleteConfirmGroup(null); }}>
      <div style={{
        background: "rgba(22, 25, 35, 0.95)",
        backdropFilter: "blur(24px) saturate(140%)",
        WebkitBackdropFilter: "blur(24px) saturate(140%)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: 20,
        padding: 28,
        maxWidth: 440,
        width: "100%",
        boxShadow: "0 24px 64px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,0.04) inset"
      }}>
        <div style={{ display: "flex", alignItems: "start", gap: 14, marginBottom: 20 }}>
          <div style={{
            width: 40, height: 40, borderRadius: 10,
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.25)",
            display: "flex", alignItems: "center", justifyContent: "center",
            flexShrink: 0
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>Supprimer le groupe ?</h2>
            <div style={{ color: "#9ca0b8", fontSize: 13, lineHeight: 1.55 }}>
              Le groupe <span style={{ color: "#e8eaf2", fontWeight: 600 }}>&quot;{deleteConfirmGroup.nom}&quot;</span> sera supprime. Les projets associes ne seront pas supprimes, ils reviendront a &quot;Tous&quot; sans groupe.
            </div>
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12, paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <button onClick={() => setDeleteConfirmGroup(null)}
            disabled={deletingGroup}
            style={{ ...btnSecondary, opacity: deletingGroup ? 0.5 : 1 }}>
            Annuler
          </button>
          <button onClick={handleDeleteGroup}
            disabled={deletingGroup}
            style={{
              background: "#ef4444",
              color: "#fff",
              border: "1px solid #ef4444",
              borderRadius: 10,
              padding: "11px 22px",
              fontSize: 13,
              fontWeight: 600,
              cursor: deletingGroup ? "not-allowed" : "pointer",
              opacity: deletingGroup ? 0.7 : 1,
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              transition: "background 0.15s",
              boxShadow: "0 4px 14px rgba(239, 68, 68, 0.25)"
            }}
            onMouseEnter={(e) => { if (!deletingGroup) e.currentTarget.style.background = "#dc2626"; }}
            onMouseLeave={(e) => { if (!deletingGroup) e.currentTarget.style.background = "#ef4444"; }}>
            {deletingGroup ? (
              <>
                <span style={{ display: "inline-block", width: 13, height: 13, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                <span>Suppression...</span>
              </>
            ) : (
              <>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                </svg>
                Supprimer
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )}

  {showGroupModal && (
    <div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0, 0, 0, 0.55)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 1000, padding: 16,
        animation: "fadeInUp 0.18s ease-out"
      }}
      onClick={(e) => { if (e.target === e.currentTarget && !savingGroup) { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); setEditingGroupId(null); } }}>
      <div style={{
        background: "rgba(22, 25, 35, 0.95)",
        backdropFilter: "blur(24px) saturate(140%)",
        WebkitBackdropFilter: "blur(24px) saturate(140%)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: 20,
        padding: 28,
        maxWidth: 440,
        width: "100%",
        boxShadow: "0 24px 64px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,0.04) inset"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: 24, gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>{editingGroupId ? "Renommer le groupe" : "Nouveau groupe"}</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>{editingGroupId ? "Modifiez le nom du groupe" : "Organisez vos projets par categorie"}</div>
          </div>
          <button onClick={() => { if (!savingGroup) { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); setEditingGroupId(null); } }}
            style={{
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              color: "#7a7d92",
              cursor: savingGroup ? "not-allowed" : "pointer",
              borderRadius: 10,
              padding: 8,
              flexShrink: 0,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.15s",
              opacity: savingGroup ? 0.5 : 1
            }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Nom du groupe <span style={{ color: "#f0c040" }}>*</span></label>
          <input
            type="text"
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !savingGroup) handleCreateGroup(); }}
            placeholder="Ex: Maisons neuves, Rénovations..."
            autoFocus
            disabled={savingGroup}
            style={inputStyle}
            maxLength={50}
          />
        </div>

        {groupError && (
          <div style={{
            background: "rgba(239, 68, 68, 0.08)",
            border: "1px solid rgba(239, 68, 68, 0.25)",
            borderRadius: 10,
            padding: 14,
            color: "#fca5a5",
            fontSize: 13,
            display: "flex",
            alignItems: "start",
            gap: 10,
            marginBottom: 16
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <div>{groupError}</div>
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12, paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
          <button onClick={() => { setShowGroupModal(false); setNewGroupName(""); setGroupError(null); setEditingGroupId(null); }}
            disabled={savingGroup}
            style={{ ...btnSecondary, opacity: savingGroup ? 0.5 : 1 }}>
            Annuler
          </button>
          <button onClick={handleCreateGroup}
            disabled={savingGroup || !newGroupName.trim()}
            style={{
              ...btnPrimary,
              padding: "11px 22px",
              opacity: (savingGroup || !newGroupName.trim()) ? 0.5 : 1,
              cursor: (savingGroup || !newGroupName.trim()) ? "not-allowed" : "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              boxShadow: savingGroup ? "none" : "0 4px 14px rgba(240, 192, 64, 0.25)"
            }}>
            {savingGroup ? (
              <>
                <span style={{ display: "inline-block", width: 13, height: 13, border: "2px solid rgba(10,10,10,0.25)", borderTopColor: "#0a0a0a", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                <span>{editingGroupId ? "Sauvegardé..." : "Creation..."}</span>
              </>
            ) : (
              <>
                {editingGroupId ? (
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                ) : (
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                  </svg>
                )}
                {editingGroupId ? "Enregistrer" : "Creer"}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )}

  {/* Pop-up de chargement avec progression */}
  {loading && (
    <div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0, 0, 0, 0.65)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 2000, padding: 16,
        animation: "fadeInUp 0.18s ease-out"
      }}>
      <div style={{
        background: "rgba(22, 25, 35, 0.98)",
        backdropFilter: "blur(24px) saturate(140%)",
        WebkitBackdropFilter: "blur(24px) saturate(140%)",
        border: "1px solid rgba(240, 192, 64, 0.2)",
        borderRadius: 20,
        padding: 32,
        maxWidth: 480,
        width: "100%",
        boxShadow: "0 24px 64px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255,255,255,0.04) inset, 0 0 32px rgba(240, 192, 64, 0.08)"
      }}>
        {/* En-tete */}
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 24 }}>
          <div style={{
            width: 44, height: 44, borderRadius: 12,
            background: "linear-gradient(135deg, rgba(240, 192, 64, 0.18), rgba(240, 192, 64, 0.05))",
            border: "1px solid rgba(240, 192, 64, 0.3)",
            display: "flex", alignItems: "center", justifyContent: "center"
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" style={{ display: "none" }}/>
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>Génération en cours</h2>
            <div style={{ color: "#7a7d92", fontSize: 12 }}>DEVIA prépare votre devis...</div>
          </div>
        </div>

        {/* Jauge de progression */}
        <div style={{ marginBottom: 24 }}>
          <div style={{
            width: "100%",
            height: 6,
            background: "rgba(255, 255, 255, 0.06)",
            borderRadius: 999,
            overflow: "hidden",
            position: "relative"
          }}>
            <div style={{
              height: "100%",
              width: loadingProgress + "%",
              background: "linear-gradient(90deg, #e0a020 0%, #f0c040 50%, #fcd34d 100%)",
              borderRadius: 999,
              transition: "width 0.4s ease-out",
              boxShadow: "0 0 8px rgba(240, 192, 64, 0.5)"
            }}/>
          </div>
          <div style={{ marginTop: 8, display: "flex", justifyContent: "space-between", fontSize: 11, color: "#7a7d92" }}>
            <span>Progression</span>
            <span style={{ fontFamily: "ui-monospace, monospace", color: "#f0c040", fontWeight: 600 }}>{loadingProgress}%</span>
          </div>
        </div>

        {/* Liste des etapes */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {[
            { icon: "search", label: "Analyse de la demande" },
            { icon: "globe", label: "Calcul de la zone climatique" },
            { icon: "cube", label: "Génération du modele 3D" },
            { icon: "brain", label: "Création du devis IA" },
            { icon: "check-circle", label: "Finalisation" }
          ].map((step, idx) => {
            const status = idx < loadingStep ? "done" : idx === loadingStep ? "active" : "pending";
            const color = status === "done" ? "#3ecf8e" : status === "active" ? "#f0c040" : "#545870";
            const bgColor = status === "done" ? "rgba(62, 207, 142, 0.08)" : status === "active" ? "rgba(240, 192, 64, 0.08)" : "rgba(255, 255, 255, 0.02)";
            const borderColor = status === "done" ? "rgba(62, 207, 142, 0.2)" : status === "active" ? "rgba(240, 192, 64, 0.25)" : "rgba(255, 255, 255, 0.04)";
            return (
              <div key={idx} style={{
                display: "flex", alignItems: "center", gap: 12,
                background: bgColor,
                border: "1px solid " + borderColor,
                borderRadius: 12,
                padding: "10px 14px",
                transition: "all 0.25s"
              }}>
                <div style={{
                  width: 30, height: 30, borderRadius: 8,
                  background: status === "active" ? "rgba(240, 192, 64, 0.15)" : status === "done" ? "rgba(62, 207, 142, 0.15)" : "rgba(255, 255, 255, 0.04)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0,
                  transition: "all 0.25s"
                }}>
                  {status === "done" ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  ) : status === "active" ? (
                    <span style={{
                      display: "inline-block",
                      width: 14, height: 14,
                      border: "2px solid rgba(240, 192, 64, 0.25)",
                      borderTopColor: "#f0c040",
                      borderRadius: "50%",
                      animation: "spin 0.7s linear infinite"
                    }}></span>
                  ) : (
                    step.icon === "search" ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                      </svg>
                    ) : step.icon === "globe" ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
                      </svg>
                    ) : step.icon === "cube" ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
                      </svg>
                    ) : step.icon === "brain" ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.96.44 2.5 2.5 0 01-2.96-3.08 3 3 0 01-.34-5.58 2.5 2.5 0 011.32-4.24 2.5 2.5 0 014.44-1.04zM14.5 2A2.5 2.5 0 0012 4.5v15a2.5 2.5 0 004.96.44 2.5 2.5 0 002.96-3.08 3 3 0 00.34-5.58 2.5 2.5 0 00-1.32-4.24 2.5 2.5 0 00-4.44-1.04z"/>
                      </svg>
                    ) : (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
                      </svg>
                    )
                  )}
                </div>
                <div style={{
                  flex: 1,
                  fontSize: 13,
                  fontWeight: status === "active" ? 600 : 500,
                  color: status === "pending" ? "#7a7d92" : "#e8eaf2",
                  transition: "color 0.25s"
                }}>
                  {step.label}
                </div>
                {status === "active" && (
                  <span style={{ fontSize: 11, color: "#f0c040", fontWeight: 600, letterSpacing: "0.02em" }}>EN COURS</span>
                )}
              </div>
            );
          })}
        </div>

        {/* Pied de page */}
        <div style={{
          marginTop: 20,
          paddingTop: 16,
          borderTop: "1px solid rgba(255, 255, 255, 0.05)",
          fontSize: 11,
          color: "#545870",
          textAlign: "center",
          letterSpacing: "0.02em"
        }}>
          Cela peut prendre quelques secondes
        </div>
      </div>
    </div>
  )}

  {showAddCatalogModal && (
    <div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0, 0, 0, 0.55)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 1000, padding: 16,
        animation: "fadeInUp 0.18s ease-out"
      }}
      onClick={(e) => { if (e.target === e.currentTarget) { setShowAddCatalogModal(false); resetCatalogForm(); } }}>
      <div style={{
        background: "rgba(22, 25, 35, 0.95)",
        backdropFilter: "blur(24px) saturate(140%)",
        WebkitBackdropFilter: "blur(24px) saturate(140%)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: 20,
        padding: 28,
        maxWidth: 560,
        width: "100%",
        maxHeight: "90vh",
        overflowY: "auto",
        boxShadow: "0 24px 64px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,0.04) inset"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: 24, gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>{editingCatalogId ? "Modifier un matériau" : "Ajouter un matériau"}</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>{editingCatalogId ? "Mettez à jour les informations" : "Ajoutez un prix à votre catalogue personnel"}</div>
          </div>
          <button onClick={() => { setShowAddCatalogModal(false); resetCatalogForm(); }}
            style={{
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              color: "#7a7d92",
              cursor: "pointer",
              borderRadius: 10,
              padding: 8,
              flexShrink: 0,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.15s"
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)"; e.currentTarget.style.color = "#e8eaf2"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.04)"; e.currentTarget.style.color = "#7a7d92"; }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div style={{ display: "grid", gap: 14 }}>
          {/* Designation - avec detection intelligente */}
          <div>
            <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Désignation <span style={{ color: "#f0c040" }}>*</span></label>
            <input type="text" value={catalogForm.designation}
              onChange={(e) => {
                const v = e.target.value;
                setCatalogForm({ ...catalogForm, designation: v });
                setDetectedType(detectMateriauType(v));
              }}
              placeholder="Ex: Chevron sapin C24, Tuile mecanique, Vis 6x180..."
              style={inputStyle} />
            {catalogForm.designation.trim().length >= 2 && (() => {
              const activeType = typeOverride || detectedType;
              const config = MATERIAL_TYPES[activeType];
              const cBg = activeType === "outillage" ? "251, 146, 60" : activeType === "couverture" ? "96, 165, 250" : activeType === "visserie" ? "252, 211, 77" : activeType === "isolation" ? "62, 207, 142" : activeType === "epi" ? "239, 68, 68" : activeType === "bois_structure" || activeType === "bois_ossature" ? "167, 139, 250" : "122, 125, 146";
              return (
                <div style={{ marginTop: 8, position: "relative", display: "inline-block" }}>
                  <button onClick={(e) => { e.preventDefault(); e.stopPropagation(); setShowTypeMenu(!showTypeMenu); }}
                    type="button"
                    style={{
                      background: "rgba(" + cBg + ", 0.12)",
                      border: "1px solid " + config.color + "40",
                      color: config.color,
                      borderRadius: 999,
                      padding: "4px 10px",
                      fontSize: 11,
                      fontWeight: 600,
                      cursor: "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 6,
                      letterSpacing: "0.02em"
                    }}>
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Type détecté : {config.label}
                    <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.7, marginLeft: 2 }}>
                      <polyline points="6 9 12 15 18 9"/>
                    </svg>
                  </button>
                  {showTypeMenu && (
                    <div style={{
                      position: "absolute",
                      top: "calc(100% + 6px)",
                      left: 0,
                      background: "rgba(22, 25, 35, 0.98)",
                      backdropFilter: "blur(20px) saturate(140%)",
                      WebkitBackdropFilter: "blur(20px) saturate(140%)",
                      border: "1px solid rgba(255, 255, 255, 0.08)",
                      borderRadius: 10,
                      padding: 4,
                      minWidth: 200,
                      boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
                      zIndex: 100
                    }}>
                      <div style={{ padding: "6px 12px 4px 12px", color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Changer le type</div>
                      {Object.entries(MATERIAL_TYPES).map(([t2, c]) => (
                        <button key={t2} type="button"
                          onClick={(ev) => { ev.preventDefault(); ev.stopPropagation(); setTypeOverride(t2); setShowTypeMenu(false); }}
                          style={{
                            width: "100%", background: "transparent", border: "none",
                            color: activeType === t2 ? c.color : "#e8eaf2",
                            textAlign: "left", padding: "7px 12px",
                            fontSize: 12, cursor: "pointer", borderRadius: 7,
                            display: "flex", alignItems: "center", gap: 7, transition: "background 0.12s",
                            fontWeight: activeType === t2 ? 600 : 500
                          }}
                          onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)"; }}
                          onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                          <span style={{ width: 6, height: 6, borderRadius: "50%", background: c.color, flexShrink: 0 }}></span>
                          {c.label}
                          {activeType === t2 && (
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: "auto" }}>
                              <polyline points="20 6 9 17 4 12"/>
                            </svg>
                          )}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })()}
          </div>

          {/* Dimensions et Unite - conditionnels */}
          {(() => {
            const activeType = typeOverride || detectedType;
            const config = MATERIAL_TYPES[activeType] || MATERIAL_TYPES.autre;
            const labels = { ml: "ml (mètre linéaire)", m2: "m2 (mètre carré)", m3: "m3 (mètre cube)", u: "u (unite)", kg: "kg (kilo)", h: "h (heure)", forfait: "forfait" };
            const others = ["ml", "m2", "m3", "u", "kg", "h", "forfait"].filter(u => !config.suggestedUnits.includes(u));
            return (
              <div style={{ display: "grid", gridTemplateColumns: config.showDimensions ? "1fr 1fr" : "1fr", gap: 12 }}>
                {config.showDimensions && (
                  <div>
                    <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Dimensions</label>
                    <input type="text" value={catalogForm.dimensions}
                      onChange={(e) => setCatalogForm({ ...catalogForm, dimensions: e.target.value })}
                      placeholder={config.placeholder || "Ex: 75x175 mm"}
                      style={inputStyle} />
                  </div>
                )}
                <div>
                  <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Unite <span style={{ color: "#f0c040" }}>*</span></label>
                  <select value={catalogForm.unite}
                    onChange={(e) => setCatalogForm({ ...catalogForm, unite: e.target.value })}
                    style={{ ...inputStyle, cursor: "pointer" }}>
                    {config.suggestedUnits.map(u => <option key={u} value={u}>{labels[u]}</option>)}
                    {others.map(u => <option key={u} value={u}>{labels[u]}</option>)}
                  </select>
                </div>
              </div>
            );
          })()}

          {/* Prix HT */}
          <div>
            <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Prix HT <span style={{ color: "#7a7d92", fontWeight: 400, textTransform: "none" }}>(EUR)</span> <span style={{ color: "#f0c040" }}>*</span></label>
            <input type="number" step="0.01" min="0" value={catalogForm.prix_ht}
              onChange={(e) => setCatalogForm({ ...catalogForm, prix_ht: e.target.value })}
              placeholder="Ex: 12.50"
              style={inputStyle} />
          </div>

          {/* Notes */}
          <div>
            <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Notes <span style={{ color: "#7a7d92", fontWeight: 400, textTransform: "none" }}>(optionnel)</span></label>
            <input type="text" value={catalogForm.notes}
              onChange={(e) => setCatalogForm({ ...catalogForm, notes: e.target.value })}
              placeholder="Ex: Fournisseur X, classe C24..."
              style={inputStyle} />
          </div>

          {catalogFormError && (
            <div style={{
              background: "rgba(239, 68, 68, 0.08)",
              border: "1px solid rgba(239, 68, 68, 0.25)",
              borderRadius: 10,
              padding: 14,
              color: "#fca5a5",
              fontSize: 13,
              display: "flex",
              alignItems: "start",
              gap: 10
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <div>{catalogFormError}</div>
            </div>
          )}

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12, paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
            <button onClick={() => { setShowAddCatalogModal(false); resetCatalogForm(); }}
              disabled={savingCatalog}
              style={{ ...btnSecondary, opacity: savingCatalog ? 0.5 : 1 }}>
              Annuler
            </button>
            <button onClick={handleAddMaterial}
              disabled={savingCatalog}
              style={{
                ...btnPrimary,
                padding: "11px 22px",
                opacity: savingCatalog ? 0.7 : 1,
                cursor: savingCatalog ? "not-allowed" : "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                boxShadow: savingCatalog ? "none" : "0 4px 14px rgba(240, 192, 64, 0.25)"
              }}>
              {savingCatalog ? (
                <>
                  <span style={{ display: "inline-block", width: 13, height: 13, border: "2px solid rgba(10,10,10,0.25)", borderTopColor: "#0a0a0a", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                  <span>{editingCatalogId ? "Sauvegardé..." : "Ajout en cours..."}</span>
                </>
              ) : (
                <>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    {editingCatalogId ? <polyline points="20 6 9 17 4 12"/> : <><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></>}
                  </svg>
                  {editingCatalogId ? "Enregistrer" : "Ajouter"}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )}
</div>

);
}


// ============================================================
// DEVIA - Gate d'authentification (Micro-etape 2.2)
// Ce wrapper affiche Login si l'utilisateur n'est pas connecte.
// Il ne vérifié PAS encore la licence (c'est la micro-etape 2.3).
// ============================================================

function DeviaAuthGate() {
  const { user, loading: authLoading } = useAuth();
  const { license, loading: licenseLoading, refresh: refreshLicense } = useLicense();

  // Spinner pendant le chargement initial
  if (authLoading || (user && licenseLoading)) {
    return (
      <div style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#1a1a2e",
        color: "#fff",
        fontFamily: "-apple-system, sans-serif",
        fontSize: "14px",
      }}>
        Chargement...
      </div>
    );
  }

  // Pas connecte -> ecran login
  if (!user) {
    return <Login />;
  }

  // Connecte mais pas de licence -> ecran d'activation
  if (!license || license.status === "no_license") {
    return (
      <ActivateLicense
        userEmail={user.email}
        onActivated={refreshLicense}
      />
    );
  }

  // Tout est OK : afficher l'app avec bandeau abonnement + menu user
  return (
    <>
      <SubscriptionBanner license={license} />
      <DeviaMain />
    </>
  );
}

export default DeviaAuthGate;
