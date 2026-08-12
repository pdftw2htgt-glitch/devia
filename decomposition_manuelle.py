# Pop-up "Decomposition manuelle" : schema 2D cliquable + editeur par volume
# + onglet Tout editer + ajouter/supprimer + boussole 3D permanente
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''const [editionVolumes, setEditionVolumes] = useState(null); // copie editable de la decomposition'''
NEW1 = '''const [editionVolumes, setEditionVolumes] = useState(null); // copie editable de la decomposition
const [editeurOuvert, setEditeurOuvert] = useState(false); // pop-up decomposition manuelle
const [volumeSel, setVolumeSel] = useState(0); // volume selectionne dans le schema
const [modeToutEditer, setModeToutEditer] = useState(false); // onglet Tout editer'''

OLD2 = '''  const majPos = (i, champ, val) => {
    setEditionVolumes(prev => prev.map((v, k) => k === i ? { ...v, pos: { ...(v.pos || {}), [champ]: val } } : v));
  };'''
NEW2 = '''  const majPos = (i, champ, val) => {
    setEditionVolumes(prev => prev.map((v, k) => k === i ? { ...v, pos: { ...(v.pos || {}), [champ]: val } } : v));
  };
  const numVal = (x, d) => { const p = parseFloat(String(x).replace(",", ".")); return isNaN(p) ? d : p; };
  // Placement 2D pour le schema du pop-up (miroir du verificateur)
  const calculerRects2D = (vols) => {
    const rects = [];
    const demi2 = (v, q) => q % 2 === 1 ? { hx: (v.largeur || 6) / 2, hz: (v.longueur || 8) / 2 } : { hx: (v.longueur || 8) / 2, hz: (v.largeur || 6) / 2 };
    vols.forEach((v, i) => { if (v.pos === undefined) { const q0 = v.faitageCardinal === "nord_sud" ? 1 : 0; const d0 = demi2(v, q0); rects[i] = { x: 0, z: 0, q: q0, hx: d0.hx, hz: d0.hz }; } });
    let garde2 = 0;
    let reste2 = true;
    while (reste2 && garde2 < 12) {
      garde2 += 1;
      reste2 = false;
      vols.forEach((v, i) => {
        if (rects[i] === undefined && v.pos) {
          const iRef = (v.pos.contre || 1) - 1;
          const R = rects[iRef];
          if (R === undefined || iRef === i) { reste2 = true; return; }
          const q = v.faitageCardinal === "nord_sud" ? 1 : (v.faitageCardinal === "est_ouest" ? 0 : ((v.pos.faitage === "perpendiculaire") ? (R.q + 1) % 4 : R.q));
          const dA = demi2(v, q);
          const dec = v.pos.decalage || 0;
          let x = R.x, z = R.z;
          const fc = v.pos.facade;
          if (fc) {
            if (fc === "est") x = R.x + R.hx + dA.hx + 0.2;
            else if (fc === "ouest") x = R.x - R.hx - dA.hx - 0.2;
            else if (fc === "sud") z = R.z + R.hz + dA.hz + 0.2;
            else z = R.z - R.hz - dA.hz - 0.2;
            const al = v.pos.alignement;
            if (fc === "est" || fc === "ouest") {
              if (al === "sud") z = R.z + (R.hz - dA.hz);
              else if (al === "nord") z = R.z - (R.hz - dA.hz);
              else z = R.z + dec;
            } else {
              if (al === "est") x = R.x + (R.hx - dA.hx);
              else if (al === "ouest") x = R.x - (R.hx - dA.hx);
              else x = R.x + dec;
            }
          } else if (v.pos.cote === "pignon_droit") { x = R.x + R.hx + dA.hx + 0.2; z = R.z + dec; }
          else if (v.pos.cote === "pignon_gauche") { x = R.x - R.hx - dA.hx - 0.2; z = R.z + dec; }
          else if (v.pos.cote === "gouttereau_avant") { z = R.z + R.hz + dA.hz + 0.2; x = R.x + dec; }
          else { z = R.z - R.hz - dA.hz - 0.2; x = R.x + dec; }
          rects[i] = { x: x, z: z, q: q, hx: dA.hx, hz: dA.hz };
        }
      });
    }
    return vols.map((v, i) => rects[i] || null);
  };
  // Une ligne d'edition d'un volume (utilisee par le schema ET l'onglet Tout editer)
  const ligneVolume = (v, i) => (
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
          <select value={v.pos.alignement || ""} onChange={e => majPos(i, "alignement", e.target.value)} style={{ ...miniInp, cursor: "pointer" }}><option value="">centre / decalage</option>{(v.pos.facade === "est" || v.pos.facade === "ouest") ? (<><option value="nord">aligne nord</option><option value="sud">aligne sud</option></>) : (<><option value="est">aligne est</option><option value="ouest">aligne ouest</option></>)}</select>
          <span>dec.</span>
          <input value={v.pos.decalage === undefined ? 0 : v.pos.decalage} onChange={e => majPos(i, "decalage", e.target.value)} style={{ ...miniInp, width: 46 }} />
        </>
      ) : null}
    </div>
  );'''

OLD3 = '''                {editionVolumes ? (
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
NEW3 = '''                {editionVolumes ? (
                  <button type="button" onClick={() => { setEditeurOuvert(true); setVolumeSel(0); }} style={{ marginTop: 8, padding: "8px 16px", borderRadius: 9, cursor: "pointer", background: "rgba(240,192,64,0.10)", border: "1px solid rgba(240,192,64,0.45)", color: "#f0c040", fontSize: 12.5, fontWeight: 700 }}>
                    Decomposition manuelle
                  </button>
                ) : null}
                {editeurOuvert && editionVolumes ? (
                  <div onClick={() => setEditeurOuvert(false)} style={{ position: "fixed", inset: 0, background: "rgba(8,10,18,0.75)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", padding: 20 }}>
                    <div onClick={e => e.stopPropagation()} style={{ width: "min(880px, 94vw)", maxHeight: "88vh", overflowY: "auto", background: "#14161f", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 16, padding: 20 }}>
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                        <div style={{ color: "#e8eaf2", fontSize: 15, fontWeight: 700 }}>Decomposition manuelle</div>
                        <div style={{ display: "flex", gap: 8 }}>
                          <button type="button" onClick={() => setModeToutEditer(false)} style={{ ...miniInp, cursor: "pointer", fontWeight: 600, color: modeToutEditer ? "#9ca0b8" : "#f0c040", borderColor: modeToutEditer ? "rgba(255,255,255,0.14)" : "rgba(240,192,64,0.5)" }}>Schema</button>
                          <button type="button" onClick={() => setModeToutEditer(true)} style={{ ...miniInp, cursor: "pointer", fontWeight: 600, color: modeToutEditer ? "#f0c040" : "#9ca0b8", borderColor: modeToutEditer ? "rgba(240,192,64,0.5)" : "rgba(255,255,255,0.14)" }}>Tout editer</button>
                          <button type="button" onClick={() => setEditeurOuvert(false)} style={{ ...miniInp, cursor: "pointer", fontWeight: 700 }}>Fermer</button>
                        </div>
                      </div>
                      {modeToutEditer ? (
                        <div>{editionVolumes.map((v, i) => ligneVolume(v, i))}</div>
                      ) : (
                        <div>
                          {(() => {
                            const volsNum = editionVolumes.map(v => ({ ...v, longueur: numVal(v.longueur, 6), largeur: numVal(v.largeur, 4), pos: v.pos ? { ...v.pos, contre: parseInt(v.pos.contre, 10) || 1, decalage: numVal(v.pos.decalage, 0) } : undefined }));
                            const rects = calculerRects2D(volsNum);
                            const places2 = rects.filter(r => r).length;
                            if (places2 === 0) return <div style={{ color: "#e05252", fontSize: 12, marginBottom: 8 }}>Schema impossible : positions non resolubles</div>;
                            let minX = 9999, maxX = -9999, minZ = 9999, maxZ = -9999;
                            rects.forEach((r) => { if (r) { minX = Math.min(minX, r.x - r.hx); maxX = Math.max(maxX, r.x + r.hx); minZ = Math.min(minZ, r.z - r.hz); maxZ = Math.max(maxZ, r.z + r.hz); } });
                            const pad = 2.4;
                            return (
                              <svg viewBox={(minX - pad) + " " + (minZ - pad) + " " + (maxX - minX + 2 * pad) + " " + (maxZ - minZ + 2 * pad)} style={{ width: "100%", maxHeight: 300, background: "rgba(255,255,255,0.02)", borderRadius: 10, marginBottom: 10 }}>
                                {rects.map((r, i) => r ? (
                                  <g key={i} onClick={() => setVolumeSel(i)} style={{ cursor: "pointer" }}>
                                    <rect x={r.x - r.hx} y={r.z - r.hz} width={2 * r.hx} height={2 * r.hz} fill={volumeSel === i ? "rgba(240,192,64,0.22)" : "rgba(255,255,255,0.06)"} stroke={volumeSel === i ? "#f0c040" : "rgba(255,255,255,0.4)"} strokeWidth="0.12" />
                                    <text x={r.x} y={r.z} textAnchor="middle" dominantBaseline="middle" fill={volumeSel === i ? "#f0c040" : "#d0d2dc"} fontSize="0.9" fontWeight="700">V{i + 1}</text>
                                    <text x={r.x} y={r.z + 1.2} textAnchor="middle" fill="#9ca0b8" fontSize="0.6">{(2 * r.hx).toFixed(1)} x {(2 * r.hz).toFixed(1)}</text>
                                  </g>
                                ) : null)}
                                <g>
                                  <line x1={minX - 1.2} y1={minZ + 0.8} x2={minX - 1.2} y2={minZ - 0.6} stroke="#f0c040" strokeWidth="0.12" />
                                  <polygon points={(minX - 1.45) + "," + (minZ - 0.5) + " " + (minX - 0.95) + "," + (minZ - 0.5) + " " + (minX - 1.2) + "," + (minZ - 1.1)} fill="#f0c040" />
                                  <text x={minX - 1.2} y={minZ - 1.5} textAnchor="middle" fill="#f0c040" fontSize="0.8" fontWeight="700">N</text>
                                </g>
                              </svg>
                            );
                          })()}
                          <div style={{ color: "#9ca0b8", fontSize: 11, marginBottom: 6 }}>Clique une structure du schema pour l'editer :</div>
                          {editionVolumes[volumeSel] ? ligneVolume(editionVolumes[volumeSel], volumeSel) : null}
                        </div>
                      )}
                      <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
                        <button type="button" onClick={() => setEditionVolumes(prev => [...prev, { type: "traditionnelle", longueur: "", largeur: "", hauteur: "", pos: { contre: 1, cote: "pignon_gauche", facade: "", alignement: "", decalage: 0, faitage: "parallele" } }])} style={{ padding: "6px 14px", borderRadius: 8, cursor: "pointer", background: "rgba(240,192,64,0.10)", border: "1px solid rgba(240,192,64,0.4)", color: "#f0c040", fontSize: 12, fontWeight: 700 }}>Ajouter un volume</button>
                        {editionVolumes.length > 1 ? (
                          <button type="button" onClick={() => setEditionVolumes(prev => prev.slice(0, -1))} style={{ padding: "6px 14px", borderRadius: 8, cursor: "pointer", background: "rgba(224,82,82,0.08)", border: "1px solid rgba(224,82,82,0.35)", color: "#e05252", fontSize: 12, fontWeight: 700 }}>Supprimer le dernier</button>
                        ) : null}
                        <button type="button" onClick={enregistrerCorrections} style={{ padding: "6px 14px", borderRadius: 8, cursor: "pointer", background: "rgba(126,201,126,0.12)", border: "1px solid rgba(126,201,126,0.45)", color: "#7ec97e", fontSize: 12, fontWeight: 700 }}>Verifier et enregistrer</button>
                      </div>
                      {analyseVerdict ? (analyseVerdict.ok ? (
                        <div style={{ marginTop: 8, color: "#7ec97e", fontSize: 11.5, fontWeight: 600 }}>Controles geometriques : conformes</div>
                      ) : (
                        <div style={{ marginTop: 8, color: "#e05252", fontSize: 11.5, lineHeight: 1.5, fontWeight: 600 }}>NON CONFORME - {analyseVerdict.erreurs.join(" | ")}</div>
                      )) : null}
                    </div>
                  </div>
                ) : null}'''

OLD4 = '''    ground.rotation.x = -Math.PI/2;
    ground.receiveShadow = true;
    scene.add(ground);'''
NEW4 = '''    ground.rotation.x = -Math.PI/2;
    ground.receiveShadow = true;
    scene.add(ground);

    // BOUSSOLE permanente : fleche doree pointee plein NORD (nord = -Z)
    const xBou = -((params.longueur || 10) / 2) - 4;
    const bouMat = new THREE.MeshStandardMaterial({ color: 0xf0c040, roughness: 0.6 });
    const bouTige = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.2, 8), bouMat);
    bouTige.rotation.x = Math.PI / 2;
    bouTige.position.set(xBou, 0.08, -0.1);
    scene.add(bouTige);
    const bouPointe = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.7, 12), bouMat);
    bouPointe.rotation.x = -Math.PI / 2;
    bouPointe.position.set(xBou, 0.08, -1.55);
    scene.add(bouPointe);
    const bouCan = document.createElement("canvas");
    bouCan.width = 64;
    bouCan.height = 64;
    const bouCtx = bouCan.getContext("2d");
    bouCtx.fillStyle = "#f0c040";
    bouCtx.font = "bold 46px Arial";
    bouCtx.textAlign = "center";
    bouCtx.textBaseline = "middle";
    bouCtx.fillText("N", 32, 34);
    const bouSpr = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(bouCan), transparent: true, depthTest: false }));
    bouSpr.scale.set(1.1, 1.1, 1);
    bouSpr.position.set(xBou, 0.9, -2.4);
    scene.add(bouSpr);'''

anchors = [("etats pop-up", OLD1, NEW1), ("helpers schema", OLD2, NEW2), ("interface pop-up", OLD3, NEW3), ("boussole 3D", OLD4, NEW4)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_decomposition_manuelle")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : pop-up Decomposition manuelle (schema cliquable) + boussole 3D")
