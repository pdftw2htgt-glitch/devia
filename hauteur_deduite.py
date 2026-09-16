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

# 1) Le schema des volumes accepte la hauteur au faitage
remp("schema hauteur_faitage",
'"longueur":num,"largeur":num,"hauteur_murs":num_ou_null,',
'"longueur":num,"largeur":num,"hauteur_murs":num_ou_null,"hauteur_faitage":num_ou_null,')

# 2) Consigne : mieux vaut le faitage que rien
remp("consigne faitage par volume",
"""REGLES DE LECTURE DES HAUTEURS (tres important) : hauteur_murs = hauteur a l'egout""",
"""HAUTEUR DE CHAQUE VOLUME (tres important) : aucun volume ne doit repartir sans aucune hauteur. Si la coupe donne l'egout de ce volume, remplis hauteur_murs. Si elle ne donne que le point le plus haut, remplis hauteur_faitage et laisse hauteur_murs a null : le moteur convertit lui-meme l'egout a partir de la pente et de la largeur. Ne remplis les deux a null que si AUCUNE cote de ce volume ne figure au dossier. REGLES DE LECTURE DES HAUTEURS (tres important) : hauteur_murs = hauteur a l'egout""")

# 3) Transporter la hauteur de faitage jusqu au moteur
remp("faitageH dans structs",
"""            hauteur: o.hauteur_murs || undefined,""",
"""            hauteur: o.hauteur_murs || undefined,
            faitageH: (typeof o.hauteur_faitage === "number" && o.hauteur_faitage > 0) ? o.hauteur_faitage : undefined,""")

# 4) Completement deterministe des hauteurs, avant le verificateur
remp("completerHauteurs",
"""        const verdictDecomp = verifierDecomposition(structs);""",
"""        const completerHauteurs = (liste) => {
          const notes = [];
          for (let tour = 0; tour < 2; tour++) {
            for (let iH = 0; iH < liste.length; iH++) {
              const s = liste[iH];
              if (typeof s.hauteur === "number" && s.hauteur > 0) continue;
              if (typeof s.faitageH === "number" && s.faitageH > 0 && typeof s.pente === "number" && s.pente > 0 && s.largeur > 0) {
                const eg = Math.round((s.faitageH - (s.largeur / 2) * Math.tan(s.pente * Math.PI / 180)) * 100) / 100;
                if (eg > 1 && eg < s.faitageH) {
                  s.hauteur = eg;
                  notes.push("V" + (iH + 1) + " : egout " + eg + " m calcule depuis le faitage " + s.faitageH + " m et la pente " + s.pente + " deg");
                  continue;
                }
              }
              const numPorteur = (s.pos && s.pos.contre) ? s.pos.contre : 0;
              const porteur = numPorteur > 0 ? liste[numPorteur - 1] : null;
              if (s.type === "sas") {
                const hv = [];
                if (porteur && typeof porteur.hauteur === "number" && porteur.hauteur > 0) hv.push(porteur.hauteur);
                liste.forEach((a, k) => { if (a.pos && a.pos.contre === iH + 1 && typeof a.hauteur === "number" && a.hauteur > 0) hv.push(a.hauteur); });
                if (hv.length > 0) {
                  const hs = Math.round((Math.min.apply(null, hv) - 0.3) * 100) / 100;
                  if (hs > 1.8) {
                    s.hauteur = hs;
                    notes.push("V" + (iH + 1) + " (sas) : toit plat pose 30 cm sous l egout du volume le plus bas (" + hs + " m)");
                    continue;
                  }
                }
              }
              if (tour === 1 && porteur && typeof porteur.hauteur === "number" && porteur.hauteur > 0) {
                s.hauteur = porteur.hauteur;
                notes.push("V" + (iH + 1) + " : hauteur reprise du volume porteur V" + numPorteur + " (" + porteur.hauteur + " m) - A VERIFIER");
              }
            }
          }
          return notes;
        };
        const notesH = completerHauteurs(structs);
        if (notesH.length > 0) {
          notesH.forEach(t => console.warn("[DEVIA] Hauteur deduite - " + t));
          setAnalyseHauteursDeduites(notesH);
        } else { setAnalyseHauteursDeduites([]); }
        const verdictDecomp = verifierDecomposition(structs);""")

# 5) Etat React pour l affichage
remp("etat analyseHauteursDeduites",
"""  const rendrePagesImages = async (buf, nums, largeurMax, qualite) => {""",
"""  const [analyseHauteursDeduites, setAnalyseHauteursDeduites] = useState([]);
  const rendrePagesImages = async (buf, nums, largeurMax, qualite) => {""")

# 6) Bandeau orange : les hauteurs deduites sont dites, pas cachees
remp("bandeau hauteurs deduites",
"""                      Demander une nouvelle lecture (tu compareras avant de remplacer)
                    </button>
                    {analyseVerdict ? (analyseVerdict.ok ? (""",
"""                      Demander une nouvelle lecture (tu compareras avant de remplacer)
                    </button>
                    {analyseHauteursDeduites.length > 0 ? (
                      <div style={{ marginTop: 8, padding: "8px 10px", borderRadius: 8, background: "rgba(240,192,64,0.07)", border: "1px solid rgba(240,192,64,0.35)" }}>
                        <div style={{ color: "#f0c040", fontSize: 11.5, fontWeight: 700 }}>HAUTEURS DEDUITES ({analyseHauteursDeduites.length})</div>
                        {analyseHauteursDeduites.map((t, k) => (<div key={k} style={{ marginTop: 3, color: cl("#b8bccc", "#565a6c"), fontSize: 11, lineHeight: 1.5 }}>{t}</div>))}
                        <div style={{ marginTop: 4, color: cl("#9ca0b8", "#6a6e80"), fontSize: 10.5, lineHeight: 1.5 }}>Le dossier ne cotait pas ces hauteurs : elles sont calculees depuis le faitage ou reprises du volume porteur. Verifie-les dans la decomposition.</div>
                      </div>
                    ) : null}
                    {analyseVerdict ? (analyseVerdict.ok ? (""")

# 7) Bump de version
remp("version prompt",
'const versionPrompt = vh.toString(36) + "-p6v13";',
'const versionPrompt = vh.toString(36) + "-p6v14";')

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
