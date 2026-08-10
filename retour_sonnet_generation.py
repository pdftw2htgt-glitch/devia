# Generation multi : retour sur sonnet-5 (opus sans gain constate)
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()
OLD1 = '''        const { parsed, data } = await callDeviaIA(systemPrompt, fp.description, "claude-opus-5");'''
NEW1 = '''        const { parsed, data } = await callDeviaIA(systemPrompt, fp.description);'''
n = c.count(OLD1)
if n != 1:
    print("ERREUR ancre : " + str(n) + " occurrence(s) - abandon")
    sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_retour_sonnet")
c = c.replace(OLD1, NEW1)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : generation multi de retour sur sonnet-5")
