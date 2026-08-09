# Marche 3-2 : le type sas_liaison connu de la GENERATION + type 3D force cote code
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''"'etage' (plancher d'etage interieur, solivage, mezzanine, plancher bois porteur dans un batiment), " +'''
NEW1 = '''"'etage' (plancher d'etage interieur, solivage, mezzanine, plancher bois porteur dans un batiment), " +
"'sas_liaison' (sas de liaison a TOIT PLAT entre deux batiments accoles : genere UNIQUEMENT 2 murailleres fixees aux murs voisins, des solives entre elles entraxe 50 cm, panneau de toiture et etancheite, visserie et fixations - PAS de pannes, PAS de chevrons, PAS de fermes, PAS de couverture tuiles), " +'''

OLD2 = ''''"type_projet":"carport_OU_charpente_trad_OU_monopente_OU_hangar_OU_appentis_OU_4_pans_OU_abri_OU_autre"},' +'''
NEW2 = ''''"type_projet":"carport_OU_charpente_trad_OU_monopente_OU_hangar_OU_appentis_OU_4_pans_OU_abri_OU_sas_liaison_OU_autre"},' +'''

OLD3 = '''        type_projet: (devisParOuvrage[i] && devisParOuvrage[i].projet && devisParOuvrage[i].projet.type_projet) || TYPE_TO_PROJET[s.type] || "charpente_trad",'''
NEW3 = '''        type_projet: s.type === "sas" ? "sas_liaison" : ((devisParOuvrage[i] && devisParOuvrage[i].projet && devisParOuvrage[i].projet.type_projet) || TYPE_TO_PROJET[s.type] || "charpente_trad"),'''

anchors = [("prompt generation types", OLD1, NEW1), ("enum json type_projet", OLD2, NEW2), ("type 3D force pour sas", OLD3, NEW3)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_sas_32")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK 3-2 : sas_liaison connu de la generation + type 3D force")
