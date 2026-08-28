# alerte_decomp.py — analyse non conforme : alerte visible + correction manuelle
# 1) message vert remplace par un avertissement quand la decomposition a un probleme
# 2) bouton "Generer" devient rouge "Generer quand meme"
# 3) grosse alerte rouge avec bouton "Corriger la decomposition"
# 4) l editeur de decomposition s ouvre tout seul quand le verificateur dit NON CONFORME
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''Plan analyse, champs pre-remplis. {!commune.trim() ? "Renseigne la commune puis genere." : "Tout est pret."}'''
R1 = r'''{analyseVerdict && analyseVerdict.ok === false ? "Plan analyse, mais la decomposition a un probleme : corrige-la plus bas avant de generer." : (commune.trim() ? "Plan analyse, champs pre-remplis. Tout est pret." : "Plan analyse, champs pre-remplis. Renseigne la commune puis genere.")}'''

A2 = r'''color: (loading || !formType || !formLongueur || !commune.trim()) ? "#545870" : "#f0c040",'''
R2 = r'''color: (loading || !formType || !formLongueur || !commune.trim()) ? "#545870" : (analyseVerdict && analyseVerdict.ok === false ? "#e05252" : "#f0c040"),'''

A3 = r'''Generer le devis depuis ce plan'''
R3 = r'''{analyseVerdict && analyseVerdict.ok === false ? "Generer quand meme (analyse non conforme)" : "Generer le devis depuis ce plan"}'''

A4 = r'''<div style={{ marginTop: 6, color: "#e05252", fontSize: 11, lineHeight: 1.5, fontWeight: 600 }}>ANALYSE NON CONFORME - {analyseVerdict.erreurs.join(" | ")}</div>'''
R4 = r'''<div style={{ marginTop: 8, padding: "8px 10px", borderRadius: 8, background: "rgba(224,82,82,0.08)", border: "1px solid rgba(224,82,82,0.45)" }}>
                        <div style={{ color: "#e05252", fontSize: 11.5, lineHeight: 1.5, fontWeight: 700 }}>ANALYSE NON CONFORME - {analyseVerdict.erreurs.join(" | ")}</div>
                        <div style={{ marginTop: 4, color: cl("#b8bccc", "#565a6c"), fontSize: 11, lineHeight: 1.5 }}>Le 3D risque de sortir faux : corrige la decomposition avant de generer le devis.</div>
                        <button type="button" onClick={() => { setEditeurOuvert(true); setVolumeSel(0); }} style={{ marginTop: 6, padding: "6px 14px", borderRadius: 8, cursor: "pointer", background: "rgba(224,82,82,0.12)", border: "1px solid rgba(224,82,82,0.5)", color: "#e05252", fontSize: 11.5, fontWeight: 700, display: "block" }}>Corriger la decomposition</button>
                      </div>'''

A5 = r'''else console.warn("[DEVIA] Verificateur : NON CONFORME -", verdictDecomp.erreurs.join(" | "));'''
R5 = r'''else { console.warn("[DEVIA] Verificateur : NON CONFORME -", verdictDecomp.erreurs.join(" | ")); setEditeurOuvert(true); setVolumeSel(0); }'''

paires = [
    ("message vert conditionnel", A1, R1),
    ("couleur bouton generer", A2, R2),
    ("libelle bouton generer", A3, R3),
    ("alerte rouge + bouton corriger", A4, R4),
    ("ouverture auto editeur", A5, R5),
]

erreurs = 0
for nom, ancre, rempl in paires:
    n = src.count(ancre)
    if n == 1:
        print("OK ancre : " + nom)
    else:
        erreurs = erreurs + 1
        print("ANCRE '" + nom + "' : " + str(n) + " occurrence(s) au lieu de 1")
        frag = ancre.strip().split("\n")[0][:50]
        i = src.find(frag)
        if i >= 0:
            print("--- zone reelle ---")
            print(src[max(0, i - 150):i + 400])

if erreurs > 0:
    print("ABANDON — aucune modification ecrite.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
for nom, ancre, rempl in paires:
    src = src.replace(ancre, rempl)
open(F, "w", encoding="utf-8").write(src)
print("5 modifications ecrites. Backup : " + F + ".bak_" + tag)
