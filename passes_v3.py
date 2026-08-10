# Passes v3 : budget 20000, passe vide = erreur franche, cache purge (v3)
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''            max_tokens: 12000,'''
NEW1 = '''            max_tokens: 20000,'''

OLD2 = '''        return (tb2 && tb2.text) ? tb2.text.replace(/\\x60\\x60\\x60json|\\x60\\x60\\x60/g, "").trim() : "";'''
NEW2 = '''        const texteFinal = (tb2 && tb2.text) ? tb2.text.replace(/\\x60\\x60\\x60json|\\x60\\x60\\x60/g, "").trim() : "";
        if (texteFinal === "") throw new Error("Passe d'analyse vide (stop_reason " + ((dat && dat.stop_reason) || "inconnu") + ") - relance l'analyse");
        return texteFinal;'''

OLD3 = '''const versionPrompt = vh.toString(36) + "-p3v2";'''
NEW3 = '''const versionPrompt = vh.toString(36) + "-p3v3";'''

anchors = [("budget passes", OLD1, NEW1), ("garde passe vide", OLD2, NEW2), ("purge cache v3", OLD3, NEW3)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_passes_v3")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : passes v3 (budget 20000, vide = erreur, cache purge)")
