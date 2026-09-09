# portee_plancher.py — PORTEE DU PLANCHER : DEVIA signale et laisse choisir
# Si aucune solive ne tient la portee a l EC5, une alerte apparait dans le
# formulaire avec deux remedes de charpentier :
#   - poutre porteuse au milieu (solives en deux travees)
#   - solivage plus dense (entraxe 0,40 au lieu de 0,50)
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''const [formAppuis, setFormAppuis] = useState("poteaux");'''
R1 = r'''const [formAppuis, setFormAppuis] = useState("poteaux");
const [formRemede, setFormRemede] = useState(""); // plancher trop porteur : "" / "porteuse" / "dense"'''

A2 = r'''                      <option value="murs">les murs porteurs (sous-sol, murs existants) - sans poteaux</option>
                    </select>
                  </div>
                ) : null}'''
R2 = r'''                      <option value="murs">les murs porteurs (sous-sol, murs existants) - sans poteaux</option>
                    </select>
                    {(() => {
                      const lgP = parseFloat(String(formLargeur || "").replace(",", "."));
                      if (isNaN(lgP) || lgP <= 0) return null;
                      const porteeBrute = Math.max(0.5, lgP - 0.24);
                      const porteeEff = formRemede === "porteuse" ? porteeBrute / 2 : porteeBrute;
                      const entraxeEff = formRemede === "dense" ? 0.4 : 0.5;
                      let dimP = null;
                      try {
                        const zP = getZone(commune || "", altitude || 200);
                        const chP = ec5DescenteCharge(formCouverture || "tuile_terre", zP ? zP.sk : 0.45, 0, zP ? zP.dS : 0, false);
                        dimP = dimensionnerPiece("Solive", { portee: porteeEff, entraxe: entraxeEff, G: chP.G, Q: chP.Q, S: chP.S, classeService: 2, dureeVariable: "moyen", typeBatiment: "courant", altitude: parseFloat(altitude) || 200, console: false });
                      } catch (eP) { dimP = null; }
                      if (dimP && formRemede === "") return null;
                      if (dimP) {
                        return (
                          <div style={{ marginTop: 8, padding: "8px 10px", borderRadius: 8, background: "rgba(126,201,126,0.10)", border: "1px solid rgba(126,201,126,0.4)", color: "#7ec97e", fontSize: 11.5, lineHeight: 1.5 }}>
                            {formRemede === "porteuse" ? "Poutre porteuse au milieu : les solives portent en deux travees de " + porteeEff.toFixed(2) + " m, le calcul passe." : "Solivage resserre a 40 cm : le calcul passe."}
                            <button type="button" onClick={() => setFormRemede("")} style={{ marginLeft: 8, padding: "2px 8px", borderRadius: 6, cursor: "pointer", background: "transparent", border: "1px solid rgba(126,201,126,0.5)", color: "#7ec97e", fontSize: 11 }}>annuler</button>
                          </div>
                        );
                      }
                      return (
                        <div style={{ marginTop: 8, padding: "9px 11px", borderRadius: 8, background: "rgba(224,82,82,0.08)", border: "1px solid rgba(224,82,82,0.45)" }}>
                          <div style={{ color: "#e05252", fontSize: 11.5, fontWeight: 700, lineHeight: 1.5 }}>Portee trop grande : {porteeBrute.toFixed(2)} m entre appuis, aucune section de solive ne tient le calcul.</div>
                          <div style={{ color: cl("#b8bccc", "#565a6c"), fontSize: 11, lineHeight: 1.5, marginTop: 3 }}>Choisis le remede :</div>
                          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 6 }}>
                            <button type="button" onClick={() => setFormRemede("porteuse")} style={{ padding: "5px 12px", borderRadius: 7, cursor: "pointer", background: "rgba(240,192,64,0.12)", border: "1px solid rgba(240,192,64,0.5)", color: "#f0c040", fontSize: 11.5, fontWeight: 700 }}>Poutre porteuse au milieu</button>
                            <button type="button" onClick={() => setFormRemede("dense")} style={{ padding: "5px 12px", borderRadius: 7, cursor: "pointer", background: "rgba(240,192,64,0.12)", border: "1px solid rgba(240,192,64,0.5)", color: "#f0c040", fontSize: 11.5, fontWeight: 700 }}>Solives plus rapprochees (40 cm)</button>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                ) : null}'''

A3 = r'''    const nbSolives = Math.max(2, Math.round(L / 0.5) + 1);
    for (let i = 0; i < nbSolives; i++) {
      const x = -L/2 + soB/2 + (i / (nbSolives - 1)) * (L - soB);
      addBox(soB, soH, lgSolive, x, ySolive, 0, woodMat);
    }'''
R3 = r'''    const remedeP = (params && params.remede) || "";
    const entraxeSol = remedeP === "dense" ? 0.4 : 0.5;
    const nbSolives = Math.max(2, Math.round(L / entraxeSol) + 1);
    if (remedeP === "porteuse") {
      // Poutre porteuse centrale : les solives portent en DEUX travees
      const [pbB, pbH] = sec("Poutre porteuse", 0.12, 0.30);
      setPiece("Poutre porteuse");
      addBox(L, pbH, pbB, 0, ySolive - soH / 2 - pbH / 2, 0, woodMat);
      if (appuisEtage === "poteaux") {
        setPiece("Poteau");
        const nbPotC = Math.max(2, Math.ceil(L / 3.0) + 1);
        const hPotC = ySolive - soH / 2 - pbH;
        for (let i = 0; i < nbPotC; i++) {
          const x = -L/2 + potB/2 + (i / (nbPotC - 1)) * (L - potB);
          addBox(potB, hPotC, potB, x, hPotC / 2, 0);
        }
      }
      setPiece("Solive");
      const demi = (lgSolive - pbB) / 2;
      for (let i = 0; i < nbSolives; i++) {
        const x = -L/2 + soB/2 + (i / (nbSolives - 1)) * (L - soB);
        for (const sz of [-1, 1]) {
          addBox(soB, soH, demi, x, ySolive, sz * (pbB / 2 + demi / 2), woodMat);
        }
      }
      console.log("[DEVIA] Plancher : poutre porteuse centrale, solives en 2 travees de " + demi.toFixed(2) + " m");
    } else {
      for (let i = 0; i < nbSolives; i++) {
        const x = -L/2 + soB/2 + (i / (nbSolives - 1)) * (L - soB);
        addBox(soB, soH, lgSolive, x, ySolive, 0, woodMat);
      }
      if (remedeP === "dense") console.log("[DEVIA] Plancher : solivage resserre a 40 cm");
    }'''

A4 = r'''      murs: formMurs || undefined,
      appuis: formAppuis || undefined,'''
R4 = r'''      murs: formMurs || undefined,
      appuis: formAppuis || undefined,
      remede: formRemede || undefined,'''

A5 = r'''                        appuis: formAppuis || undefined,'''
R5 = r'''                        appuis: formAppuis || undefined,
                        remede: formRemede || undefined,'''

A6 = r'''        appuis: finalParams.appuis || undefined,'''
R6 = r'''        appuis: finalParams.appuis || undefined,
        remede: finalParams.remede || undefined,'''

A7 = r'''appuis: s.appuis || undefined, debord:'''
R7 = r'''appuis: s.appuis || undefined, remede: s.remede || undefined, debord:'''

A8 = r'''  if (finalParams.appuis) parsed._appuis = finalParams.appuis;'''
R8 = r'''  if (finalParams.appuis) parsed._appuis = finalParams.appuis;
  if (finalParams.remede) parsed._remede = finalParams.remede;'''

A9 = r'''        appuis: project.devis_data._appuis || undefined,'''
R9 = r'''        appuis: project.devis_data._appuis || undefined,
        remede: project.devis_data._remede || undefined,'''

A10 = r'''      appuis: p.appuis,'''
R10 = r'''      appuis: p.appuis,
      remede: p.remede,'''

A11 = r'''      appuis: (src && src.appuis) || (parsed && parsed._appuis) || undefined,'''
R11 = r'''      appuis: (src && src.appuis) || (parsed && parsed._appuis) || undefined,
      remede: (src && src.remede) || (parsed && parsed._remede) || undefined,'''

paires = [
    ("etat formRemede", A1, R1),
    ("alerte portee dans le formulaire", A2, R2),
    ("moteur : remede applique", A3, R3),
    ("params formulaire", A4, R4),
    ("structure multi-ouvrages", A5, R5),
    ("view3DParams", A6, R6),
    ("ouvrages3D", A7, R7),
    ("persistance devis", A8, R8),
    ("rechargement projet", A9, R9),
    ("metre moteur", A10, R10),
    ("harmonisation", A11, R11),
]

erreurs = 0
for nom, ancre, rempl in paires:
    n = src.count(ancre)
    if n == 1:
        print("OK ancre : " + nom)
    else:
        erreurs = erreurs + 1
        print("ANCRE '" + nom + "' : " + str(n) + " occurrence(s) au lieu de 1")

if erreurs > 0:
    print("ABANDON — aucune modification ecrite.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
for nom, ancre, rempl in paires:
    src = src.replace(ancre, rempl)
open(F, "w", encoding="utf-8").write(src)
print("11 modifications ecrites. Backup : " + F + ".bak_" + tag)
