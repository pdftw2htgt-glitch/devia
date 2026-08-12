# Bouton "Relancer l'analyse" : purge le cache du fichier courant + relecture complete
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''const [analyseResume, setAnalyseResume] = useState(""); // resume visible de la decomposition detectee'''
NEW1 = '''const [analyseResume, setAnalyseResume] = useState(""); // resume visible de la decomposition detectee
const [analyseEmpreinte, setAnalyseEmpreinte] = useState(""); // empreinte du dernier fichier analyse'''

OLD2 = '''      const empreinte = Array.from(new Uint8Array(dig)).map(x => x.toString(16).padStart(2, "0")).join("");'''
NEW2 = '''      const empreinte = Array.from(new Uint8Array(dig)).map(x => x.toString(16).padStart(2, "0")).join("");
      setAnalyseEmpreinte(empreinte);'''

OLD3 = '''                {analyseResume ? (
                  <div style={{ marginTop: 8, padding: "8px 10px", background: "rgba(240,192,64,0.06)", border: "1px solid rgba(240,192,64,0.25)", borderRadius: 8, color: "#d8b95a", fontSize: 11.5, lineHeight: 1.5 }}>
                    Decomposition du plan : {analyseResume}
                  </div>
                ) : null}'''
NEW3 = '''                {analyseResume ? (
                  <div style={{ marginTop: 8, padding: "8px 10px", background: "rgba(240,192,64,0.06)", border: "1px solid rgba(240,192,64,0.25)", borderRadius: 8, color: "#d8b95a", fontSize: 11.5, lineHeight: 1.5 }}>
                    Decomposition du plan : {analyseResume}
                    <button type="button" onClick={async () => {
                      try {
                        if (analyseEmpreinte) await supabase.from("analyses_plans").delete().eq("empreinte", analyseEmpreinte);
                      } catch (eDel) { console.warn("[DEVIA] Purge cache impossible", eDel); }
                      analyserFichiers(files);
                    }} style={{ marginTop: 6, padding: "4px 10px", borderRadius: 7, cursor: "pointer", background: "rgba(240,192,64,0.10)", border: "1px solid rgba(240,192,64,0.4)", color: "#f0c040", fontSize: 11, fontWeight: 600, display: "block" }}>
                      Relancer l'analyse (relecture complete du plan)
                    </button>
                  </div>
                ) : null}'''

anchors = [("etat empreinte", OLD1, NEW1), ("memorise empreinte", OLD2, NEW2), ("bouton relancer", OLD3, NEW3)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_relancer_analyse")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : bouton Relancer l'analyse en place")
