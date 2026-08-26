import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

a = "let metreVue = null;"
b = '''let metreVue = null;
    console.log("[DEVIA][3D]", JSON.stringify({ L: params.longueur, lg: params.largeur, H: params.hauteur, pente: params.pente, type: params.type_projet, debord: params.debord, sk: params.sk, dS: params.dS, murs: params.murs, essence: params.essence, finition: params.finition, nbOuvrages: (params.ouvrages || []).length }));'''

n = txt.count(a)
if n != 1:
    print("ABANDON : ancre en", n, "exemplaire(s)")
    raise SystemExit(1)

txt = txt.replace(a, b)
shutil.copy(CHEMIN, CHEMIN + ".backup_debug3d_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : log de diagnostic 3D active")
