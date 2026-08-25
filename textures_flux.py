import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

REMPL = [
    # 1. Sauvegarde solo : persiste essence et finition dans le devis
    ("if (finalParams.debord) parsed._debord = finalParams.debord;",
     "if (finalParams.debord) parsed._debord = finalParams.debord;\n"
     "  if (finalParams.essence) parsed._essence = finalParams.essence;\n"
     "  if (finalParams.finition) parsed._finition = finalParams.finition;"),
    # 2. Vue 3D solo : transmet essence et finition au viewer
    ("debord: finalParams.debord || undefined",
     "debord: finalParams.debord || undefined,\n"
     "        essence: finalParams.essence || undefined,\n"
     "        finition: finalParams.finition || undefined"),
    # 3. Rechargement d'un projet : relit essence et finition
    ("debord: project.devis_data._debord || undefined,",
     "debord: project.devis_data._debord || undefined,\n"
     "        essence: project.devis_data._essence || undefined,\n"
     "        finition: project.devis_data._finition || undefined,"),
    # 4. Multi-ouvrages : chaque ouvrage 3D garde sa finition
    ("couverture: s.couverture, essence: s.essence, murs: s.murs, debord: s.debord || undefined,",
     "couverture: s.couverture, essence: s.essence, finition: s.finition || undefined, murs: s.murs, debord: s.debord || undefined,"),
    # 5. Editeur de decomposition : ne perd plus la finition
    ("pente: v.pente, couverture: v.couverture, essence: v.essence,",
     "pente: v.pente, couverture: v.couverture, essence: v.essence, finition: v.finition || undefined,"),
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

shutil.copy(CHEMIN, CHEMIN + ".backup_textures_flux_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : essence et finition transmises a la 3D (solo, rechargement, multi, decomposition)")
