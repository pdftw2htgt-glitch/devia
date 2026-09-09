# appuis_plancher.py — ETAPE 1b : le plancher porte sur des MURS ou sur des POTEAUX,
# au choix dans le formulaire. Sur murs (cas du sous-sol maconne) : aucun poteau
# bois au devis, les solives portent sur les murailleres et les sabots.
# Le champ traverse les 7 points de passage des parametres 3D.
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

# --- 1. Etat du formulaire ---
A1 = r'''const [formMurs, setFormMurs] = useState(""); // "" = beton existant (defaut) / "ossature_bois"'''
R1 = r'''const [formMurs, setFormMurs] = useState(""); // "" = beton existant (defaut) / "ossature_bois"
const [formAppuis, setFormAppuis] = useState("poteaux"); // plancher : "poteaux" (autoporte) / "murs" (sur murs porteurs)'''

# --- 2. Moteur : poteaux seulement si appuis = poteaux ---
A2 = r'''    // ===== POTEAUX (2 files laterales sous les murailleres, entraxe max 3m) =====
    setPiece("Poteau");
    const ENTRAXE_MAX_POTEAUX = 3.0;
    const nbPotX = Math.max(2, Math.ceil(L / ENTRAXE_MAX_POTEAUX) + 1);
    for (const zf of [-zMur, zMur]) {
      for (let i = 0; i < nbPotX; i++) {
        const x = -L/2 + potB/2 + (i / (nbPotX - 1)) * (L - potB);
        addBox(potB, hPot, potB, x, hPot / 2, zf);
      }
    }'''
R2 = r'''    // ===== POTEAUX (2 files laterales sous les murailleres, entraxe max 3m) =====
    // Uniquement si le plancher est autoporte : sur murs porteurs (sous-sol maconne),
    // les solives reposent sur les murailleres et leurs sabots, sans poteau bois.
    const appuisEtage = ((params && params.appuis) === "murs") ? "murs" : "poteaux";
    if (appuisEtage === "poteaux") {
      setPiece("Poteau");
      const ENTRAXE_MAX_POTEAUX = 3.0;
      const nbPotX = Math.max(2, Math.ceil(L / ENTRAXE_MAX_POTEAUX) + 1);
      for (const zf of [-zMur, zMur]) {
        for (let i = 0; i < nbPotX; i++) {
          const x = -L/2 + potB/2 + (i / (nbPotX - 1)) * (L - potB);
          addBox(potB, hPot, potB, x, hPot / 2, zf);
        }
      }
    } else {
      console.log("[DEVIA] Plancher sur murs porteurs : aucun poteau bois chiffre");
    }'''

# --- 3. UI : selecteur d appuis, visible pour un plancher ---
A3 = r'''<div style={{ color: "#545870", fontSize: 11, marginTop: 4, textAlign: "center" }}>{typeEffectif === "terrasse" ? "Hauteur du platelage (m)" : typeEffectif === "etage" ? "Hauteur sous plancher (m)" : typeEffectif === "balcon" ? "Hauteur du plancher (m)" : "Hauteur mur (m)"}</div>'''
R3 = r'''<div style={{ color: "#545870", fontSize: 11, marginTop: 4, textAlign: "center" }}>{typeEffectif === "terrasse" ? "Hauteur du platelage (m)" : typeEffectif === "etage" ? "Hauteur sous plancher (m)" : typeEffectif === "balcon" ? "Hauteur du plancher (m)" : "Hauteur mur (m)"}</div>
                {typeEffectif === "etage" ? (
                  <div style={{ marginTop: 10 }}>
                    <label style={{ display: "block", color: cl("#9ca0b8", "#565a6c"), fontSize: 11, marginBottom: 6, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Le plancher porte sur</label>
                    <select value={formAppuis} onChange={e => setFormAppuis(e.target.value)} style={{ width: "100%", padding: "9px 12px", borderRadius: 8, background: cl("#181a26", "#ffffff"), border: cl("1px solid rgba(255,255,255,0.10)", "1px solid rgba(0,0,0,0.14)"), color: cl("#e8eaf2", "#1a1d2a"), fontSize: 13, cursor: "pointer" }}>
                      <option value="poteaux">des poteaux bois (plancher autoporte, mezzanine)</option>
                      <option value="murs">les murs porteurs (sous-sol, murs existants) - sans poteaux</option>
                    </select>
                  </div>
                ) : null}'''

# --- 4 a 9. Les points de passage du parametre ---
A4 = r'''      type: formType || undefined,
      murs: formMurs || undefined,'''
R4 = r'''      type: formType || undefined,
      murs: formMurs || undefined,
      appuis: formAppuis || undefined,'''

A5 = r'''                        type: formSousType,
                        murs: formMurs || undefined,'''
R5 = r'''                        type: formSousType,
                        murs: formMurs || undefined,
                        appuis: formAppuis || undefined,'''

A6 = r'''        murs: finalParams.murs || undefined,'''
R6 = r'''        murs: finalParams.murs || undefined,
        appuis: finalParams.appuis || undefined,'''

A7 = r'''finition: s.finition || undefined, murs: s.murs, debord: s.debord || undefined,'''
R7 = r'''finition: s.finition || undefined, murs: s.murs, appuis: s.appuis || undefined, debord: s.debord || undefined,'''

A8 = r'''  if (finalParams.murs) parsed._murs = finalParams.murs;'''
R8 = r'''  if (finalParams.murs) parsed._murs = finalParams.murs;
  if (finalParams.appuis) parsed._appuis = finalParams.appuis;'''

A9 = r'''        murs: project.devis_data._murs || undefined,'''
R9 = r'''        murs: project.devis_data._murs || undefined,
        appuis: project.devis_data._appuis || undefined,'''

A10 = r'''      murs: p.murs,'''
R10 = r'''      murs: p.murs,
      appuis: p.appuis,'''

A11 = r'''      murs: (src && src.murs) || (parsed && parsed._murs) || undefined,'''
R11 = r'''      murs: (src && src.murs) || (parsed && parsed._murs) || undefined,
      appuis: (src && src.appuis) || (parsed && parsed._appuis) || undefined,'''

paires = [
    ("etat formAppuis", A1, R1),
    ("moteur : poteaux conditionnels", A2, R2),
    ("UI selecteur appuis", A3, R3),
    ("params formulaire", A4, R4),
    ("structure multi-ouvrages", A5, R5),
    ("view3DParams", A6, R6),
    ("ouvrages3D", A7, R7),
    ("persistance devis", A8, R8),
    ("rechargement projet", A9, R9),
    ("metre moteur", A10, R10),
    ("harmonisation", A11, R11),
]

erreurs = 0
for nom, ancre, rempl in paires:
    n = src.count(ancre)
    if n == 1:
        print("OK ancre : " + nom)
    else:
        erreurs = erreurs + 1
        print("ANCRE '" + nom + "' : " + str(n) + " occurrence(s) au lieu de 1")

if erreurs > 0:
    print("ABANDON — aucune modification ecrite.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
for nom, ancre, rempl in paires:
    src = src.replace(ancre, rempl)
open(F, "w", encoding="utf-8").write(src)
print("11 modifications ecrites. Backup : " + F + ".bak_" + tag)
