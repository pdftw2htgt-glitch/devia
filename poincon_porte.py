# -*- coding: utf-8 -*-
import io, sys

chemin = sys.argv[1] if len(sys.argv) > 1 else "devia.jsx"
s = io.open(chemin, encoding="utf-8").read()
etapes = []

def rempl(titre, ancre, nouveau, attendu=1):
    global s
    n = s.count(ancre)
    etapes.append((titre, n, attendu))
    if n > attendu or n < attendu:
        raise SystemExit("ABANDON sur '" + titre + "' : " + str(n) + " occurrence(s), attendu " + str(attendu))
    s = s.replace(ancre, nouveau)

rempl("1. le poincon passe sous la faitiere",
"""    // Tete du poincon : il monte jusqu au DESSUS de la panne faitiere. Memes formules que la
    // pose de la faitiere plus bas - dPerp0 vaut dPerpSousChevron, elles sont calculees pareil.
    const yFaitierePoincon = Ht + hf + dPerp0 / cosA0 - (pfB0 / 2) * tanA0 + delardement - pfH0 / 2;
    const yTetePoincon = yFaitierePoincon + pfH0 / 2;
""",
"""    // Tete du poincon : il passe SOUS la faitiere et la PORTE. Son dessus s arrete a la
    // sous-face de la panne, et l embrevement creuse dedans la cale lateralement. Les joues
    // ne montent donc que de la profondeur de l encoche : le poincon soutient, il n enserre pas.
    // Memes formules que la pose de la faitiere plus bas - dPerp0 vaut dPerpSousChevron.
    const EMBREVEMENT_FAITIERE = 0.04;              // profondeur de l encoche sous la faitiere (m)
    const yFaitierePoincon = Ht + hf + dPerp0 / cosA0 - (pfB0 / 2) * tanA0 + delardement - pfH0 / 2;
    const ySousFaitiere = yFaitierePoincon - pfH0 / 2;
    const yTetePoincon = ySousFaitiere + EMBREVEMENT_FAITIERE;
""")

rempl("2. encoche de calage, pas de fourche",
"      addPoinconEncoche(x, poB, poH, Ht, yTetePoincon, pfB0, pfH0);\n",
"      addPoinconEncoche(x, poB, poH, Ht, yTetePoincon, pfB0, EMBREVEMENT_FAITIERE);\n")

rempl("3. tenon des arbaletriers",
"      const z0 = poHa / 2;                            // joue du poincon : la ou l arbaletrier s arrete\n",
"      const z0 = Math.max(0.02, poHa / 2 - 0.03);     // l arbaletrier entre de 3 cm dans le poincon (tenon)\n")

io.open(chemin, "w", encoding="utf-8").write(s)
for t, n, a in etapes:
    print("  " + t + " : " + str(n) + "/" + str(a))
print("OK poincon porteur")
