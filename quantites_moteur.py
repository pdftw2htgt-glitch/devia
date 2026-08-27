import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

FN_RECALAGE = '''// ================================================================
// RECALAGE DES QUANTITES : les postes bois du devis prennent les
// quantites EXACTES du metre moteur 3D (l'IA ne fait plus que
// l'habillage et les prix). Devis, PDF et 3D disent la meme chose.
// ================================================================
const MAP_TYPE_DEVIA = { traditionnelle: "charpente_trad", fermette: "charpente_trad", monopente: "monopente", carport: "carport", hangar: "hangar", appentis: "appentis", "4_pans": "4_pans", terrasse: "terrasse", etage: "etage", balcon: "balcon", garde_corps: "garde_corps", sas: "sas_liaison" };

function recalerQuantitesDevis(parsed, agg) {
  try {
    if (parsed === null || parsed === undefined) return 0;
    if (agg === null || agg === undefined) return 0;
    const groupes = agg.groupes || [];
    if (groupes.length === 0) return 0;
    const parNom = {};
    groupes.forEach((g) => {
      if (parNom[g.nom] === undefined) parNom[g.nom] = { nombre: 0, longueurTotale: 0, volume: 0 };
      parNom[g.nom].nombre += g.nombre;
      parNom[g.nom].longueurTotale += g.longueurTotale;
      parNom[g.nom].volume += g.volume;
    });
    const stripQ = (s) => (s || "").toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g, "");
    const MAPQ = [
      ["panne faitiere", ["Panne faitiere"]], ["faitiere", ["Panne faitiere"]],
      ["poutre porteuse", ["Poutre porteuse"]], ["porteuse", ["Porteuse", "Poutre porteuse"]],
      ["sabliere", ["Sabliere"]], ["muraillere", ["Muraillere"]],
      ["arbaletrier", ["Arbaletrier"]], ["entrait", ["Entrait"]],
      ["contrefiche", ["Contrefiche"]], ["poincon", ["Poincon"]],
      ["lien de faitage", ["Lien de faitage"]], ["echantignole", ["Echantignole"]],
      ["empannon", ["Empannon", "Empannon de croupe"]], ["chevron", ["Chevron"]],
      ["aretier", ["Aretier"]], ["panne", ["Panne"]],
      ["solive", ["Solive", "Solive balcon"]], ["poteau", ["Poteau"]],
    ];
    let nbRecales = 0;
    (parsed.postes || []).forEach((po) => {
      const cat = stripQ(po.categorie);
      if (cat.includes("pose") || cat.includes("etude") || cat.includes("quincaillerie")) return;
      const d = stripQ(po.designation);
      for (const paire of MAPQ) {
        if (d.includes(paire[0]) === false) continue;
        let g = null;
        for (const cand of paire[1]) {
          if (parNom[cand] !== undefined) { g = parNom[cand]; break; }
        }
        if (g === null) break;
        const u = stripQ(po.unite);
        let q = 0;
        if (u.includes("m3") || u.includes("cube")) q = Math.round(g.volume * 1000) / 1000;
        else if (u.includes("ml") || u.includes("metre") || u === "m") q = Math.round(g.longueurTotale * 10) / 10;
        else q = g.nombre;
        if (q > 0) {
          const pu = Number(po.prixUnitaireHT) || 0;
          po.quantite = q;
          po.totalHT = Math.round(q * pu * 100) / 100;
          nbRecales += 1;
        }
        break;
      }
    });
    if (nbRecales > 0) {
      const ht = (parsed.postes || []).reduce((s, po) => s + (Number(po.totalHT) || 0), 0);
      const ancienHT = (parsed.totaux && Number(parsed.totaux.totalHT)) || 0;
      const ancienneTVA = (parsed.totaux && Number(parsed.totaux.tva)) || 0;
      const taux = ancienHT > 0 ? (ancienneTVA / ancienHT) : 0.2;
      const tva = Math.round(ht * taux * 100) / 100;
      parsed.totaux = { totalHT: Math.round(ht * 100) / 100, tva: tva, totalTTC: Math.round((ht + tva) * 100) / 100 };
      console.log("[DEVIA] Quantites recalees sur le metre moteur : " + nbRecales + " poste(s)");
    }
    return nbRecales;
  } catch (eRec) {
    console.warn("[DEVIA] Recalage quantites:", eRec);
    return 0;
  }
}

function harmoniserSectionsDevis(parsed, sk, dS, src) {'''

REMPL = [
    # --- Etape 1a : le metre injecte recoit les memes charges que la 3D
    ('''      debord: p.debord || 0,
      murs: p.murs,
    };''',
     '''      debord: p.debord || 0,
      murs: p.murs,
      sk: (p.sk === undefined || p.sk === null) ? undefined : Number(p.sk),
      dS: (p.dS === undefined || p.dS === null) ? undefined : Number(p.dS),
      solaire: p.solaire,
      altitude: p.altitude,
    };'''),
    # --- Etape 2 : fonction de recalage + nouvelle signature
    ('function harmoniserSectionsDevis(parsed, sk, dS) {', FN_RECALAGE),
    # --- Etape 1b : l'harmonisation construit avec les memes charges/options
    ('''      dS: dS || 0,
      solaire: Boolean(parsed && parsed._solaire),
    };''',
     '''      dS: dS || 0,
      solaire: Boolean(parsed && parsed._solaire),
      sk: sk || 0.45,
      murs: (src && src.murs) || (parsed && parsed._murs) || undefined,
      debord: (src && src.debord !== undefined && src.debord !== null) ? src.debord : ((parsed && parsed._debord) || 0),
      altitude: (src && src.altitude) || undefined,
    };'''),
    # --- Etape 2 : declenchement du recalage
    ('''    const agg = agregerMetre(pre.metre, pre.densiteBois || 450);
    const secs = calculerSectionsCharpente(agg, paramsCalc, sk);''',
     '''    const agg = agregerMetre(pre.metre, pre.densiteBois || 450);
    recalerQuantitesDevis(parsed, agg);
    const secs = calculerSectionsCharpente(agg, paramsCalc, sk);'''),
    # --- Points d'appel : metre injecte (solo puis multi)
    ('  const texteMetre = metreTexteDepuisParams(finalParams);',
     '  const texteMetre = metreTexteDepuisParams({ ...finalParams, sk: zoneInfo ? zoneInfo.sk : undefined, dS: zoneInfo ? zoneInfo.dS : undefined, altitude: altitude });'),
    ('          const texteMetreO = metreTexteDepuisParams(fp);',
     '          const ziO = getZone(commune, altitude);\n          const texteMetreO = metreTexteDepuisParams({ ...fp, sk: ziO ? ziO.sk : undefined, dS: ziO ? ziO.dS : undefined, altitude: altitude });'),
    # --- Points d'appel : harmonisation recoit les params source
    ('harmoniserSectionsDevis(parsed, ziH ? ziH.sk : 0.45, ziH ? ziH.dS : 0);',
     'harmoniserSectionsDevis(parsed, ziH ? ziH.sk : 0.45, ziH ? ziH.dS : 0, fp);'),
    ('harmoniserSectionsDevis(parsed, zoneInfo ? zoneInfo.sk : 0.45, zoneInfo ? zoneInfo.dS : 0);',
     'harmoniserSectionsDevis(parsed, zoneInfo ? zoneInfo.sk : 0.45, zoneInfo ? zoneInfo.dS : 0, finalParams);'),
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

shutil.copy(CHEMIN, CHEMIN + ".backup_quantites_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : charges alignees + quantites des postes bois recalees sur le metre moteur")
