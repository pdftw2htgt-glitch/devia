import re, shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

A1 = "// ====== Palettes Theme (Mode Clair / Sombre) ======"
B1 = '''// ====== Interrupteur global mode clair (assombrit les couleurs codees en dur) ======
let MODE_CLAIR = false;
const cl = (sombre, clair) => (MODE_CLAIR ? clair : sombre);

// ====== Palettes Theme (Mode Clair / Sombre) ======'''

A2 = "const t = themes[themeMode] || themes.dark;"
B2 = "const t = themes[themeMode] || themes.dark;\n  MODE_CLAIR = themeMode === \"light\";"

for a in (A1, A2):
    if txt.count(a) != 1:
        print("ABANDON : ancre en", txt.count(a), "exemplaire(s) :", a[:60])
        raise SystemExit(1)

txt = txt.replace(A1, B1)
txt = txt.replace(A2, B2)

# (couleur sombre, equivalent fonce en clair) — remplace partout SAUF en attribut JSX (precede de =)
PAIRES = [
    ('"#d0d2dc"', '"#3a3e50"'),
    ('"#9ca0b8"', '"#565a6c"'),
    ('"#7a7d92"', '"#5f6374"'),
    ('"#e8eaf2"', '"#1a1d2a"'),
    ('"#f5f6fa"', '"#14161f"'),
    ('"rgba(255, 255, 255, 0.02)"', '"rgba(0, 0, 0, 0.03)"'),
    ('"rgba(255, 255, 255, 0.04)"', '"rgba(0, 0, 0, 0.04)"'),
    ('"rgba(255, 255, 255, 0.05)"', '"rgba(0, 0, 0, 0.08)"'),
    ('"rgba(255, 255, 255, 0.06)"', '"rgba(0, 0, 0, 0.09)"'),
    ('"rgba(255,255,255,0.03)"', '"rgba(0,0,0,0.04)"'),
    ('"rgba(255,255,255,0.06)"', '"rgba(0,0,0,0.09)"'),
    ('"rgba(255,255,255,0.08)"', '"rgba(0,0,0,0.10)"'),
    ('"1px solid rgba(255, 255, 255, 0.05)"', '"1px solid rgba(0, 0, 0, 0.08)"'),
    ('"1px solid rgba(255, 255, 255, 0.06)"', '"1px solid rgba(0, 0, 0, 0.09)"'),
    ('"1px solid rgba(255, 255, 255, 0.08)"', '"1px solid rgba(0, 0, 0, 0.10)"'),
    ('"1px solid rgba(255,255,255,0.06)"', '"1px solid rgba(0,0,0,0.09)"'),
    ('"1px solid rgba(255,255,255,0.08)"', '"1px solid rgba(0,0,0,0.10)"'),
]

total = 0
for sombre, clair in PAIRES:
    motif = "(?<!=)" + re.escape(sombre)
    rempl = 'cl(' + sombre + ', ' + clair + ')'
    txt, n = re.subn(motif, rempl.replace("\\\\", "\\\\\\\\"), txt)
    total += n
    print(sombre, "->", n, "remplacement(s)")

shutil.copy(CHEMIN, CHEMIN + ".backup_mode_clair3_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK :", total, "couleurs basculees via cl() — mode clair fonce partout")
