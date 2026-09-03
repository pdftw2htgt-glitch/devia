# sas_orientation.py — orientation du sas FORCEE par le moteur :
# murailleres toujours tournees vers les volumes relies (faces d appui),
# ossature toujours sur les deux cotes exterieurs libres
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''          if (o.type_projet === "monopente" || o.type_projet === "appentis") {'''
R1 = r'''          if (o.type_projet === "sas_liaison") {
            const fcS = o.pos.facade || "";
            const cotS = o.pos.cote || "";
            if (fcS === "est" || fcS === "ouest" || cotS === "pignon_droit" || cotS === "pignon_gauche") { rot = 0; }
            else { rot = Math.PI / 2; }
            console.log("[DEVIA] Sas accole : orientation FORCEE, murailleres vers les volumes relies");
          }
          if (o.type_projet === "monopente" || o.type_projet === "appentis") {'''

n = src.count(A1)
if n == 1:
    print("OK ancre : orientation sas")
else:
    print("ANCRE : " + str(n) + " occurrence(s) au lieu de 1 — ABANDON, rien ecrit.")
    sys.exit(1)

if src.count("Sas accole : orientation FORCEE") > 0:
    print("Script deja passe — rien a faire.")
    sys.exit(0)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
src = src.replace(A1, R1)
open(F, "w", encoding="utf-8").write(src)
print("1 modification ecrite. Backup : " + F + ".bak_" + tag)
