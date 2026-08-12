# Lecture sous contrat M1 : verificateur deterministe de la decomposition
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''const [analyseEmpreinte, setAnalyseEmpreinte] = useState(""); // empreinte du dernier fichier analyse'''
NEW1 = '''const [analyseEmpreinte, setAnalyseEmpreinte] = useState(""); // empreinte du dernier fichier analyse
const [analyseVerdict, setAnalyseVerdict] = useState(null); // verdict du verificateur deterministe'''

OLD2 = '''    setAnalyseResume("");'''
NEW2 = '''    setAnalyseResume("");
    setAnalyseVerdict(null);'''

OLD3 = '''  // Analyse du plan : extrait les caracteristiques et pre-remplit le formulaire'''
NEW3 = '''  // VERIFICATEUR DETERMINISTE : rejoue le placement en 2D et controle la coherence.
  // Code pur, zero IA, zero cout. Toute lecture est jugee par lui avant d'etre crue.
  const verifierDecomposition = (vols) => {
    const erreurs = [];
    const rects = [];
    const TYPESV = ["traditionnelle", "fermette", "monopente", "carport", "hangar", "appentis", "4_pans", "terrasse", "etage", "balcon", "garde_corps", "sas"];
    vols.forEach((v, i) => {
      const n = "V" + (i + 1);
      if (TYPESV.includes(v.type) === false) erreurs.push(n + " : type inconnu (" + v.type + ")");
      if ((v.longueur > 0.2 && v.longueur < 60) === false) erreurs.push(n + " : longueur invalide ou illisible");
      if ((v.largeur > 0.2 && v.largeur < 60) === false) erreurs.push(n + " : largeur invalide ou illisible");
      if (v.hauteur === undefined || v.hauteur === null) erreurs.push(n + " : hauteur manquante (cote non lue sur les coupes)");
    });
    const demi = (v, q) => q % 2 === 1 ? { hx: (v.largeur || 6) / 2, hz: (v.longueur || 8) / 2 } : { hx: (v.longueur || 8) / 2, hz: (v.largeur || 6) / 2 };
    vols.forEach((v, i) => { if (v.pos === undefined) rects[i] = { x: 0, z: 0, q: v.faitageCardinal === "nord_sud" ? 1 : 0 }; });
    let garde = 0;
    let resteAPlacer = true;
    while (resteAPlacer && garde < 12) {
      garde += 1;
      resteAPlacer = false;
      vols.forEach((v, i) => {
        if (rects[i] === undefined && v.pos) {
          const iRef = (v.pos.contre || 1) - 1;
          const R = rects[iRef];
          if (R === undefined || iRef === i) { resteAPlacer = true; return; }
          const vRef = vols[iRef];
          const q = v.faitageCardinal === "nord_sud" ? 1 : (v.faitageCardinal === "est_ouest" ? 0 : ((v.pos.faitage === "perpendiculaire") ? (R.q + 1) % 4 : R.q));
          const dR = demi(vRef, R.q);
          const dA = demi(v, q);
          const dec = v.pos.decalage || 0;
          let x = R.x, z = R.z;
          const fc = v.pos.facade;
          if (fc) {
            if (fc === "est") x = R.x + dR.hx + dA.hx + 0.2;
            else if (fc === "ouest") x = R.x - dR.hx - dA.hx - 0.2;
            else if (fc === "sud") z = R.z + dR.hz + dA.hz + 0.2;
            else z = R.z - dR.hz - dA.hz - 0.2;
            const al = v.pos.alignement;
            if (fc === "est" || fc === "ouest") {
              if (al === "sud") z = R.z + (dR.hz - dA.hz);
              else if (al === "nord") z = R.z - (dR.hz - dA.hz);
              else z = R.z + dec;
            } else {
              if (al === "est") x = R.x + (dR.hx - dA.hx);
              else if (al === "ouest") x = R.x - (dR.hx - dA.hx);
              else x = R.x + dec;
            }
          } else if (v.pos.cote === "pignon_droit") { x = R.x + dR.hx + dA.hx + 0.2; z = R.z + dec; }
          else if (v.pos.cote === "pignon_gauche") { x = R.x - dR.hx - dA.hx - 0.2; z = R.z + dec; }
          else if (v.pos.cote === "gouttereau_avant") { z = R.z + dR.hz + dA.hz + 0.2; x = R.x + dec; }
          else { z = R.z - dR.hz - dA.hz - 0.2; x = R.x + dec; }
          rects[i] = { x: x, z: z, q: q };
        }
      });
    }
    vols.forEach((v, i) => { if (rects[i] === undefined) erreurs.push("V" + (i + 1) + " : position impossible a resoudre (reference circulaire ou manquante)"); });
    for (let a = 0; a < vols.length; a++) {
      for (let b = a + 1; b < vols.length; b++) {
        if (rects[a] === undefined || rects[b] === undefined) continue;
        const da = demi(vols[a], rects[a].q);
        const db = demi(vols[b], rects[b].q);
        const ox = Math.min(rects[a].x + da.hx, rects[b].x + db.hx) - Math.max(rects[a].x - da.hx, rects[b].x - db.hx);
        const oz = Math.min(rects[a].z + da.hz, rects[b].z + db.hz) - Math.max(rects[a].z - da.hz, rects[b].z - db.hz);
        if (ox > 0.05 && oz > 0.05) erreurs.push("V" + (a + 1) + " et V" + (b + 1) + " se chevauchent (" + ox.toFixed(2) + " x " + oz.toFixed(2) + " m) : positions incoherentes");
      }
    }
    vols.forEach((v, i) => {
      if (v.type === "sas" && v.pos && v.hauteur) {
        const iRef = (v.pos.contre || 1) - 1;
        const hRef = (vols[iRef] && vols[iRef].hauteur) || null;
        if (hRef && v.hauteur > hRef) erreurs.push("V" + (i + 1) + " (sas) plus haut que son voisin V" + (iRef + 1) + " : hauteurs incoherentes");
      }
    });
    return { ok: erreurs.length === 0, erreurs: erreurs };
  };

  // Analyse du plan : extrait les caracteristiques et pre-remplit le formulaire'''

OLD4 = '''        setAnalyseResume(structs.map((s, k) => "V" + (k + 1) + " " + (LT_DECOMP[s.type] || s.type) + " " + s.longueur + "x" + s.largeur + "m" + (s.hauteur ? " h" + s.hauteur + "m" : " h?") + (s.pos ? " - contre V" + s.pos.contre + ", " + (s.pos.facade ? "FACADE " + s.pos.facade + (s.pos.alignement ? " aligne " + s.pos.alignement : "") + ", " : "") + String(s.pos.cote).replace("_", " ") + ", faitage " + (s.pos.faitage || "?") + ", decalage " + (s.pos.decalage || 0) + "m" : "")).join(" | "));'''
NEW4 = '''        setAnalyseResume(structs.map((s, k) => "V" + (k + 1) + " " + (LT_DECOMP[s.type] || s.type) + " " + s.longueur + "x" + s.largeur + "m" + (s.hauteur ? " h" + s.hauteur + "m" : " h?") + (s.pos ? " - contre V" + s.pos.contre + ", " + (s.pos.facade ? "FACADE " + s.pos.facade + (s.pos.alignement ? " aligne " + s.pos.alignement : "") + ", " : "") + String(s.pos.cote).replace("_", " ") + ", faitage " + (s.pos.faitage || "?") + ", decalage " + (s.pos.decalage || 0) + "m" : "")).join(" | "));
        const verdictDecomp = verifierDecomposition(structs);
        setAnalyseVerdict(verdictDecomp);
        if (verdictDecomp.ok) console.log("[DEVIA] Verificateur : decomposition CONFORME");
        else console.warn("[DEVIA] Verificateur : NON CONFORME -", verdictDecomp.erreurs.join(" | "));'''

OLD5 = '''                      Relancer l'analyse (relecture complete du plan)
                    </button>'''
NEW5 = '''                      Relancer l'analyse (relecture complete du plan)
                    </button>
                    {analyseVerdict ? (analyseVerdict.ok ? (
                      <div style={{ marginTop: 6, color: "#7ec97e", fontSize: 11, fontWeight: 600 }}>Controles geometriques : conformes</div>
                    ) : (
                      <div style={{ marginTop: 6, color: "#e05252", fontSize: 11, lineHeight: 1.5, fontWeight: 600 }}>ANALYSE NON CONFORME - {analyseVerdict.erreurs.join(" | ")}</div>
                    )) : null}'''

anchors = [("etat verdict", OLD1, NEW1), ("reset verdict", OLD2, NEW2), ("verificateur", OLD3, NEW3), ("calcul verdict", OLD4, NEW4), ("affichage verdict", OLD5, NEW5)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_verificateur_M1")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK M1 : verificateur deterministe en place")
