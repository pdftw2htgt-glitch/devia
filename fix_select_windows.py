# -*- coding: utf-8 -*-
import io

chemin = "devia.jsx"
s = io.open(chemin, encoding="utf-8").read()

ancre = '    @keyframes fadeInUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }\n'
n = s.count(ancre)
print("ancre trouvee :", n, "(attendu 1)")
if n != 1:
    raise SystemExit("ABANDON : ancre introuvable ou multiple")

if s.count("select option") > 0:
    raise SystemExit("ABANDON : la regle existe deja")

ajout = ancre + '''    /* Windows dessine la liste deroulante avec les couleurs du select lui-meme.
       Un fond translucide y devient blanc : sans couleurs opaques posees ici,
       le texte clair se retrouve blanc sur blanc et les choix sont invisibles. */
    select option, select optgroup {
      background-color: ${themeMode === "light" ? "#ffffff" : "#181a26"};
      color: ${themeMode === "light" ? "#1a1d2a" : "#e8eaf2"};
    }
'''

s = s.replace(ancre, ajout)
io.open(chemin, "w", encoding="utf-8").write(s)
print("OK regle posee")
