# Chantier lecture croisee : protocole d'extraction par vues + ligne jaune complete
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''        "REGLE COTES (tres important) : recopie les cotes ECRITES sur le plan (plan de masse, plan de toitures, coupes) - ne mesure jamais a l'oeil, n'estime jamais, n'arrondis jamais. Cherche la cote ecrite la plus proche de chaque volume avant de conclure. Si une dimension n'est vraiment pas cotee, mets null plutot que d'inventer. Deux analyses du meme plan doivent donner exactement les memes chiffres. " +'''
NEW1 = '''        "REGLE COTES (tres important) : recopie les cotes ECRITES sur le plan (plan de masse, plan de toitures, coupes) - ne mesure jamais a l'oeil, n'estime jamais, n'arrondis jamais. Cherche la cote ecrite la plus proche de chaque volume avant de conclure. Si une dimension n'est vraiment pas cotee, mets null plutot que d'inventer. Deux analyses du meme plan doivent donner exactement les memes chiffres. " +
        "PROTOCOLE DE LECTURE CROISEE (tres important, dans l'ordre) : " +
        "1. Inventorie les vues du dossier : plan de masse, plan de toitures, coupes, facades, plans d'etage. " +
        "2. Identifie chaque volume sur le plan de toitures : un faitage dessine = un volume ; note le SENS de chaque faitage (parallele ou perpendiculaire a celui du volume principal) d'apres les lignes de faite. " +
        "3. Pour CHAQUE volume : longueur et largeur = cotes ecrites du plan de toitures ou de masse ; hauteur_murs = la coupe qui traverse CE volume (un corps a etage est plus haut qu'un corps en rez-de-chaussee) ; decalage_m = mesure sur les cotes du plan de masse (0 uniquement si les volumes sont reellement centres l'un sur l'autre). " +
        "4. Renseigne pour chaque volume le champ src : d'ou viennent ses chiffres. " +
        "5. COHERENCE avant de repondre : les emprises des volumes additionnees doivent redonner l'emprise totale ; les hauteurs doivent correspondre aux coupes ; tes accolements reconstitues mentalement doivent reproduire le plan de masse. Corrige avant de repondre. " +'''

OLD2 = '''"faitage":"parallele|perpendiculaire|null","desc":"role et position du volume en une phrase"'''
NEW2 = '''"faitage":"parallele|perpendiculaire|null","src":"vues sources des chiffres (ex plan toitures + coupe A)","desc":"role et position du volume en une phrase"'''

OLD3 = '''        setAnalyseResume(structs.map((s, k) => "V" + (k + 1) + " " + (LT_DECOMP[s.type] || s.type) + " " + s.longueur + "x" + s.largeur + "m" + (s.pos ? " - contre V" + s.pos.contre + ", " + String(s.pos.cote).replace("_", " ") + (s.pos.decalage ? ", decalage " + s.pos.decalage + "m" : "") : "")).join(" | "));'''
NEW3 = '''        setAnalyseResume(structs.map((s, k) => "V" + (k + 1) + " " + (LT_DECOMP[s.type] || s.type) + " " + s.longueur + "x" + s.largeur + "m" + (s.hauteur ? " h" + s.hauteur + "m" : " h?") + (s.pos ? " - contre V" + s.pos.contre + ", " + String(s.pos.cote).replace("_", " ") + ", faitage " + (s.pos.faitage || "?") + ", decalage " + (s.pos.decalage || 0) + "m" : "")).join(" | "));'''

anchors = [("protocole lecture", OLD1, NEW1), ("schema src", OLD2, NEW2), ("ligne jaune complete", OLD3, NEW3)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie (si 0 : script peut-etre deja passe)")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_lecture_croisee")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : protocole de lecture croisee + ligne jaune complete")
