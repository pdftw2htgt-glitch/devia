# Lecture sous contrat M3 : editeur de decomposition (les valeurs de l'utilisateur font foi)
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''const [analyseVerdict, setAnalyseVerdict] = useState(null); // verdict du verificateur deterministe'''
NEW1 = '''const [analyseVerdict, setAnalyseVerdict] = useState(null); // verdict du verificateur deterministe
const [editionVolumes, setEditionVolumes] = useState(null); // copie editable de la decomposition
const analyseJRef = useRef(null); // dernier JSON d'analyse (pour sauvegarder les corrections)
const analyseVersionRef = useRef(""); // version de prompt du dernier cache'''

OLD2 = '''      } else {
        j = jCache;
        console.log("[DEVIA] Analyse servie par le cache (" + empreinte.slice(0, 8) + ")");
      }'''
NEW2 = '''      } else {
        j = jCache;
        console.log("[DEVIA] Analyse servie par le cache (" + empreinte.slice(0, 8) + ")");
      }
      analyseJRef.current = j;
      analyseVersionRef.current = versionPrompt;'''

OLD3 = '''        else console.warn("[DEVIA] Verificateur : NON CONFORME -", verdictDecomp.erreurs.join(" | "));'''
NEW3 = '''        else console.warn("[DEVIA] Verificateur : NON CONFORME -", verdictDecomp.erreurs.join(" | "));
        setEditionVolumes(structs.map(s => ({ ...s, pos: s.pos ? { ...s.pos } : undefined })));'''

OLD4 = '''  // Analyse du plan : extrait les caracteristiques et pre-remplit le formulaire'''
NEW4 = '''  // EDITEUR DE DECOMPOSITION : les valeurs saisies par l'utilisateur font foi
  const miniInp = { background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.14)", borderRadius: 6, color: "#e8eaf2", fontSize: 11.5, padding: "3px 6px" };
  const majVolume = (i, champ, val) => {
    setEditionVolumes(prev => prev.map((v, k) => k === i ? { ...v, [champ]: val === "" ? undefined : val } : v));
  };
  const majPos = (i, champ, val) => {
    setEditionVolumes(prev => prev.map((v, k) => k === i ? { ...v, pos: { ...(v.pos || {}), [champ]: val } } : v));
  };
  const enregistrerCorrections = async () => {
    if (editionVolumes === null) return;
    const num = (x, d) => { const p = parseFloat(String(x).replace(",", ".")); return isNaN(p) ? d : p; };
    const LTC = { fermette: "fermette industrielle", traditionnelle: "charpente traditionnelle", monopente: "monopente", carport: "carport abri voiture", terrasse: "terrasse bois exterieure", etage: "plancher d'etage sur solivage bois", balcon: "balcon bois en porte-a-faux", garde_corps: "garde-corps bois (rambarde)", hangar: "hangar agricole", appentis: "appentis accole a un mur", "4_pans": "toit 4 pans avec croupe", sas: "sas de liaison a toit plat" };
    const structs2 = editionVolumes.map((v, i) => {
      const base = {
        type: v.type,
        longueur: num(v.longueur, 0), largeur: num(v.largeur, 0),
        hauteur: (v.hauteur === undefined || v.hauteur === "") ? undefined : num(v.hauteur, undefined),
        pente: v.pente, couverture: v.couverture, essence: v.essence,
        faitageCardinal: v.faitageCardinal || undefined,
      };
      if (i > 0 && v.pos) {
        base.pos = { contre: parseInt(v.pos.contre, 10) || 1, cote: v.pos.cote || "pignon_gauche", facade: v.pos.facade || null, alignement: v.pos.alignement || null, decalage: num(v.pos.decalage, 0), faitage: v.pos.faitage || "parallele" };
      }
      const p2 = [LTC[base.type] || base.type, base.longueur + "x" + base.largeur + "m"];
      if (base.hauteur) p2.push("hauteur " + base.hauteur + "m");
      if (base.pente) p2.push("pente " + base.pente + " degres");
      if (base.pos && base.pos.facade) p2.push("accole facade " + base.pos.facade + " de l'ouvrage " + base.pos.contre + (base.pos.alignement ? ", aligne " + base.pos.alignement : ""));
      base.desc = p2.join(", ");
      return base;
    });
    const verdict2 = verifierDecomposition(structs2);
    setAnalyseVerdict(verdict2);
    if (verdict2.ok === false) { console.warn("[DEVIA] Corrections refusees par le verificateur :", verdict2.erreurs.join(" | ")); return; }
    setFormType("custom");
    setFormStructures(structs2);
    setEditionVolumes(structs2.map(s => ({ ...s, pos: s.pos ? { ...s.pos } : undefined })));
    setAnalyseResume(structs2.map((s, k) => "V" + (k + 1) + " " + s.desc).join(" | "));
    try {
      const jBase = analyseJRef.current || {};
      const j2 = { ...jBase, corrige_par_utilisateur: true, ouvrages: structs2.map(s => ({ type: s.type, longueur: s.longueur, largeur: s.largeur, hauteur_murs: s.hauteur || null, pente_valeur: s.pente || null, pente_unite: s.pente ? "degres" : null, couverture: s.couverture || null, contre: s.pos ? s.pos.contre : null, cote: s.pos ? s.pos.cote : null, facade: s.pos ? s.pos.facade : null, alignement: s.pos ? s.pos.alignement : null, decalage_m: s.pos ? s.pos.decalage : null, faitage: s.pos ? s.pos.faitage : null, faitage_cardinal: s.faitageCardinal || null, desc: s.desc })) };
      const { data: { user: uCor } } = await supabase.auth.getUser();
      if (uCor && analyseEmpreinte) {
        await supabase.from("analyses_plans").upsert({ user_id: uCor.id, empreinte: analyseEmpreinte, version: analyseVersionRef.current || "manuel", resultat: j2 }, { onConflict: "user_id,empreinte,version" });
        console.log("[DEVIA] Corrections enregistrees : lecture de reference du fichier mise a jour");
      }
      analyseJRef.current = j2;
    } catch (eCor) { console.warn("[DEVIA] Sauvegarde des corrections impossible", eCor); }
  };

  // Analyse du plan : extrait les caracteristiques et pre-remplit le formulaire'''

OLD5 = '''                    )) : null}
                  </div>
                ) : null}'''
NEW5 = '''                    )) : null}
                  </div>
                ) : null}
                {editionVolumes ? (
                  <div style={{ marginTop: 8, padding: "10px 12px", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.10)", borderRadius: 10 }}>
                    <div style={{ color: "#9ca0b8", fontSize: 11, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 8 }}>Corriger la decomposition - vos valeurs font foi</div>
                    {editionVolumes.map((v, i) => (
                      <div key={i} style={{ display: "flex", flexWrap: "wrap", gap: 6, alignItems: "center", marginBottom: 6, fontSize: 11.5, color: "#d0d2dc" }}>
                        <span style={{ color: "#f0c040", fontWeight: 700, width: 24 }}>V{i + 1}</span>
                        <select value={v.type} onChange={e => majVolume(i, "type", e.target.value)} style={{ ...miniInp, cursor: "pointer" }}>{["traditionnelle", "fermette", "monopente", "carport", "hangar", "appentis", "4_pans", "terrasse", "etage", "balcon", "garde_corps", "sas"].map(t => <option key={t} value={t}>{t}</option>)}</select>
                        <input value={v.longueur === undefined ? "" : v.longueur} onChange={e => majVolume(i, "longueur", e.target.value)} style={{ ...miniInp, width: 52 }} />
                        <span>x</span>
                        <input value={v.largeur === undefined ? "" : v.largeur} onChange={e => majVolume(i, "largeur", e.target.value)} style={{ ...miniInp, width: 52 }} />
                        <span>m, h</span>
                        <input value={v.hauteur === undefined ? "" : v.hauteur} onChange={e => majVolume(i, "hauteur", e.target.value)} style={{ ...miniInp, width: 46 }} />
                        <select value={v.faitageCardinal || ""} onChange={e => majVolume(i, "faitageCardinal", e.target.value)} style={{ ...miniInp, cursor: "pointer" }}><option value="">faitage ?</option><option value="est_ouest">faitage est-ouest</option><option value="nord_sud">faitage nord-sud</option></select>
                        {i > 0 && v.pos ? (
                          <>
                            <span>contre</span>
                            <select value={v.pos.contre} onChange={e => majPos(i, "contre", e.target.value)} style={{ ...miniInp, cursor: "pointer" }}>{editionVolumes.map((x, k) => k === i ? null : <option key={k} value={k + 1}>V{k + 1}</option>)}</select>
                            <select value={v.pos.facade || ""} onChange={e => majPos(i, "facade", e.target.value)} style={{ ...miniInp, cursor: "pointer" }}><option value="">facade ?</option><option value="nord">facade nord</option><option value="sud">facade sud</option><option value="est">facade est</option><option value="ouest">facade ouest</option></select>
                            <select value={v.pos.alignement || ""} onChange={e => majPos(i, "alignement", e.target.value)} style={{ ...miniInp, cursor: "pointer" }}><option value="">centre / decalage</option><option value="nord">aligne nord</option><option value="sud">aligne sud</option><option value="est">aligne est</option><option value="ouest">aligne ouest</option></select>
                            <span>dec.</span>
                            <input value={v.pos.decalage === undefined ? 0 : v.pos.decalage} onChange={e => majPos(i, "decalage", e.target.value)} style={{ ...miniInp, width: 46 }} />
                          </>
                        ) : null}
                      </div>
                    ))}
                    <button type="button" onClick={enregistrerCorrections} style={{ marginTop: 4, padding: "6px 14px", borderRadius: 8, cursor: "pointer", background: "rgba(126,201,126,0.12)", border: "1px solid rgba(126,201,126,0.45)", color: "#7ec97e", fontSize: 12, fontWeight: 700 }}>Verifier et enregistrer mes valeurs</button>
                  </div>
                ) : null}'''

anchors = [("etats editeur", OLD1, NEW1), ("refs analyse", OLD2, NEW2), ("peuplement editeur", OLD3, NEW3), ("logique editeur", OLD4, NEW4), ("interface editeur", OLD5, NEW5)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_editeur_M3")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK M3 : editeur de decomposition en place")
