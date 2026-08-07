# Retrait de temperature (refuse par le modele) - l'analyse reste sans thinking
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()
OLD1 = '''          model: "claude-sonnet-5",
          max_tokens: 12000,
          temperature: 0,'''
NEW1 = '''          model: "claude-sonnet-5",
          max_tokens: 12000,'''
n = c.count(OLD1)
if n != 1:
    print("ERREUR ancre : " + str(n) + " occurrence(s) - abandon")
    sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_fix_temperature")
c = c.replace(OLD1, NEW1)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : temperature retiree")
