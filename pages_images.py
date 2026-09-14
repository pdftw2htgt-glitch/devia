# pages_images.py — LES PAGES SONT RENDUES EN IMAGES, PLUS RIEN NE PART AU STOCKAGE
# 1) inventaire : toutes les pages en definition legere (reconnaitre une vue suffit)
# 2) chaque passe de lecture recoit SES pages en haute definition (2400 px, qualite 85)
#    - orientation : masse, toitures, facades
#    - geometrie   : toitures, masse, etages
#    - hauteurs    : coupes, notice, cartouche, facades
#    - confrontation : facades
# Repli sur le dossier complet si le rendu echoue ou si l inventaire ne classe rien.
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''import { PDFDocument } from "pdf-lib";'''
R1 = r'''import { PDFDocument } from "pdf-lib";
import * as pdfjsLib from "pdfjs-dist";
import pdfWorkerUrl from "pdfjs-dist/build/pdf.worker.min.mjs?url";
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerUrl;'''

A2 = r'''  const buildFileBlocks = async (fileList) => {'''
R2 = r'''  // Rend des pages du PDF en images JPEG (base64) pretes pour l analyse.
  // nums vide = toutes les pages. largeurMax en pixels sur le grand cote.
  const rendrePagesImages = async (buf, nums, largeurMax, qualite) => {
    const doc = await pdfjsLib.getDocument({ data: buf.slice(0) }).promise;
    const total = doc.numPages;
    let liste = (Array.isArray(nums) && nums.length > 0) ? nums.slice() : [];
    if (liste.length === 0) { for (let i = 1; i <= total; i++) { liste.push(i); } }
    liste = liste.filter(n => n >= 1 && n <= total).slice(0, 20);
    const out = [];
    for (const n of liste) {
      const page = await doc.getPage(n);
      const v1 = page.getViewport({ scale: 1 });
      const grand = Math.max(v1.width, v1.height);
      const sc = Math.min(4, Math.max(0.5, largeurMax / grand));
      const vp = page.getViewport({ scale: sc });
      const cv = document.createElement("canvas");
      cv.width = Math.round(vp.width);
      cv.height = Math.round(vp.height);
      const ctx = cv.getContext("2d");
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, cv.width, cv.height);
      await page.render({ canvasContext: ctx, viewport: vp }).promise;
      const durl = cv.toDataURL("image/jpeg", qualite);
      out.push({ type: "image", source: { type: "base64", media_type: "image/jpeg", data: durl.slice(durl.indexOf(",") + 1) } });
      cv.width = 0; cv.height = 0;
    }
    try { await doc.destroy(); } catch (eD) {}
    return out;
  };
  const buildFileBlocks = async (fileList) => {'''

A3 = r'''      // Televersement UNIQUEMENT ici : le dossier n est ni en cache ni verrouille
      blocks = await buildFileBlocks(fileList);
      if (blocks.length === 0) { setAnalyseFichier(""); return; }'''
R3 = r'''      // Les pages sont rendues en images ICI : aucun fichier ne part au stockage.
      const unPdf = fileList.length === 1 && fileList[0].type === "application/pdf";
      if (unPdf) {
        try {
          blocks = await rendrePagesImages(bufs[0], null, 1300, 0.55);
          console.log("[DEVIA] Dossier rendu en " + blocks.length + " image(s) legere(s) pour l inventaire");
        } catch (eImg) { console.warn("[DEVIA] Rendu des pages impossible, envoi du fichier", eImg); blocks = []; }
      }
      if (blocks.length === 0) { blocks = await buildFileBlocks(fileList); }
      if (blocks.length === 0) { setAnalyseFichier(""); return; }'''

A4 = r'''      // ===== DOSSIER REDUIT : on ne garde que les pages utiles au charpentier =====
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
            if (octets.length > SEUIL_FICHIER_LOURD) {
              const fReduit = new File([octets], "dossier_reduit.pdf", { type: "application/pdf" });
              const urlReduit = await uploadFichierLourd(fReduit);
              blocksUtiles = [{ type: "document", source: { type: "url", url: urlReduit } }];
              console.log("[DEVIA] Dossier reduit envoye par lien signe (" + Math.round(octets.length / 1048576 * 10) / 10 + " Mo)");
            } else {
              let bin = "";
              const CH = 8192;
              for (let k = 0; k < octets.length; k += CH) { bin += String.fromCharCode.apply(null, octets.subarray(k, k + CH)); }
              blocksUtiles = [{ type: "document", source: { type: "base64", media_type: "application/pdf", data: btoa(bin) } }];
            }
            console.log("[DEVIA] Dossier reduit : " + idx.length + " page(s) utile(s) sur " + total + " (pages " + idx.map(i => i + 1).join(", ") + ")");
          } else {
            console.log("[DEVIA] Dossier reduit : toutes les pages sont utiles, dossier complet conserve");
          }
        }
      } catch (eRed) { console.warn("[DEVIA] Dossier reduit impossible, dossier complet conserve", eRed); blocksUtiles = blocks; }'''

R4 = r'''      // ===== PAGES EN HAUTE DEFINITION : chaque passe recoit SES pages =====
      const blocsPour = async (types) => {
        try {
          const unPdf2 = fileList.length === 1 && fileList[0].type === "application/pdf";
          if (unPdf2 === false) return blocks;
          const nums = pagesInv.filter(p => types.indexOf(p.type) >= 0).map(p => parseInt(p.page, 10)).filter(x => isNaN(x) === false);
          if (nums.length === 0) { console.log("[DEVIA] Aucune page identifiee pour " + types.join(", ") + " : dossier complet conserve"); return blocks; }
          const imgs = await rendrePagesImages(bufs[0], nums, 2400, 0.85);
          if (imgs.length === 0) return blocks;
          console.log("[DEVIA] " + imgs.length + " page(s) en haute definition pour " + types.join(", ") + " (pages " + nums.join(", ") + ")");
          return imgs;
        } catch (eB) { console.warn("[DEVIA] Haute definition impossible, pages legeres conservees", eB); return blocks; }
      };
      const blocsOrientation = await blocsPour(["plan_de_masse", "plan_de_toitures", "facade"]);
      const blocsGeo = await blocsPour(["plan_de_toitures", "plan_de_masse", "plan_etage"]);
      const blocsHauteurs = await blocsPour(["coupe", "notice", "cartouche", "facade"]);
      const blocsFacades = await blocsPour(["facade"]);'''

A5 = r'''[...blocksUtiles, { type: "text", text: "Etablis l orientation du batiment et le cardinal de chaque facade." }],'''
R5 = r'''[...blocsOrientation, { type: "text", text: "Etablis l orientation du batiment et le cardinal de chaque facade." }],'''

A6 = r'''[...blocksUtiles, { type: "text", text: "Lis la geometrie des volumes." }],'''
R6 = r'''[...blocsGeo, { type: "text", text: "Lis la geometrie des volumes." }],'''

A7 = r'''[...blocksUtiles, { type: "text", text: "Lis les hauteurs et les infos generales." }],'''
R7 = r'''[...blocsHauteurs, { type: "text", text: "Lis les hauteurs et les infos generales." }],'''

A8 = r'''[...blocksUtiles, { type: "text", text: "Confronte ce montage aux facades du dossier." }],'''
R8 = r'''[...blocsFacades, { type: "text", text: "Confronte ce montage aux facades du dossier." }],'''

paires = [
    ("import pdf.js", A1, R1),
    ("fonction de rendu", A2, R2),
    ("inventaire en images legeres", A3, R3),
    ("pages haute definition par passe", A4, R4),
    ("passe orientation", A5, R5),
    ("passe geometrie", A6, R6),
    ("passe hauteurs", A7, R7),
    ("passe confrontation", A8, R8),
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
print("8 modifications ecrites. Backup : " + F + ".bak_" + tag)
