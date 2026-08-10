# Routage des modeles : geometrie -> fable-5, devis multi -> opus-5, reste -> sonnet-5
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''      const appelAnalyse = async (sysTxt, contenu, effortNiveau) => {'''
NEW1 = '''      const appelAnalyse = async (sysTxt, contenu, effortNiveau, modele) => {'''

OLD2 = '''            model: "claude-sonnet-5",'''
NEW2 = '''            model: modele || "claude-sonnet-5",'''

OLD3 = '''        "high");'''
NEW3 = '''        "high", "claude-fable-5");'''

OLD4 = '''  const callDeviaIA = async (systemPrompt, userContent) => {'''
NEW4 = '''  const callDeviaIA = async (systemPrompt, userContent, modele) => {'''

OLD5 = '''        model: "claude-sonnet-5",'''
NEW5 = '''        model: modele || "claude-sonnet-5",'''

OLD6 = '''        const { parsed, data } = await callDeviaIA(systemPrompt, fp.description);'''
NEW6 = '''        const { parsed, data } = await callDeviaIA(systemPrompt, fp.description, "claude-opus-5");'''

OLD7 = '''const versionPrompt = vh.toString(36) + "-p3v3";'''
NEW7 = '''const versionPrompt = vh.toString(36) + "-p3v4";'''

anchors = [("helper analyse param", OLD1, NEW1), ("modele analyse", OLD2, NEW2), ("geometrie fable", OLD3, NEW3), ("callDeviaIA param", OLD4, NEW4), ("modele generation", OLD5, NEW5), ("multi vers opus", OLD6, NEW6), ("cache v4", OLD7, NEW7)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_routage_modeles")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : routage modeles (geometrie fable-5, devis multi opus-5, reste sonnet-5)")
