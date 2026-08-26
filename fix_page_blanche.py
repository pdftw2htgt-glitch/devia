import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

a = '''let MODE_CLAIR = false;
const cl = (sombre, clair) => (MODE_CLAIR ? clair : sombre);'''

b = '''var MODE_CLAIR = false;
function cl(sombre, clair) { return MODE_CLAIR ? clair : sombre; }'''

n = txt.count(a)
if n != 1:
    print("ABANDON : ancre en", n, "exemplaire(s), attendu 1")
    raise SystemExit(1)

txt = txt.replace(a, b)
shutil.copy(CHEMIN, CHEMIN + ".backup_fix_blanche_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : cl() disponible des le chargement, page blanche corrigee")
