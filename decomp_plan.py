# Phase 1 decomposition de plans : une emprise complexe (L, T, maison+garage...)
# est decomposee par l'IA en ouvrages du catalogue -> mode multi-ouvrages pre-rempli.
# Un plan rectangulaire simple garde exactement le comportement actuel.
import shutil, datetime, sys

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"

with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''        '"nom_projet":"nom_court_du_projet_ou_null","notes":"resume 1 phrase de ce que montre le plan"}. ' +'''
NEW1 = '''        '"nom_projet":"nom_court_du_projet_ou_null","notes":"resume 1 phrase de ce que montre le plan",' +
        '"ouvrages":null_ou_[{"type":"meme_liste_que_le_champ_type","longueur":num,"largeur":num,"hauteur_murs":num_ou_null,"pente_valeur":num_ou_null,"pente_unite":"degres|pourcent|null","couverture":"meme_liste_que_couverture_ou_null","desc":"role et position du volume en une phrase"}]}. ' +'''

OLD2 = '''        "Mets null quand l'info n'est pas lisible sur le document. Les dimensions en metres.";'''
NEW2 = '''        "REGLE DECOMPOSITION (tres important) : si l'emprise du batiment n'est PAS un simple rectangle (plusieurs volumes accoles, plan en L ou en T, maison plus garage, corps principal plus extension ou liaison), remplis EN PLUS le champ ouvrages : un element par volume rectangulaire simple, chacun avec son type choisi dans la meme liste que le champ type, ses dimensions lues sur le plan, et une desc d'une phrase donnant son role et sa position par rapport au premier volume (ex : garage accole au pignon ouest du corps principal). Le PREMIER element du tableau = le volume principal (le plus grand ou le plus haut). Ne cree un element que pour les volumes qui portent une charpente ou une structure bois a chiffrer : ignore les terrasses dallees et les piscines. Si le batiment est un simple rectangle, mets ouvrages a null et remplis seulement les champs simples. " +
        "Mets null quand l'info n'est pas lisible sur le document. Les dimensions en metres.";'''

OLD3 = '''      const j = JSON.parse(m[0]);
      if (j.type) setFormType(j.type);'''
NEW3 = '''      const j = JSON.parse(m[0]);
      // DECOMPOSITION : plan complexe -> liste d'ouvrages -> mode multi pre-rempli
      const TYPES_DECOMP = ["traditionnelle", "fermette", "monopente", "carport", "hangar", "appentis", "4_pans", "terrasse", "etage", "balcon", "garde_corps"];
      const LT_DECOMP = { fermette: "fermette industrielle", traditionnelle: "charpente traditionnelle", monopente: "monopente", carport: "carport abri voiture", terrasse: "terrasse bois exterieure", etage: "plancher d'etage sur solivage bois", balcon: "balcon bois en porte-a-faux", garde_corps: "garde-corps bois (rambarde)", hangar: "hangar agricole", appentis: "appentis accole a un mur", "4_pans": "toit 4 pans avec croupe" };
      const decomp = Array.isArray(j.ouvrages)
        ? j.ouvrages.filter(o => o && TYPES_DECOMP.includes(o.type) && o.longueur > 0 && o.largeur > 0)
        : [];
      if (decomp.length >= 2) {
        const structs = decomp.map(o => {
          const pDeg = o.pente_valeur
            ? (o.pente_unite === "pourcent" ? Math.round(Math.atan(o.pente_valeur / 100) * 180 / Math.PI * 10) / 10 : o.pente_valeur)
            : undefined;
          const sansToit = ["terrasse", "etage", "balcon", "garde_corps"].includes(o.type);
          const p2 = [LT_DECOMP[o.type] || o.type, o.longueur + "x" + o.largeur + "m"];
          if (o.hauteur_murs) p2.push("hauteur " + o.hauteur_murs + "m");
          if (pDeg && sansToit === false) p2.push("pente " + pDeg + " degres");
          if (o.desc) p2.push(String(o.desc));
          return {
            type: o.type,
            longueur: o.longueur, largeur: o.largeur,
            hauteur: o.hauteur_murs || undefined,
            pente: (pDeg && sansToit === false) ? pDeg : undefined,
            couverture: (sansToit === false && o.couverture) || undefined,
            desc: p2.join(", "),
          };
        });
        console.log("[DEVIA] Decomposition plan : " + structs.length + " ouvrages detectes");
        setFormType("custom");
        setFormStructures(structs);
        // Neutralise les champs mono-ouvrage : le code existant ci-dessous s'ignore alors tout seul
        j.type = null; j.longueur = null; j.largeur = null;
        j.hauteur_murs = null; j.hauteur_faitage = null;
        j.pente_valeur = null; j.pente = null; j.combles = null; j.murs = null;
      }
      if (j.type) setFormType(j.type);'''

anchors = [("schema JSON analyse", OLD1, NEW1), ("consignes analyse", OLD2, NEW2), ("branche apres parse", OLD3, NEW3)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)

shutil.copy2(F, F + ".backup_" + stamp + "_decomp_plan")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : decomposition de plans (phase 1) en place - plan simple inchange")
