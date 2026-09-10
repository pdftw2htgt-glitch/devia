# sans_upsert.py — l option upsert exigeait le droit UPDATE sur le stockage
# alors que le chemin du fichier est deja unique (horodatage + aleatoire).
# On envoie en simple creation : plus besoin de ce droit.
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''const { error: upErr } = await supabase.storage.from("plans").upload(chemin, f, { upsert: true, cacheControl: "0" });'''
R1 = r'''const { error: upErr } = await supabase.storage.from("plans").upload(chemin, f, { cacheControl: "0" });'''

n = src.count(A1)
if n == 1:
    print("OK ancre : envoi du plan")
else:
    print("ANCRE : " + str(n) + " occurrence(s) au lieu de 1 — ABANDON, rien ecrit.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
src = src.replace(A1, R1)
open(F, "w", encoding="utf-8").write(src)
print("1 modification ecrite. Backup : " + F + ".bak_" + tag)
