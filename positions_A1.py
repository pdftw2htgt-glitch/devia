# Phase 2A-1 : positions structurees (contre / cote / decalage / faitage)
# extraites du plan et transportees jusqu'a la 3D. AUCUN changement visuel.
import shutil, datetime, sys

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"

with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''"couverture":"meme_liste_que_couverture_ou_null","desc":"role et position du volume en une phrase"}]}. ' +'''
NEW1 = '''"couverture":"meme_liste_que_couverture_ou_null","contre":num_ou_null,"cote":"pignon_gauche|pignon_droit|gouttereau_avant|gouttereau_arriere|null","decalage_m":num_ou_null,"faitage":"parallele|perpendiculaire|null","desc":"role et position du volume en une phrase"}]}. ' +'''

OLD2 = '''Recopie pour CHAQUE volume sa pente et sa couverture telles que donnees par le plan (elles peuvent differer d'un volume a l'autre). '''
NEW2 = '''Recopie pour CHAQUE volume sa pente et sa couverture telles que donnees par le plan (elles peuvent differer d'un volume a l'autre). POSITIONS (tres important) : pour chaque volume secondaire, renseigne son accolement : contre = numero du volume de reference dans le tableau (1 = volume principal), cote = ou il se colle vu du volume de reference (pignon_gauche et pignon_droit = les petits cotes, gouttereau_avant et gouttereau_arriere = les longs cotes), decalage_m = glissement en metres du centre du volume le long de ce mur par rapport au centre du mur (0 = centre), faitage = sens de son faitage par rapport a celui du volume de reference. Lis ces informations sur le plan de masse ou le plan de toitures. Le volume principal a contre, cote, decalage_m et faitage a null. Si deux volumes sont relies par une liaison (sas), chaine les accolements : la liaison contre le volume principal, le volume suivant contre la liaison. '''

OLD3 = '''          return {
            type: o.type,
            longueur: o.longueur, largeur: o.largeur,
            hauteur: o.hauteur_murs || undefined,
            pente: (pDeg && sansToit === false) ? pDeg : undefined,
            couverture: (sansToit === false && o.couverture) || undefined,
            desc: p2.join(", "),
          };'''
NEW3 = '''          return {
            type: o.type,
            longueur: o.longueur, largeur: o.largeur,
            hauteur: o.hauteur_murs || undefined,
            pente: (pDeg && sansToit === false) ? pDeg : undefined,
            couverture: (sansToit === false && o.couverture) || undefined,
            pos: (o.contre && o.cote) ? { contre: o.contre, cote: o.cote, decalage: (typeof o.decalage_m === "number" ? o.decalage_m : 0), faitage: o.faitage || "parallele" } : undefined,
            desc: p2.join(", "),
          };'''

OLD4 = '''        console.log("[DEVIA] Decomposition plan : " + structs.length + " ouvrages detectes");'''
NEW4 = '''        console.log("[DEVIA] Decomposition plan : " + structs.length + " ouvrages detectes");
        console.log("[DEVIA] Positions extraites : " + structs.map((s, k) => "V" + (k + 1) + (s.pos ? " contre V" + s.pos.contre + " cote " + s.pos.cote + " decalage " + s.pos.decalage + "m faitage " + s.pos.faitage : " libre")).join(" | "));'''

OLD5 = '''      const ouvrages3D = structures.map((s, i) => ({
        longueur: s.longueur, largeur: s.largeur, hauteur: s.hauteur, pente: s.pente,
        couverture: s.couverture, essence: s.essence, murs: s.murs,
        type_projet: (devisParOuvrage[i] && devisParOuvrage[i].projet && devisParOuvrage[i].projet.type_projet) || TYPE_TO_PROJET[s.type] || "charpente_trad",
      }));'''
NEW5 = '''      const ouvrages3D = structures.map((s, i) => ({
        longueur: s.longueur, largeur: s.largeur, hauteur: s.hauteur, pente: s.pente,
        couverture: s.couverture, essence: s.essence, murs: s.murs,
        pos: s.pos || undefined,
        type_projet: (devisParOuvrage[i] && devisParOuvrage[i].projet && devisParOuvrage[i].projet.type_projet) || TYPE_TO_PROJET[s.type] || "charpente_trad",
      }));'''

anchors = [("schema ouvrages", OLD1, NEW1), ("regle positions", OLD2, NEW2), ("struct pos", OLD3, NEW3), ("log positions", OLD4, NEW4), ("ouvrages3D pos", OLD5, NEW5)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)

shutil.copy2(F, F + ".backup_" + stamp + "_positions_A1")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK 2A-1 : positions extraites et transportees jusqu'a la 3D (visuel inchange)")
