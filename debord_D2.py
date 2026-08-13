import shutil, time

f = "devia.jsx"
shutil.copy(f, f + ".backup_debord_D2_" + time.strftime("%Y%m%d_%H%M%S"))
c = open(f).read()
erreurs = []

def remplacer(ancre, nouveau, nom):
    global c
    n = c.count(ancre)
    if n != 1:
        erreurs.append(nom + " : ancre trouvee " + str(n) + " fois (attendu 1)")
        return
    c = c.replace(ancre, nouveau)

# ===== S1 : champ debord_toiture_cm dans le schema JSON des ouvrages =====
remplacer("""\"decalage_m\":num_ou_null,\"faitage\":\"parallele|perpendiculaire|null\",\"src\":""",
"""\"decalage_m\":num_ou_null,\"faitage\":\"parallele|perpendiculaire|null\",\"debord_toiture_cm\":num_ou_null,\"src\":""", "S1")

# ===== S2 : regle de lecture du depasse + garde-fou contour toiture =====
remplacer("""        "REGLE COTES (tres important) : recopie les cotes ECRITES sur le plan (plan de masse, plan de toitures, coupes) - ne mesure jamais a l'oeil, n'estime jamais, n'arrondis jamais. Cherche la cote ecrite la plus proche de chaque volume avant de conclure. Si une dimension n'est vraiment pas cotee, mets null plutot que d'inventer. Deux analyses du meme plan doivent donner exactement les memes chiffres. " +""",
"""        "REGLE COTES (tres important) : recopie les cotes ECRITES sur le plan (plan de masse, plan de toitures, coupes) - ne mesure jamais a l'oeil, n'estime jamais, n'arrondis jamais. Cherche la cote ecrite la plus proche de chaque volume avant de conclure. Si une dimension n'est vraiment pas cotee, mets null plutot que d'inventer. Deux analyses du meme plan doivent donner exactement les memes chiffres. " +
        "REGLE DEPASSE DE TOITURE (tres important) : cherche pour CHAQUE volume son depasse de toiture (debord du toit au-dela des murs), note sur le plan de toitures ou les coupes, et recopie-le en CENTIMETRES dans debord_toiture_cm (une cote 0.80 m donne 80, une cote 120 donne 120). Mets null si non lisible, n'invente jamais. GARDE-FOU CONTOUR : sur un plan de toitures le contour dessine INCLUT les depasses (contour = murs plus 2 fois le depasse) ; les cotes d'emprise des murs (longueur, largeur) viennent des plans d'etage ou du plan de masse - ne recopie jamais une cote de contour de toiture comme cote de murs. " +""", "S2")

# ===== S3 : la passe geometrie lit le depasse par volume =====
remplacer("""Cite la page d'ou vient chaque chiffre. Reponds en texte structure, un paragraphe par volume. INVENTAIRE DES VUES : " + inv,""",
"""Donne aussi pour CHAQUE volume son DEPASSE DE TOITURE (debord du toit au-dela des murs) tel qu'ecrit sur le plan de toitures ou les coupes, avec son unite. ATTENTION : le contour dessine du plan de toitures inclut les depasses (contour = murs plus 2 fois le depasse) - les cotes d'emprise des murs viennent des plans d'etage ou du plan de masse, ne confonds jamais les deux. Cite la page d'ou vient chaque chiffre. Reponds en texte structure, un paragraphe par volume. INVENTAIRE DES VUES : " + inv,""", "S3")

# ===== S4 : bump version du cache (obligatoire, prompt modifie) =====
remplacer("""const versionPrompt = vh.toString(36) + "-p3v7";""",
"""const versionPrompt = vh.toString(36) + "-p3v8";""", "S4")

# ===== S5 : debord_toiture_cm -> structs (en metres) =====
remplacer("""            couverture: (sansToit === false && o.couverture) || undefined,""",
"""            couverture: (sansToit === false && o.couverture) || undefined,
            debord: (typeof o.debord_toiture_cm === "number" && o.debord_toiture_cm > 0) ? Math.round(o.debord_toiture_cm) / 100 : undefined,""", "S5")

# ===== S6 : depasse affiche dans la ligne jaune =====
remplacer("""(s.hauteur ? " h" + s.hauteur + "m" : " h?")""",
"""(s.hauteur ? " h" + s.hauteur + "m" : " h?") + (s.debord ? " depasse " + Math.round(s.debord * 100) + "cm" : "")""", "S6")

# ===== S7 : champ depasse (cm) dans l'editeur du pop-up =====
remplacer("""      <input value={v.hauteur === undefined ? "" : v.hauteur} onChange={e => majVolume(i, "hauteur", e.target.value)} style={{ ...miniInp, width: 46 }} />""",
"""      <input value={v.hauteur === undefined ? "" : v.hauteur} onChange={e => majVolume(i, "hauteur", e.target.value)} style={{ ...miniInp, width: 46 }} />
      <span>dep.</span>
      <input value={v.debord === undefined || v.debord === "" ? "" : Math.round((parseFloat(v.debord) || 0) * 100)} onChange={e => majVolume(i, "debord", e.target.value === "" ? "" : String((parseFloat(e.target.value) || 0) / 100))} style={{ ...miniInp, width: 44 }} />
      <span>cm</span>""", "S7")

# ===== S8 : le depasse survit a "Verifier et enregistrer" =====
remplacer("""        pente: v.pente, couverture: v.couverture, essence: v.essence,
        faitageCardinal: v.faitageCardinal || undefined,""",
"""        pente: v.pente, couverture: v.couverture, essence: v.essence,
        debord: (v.debord === undefined || v.debord === "") ? undefined : (num(v.debord, 0) || undefined),
        faitageCardinal: v.faitageCardinal || undefined,""", "S8")

# ===== S9 : le depasse entre dans le cache de reference (corrections) =====
remplacer("""faitage_cardinal: s.faitageCardinal || null, desc: s.desc }))""",
"""faitage_cardinal: s.faitageCardinal || null, debord_toiture_cm: s.debord ? Math.round(s.debord * 100) : null, desc: s.desc }))""", "S9")

# ===== S10 : le depasse dans le devis de chaque ouvrage (multi) =====
remplacer("""          combles: s.combles, longueur: s.longueur, largeur: s.largeur, hauteur: s.hauteur,
          pente: s.pente, description: s.desc,
        };""",
"""          combles: s.combles, longueur: s.longueur, largeur: s.largeur, hauteur: s.hauteur,
          pente: s.pente, debord: s.debord, description: s.desc,
        };""", "S10")

if erreurs:
    print("ERREUR, rien ecrit :")
    for e in erreurs: print(" -", e)
    raise SystemExit(1)

open(f, "w").write(c)
print("OK : depasse de toiture dans toute la chaine d analyse (lecture, cache v8, ligne jaune, editeur, corrections, devis).")
