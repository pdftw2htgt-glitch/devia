import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

REMPL = [
    # --- Toggle Neuf / Renovation : suit le theme ---
    ('''              marginBottom: 20,
              padding: "14px 18px",
              background: "rgba(255, 255, 255, 0.02)",
              border: "1px solid rgba(255, 255, 255, 0.05)",''',
     '''              marginBottom: 20,
              padding: "14px 18px",
              background: themeMode === "light" ? "rgba(0, 0, 0, 0.03)" : "rgba(255, 255, 255, 0.02)",
              border: themeMode === "light" ? "1px solid rgba(0, 0, 0, 0.08)" : "1px solid rgba(255, 255, 255, 0.05)",'''),
    ('''                <div style={{ color: "#9ca0b8", fontSize: 11, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>
                  Type de travaux''',
     '''                <div style={{ color: themeMode === "light" ? "#474b5c" : "#9ca0b8", fontSize: 11, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>
                  Type de travaux'''),
    ('''                <div style={{ color: "#e8eaf2", fontSize: 13, fontWeight: 500 }}>
                  {typeTravaux === "neuf" ? "Construction neuve" : "Rénovation"}''',
     '''                <div style={{ color: themeMode === "light" ? "#1a1d2a" : "#e8eaf2", fontSize: 13, fontWeight: 500 }}>
                  {typeTravaux === "neuf" ? "Construction neuve" : "Rénovation"}'''),
    ('''                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 999,''',
     '''                background: themeMode === "light" ? "rgba(0,0,0,0.05)" : "rgba(255,255,255,0.03)",
                border: themeMode === "light" ? "1px solid rgba(0,0,0,0.08)" : "1px solid rgba(255,255,255,0.06)",
                borderRadius: 999,'''),
    ('background: typeTravaux === t.id ? "rgba(255,255,255,0.08)" : "transparent",',
     'background: typeTravaux === t.id ? (themeMode === "light" ? "#1a1d2a" : "rgba(255,255,255,0.08)") : "transparent",'),
    ('color: typeTravaux === t.id ? "#ffffff" : "#7a7d92",',
     'color: typeTravaux === t.id ? "#ffffff" : (themeMode === "light" ? "#474b5c" : "#7a7d92"),'),
    ('onMouseEnter={(e) => { if (typeTravaux !== t.id) e.currentTarget.style.color = "#d0d2dc"; }}',
     'onMouseEnter={(e) => { if (typeTravaux !== t.id) e.currentTarget.style.color = themeMode === "light" ? "#1a1d2a" : "#d0d2dc"; }}'),
    ('onMouseLeave={(e) => { if (typeTravaux !== t.id) e.currentTarget.style.color = "#7a7d92"; }}',
     'onMouseLeave={(e) => { if (typeTravaux !== t.id) e.currentTarget.style.color = themeMode === "light" ? "#474b5c" : "#7a7d92"; }}'),
    ('background: typeTravaux === t.id ? t.color : "#3a3d4f",',
     'background: typeTravaux === t.id ? t.color : (themeMode === "light" ? "#c8cbd8" : "#3a3d4f"),'),
    # --- Theme clair : gris assombris partout ou les tokens sont utilises ---
    ('textSecondary: "#5a5e72",', 'textSecondary: "#474b5c",'),
    ('textMuted: "#8a8d9c",', 'textMuted: "#6a6e80",'),
    ('textFaint: "#a8abb8",', 'textFaint: "#8f93a3",'),
    ('navTabText: "#5a5e72",', 'navTabText: "#474b5c",'),
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

shutil.copy(CHEMIN, CHEMIN + ".backup_mode_clair_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : toggle Neuf/Renovation lisible en clair, gris du theme clair assombris")
