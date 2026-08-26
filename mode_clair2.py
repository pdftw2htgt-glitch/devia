import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

REMPL = []

for fx in ["formCouverture", "formEssence", "formCombles", "formMurs", "formSolaire"]:
    a1 = 'background: ' + fx + ' === opt.val ? "rgba(240,192,64,0.09)" : "rgba(255,255,255,0.02)", border: ' + fx + ' === opt.val ? "1px solid rgba(240,192,64,0.5)" : "1px solid rgba(255,255,255,0.06)"'
    b1 = 'background: ' + fx + ' === opt.val ? (themeMode === "light" ? "rgba(184,134,11,0.12)" : "rgba(240,192,64,0.09)") : (themeMode === "light" ? "rgba(0,0,0,0.03)" : "rgba(255,255,255,0.02)"), border: ' + fx + ' === opt.val ? (themeMode === "light" ? "1px solid rgba(156,112,0,0.55)" : "1px solid rgba(240,192,64,0.5)") : (themeMode === "light" ? "1px solid rgba(0,0,0,0.10)" : "1px solid rgba(255,255,255,0.06)")'
    REMPL.append((a1, b1, 1))
    a2 = 'color: ' + fx + ' === opt.val ? "#f0c040" : "#d0d2dc",'
    b2 = 'color: ' + fx + ' === opt.val ? (themeMode === "light" ? "#9c7000" : "#f0c040") : (themeMode === "light" ? "#3a3e50" : "#d0d2dc"),'
    REMPL.append((a2, b2, 1))

for fx in ["formCouverture", "formEssence", "formCombles"]:
    a3 = fx + ' === opt.val ? "#f0c040" : "#9ca0b8")'
    b3 = fx + ' === opt.val ? (themeMode === "light" ? "#9c7000" : "#f0c040") : (themeMode === "light" ? "#5a5e72" : "#9ca0b8"))'
    REMPL.append((a3, b3, 1))

REMPL.append(('display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 10',
              'display: "block", color: themeMode === "light" ? "#474b5c" : "#9ca0b8", fontSize: 11, marginBottom: 10', 8))
REMPL.append(('color: ouvrageActif === opt.idx ? "#f0c040" : "#9ca0b8",',
              'color: ouvrageActif === opt.idx ? (themeMode === "light" ? "#9c7000" : "#f0c040") : (themeMode === "light" ? "#5a5e72" : "#9ca0b8"),', 1))
REMPL.append(('color: selectedGroupe === "all" ? "#f0c040" : "#9ca0b8",',
              'color: selectedGroupe === "all" ? (themeMode === "light" ? "#9c7000" : "#f0c040") : (themeMode === "light" ? "#5a5e72" : "#9ca0b8"),', 1))
REMPL.append(('color: isActive ? "#f0c040" : "#9ca0b8",',
              'color: isActive ? (themeMode === "light" ? "#9c7000" : "#f0c040") : (themeMode === "light" ? "#5a5e72" : "#9ca0b8"),', 1))
REMPL.append(('color: !p.groupe_id ? "#f0c040" : "#9ca0b8", textAlign: "left",',
              'color: !p.groupe_id ? (themeMode === "light" ? "#9c7000" : "#f0c040") : (themeMode === "light" ? "#5a5e72" : "#9ca0b8"), textAlign: "left",', 1))

ok = True
for a, b, attendu in REMPL:
    n = txt.count(a)
    if n != attendu:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu", attendu, ":", a[:70])
        ok = False
if ok == False:
    raise SystemExit(1)

for a, b, attendu in REMPL:
    txt = txt.replace(a, b)

shutil.copy(CHEMIN, CHEMIN + ".backup_mode_clair2_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : formulaire lisible en mode clair (boutons, icones, etiquettes, selecteurs)")
