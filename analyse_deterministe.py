# Analyse deterministe : temperature 0 sans thinking (meme plan -> memes chiffres)
# + resume visible de la decomposition dans le formulaire
import shutil, datetime, sys

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"

with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''          model: "claude-sonnet-5",
          max_tokens: 12000,
          thinking: { type: "adaptive" },
          output_config: { effort: "low" },'''
NEW1 = '''          model: "claude-sonnet-5",
          max_tokens: 12000,
          temperature: 0,'''

OLD2 = '''const [analyseErreur, setAnalyseErreur] = useState(""); // detail technique du dernier echec d'analyse'''
NEW2 = '''const [analyseErreur, setAnalyseErreur] = useState(""); // detail technique du dernier echec d'analyse
const [analyseResume, setAnalyseResume] = useState(""); // resume visible de la decomposition detectee'''

OLD3 = '''    setAnalyseErreur("");'''
NEW3 = '''    setAnalyseErreur("");
    setAnalyseResume("");'''

OLD4 = '''        console.log("[DEVIA] Positions extraites : " + structs.map((s, k) => "V" + (k + 1) + (s.pos ? " contre V" + s.pos.contre + " cote " + s.pos.cote + " decalage " + s.pos.decalage + "m faitage " + s.pos.faitage : " libre")).join(" | "));'''
NEW4 = '''        console.log("[DEVIA] Positions extraites : " + structs.map((s, k) => "V" + (k + 1) + (s.pos ? " contre V" + s.pos.contre + " cote " + s.pos.cote + " decalage " + s.pos.decalage + "m faitage " + s.pos.faitage : " libre")).join(" | "));
        setAnalyseResume(structs.map((s, k) => "V" + (k + 1) + " " + (LT_DECOMP[s.type] || s.type) + " " + s.longueur + "x" + s.largeur + "m" + (s.pos ? " - contre V" + s.pos.contre + ", " + String(s.pos.cote).replace("_", " ") + (s.pos.decalage ? ", decalage " + s.pos.decalage + "m" : "") : "")).join(" | "));'''

OLD5 = '''                {analyseFichier === "erreur" && (
                  <div style={{ marginTop: 8, color: "#e05252", fontSize: 12 }}>
                    Analyse du plan impossible - remplis les champs manuellement (le fichier sera quand meme joint au devis).
                    {analyseErreur ? <div style={{ marginTop: 4, color: "#b8bccc", fontSize: 11 }}>Detail technique : {analyseErreur}</div> : null}
                  </div>
                )}'''
NEW5 = '''                {analyseFichier === "erreur" && (
                  <div style={{ marginTop: 8, color: "#e05252", fontSize: 12 }}>
                    Analyse du plan impossible - remplis les champs manuellement (le fichier sera quand meme joint au devis).
                    {analyseErreur ? <div style={{ marginTop: 4, color: "#b8bccc", fontSize: 11 }}>Detail technique : {analyseErreur}</div> : null}
                  </div>
                )}
                {analyseResume ? (
                  <div style={{ marginTop: 8, padding: "8px 10px", background: "rgba(240,192,64,0.06)", border: "1px solid rgba(240,192,64,0.25)", borderRadius: 8, color: "#d8b95a", fontSize: 11.5, lineHeight: 1.5 }}>
                    Decomposition du plan : {analyseResume}
                  </div>
                ) : null}'''

anchors = [("appel analyse", OLD1, NEW1), ("etat resume", OLD2, NEW2), ("reset resume", OLD3, NEW3), ("set resume", OLD4, NEW4), ("affichage resume", OLD5, NEW5)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)

shutil.copy2(F, F + ".backup_" + stamp + "_analyse_deterministe")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : analyse deterministe (temp 0) + decomposition affichee dans le formulaire")
