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

# 1) Bouton de suppression sur chaque ligne de volume
remp("bouton suppr",
"""          <span>dec.</span>
          <input value={v.pos.decalage === undefined ? 0 : v.pos.decalage} onChange={e => majPos(i, "decalage", e.target.value)} style={{ ...miniInp, width: 46 }} />
        </>
      ) : null}
    </div>
  );""",
"""          <span>dec.</span>
          <input value={v.pos.decalage === undefined ? 0 : v.pos.decalage} onChange={e => majPos(i, "decalage", e.target.value)} style={{ ...miniInp, width: 46 }} />
        </>
      ) : null}
      <button type="button" onClick={() => supprimerVolume(i)} title="supprimer ce volume" style={{ ...miniInp, cursor: "pointer", color: "#e05252", borderColor: "rgba(224,82,82,0.4)", fontWeight: 700, padding: "2px 7px" }}>suppr</button>
    </div>
  );""")

# 2) Ajouter et supprimer un volume a la main
remp("fonctions ajout suppression",
"""  const enregistrerCorrections = async () => {""",
"""  const ajouterVolume = (modele) => {
    setEditionVolumes(prev => {
      const liste = Array.isArray(prev) ? prev : [];
      const base0 = liste.length > 0 ? liste[0] : null;
      if (modele === "enterre") {
        console.log("[DEVIA] Volume ajoute a la main : niveau enterre");
        return liste.concat([{ type: "etage", longueur: base0 ? base0.longueur : 8, largeur: base0 ? base0.largeur : 6, hauteur: 2.6, pose: -2.6, appuis: "murs", desc: "niveau enterre (sous-sol)" }]);
      }
      const nv = { type: "traditionnelle", longueur: 6, largeur: 4, hauteur: 2.5, pente: 35, desc: "volume ajoute a la main" };
      if (liste.length > 0) nv.pos = { contre: 1, cote: "pignon_droit", facade: null, alignement: null, decalage: 0, faitage: "parallele" };
      console.log("[DEVIA] Volume ajoute a la main");
      return liste.concat([nv]);
    });
    setModeToutEditer(true);
  };
  const supprimerVolume = (idx) => {
    setEditionVolumes(prev => {
      const liste = Array.isArray(prev) ? prev : [];
      if (liste.length <= 1) return liste;
      const reste = liste.filter((x, k) => (k === idx) === false);
      return reste.map((v, k) => {
        if (k === 0) { const v0 = { ...v }; delete v0.pos; return v0; }
        if (v.pos === undefined || v.pos === null) return v;
        let c = parseInt(v.pos.contre, 10) || 1;
        if (c === idx + 1) c = 1;
        else if (c > idx + 1) c = c - 1;
        if (c === k + 1) c = 1;
        return { ...v, pos: { ...v.pos, contre: c } };
      });
    });
    setVolumeSel(0);
  };
  const enregistrerCorrections = async () => {""")

# 3) Le mode d appui suit le volume jusqu au moteur
remp("appuis conserve",
"""        pose: (v.pose === undefined || v.pose === "") ? undefined : num(v.pose, 0),""",
"""        pose: (v.pose === undefined || v.pose === "") ? undefined : num(v.pose, 0),
        appuis: v.appuis || undefined,""")

# 4) Les boutons dans la decomposition manuelle
remp("barre de boutons",
"""<div>{editionVolumes.map((v, i) => ligneVolume(v, i))}</div>""",
"""<div>
                          {editionVolumes.map((v, i) => ligneVolume(v, i))}
                          <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
                            <button type="button" onClick={() => ajouterVolume("simple")} style={{ ...miniInp, cursor: "pointer", fontWeight: 700, color: "#f0c040", borderColor: "rgba(240,192,64,0.5)" }}>+ Ajouter un volume</button>
                            <button type="button" onClick={() => ajouterVolume("enterre")} style={{ ...miniInp, cursor: "pointer", fontWeight: 700, color: "#f0c040", borderColor: "rgba(240,192,64,0.5)" }}>+ Ajouter un niveau enterre (sous-sol)</button>
                          </div>
                          <div style={{ marginTop: 6, color: cl("#9ca0b8", "#6a6e80"), fontSize: 10.5, lineHeight: 1.5 }}>Un volume ajoute a la main se regle comme les autres ; un niveau enterre se place sous le volume principal, avec une pose negative.</div>
                        </div>""")

# 5) MOTEUR : un volume a pose negative va SOUS son volume de reference, pas a cote
remp("tri des volumes enterres",
"""      const rangee = [];
      const ancres = [];
      const accoles = [];
      listeOuvrages.forEach((o, i) => {
        if (idxPorteur < 0 || i === idxPorteur) { rangee.push(o); return; }""",
"""      const rangee = [];
      const ancres = [];
      const accoles = [];
      const enterres = [];
      listeOuvrages.forEach((o, i) => {
        if (typeof o.pose === "number" && o.pose < -0.05) { enterres.push(o); return; }
        if (idxPorteur < 0 || i === idxPorteur) { rangee.push(o); return; }""")

remp("placement des volumes enterres",
"""      // Ancres : colles sur le porteur, sans mur d'ancrage propre""",
"""      // Niveaux enterres : sous leur volume de reference, jamais a cote
      enterres.forEach((o) => {
        let ref = (o.pos && o.pos.contre) ? listeOuvrages[o.pos.contre - 1] : null;
        if (ref === undefined || ref === null) ref = (idxPorteur >= 0) ? listeOuvrages[idxPorteur] : listeOuvrages[0];
        const grp = construire(o);
        if (o.faitageCardinal === "nord_sud") grp.rotation.y = Math.PI / 2;
        grp.position.x = posRangee.get(ref) || 0;
        console.log("[DEVIA] Niveau enterre place sous V" + (listeOuvrages.indexOf(ref) + 1) + " a " + o.pose + " m");
      });

      // Ancres : colles sur le porteur, sans mur d'ancrage propre""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
