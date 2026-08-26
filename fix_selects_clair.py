import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

REMPL = [
    # Les 2 menus deroulants au-dessus de la 3D (fond + vue)
    ('background: "#181a26", color: cl("#d0d2dc", "#3a3e50") }}>',
     'background: cl("#181a26", "#ffffff"), color: cl("#d0d2dc", "#3a3e50") }}>', 2),
    # Fenetre de decomposition (fond sombre en dur)
    ('background: "#14161f", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 16, padding: 20 }}>',
     'background: cl("#14161f", "#ffffff"), border: cl("1px solid rgba(255,255,255,0.12)", "1px solid rgba(0,0,0,0.12)"), borderRadius: 16, padding: 20 }}>', 1),
]

ok = True
for a, b, attendu in REMPL:
    n = txt.count(a)
    if n != attendu:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu", attendu, ":", a[:60])
        ok = False
if ok == False:
    raise SystemExit(1)

for a, b, attendu in REMPL:
    txt = txt.replace(a, b)

shutil.copy(CHEMIN, CHEMIN + ".backup_selects_clair_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : menus fond/vue et fenetre de decomposition lisibles en mode clair")
