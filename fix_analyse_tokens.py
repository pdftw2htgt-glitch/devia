# Analyse de plans : plafond de tokens releve (le JSON de decomposition est plus long)
# + messages d'erreur API explicites dans la console
import shutil, datetime, sys

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"

with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''          max_tokens: 4000,'''
NEW1 = '''          max_tokens: 12000,'''

OLD2 = '''      const data = await response.json();
      const tb = (data.content && Array.isArray(data.content)) ? data.content.find(b => b && b.type === "text" && b.text) : null;'''
NEW2 = '''      const data = await response.json();
      if (data && data.error) throw new Error("API analyse : " + (data.error.message || JSON.stringify(data.error)));
      if (data && data.stop_reason === "max_tokens") console.warn("[DEVIA] Analyse : reponse tronquee (max_tokens atteint)");
      const tb = (data.content && Array.isArray(data.content)) ? data.content.find(b => b && b.type === "text" && b.text) : null;'''

anchors = [("plafond tokens analyse", OLD1, NEW1), ("lecture reponse analyse", OLD2, NEW2)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)

shutil.copy2(F, F + ".backup_" + stamp + "_fix_analyse_tokens")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : analyse a 12000 tokens + erreurs API visibles en console")
