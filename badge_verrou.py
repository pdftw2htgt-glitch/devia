# badge_verrou.py — temoin visuel du verrou : tu vois a l ecran si le dossier
# est verrouille par tes corrections (donc identique a chaque relance)
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''const analyseJRef = useRef(null); // dernier JSON d'analyse (pour sauvegarder les corrections)'''
R1 = r'''const analyseJRef = useRef(null); // dernier JSON d'analyse (pour sauvegarder les corrections)
const [verrouActif, setVerrouActif] = useState(false); // dossier fige par les corrections utilisateur'''

A2 = r'''          console.log("[DEVIA] Corrections utilisateur servies (dossier verrouille par tes corrections)");'''
R2 = r'''          console.log("[DEVIA] Corrections utilisateur servies (dossier verrouille par tes corrections)");
          setVerrouActif(true);'''

A3 = r'''          if (ligneCache && ligneCache.resultat) jCache = ligneCache.resultat;'''
R3 = r'''          if (ligneCache && ligneCache.resultat) jCache = ligneCache.resultat;
          setVerrouActif(false);'''

A4 = r'''        console.log("[DEVIA] Corrections enregistrees ET verrouillees (elles survivront aux re-analyses et mises a jour)");'''
R4 = r'''        console.log("[DEVIA] Corrections enregistrees ET verrouillees (elles survivront aux re-analyses et mises a jour)");
        setVerrouActif(true);'''

A5 = r'''                    Decomposition du plan : {analyseResume}'''
R5 = r'''                    Decomposition du plan : {analyseResume}
                    {verrouActif ? (
                      <div style={{ marginTop: 6, padding: "5px 9px", borderRadius: 7, background: "rgba(126,201,126,0.10)", border: "1px solid rgba(126,201,126,0.45)", color: "#7ec97e", fontSize: 11, fontWeight: 700 }}>DOSSIER VERROUILLE - tes corrections sont figees, ce plan ressortira identique a chaque relance</div>
                    ) : (
                      <div style={{ marginTop: 6, color: cl("#9ca0b8", "#565a6c"), fontSize: 10.5, lineHeight: 1.5 }}>Non verrouille : ouvre la decomposition manuelle, verifie les valeurs et clique "Verifier et enregistrer" pour figer ce dossier definitivement.</div>
                    )}'''

paires = [
    ("etat verrou", A1, R1),
    ("verrou actif a la lecture", A2, R2),
    ("verrou inactif sur cache simple", A3, R3),
    ("verrou actif a l enregistrement", A4, R4),
    ("badge encadre", A5, R5),
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
print("5 modifications ecrites. Backup : " + F + ".bak_" + tag)
