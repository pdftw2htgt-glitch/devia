# Restauration config analyse qui marchait (thinking adaptive + effort low)
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()
OLD1 = '''          model: "claude-sonnet-5",
          max_tokens: 12000,'''
NEW1 = '''          model: "claude-sonnet-5",
          max_tokens: 12000,
          thinking: { type: "adaptive" },
          output_config: { effort: "low" },'''
n = c.count(OLD1)
if n != 1:
    print("ERREUR ancre : " + str(n) + " occurrence(s) - abandon")
    sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_restaure_analyse")
c = c.replace(OLD1, NEW1)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : analyse restauree (thinking adaptive + effort low)")
