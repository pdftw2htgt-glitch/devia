# Split habitat, 2e passe : effort analyse medium + regle gouttereau debiaisee + exemple L
import shutil, datetime, sys
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
F = "devia.jsx"
with open(F, "r", encoding="utf-8") as f:
    c = f.read()

OLD1 = '''          output_config: { effort: "low" },'''
NEW1 = '''          output_config: { effort: "medium" },'''

OLD2 = '''Un gouttereau ne se choisit que si le plan de masse montre clairement le volume sur le long cote.'''
NEW2 = '''Un gouttereau se choisit quand le plan de masse montre le volume sur le long cote - cas typique : batiment en L.'''

OLD3 = '''Ne fusionne jamais deux corps de faitages differents en un seul rectangle. '''
NEW3 = '''Ne fusionne jamais deux corps de faitages differents en un seul rectangle. Cas typique du batiment en L : corps principal, plus corps secondaire ACCOLE EN GOUTTEREAU (sur le long cote) avec un decalage_m, chacun avec sa hauteur lue sur sa coupe. '''

anchors = [("effort analyse", OLD1, NEW1), ("regle gouttereau", OLD2, NEW2), ("exemple L", OLD3, NEW3)]
for nom, old, new in anchors:
    n = c.count(old)
    if n != 1:
        print("ERREUR ancre (" + nom + ") : " + str(n) + " occurrence(s) au lieu de 1 - abandon, rien modifie")
        sys.exit(1)
shutil.copy2(F, F + ".backup_" + stamp + "_split_habitat_2")
for nom, old, new in anchors:
    c = c.replace(old, new)
with open(F, "w", encoding="utf-8") as f:
    f.write(c)
print("OK : effort medium + gouttereau debiaise + exemple L")
