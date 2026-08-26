import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

a = '''                  e.currentTarget.style.borderColor = cl("rgba(255, 255, 255, 0.06)", "rgba(0, 0, 0, 0.09)");
                  e.currentTarget.style.background = "rgba(22, 25, 35, 0.55)";'''

b = '''                  e.currentTarget.style.borderColor = t.cardBorder;
                  e.currentTarget.style.background = t.cardBg;'''

n = txt.count(a)
if n != 1:
    print("ABANDON : ancre en", n, "exemplaire(s), attendu 1")
    raise SystemExit(1)

txt = txt.replace(a, b)
shutil.copy(CHEMIN, CHEMIN + ".backup_hover_projet_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : la carte projet retrouve sa couleur d'origine apres le survol")
