# pose_moteur.py — HAUTEUR DE POSE par ouvrage (0 = au sol)
# moteur 3D + editeur + verificateur (chevauchement tolere entre niveaux differents)
# + persistance _ouvrages3D + cache corrections
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

A1 = r'''      const construire = (o, extraOpts) => {
        const grp = construireOuvrage(o, extraOpts, decoupesParOuvrage.get(o) || null);
        groupes.push(grp);
        return grp;
      };'''
R1 = r'''      const construire = (o, extraOpts) => {
        const grp = construireOuvrage(o, extraOpts, decoupesParOuvrage.get(o) || null);
        const poseY = typeof o.pose === "number" && o.pose > 0 ? o.pose : 0;
        if (poseY > 0) { grp.position.y = poseY; }
        groupes.push(grp);
        return grp;
      };'''

A2 = r'''        if (ox > 0.05 && oz > 0.05) erreurs.push("V" + (a + 1) + " et V" + (b + 1) + " se chevauchent (" + ox.toFixed(2) + " x " + oz.toFixed(2) + " m) : positions incoherentes");'''
R2 = r'''        const ecartPose = Math.abs((vols[a].pose || 0) - (vols[b].pose || 0));
        if (ox > 0.05 && oz > 0.05 && ecartPose < 0.5) erreurs.push("V" + (a + 1) + " et V" + (b + 1) + " se chevauchent (" + ox.toFixed(2) + " x " + oz.toFixed(2) + " m) : positions incoherentes - si l un est pose sur l autre, donne-lui une hauteur de pose");'''

A3 = r'''      <span>cm</span>
      <select value={v.faitageCardinal || ""}'''
R3 = r'''      <span>cm</span>
      <span>pose</span>
      <input value={v.pose === undefined || v.pose === "" ? "" : v.pose} onChange={e => majVolume(i, "pose", e.target.value)} style={{ ...miniInp, width: 44 }} title="hauteur de pose en metres (0 = au sol)" />
      <span>m</span>
      <select value={v.faitageCardinal || ""}'''

A4 = r'''        faitageCardinal: v.faitageCardinal || undefined,
      };'''
R4 = r'''        faitageCardinal: v.faitageCardinal || undefined,
        pose: (v.pose === undefined || v.pose === "") ? undefined : num(v.pose, 0),
      };'''

A5 = r'''debord_toiture_cm: s.debord ? Math.round(s.debord * 100) : null, desc: s.desc })) };'''
R5 = r'''debord_toiture_cm: s.debord ? Math.round(s.debord * 100) : null, pose_hauteur_m: s.pose || null, desc: s.desc })) };'''

A6 = r'''faitage: o.faitage || "parallele" } : undefined,'''
R6 = r'''faitage: o.faitage || "parallele" } : undefined,
            pose: (typeof o.pose_hauteur_m === "number" && o.pose_hauteur_m > 0) ? o.pose_hauteur_m : undefined,'''

A7 = r'''        pos: s.pos || undefined,
        faitageCardinal: s.faitageCardinal || undefined,'''
R7 = r'''        pos: s.pos || undefined,
        pose: s.pose || undefined,
        faitageCardinal: s.faitageCardinal || undefined,'''

paires = [
    ("moteur pose Y", A1, R1),
    ("verificateur niveaux", A2, R2),
    ("editeur champ pose", A3, R3),
    ("corrections structs2", A4, R4),
    ("cache corrections", A5, R5),
    ("parsing analyse", A6, R6),
    ("persistance ouvrages3D", A7, R7),
]

erreurs = 0
for nom, ancre, rempl in paires:
    n = src.count(ancre)
    if n == 1:
        print("OK ancre : " + nom)
    else:
        erreurs = erreurs + 1
        print("ANCRE '" + nom + "' : " + str(n) + " occurrence(s) au lieu de 1")
        frag = ancre.strip().split("\n")[0][:50]
        i = src.find(frag)
        if i >= 0:
            print("--- zone reelle ---")
            print(src[max(0, i - 150):i + 400])

if erreurs > 0:
    print("ABANDON — aucune modification ecrite.")
    sys.exit(1)

tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, F + ".bak_" + tag)
for nom, ancre, rempl in paires:
    src = src.replace(ancre, rempl)
open(F, "w", encoding="utf-8").write(src)
print("7 modifications ecrites. Backup : " + F + ".bak_" + tag)
