# Boussole M1 : la passe geometrie lit la fleche du nord et donne les facades cardinales
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''mets 0 UNIQUEMENT si le volume est visiblement centre sur le mur.'''
NEW1 = '''mets 0 UNIQUEMENT si le volume est visiblement centre sur le mur. ORIENTATION CARDINALE (prioritaire) : repere la fleche du NORD dessinee sur le plan de masse ou le plan de toitures, puis donne pour chaque volume accole la FACADE cardinale du volume de reference contre laquelle il se colle (nord, sud, est ou ouest) et son ALIGNEMENT (aligne sur le bord est, ouest, nord ou sud du mur, ou centre). Verifie ces facades contre les noms des facades du dossier (facade nord, sud, est, ouest) quand elles existent.'''

OLD2 = '''"cote":"pignon_gauche|pignon_droit|gouttereau_avant|gouttereau_arriere|null",'''
NEW2 = '''"cote":"pignon_gauche|pignon_droit|gouttereau_avant|gouttereau_arriere|null","facade":"nord|sud|est|ouest|null","alignement":"nord|sud|est|ouest|centre|null",'''

OLD3 = '''            pos: (o.contre && o.cote) ? { contre: o.contre, cote: o.cote, decalage: (typeof o.decalage_m === "number" ? o.decalage_m : 0), faitage: o.faitage || "parallele" } : undefined,'''
NEW3 = '''            pos: (o.contre && o.cote) ? { contre: o.contre, cote: o.cote, facade: o.facade || null, alignement: o.alignement || null, decalage: (typeof o.decalage_m === "number" ? o.decalage_m : 0), faitage: o.faitage || "parallele" } : undefined,'''

OLD4 = '''(s.pos ? " - contre V" + s.pos.contre + ", " + String(s.pos.cote).replace("_", " ") + ", faitage " + (s.pos.faitage || "?") + ", decalage " + (s.pos.decalage || 0) + "m" : "")'''
NEW4 = '''(s.pos ? " - contre V" + s.pos.contre + ", " + (s.pos.facade ? "FACADE " + s.pos.facade + (s.pos.alignement ? " aligne " + s.pos.alignement : "") + ", " : "") + String(s.pos.cote).replace("_", " ") + ", faitage " + (s.pos.faitage || "?") + ", decalage " + (s.pos.decalage || 0) + "m" : "")'''

OLD5 = '''const versionPrompt = vh.toString(36) + "-p3v5";'''
NEW5 = '''const versionPrompt = vh.toString(36) + "-p3v6";'''

anchors = [("prompt cardinal", OLD1, NEW1), ("schema facade", OLD2, NEW2), ("pos facade", OLD3, NEW3), ("ligne jaune facade", OLD4, NEW4), ("cache v6", OLD5, NEW5)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_boussole_M1")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK M1 : lecture cardinale (facades + alignements) en place")
