import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

ANCRE = "</button>\\n                  <Viewer3D params={{ ...view3DParams,"
ANCRE = ANCRE.replace("\\n", "\n")

BARRE = '''</button>
                  {is3DFullscreen && (
                    <div style={{ position: "absolute", top: 12, left: 12, zIndex: 10, display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                      {[{ id: "technique", label: "Vue technique" }, { id: "realiste", label: "Vue realiste" }].map(m => (
                        <button key={"fsv-" + m.id} onClick={() => setMode3D(m.id)}
                          style={{ padding: "7px 14px", borderRadius: 8, cursor: "pointer", fontSize: 13, fontWeight: mode3D === m.id ? 600 : 500,
                            border: "1px solid " + (mode3D === m.id ? "rgba(240,192,64,0.5)" : "rgba(255,255,255,0.14)"),
                            background: mode3D === m.id ? "rgba(240,192,64,0.16)" : "rgba(10,12,18,0.55)", backdropFilter: "blur(8px)",
                            color: mode3D === m.id ? "#f0c040" : "#c8cad4" }}>
                          {m.label}
                        </button>
                      ))}
                      <select value={fond3D} onChange={e => setFond3D(e.target.value)}
                        style={{ padding: "7px 12px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                          border: "1px solid rgba(255,255,255,0.14)", background: "rgba(10,12,18,0.75)", color: "#d0d2dc" }}>
                        <option value="noir">Fond noir</option>
                        <option value="blanc">Fond blanc</option>
                        <option value="soleil">Ensoleille</option>
                        <option value="pluie">Pluie</option>
                        <option value="nuit">Nuit</option>
                      </select>
                      {[{ id: "mini", label: "Section mini" }, { id: "conseillee", label: "Section conseillee" }].map(m => (
                        <button key={"fss-" + m.id} onClick={() => setSectionMode(m.id)}
                          style={{ padding: "7px 14px", borderRadius: 8, cursor: "pointer", fontSize: 13, fontWeight: sectionMode === m.id ? 600 : 500,
                            border: "1px solid " + (sectionMode === m.id ? "rgba(240,192,64,0.5)" : "rgba(255,255,255,0.14)"),
                            background: sectionMode === m.id ? "rgba(240,192,64,0.16)" : "rgba(10,12,18,0.55)", backdropFilter: "blur(8px)",
                            color: sectionMode === m.id ? "#f0c040" : "#c8cad4" }}>
                          {m.label}
                        </button>
                      ))}
                    </div>
                  )}
                  <Viewer3D params={{ ...view3DParams,'''

n = txt.count(ANCRE)
if n != 1:
    print("ABANDON : ancre en", n, "exemplaire(s), attendu 1")
    raise SystemExit(1)

txt = txt.replace(ANCRE, BARRE)

shutil.copy(CHEMIN, CHEMIN + ".backup_fs_controles_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : controles vue / fond / sections disponibles en plein ecran")
