# Passes v2 : mesure des decalages (bords affleurants) + hauteurs coherentes
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = ''', et le decalage cote quand il existe.'''
NEW1 = ''', et le DECALAGE : un volume accole est rarement centre - s'il est aligne sur un bord du volume de reference (bords affleurants sur le plan), decalage = (longueur du mur de reference moins longueur du volume) / 2, signe positif vers la droite ou l'avant ; mets 0 UNIQUEMENT si le volume est visiblement centre sur le mur.'''

OLD2 = '''un corps a etage est plus haut qu'un corps en rez-de-chaussee), la pente de toiture telle qu'ecrite avec son unite'''
NEW2 = '''un corps a etage est plus haut qu'un corps en rez-de-chaussee ; un sas a toit plat est plus BAS que ses deux voisins, sa hauteur = celle de sa toiture plate ; CHAQUE volume doit repartir avec une hauteur d'egout, le volume principal aussi), la pente de toiture telle qu'ecrite avec son unite'''

OLD3 = '''const versionPrompt = vh.toString(36) + "-p3v1";'''
NEW3 = '''const versionPrompt = vh.toString(36) + "-p3v2";'''

anchors = [("decalage passe geometrie", OLD1, NEW1), ("hauteurs passe 2B", OLD2, NEW2), ("version cache", OLD3, NEW3)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_passes_v2")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : passes v2 (decalages mesures + hauteurs coherentes)")
