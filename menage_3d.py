import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

LOG_DEBUG = '''let metreVue = null;
    console.log("[DEVIA][3D]", JSON.stringify({ L: params.longueur, lg: params.largeur, H: params.hauteur, pente: params.pente, type: params.type_projet, debord: params.debord, sk: params.sk, dS: params.dS, murs: params.murs, essence: params.essence, finition: params.finition, nbOuvrages: (params.ouvrages || []).length }));'''

REMPL = [
    # 1. Vider completement le cadre 3D avant chaque construction (canvas + boussole + restes)
    ("mountRef.current.appendChild(renderer.domElement);",
     "while (mountRef.current.firstChild) { mountRef.current.removeChild(mountRef.current.firstChild); }\n    mountRef.current.appendChild(renderer.domElement);"),
    # 2. Balayage du pre-calcul : detacher chaque piece de son VRAI parent (sous-groupes compris)
    ("toRemove.forEach((o) => { scene.remove(o); if (o.geometry) o.geometry.dispose(); });",
     "toRemove.forEach((o) => { if (o.parent) o.parent.remove(o); if (o.geometry) o.geometry.dispose(); });"),
    # 3. Retrait du log de diagnostic
    (LOG_DEBUG, "let metreVue = null;"),
]

ok = True
for a, b in REMPL:
    n = txt.count(a)
    if n != 1:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu 1 :", a[:70].replace(chr(10), " / "))
        ok = False
if ok == False:
    raise SystemExit(1)

for a, b in REMPL:
    txt = txt.replace(a, b)

shutil.copy(CHEMIN, CHEMIN + ".backup_menage3d_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : cadre 3D vide avant chaque construction, balayage repare, log retire")
