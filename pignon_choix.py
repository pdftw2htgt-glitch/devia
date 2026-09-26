import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

def remp(nom, ancre, nouveau):
    global src
    n = src.count(ancre)
    if n != 1:
        print("ABANDON " + nom + " : ancre trouvee " + str(n) + " fois")
        cle = ancre.strip().split("\n")[0][:45]
        for i, l in enumerate(src.split("\n")):
            if cle in l:
                print("  ligne " + str(i + 1) + " : " + l.strip()[:200])
        sys.exit(1)
    src = src.replace(ancre, nouveau)
    print("OK " + nom)

# --- 1) Etat du formulaire ---
remp("etat formPignon",
'''const [formMurs, setFormMurs] = useState(""); // "" = beton existant (defaut) / "ossature_bois"''',
'''const [formMurs, setFormMurs] = useState(""); // "" = beton existant (defaut) / "ossature_bois"
const [formPignon, setFormPignon] = useState("plein"); // plein | egout | aucun''')

# --- 2) MOTEUR : le pignon obeit au reglage ---
remp("moteur pignon",
"""    sansFace === "pignon_droit" ? null : murZ(Lb/2, true);
    sansFace === "pignon_gauche" ? null : murZ(-Lb/2, false);

    // --- TRIANGLES DE PIGNON : la maconnerie monte jusqu aux rampants ---
    const htTriangle = (lgb / 2) * Math.tan((pente * Math.PI) / 180);
    if (htTriangle > 0.05) {
      if ((sansFace === "pignon_droit") === false) drawPignonBeton(Lb / 2, lgb, Hb, htTriangle, ep);
      if ((sansFace === "pignon_gauche") === false) drawPignonBeton(-Lb / 2, lgb, Hb, htTriangle, ep);
      console.log("[DEVIA] Pignons fermes : triangle de " + htTriangle.toFixed(2) + " m de haut");
    }""",
"""    // --- MUR DE PIGNON : plein (jusque sous les pannes) / egout (arrete a la sabliere) / aucun ---
    const modePignon = (params && params.pignon) || "plein";
    if (modePignon === "aucun") {
      console.log("[DEVIA] Pignons : aucun mur, la ferme reste apparente");
    } else {
      sansFace === "pignon_droit" ? null : murZ(Lb/2, true);
      sansFace === "pignon_gauche" ? null : murZ(-Lb/2, false);
      const htTriangle = (lgb / 2) * Math.tan((pente * Math.PI) / 180);
      if (modePignon === "plein" && htTriangle > 0.05) {
        if ((sansFace === "pignon_droit") === false) drawPignonBeton(Lb / 2, lgb, Hb, htTriangle, ep);
        if ((sansFace === "pignon_gauche") === false) drawPignonBeton(-Lb / 2, lgb, Hb, htTriangle, ep);
        console.log("[DEVIA] Pignons maconnes jusqu aux rampants (triangle " + htTriangle.toFixed(2) + " m)");
      } else {
        console.log("[DEVIA] Pignons arretes a la sabliere (triangle ouvert)");
      }
    }""")

# --- 3 a 9) LES SEPT POINTS DE PASSAGE ---
remp("metre",
"""      murs: p.murs,
      appuis: p.appuis,""",
"""      murs: p.murs,
      pignon: p.pignon,
      appuis: p.appuis,""")

remp("harmonisation",
"""      murs: (src && src.murs) || (parsed && parsed._murs) || undefined,""",
"""      murs: (src && src.murs) || (parsed && parsed._murs) || undefined,
      pignon: (src && src.pignon) || (parsed && parsed._pignon) || undefined,""")

remp("ouvrages3D",
"""murs: s.murs, appuis: s.appuis || undefined,""",
"""murs: s.murs, pignon: s.pignon || undefined, appuis: s.appuis || undefined,""")

remp("persistance",
"""  if (finalParams.appuis) parsed._appuis = finalParams.appuis;""",
"""  if (finalParams.pignon) parsed._pignon = finalParams.pignon;
  if (finalParams.appuis) parsed._appuis = finalParams.appuis;""")

remp("view3DParams",
"""        murs: finalParams.murs || undefined,""",
"""        murs: finalParams.murs || undefined,
        pignon: finalParams.pignon || undefined,""")

remp("rechargement",
"""        murs: project.devis_data._murs || undefined,""",
"""        murs: project.devis_data._murs || undefined,
        pignon: project.devis_data._pignon || undefined,""")

remp("params formulaire",
"""      murs: formMurs || undefined,
      appuis: formAppuis || undefined,""",
"""      murs: formMurs || undefined,
      pignon: formPignon || undefined,
      appuis: formAppuis || undefined,""")

remp("structure multi",
"""                        murs: formMurs || undefined,
                        appuis: formAppuis || undefined,""",
"""                        murs: formMurs || undefined,
                        pignon: formPignon || undefined,
                        appuis: formAppuis || undefined,""")

# --- 10) Le choix dans le formulaire ---
remp("bloc UI pignon",
"""              {/* Panneaux solaires */}""",
"""              {/* Mur de pignon */}
              <div style={{ marginBottom: 18, display: ["traditionnelle","fermette","4_pans"].includes(typeEffectif) ? undefined : "none" }}>
                <label style={{ display: "block", color: themeMode === "light" ? "#474b5c" : cl("#9ca0b8", "#565a6c"), fontSize: 11, marginBottom: 10, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Mur de pignon</label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
                  {[
                    { val: "plein", label: "Maconne jusque sous les pannes" },
                    { val: "egout", label: "Maconne jusqu a la sabliere" },
                    { val: "aucun", label: "Sans mur : ferme apparente" }
                  ].map(opt => (
                    <button key={opt.val} type="button" onClick={() => setFormPignon(opt.val)}
                      style={{ background: formPignon === opt.val ? (themeMode === "light" ? "rgba(184,134,11,0.12)" : "rgba(240,192,64,0.09)") : (themeMode === "light" ? "rgba(0,0,0,0.03)" : "rgba(255,255,255,0.02)"), border: formPignon === opt.val ? (themeMode === "light" ? "1px solid rgba(156,112,0,0.55)" : "1px solid rgba(240,192,64,0.5)") : (themeMode === "light" ? "1px solid rgba(0,0,0,0.10)" : cl("1px solid rgba(255,255,255,0.06)", "1px solid rgba(0,0,0,0.09)")), borderRadius: 10, padding: "11px 10px", cursor: "pointer", color: formPignon === opt.val ? (themeMode === "light" ? "#9c7000" : "#f0c040") : (themeMode === "light" ? "#3a3e50" : cl("#d0d2dc", "#3a3e50")), textAlign: "left", fontSize: 12, fontWeight: 500, transition: "all 0.15s" }}>
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
              {/* Panneaux solaires */}""")

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
