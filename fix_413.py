# fix_413.py — le dossier reduit passe par lien signe s il depasse 3 Mo
# (comme le fichier d origine), au lieu d etre envoye en direct au serveur
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''            const octets = await docOut.save();
            let bin = "";
            const CH = 8192;
            for (let k = 0; k < octets.length; k += CH) { bin += String.fromCharCode.apply(null, octets.subarray(k, k + CH)); }
            const b64Utiles = btoa(bin);
            blocksUtiles = [{ type: "document", source: { type: "base64", media_type: "application/pdf", data: b64Utiles } }];'''
R1 = r'''            const octets = await docOut.save();
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
            }'''

n = src.count(A1)
if n == 1:
    print("OK ancre : envoi du dossier reduit")
else:
    print("ANCRE : " + str(n) + " occurrence(s) au lieu de 1 — ABANDON, rien ecrit.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
src = src.replace(A1, R1)
open(F, "w", encoding="utf-8").write(src)
print("1 modification ecrite. Backup : " + F + ".bak_" + tag)
