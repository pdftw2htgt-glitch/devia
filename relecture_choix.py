# relecture_choix.py — LA RELECTURE NE REMPLACE PLUS RIEN SANS TON ACCORD
# 1) memoire attachee au FICHIER : les mises a jour de DEVIA ne relisent plus
#    jamais un plan deja analyse (meme resultat a l infini, sans IA, gratuit)
# 2) le bouton relit SANS effacer : la nouvelle lecture est proposee a cote de
#    l ancienne, tu choisis laquelle garder. Rien n est ecrase en silence.
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''const [verrouActif, setVerrouActif] = useState(false); // dossier fige par les corrections utilisateur'''
R1 = r'''const [verrouActif, setVerrouActif] = useState(false); // dossier fige par les corrections utilisateur
const [lectureAncienne, setLectureAncienne] = useState(null); // lecture memorisee avant une relecture
const [lectureCandidate, setLectureCandidate] = useState(null); // nouvelle lecture proposee, en attente de ton choix'''

A2 = r'''  const analyserFichiers = async (fileList) => {'''
R2 = r'''  const analyserFichiers = async (fileList, forcer) => {'''

A3 = r'''        const { data: ligneCorr } = await supabase.from("analyses_plans").select("resultat").eq("empreinte", empreinte).eq("version", "corrections").limit(1).maybeSingle();
        if (ligneCorr && ligneCorr.resultat) {
          jCache = ligneCorr.resultat;
          console.log("[DEVIA] Corrections utilisateur servies (dossier verrouille par tes corrections)");
          setVerrouActif(true);
        } else {
          const { data: ligneCache } = await supabase.from("analyses_plans").select("resultat").eq("empreinte", empreinte).eq("version", versionPrompt).limit(1).maybeSingle();
          if (ligneCache && ligneCache.resultat) jCache = ligneCache.resultat;
          setVerrouActif(false);
        }'''
R3 = r'''        // Memoire attachee au FICHIER : toutes les lectures de cette empreinte,
        // quelle que soit la version des prompts. Priorite aux corrections, puis
        // choix deterministe (tri des versions, la premiere gagne toujours).
        const { data: lignes } = await supabase.from("analyses_plans").select("version, resultat").eq("empreinte", empreinte);
        const dispo = Array.isArray(lignes) ? lignes.filter(x => x && x.resultat) : [];
        const corr = dispo.find(x => x.version === "corrections");
        const tri = dispo.filter(x => x.version !== "corrections").slice().sort((a, b) => String(a.version).localeCompare(String(b.version)));
        ancienJ = corr ? corr.resultat : (tri.length > 0 ? tri[0].resultat : null);
        if (forcer === true) {
          setVerrouActif(false);
          console.log("[DEVIA] Relecture demandee : l ancienne lecture est conservee jusqu a ton choix");
        } else if (corr) {
          jCache = corr.resultat;
          console.log("[DEVIA] Corrections utilisateur servies (dossier verrouille par tes corrections)");
          setVerrouActif(true);
        } else if (ancienJ) {
          jCache = ancienJ;
          console.log("[DEVIA] Lecture memorisee servie : ce plan ne sera plus relu, resultat identique a chaque fois");
          setVerrouActif(false);
        } else {
          setVerrouActif(false);
        }'''

A4 = r'''      let jCache = null;'''
R4 = r'''      let jCache = null;
      let ancienJ = null;'''

A5 = r'''      if (uCache) {
        try {
          await supabase.from("analyses_plans").upsert({ user_id: uCache.id, empreinte: empreinte, version: versionPrompt, resultat: j }, { onConflict: "user_id,empreinte,version" });'''
R5 = r'''      if (uCache && (forcer !== true || ancienJ === null)) {
        try {
          await supabase.from("analyses_plans").upsert({ user_id: uCache.id, empreinte: empreinte, version: versionPrompt, resultat: j }, { onConflict: "user_id,empreinte,version" });'''

A6 = r'''      analyseJRef.current = j;
      analyseVersionRef.current = versionPrompt;'''
R6 = r'''      if (forcer === true && ancienJ) {
        // Nouvelle lecture obtenue : on ne remplace RIEN, on te propose le choix
        setLectureAncienne(ancienJ);
        setLectureCandidate(j);
        setAnalyseFichier("choix");
        console.log("[DEVIA] Nouvelle lecture prete : en attente de ton choix (ancienne conservee)");
        return;
      }
      analyseJRef.current = j;
      analyseVersionRef.current = versionPrompt;'''

A7 = r'''                      Relancer l'analyse (relecture complete du plan)'''
R7 = r'''                      Demander une nouvelle lecture (tu compareras avant de remplacer)'''

A8 = r'''                {analyseFichier === "erreur" && ('''
R8 = r'''                {analyseFichier === "choix" && lectureCandidate ? (
                  <div style={{ marginTop: 8, padding: "10px 12px", background: "rgba(240,192,64,0.06)", border: "1px solid rgba(240,192,64,0.35)", borderRadius: 10 }}>
                    <div style={{ color: "#f0c040", fontSize: 12.5, fontWeight: 700, marginBottom: 8 }}>Deux lectures de ce plan - laquelle garde-t-on ?</div>
                    {[["Lecture actuelle (celle qui est en place)", lectureAncienne], ["Nouvelle lecture", lectureCandidate]].map((duo, di) => (
                      <div key={di} style={{ marginBottom: 8 }}>
                        <div style={{ color: cl("#d0d2dc", "#3a3e50"), fontSize: 11.5, fontWeight: 700 }}>{duo[0]}</div>
                        <div style={{ color: cl("#9ca0b8", "#565a6c"), fontSize: 11, lineHeight: 1.5 }}>{(duo[1] && Array.isArray(duo[1].ouvrages) && duo[1].ouvrages.length > 0) ? duo[1].ouvrages.map((o, k) => "V" + (k + 1) + " " + (o.type || "?") + " " + (o.longueur || "?") + "x" + (o.largeur || "?") + "m" + (o.hauteur_murs ? " h" + o.hauteur_murs : "")).join(" | ") : "ouvrage simple (pas de decomposition)"}</div>
                      </div>
                    ))}
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 4 }}>
                      <button type="button" onClick={() => { setLectureCandidate(null); setLectureAncienne(null); analyserFichiers(files); }} style={{ padding: "6px 14px", borderRadius: 8, cursor: "pointer", background: "rgba(126,201,126,0.12)", border: "1px solid rgba(126,201,126,0.45)", color: "#7ec97e", fontSize: 12, fontWeight: 700 }}>Garder la lecture actuelle</button>
                      <button type="button" onClick={async () => {
                        try {
                          const { data: { user: uAd } } = await supabase.auth.getUser();
                          if (uAd && analyseEmpreinte) await supabase.from("analyses_plans").upsert({ user_id: uAd.id, empreinte: analyseEmpreinte, version: "adoptee", resultat: lectureCandidate }, { onConflict: "user_id,empreinte,version" });
                        } catch (eAd) { console.warn("[DEVIA] Adoption impossible", eAd); }
                        setLectureCandidate(null); setLectureAncienne(null); analyserFichiers(files);
                      }} style={{ padding: "6px 14px", borderRadius: 8, cursor: "pointer", background: "rgba(240,192,64,0.12)", border: "1px solid rgba(240,192,64,0.5)", color: "#f0c040", fontSize: 12, fontWeight: 700 }}>Adopter la nouvelle lecture</button>
                    </div>
                  </div>
                ) : null}
                {analyseFichier === "erreur" && ('''

paires = [
    ("states choix", A1, R1),
    ("signature forcer", A2, R2),
    ("lecture memoire fichier", A3, R3),
    ("variable ancienJ", A4, R4),
    ("ecriture cache conditionnelle", A5, R5),
    ("arret avant remplacement", A6, R6),
    ("bouton relecture", A7, R7),
    ("bloc comparaison", A8, R8),
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
print("8 modifications ecrites. Backup : " + F + ".bak_" + tag)
