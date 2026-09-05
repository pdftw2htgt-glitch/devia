# pages_ciblees.py — LECTURE CIBLEE
# Apres l inventaire, DEVIA fabrique un dossier reduit ne contenant QUE les pages
# utiles au charpentier (masse, toitures, coupes, facades, etages, cartouche,
# notice) et ne montre plus que celles-la aux passes suivantes. Moins de bruit,
# lecture plus stable, et moins de tokens payes a chaque devis.
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A0 = r'''import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";'''
R0 = r'''import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { PDFDocument } from "pdf-lib";'''

A1 = r'''      console.log("[DEVIA] Passe 1 (inventaire) : " + inv.slice(0, 250));'''
R1 = r'''      console.log("[DEVIA] Passe 1 (inventaire) : " + inv.slice(0, 250));

      // ===== DOSSIER REDUIT : on ne garde que les pages utiles au charpentier =====
      let blocksUtiles = blocks;
      try {
        const TYPES_UTILES = ["plan_de_masse", "plan_de_toitures", "coupe", "facade", "plan_etage", "cartouche", "notice"];
        const unSeulPdf = fileList.length === 1 && fileList[0].type === "application/pdf";
        const numsUtiles = pagesInv.filter(p => TYPES_UTILES.indexOf(p.type) >= 0).map(p => parseInt(p.page, 10)).filter(x => isNaN(x) === false);
        if (unSeulPdf && numsUtiles.length > 0) {
          const docSrc = await PDFDocument.load(bufs[0]);
          const total = docSrc.getPageCount();
          const idx = [];
          numsUtiles.forEach((n) => { const i = n - 1; if (i >= 0 && i < total && idx.indexOf(i) < 0) idx.push(i); });
          idx.sort((a, b) => a - b);
          if (idx.length > 0 && idx.length < total) {
            const docOut = await PDFDocument.create();
            const pages = await docOut.copyPages(docSrc, idx);
            pages.forEach((pg) => docOut.addPage(pg));
            const octets = await docOut.save();
            let bin = "";
            const CH = 8192;
            for (let k = 0; k < octets.length; k += CH) { bin += String.fromCharCode.apply(null, octets.subarray(k, k + CH)); }
            const b64Utiles = btoa(bin);
            blocksUtiles = [{ type: "document", source: { type: "base64", media_type: "application/pdf", data: b64Utiles } }];
            console.log("[DEVIA] Dossier reduit : " + idx.length + " page(s) utile(s) sur " + total + " (pages " + idx.map(i => i + 1).join(", ") + ")");
          } else {
            console.log("[DEVIA] Dossier reduit : toutes les pages sont utiles, dossier complet conserve");
          }
        }
      } catch (eRed) { console.warn("[DEVIA] Dossier reduit impossible, dossier complet conserve", eRed); blocksUtiles = blocks; }'''

A2 = r'''[...blocks, { type: "text", text: "Etablis l orientation du batiment et le cardinal de chaque facade." }],'''
R2 = r'''[...blocksUtiles, { type: "text", text: "Etablis l orientation du batiment et le cardinal de chaque facade." }],'''

A3 = r'''[...blocks, { type: "text", text: "Lis la geometrie des volumes." }],'''
R3 = r'''[...blocksUtiles, { type: "text", text: "Lis la geometrie des volumes." }],'''

A4 = r'''[...blocks, { type: "text", text: "Lis les hauteurs et les infos generales." }],'''
R4 = r'''[...blocksUtiles, { type: "text", text: "Lis les hauteurs et les infos generales." }],'''

A5 = r'''[...blocks, { type: "text", text: "Confronte ce montage aux facades du dossier." }],'''
R5 = r'''[...blocksUtiles, { type: "text", text: "Confronte ce montage aux facades du dossier." }],'''

paires = [
    ("import pdf-lib", A0, R0),
    ("dossier reduit", A1, R1),
    ("passe 1B ciblee", A2, R2),
    ("passe 2A ciblee", A3, R3),
    ("passe 2B ciblee", A4, R4),
    ("passe 4 ciblee", A5, R5),
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
print("6 modifications ecrites. Backup : " + F + ".bak_" + tag)
