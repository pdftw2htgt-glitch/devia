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

remp("decomposition manuelle sans plan",
"""                {editionVolumes ? (
                  <button type="button" onClick={() => { setEditeurOuvert(true); setVolumeSel(0); }} style={{ marginTop: 8, padding: "8px 16px", borderRadius: 9, cursor: "pointer", background: "rgba(240,192,64,0.10)", border: "1px solid rgba(240,192,64,0.45)", color: "#f0c040", fontSize: 12.5, fontWeight: 700 }}>
                    Decomposition manuelle
                  </button>
                ) : null}""",
"""                <button type="button" onClick={() => {
                  // Sans analyse de plan, l editeur n avait aucun volume a montrer : il etait
                  // donc inaccessible depuis le formulaire. On l amorce ici avec ce qui est saisi.
                  const vide = (editionVolumes === null) || (editionVolumes === undefined) || (editionVolumes.length === 0);
                  if (vide) {
                    const num0 = (x, d) => { const p = parseFloat(String(x === undefined || x === null ? "" : x).replace(",", ".")); return isNaN(p) ? d : p; };
                    const t0 = (formType === "custom" ? formSousType : formType) || "traditionnelle";
                    const depart = (Array.isArray(formStructures) && formStructures.length > 0)
                      ? formStructures.map(s => ({ ...s }))
                      : [{
                          type: t0,
                          longueur: num0(formLongueur, 8),
                          largeur: num0(formLargeur, 6),
                          hauteur: formHauteur ? num0(formHauteur, 3) : undefined,
                          pente: formPente ? num0(formPente, 35) : undefined,
                          couverture: formCouverture || undefined,
                          desc: "volume principal",
                        }];
                    setEditionVolumes(depart);
                    console.log("[DEVIA] Decomposition manuelle ouverte depuis le formulaire : " + depart.length + " volume(s)");
                  }
                  setVolumeSel(0);
                  setModeToutEditer(true);
                  setEditeurOuvert(true);
                }} style={{ marginTop: 8, padding: "8px 16px", borderRadius: 9, cursor: "pointer", background: "rgba(240,192,64,0.10)", border: "1px solid rgba(240,192,64,0.45)", color: "#f0c040", fontSize: 12.5, fontWeight: 700 }}>
                  Decomposition manuelle
                </button>""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
