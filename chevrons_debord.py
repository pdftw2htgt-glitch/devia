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

# 1. le defaut passe a 60 cm : une queue de panne vaut exactement un entraxe de chevron
rempl("1. defaut a 60 cm",
"""  const debordPanne = Math.max(0, (params.debord_panne === undefined || params.debord_panne === null || params.debord_panne === "")
    ? 50 : (parseFloat(params.debord_panne) || 0)) / 100;
""",
"""  const debordPanne = Math.max(0, (params.debord_panne === undefined || params.debord_panne === null || params.debord_panne === "")
    ? 60 : (parseFloat(params.debord_panne) || 0)) / 100;
""")

rempl("2. etat du formulaire a 60",
'const [formDebordPanne, setFormDebordPanne] = useState("50"); // queue de panne au pignon, en cm\n',
'const [formDebordPanne, setFormDebordPanne] = useState("60"); // queue de panne au pignon, en cm\n')

rempl("3. placeholder a 60",
'<input value={formDebordPanne} onChange={e => setFormDebordPanne(e.target.value)} type="number" placeholder="50" style={{ ...inputStyle, maxWidth: 100 }} />',
'<input value={formDebordPanne} onChange={e => setFormDebordPanne(e.target.value)} type="number" placeholder="60" style={{ ...inputStyle, maxWidth: 100 }} />')

# 4. les chevrons continuent sur les queues de panne, au meme entraxe
rempl("4. chevrons sur le debord",
"""    // Chevrons de rive : au bord du depasse de pignon (portes par les queues de panne)
    if (debG > 0.05) chevronXs.push(-(L/2 + debG - chB/2));
    if (debD > 0.05) chevronXs.push(L/2 + debD - chB/2);
""",
"""    // Les queues de panne se calepinent comme le reste du toit : on remplit le debord au
    // MEME entraxe, et le dernier chevron - le chevron de rive - vient au nu du bout de panne.
    // Un debord de 60 cm vaut donc exactement une travee de chevron, d ou le defaut.
    const chevronsDebord = (signe, dp) => {
      if (dp <= 0.05) return;
      const xBout = L/2 + dp - chB/2;                              // axe du chevron de rive
      const zone = xBout - L/2;
      const nb = Math.max(1, Math.ceil(zone / ENTRAXE_CHEVRON_MAX));
      for (let k = 1; k <= nb; k++) chevronXs.push(signe * (L/2 + (k / nb) * zone));
    };
    chevronsDebord(1, dpD);
    chevronsDebord(-1, dpG);
""")

# 5. la couverture suit les pannes
rempl("5. couverture etendue aux queues de panne",
"    const panW = L + rivG + rivD + debLX;\n",
"    const panW = L + dpLX;                        // la couverture couvre les queues de panne\n")

rempl("6. recentrage de la couverture",
"    const cXpan = debCX + (rivD - rivG) / 2;\n",
"    const cXpan = dpCX;\n")

io.open(chemin, "w", encoding="utf-8").write(s)
for t, n, a in etapes:
    print("  " + t + " : " + str(n) + "/" + str(a))
print("OK chevrons et couverture etendus")
