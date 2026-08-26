import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

REMPL = [
    ('bgRoot: "radial-gradient(ellipse at top, rgba(30, 35, 50, 0.4) 0%, #08090c 50%), #08090c",',
     'bgRoot: "#08090c",'),
    ('.devia-bg-noise { background-image: radial-gradient(at 0% 0%, rgba(240, 192, 64, 0.04) 0px, transparent 40%), radial-gradient(at 100% 100%, rgba(96, 165, 250, 0.03) 0px, transparent 40%); }',
     '.devia-bg-noise { background-image: none; }'),
]

ok = True
for a, b in REMPL:
    n = txt.count(a)
    if n != 1:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu 1 :", a[:70])
        ok = False
if ok == False:
    raise SystemExit(1)

for a, b in REMPL:
    txt = txt.replace(a, b)

shutil.copy(CHEMIN, CHEMIN + ".backup_fond_uni_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : fond noir uni (#08090c), degrades retires")
