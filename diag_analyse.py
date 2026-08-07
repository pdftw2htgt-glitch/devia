# Analyse de plans : la cause exacte de l'echec s'affiche dans le formulaire
import shutil, datetime, sys

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"

with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''const [analyseFichier, setAnalyseFichier] = useState(""); // "" | "encours" | "ok" | "erreur"'''
NEW1 = '''const [analyseFichier, setAnalyseFichier] = useState(""); // "" | "encours" | "ok" | "erreur"
const [analyseErreur, setAnalyseErreur] = useState(""); // detail technique du dernier echec d'analyse'''

OLD2 = '''    setAnalyseFichier("encours");'''
NEW2 = '''    setAnalyseFichier("encours");
    setAnalyseErreur("");'''

OLD3 = '''      const data = await response.json();
      if (data && data.error) throw new Error("API analyse : " + (data.error.message || JSON.stringify(data.error)));'''
NEW3 = '''      const brut = await response.text();
      if (response.ok === false) throw new Error("HTTP " + response.status + " : " + brut.slice(0, 200));
      let data = null;
      try { data = JSON.parse(brut); } catch (pe) { throw new Error("Reponse serveur illisible : " + brut.slice(0, 200)); }
      if (data && data.error) throw new Error("API analyse : " + (data.error.message || JSON.stringify(data.error)));'''

OLD4 = '''    } catch (e) {
      console.warn("[DEVIA] Analyse fichier:", e);
      setAnalyseFichier("erreur");
    }'''
NEW4 = '''    } catch (e) {
      console.warn("[DEVIA] Analyse fichier:", e);
      setAnalyseErreur(e && e.message ? String(e.message) : "erreur inconnue");
      setAnalyseFichier("erreur");
    }'''

OLD5 = '''                {analyseFichier === "erreur" && (
                  <div style={{ marginTop: 8, color: "#e05252", fontSize: 12 }}>
                    Analyse du plan impossible - remplis les champs manuellement (le fichier sera quand meme joint au devis).
                  </div>
                )}'''
NEW5 = '''                {analyseFichier === "erreur" && (
                  <div style={{ marginTop: 8, color: "#e05252", fontSize: 12 }}>
                    Analyse du plan impossible - remplis les champs manuellement (le fichier sera quand meme joint au devis).
                    {analyseErreur ? <div style={{ marginTop: 4, color: "#b8bccc", fontSize: 11 }}>Detail technique : {analyseErreur}</div> : null}
                  </div>
                )}'''

anchors = [("etat analyse", OLD1, NEW1), ("debut analyse", OLD2, NEW2), ("lecture reponse", OLD3, NEW3), ("catch analyse", OLD4, NEW4), ("affichage erreur", OLD5, NEW5)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)

shutil.copy2(F, F + ".backup_" + stamp + "_diag_analyse")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : le detail de l'erreur d'analyse s'affiche dans le formulaire")
