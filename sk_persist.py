import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

REMPL = [
    # 1. Sauvegarde solo : persiste les charges de la generation
    ("if (finalParams.finition) parsed._finition = finalParams.finition;",
     "if (finalParams.finition) parsed._finition = finalParams.finition;\n  if (zoneInfo) { parsed._sk = zoneInfo.sk; parsed._dS = zoneInfo.dS; }"),
    # 2. Vue 3D solo a la generation : transmet aussi sk/dS
    ("finition: finalParams.finition || undefined\n      });",
     "finition: finalParams.finition || undefined,\n        sk: zoneInfo ? zoneInfo.sk : undefined,\n        dS: zoneInfo ? zoneInfo.dS : undefined\n      });"),
    # 3. Sauvegarde multi : persiste les charges
    ("fusion._ouvrages3D = ouvrages3D; // persiste dans devis_data (rechargement 3D multi)",
     "fusion._ouvrages3D = ouvrages3D; // persiste dans devis_data (rechargement 3D multi)\n      if (zoneInfo) { fusion._sk = zoneInfo.sk; fusion._dS = zoneInfo.dS; }"),
    # 4. Vue 3D multi a la generation : transmet aussi sk/dS
    ("ouvrages: ouvrages3D,\n      });",
     "ouvrages: ouvrages3D,\n        sk: zoneInfo ? zoneInfo.sk : undefined,\n        dS: zoneInfo ? zoneInfo.dS : undefined,\n      });"),
    # 5. Rechargement d'un projet : restitue les charges sauvegardees
    ("ouvrages: project.devis_data._ouvrages3D || undefined,",
     "ouvrages: project.devis_data._ouvrages3D || undefined,\n        sk: project.devis_data._sk,\n        dS: project.devis_data._dS,"),
    # 6. Le viewer prefere les charges du projet a celles de la commune en cours
    ("sk: zoneInfo ? zoneInfo.sk : 0.45, dS: zoneInfo ? zoneInfo.dS : 0 }}",
     "sk: (view3DParams.sk === undefined) ? (zoneInfo ? zoneInfo.sk : 0.45) : view3DParams.sk, dS: (view3DParams.dS === undefined) ? (zoneInfo ? zoneInfo.dS : 0) : view3DParams.dS }}"),
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

shutil.copy(CHEMIN, CHEMIN + ".backup_sk_persist_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : charges neige/vent persistees et restituees au rechargement")
