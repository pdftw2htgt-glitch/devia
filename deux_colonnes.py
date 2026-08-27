import shutil, time

CHEMIN = "devia.jsx"

with open(CHEMIN, encoding="utf-8") as f:
    txt = f.read()

TD_PIECES = '<td style={{ padding: "12px 16px", color: cl("#9ca0b8", "#565a6c"), fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{(p.nbPieces === undefined || p.nbPieces === null) ? "-" : p.nbPieces}</td>\n                                    '

REMPL = [
    # --- 1. Le recalage memorise le nombre de pieces et les ml du moteur
    ('''        if (g === null) break;
        const u = stripQ(po.unite);''',
     '''        if (g === null) break;
        po.nbPieces = g.nombre;
        po.mlTotal = Math.round(g.longueurTotale * 10) / 10;
        const u = stripQ(po.unite);'''),
    # --- 2. App : colonne "Pieces" dans les 2 tableaux (solo + multi)
    ('{ label: "Qte", align: "right" },',
     '{ label: "Pieces", align: "right" },\n                                    { label: "Qte", align: "right" },', 2),
    ('<td style={{ padding: "12px 16px", color: cl("#d0d2dc", "#3a3e50"), fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{p.quantite}</td>',
     TD_PIECES + '<td style={{ padding: "12px 16px", color: cl("#d0d2dc", "#3a3e50"), fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{p.quantite}</td>', 2),
    # --- 3. PDF : 5 colonnes (les colSpan grandissent d'un cran)
    ('colSpan: 4,', 'colSpan: 5,', 2),
    ('colSpan: 3,', 'colSpan: 4,', 2),
    ('head: [["Designation", "Qte", "Unite", "Montant HT"]],',
     'head: [["Designation", "Pieces", "Qte", "Unite", "Montant HT"]],'),
    ('''    (p.designation || "").replace(/^Ouvrage \\d+ - /, ""),
    p.quantite ? String(p.quantite) : "-",''',
     '''    (p.designation || "").replace(/^Ouvrage \\d+ - /, ""),
    (p.nbPieces === undefined || p.nbPieces === null) ? "-" : String(p.nbPieces),
    p.quantite ? String(p.quantite) : "-",'''),
    ('''      0: { cellWidth: 96 },
      1: { cellWidth: 18, halign: "right" },
      2: { cellWidth: 22, halign: "center" },
      3: { cellWidth: 44, halign: "right", fontStyle: "bold" }''',
     '''      0: { cellWidth: 84 },
      1: { cellWidth: 16, halign: "right" },
      2: { cellWidth: 18, halign: "right" },
      3: { cellWidth: 20, halign: "center" },
      4: { cellWidth: 42, halign: "right", fontStyle: "bold" }'''),
]

ok = True
for r in REMPL:
    a = r[0]
    attendu = r[2] if len(r) > 2 else 1
    n = txt.count(a)
    if n != attendu:
        print("ABANDON : ancre en", n, "exemplaire(s), attendu", attendu, ":", a[:70].replace(chr(10), " / "))
        ok = False
if ok == False:
    raise SystemExit(1)

for r in REMPL:
    txt = txt.replace(r[0], r[1])

shutil.copy(CHEMIN, CHEMIN + ".backup_deux_colonnes_" + time.strftime("%Y%m%d_%H%M%S"))
with open(CHEMIN, "w", encoding="utf-8") as f:
    f.write(txt)
print("OK : colonne Pieces ajoutee dans l'app et dans le PDF")
