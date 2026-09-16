import shutil, datetime, sys

F = "devia.jsx"
src = open(F, encoding="utf-8").read()
bak = F + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(F, bak)
print("Backup : " + bak)

def remp(nom, ancre, nouveau):
    global src
    n = src.count(ancre)
    if n != 1:
        print("ABANDON " + nom + " : ancre trouvee " + str(n) + " fois")
        cle = ancre.strip().split("\n")[0][:45]
        for i, l in enumerate(src.split("\n")):
            if cle in l:
                print("  ligne " + str(i + 1) + " : " + l.strip()[:200])
        sys.exit(1)
    src = src.replace(ancre, nouveau)
    print("OK " + nom)

# 1) BUG : le bouton de relecture n envoyait pas le drapeau de relance forcee
remp("relance forcee",
"""                      } catch (eDel) { console.warn("[DEVIA] Purge cache impossible", eDel); }
                      analyserFichiers(files);""",
"""                      } catch (eDel) { console.warn("[DEVIA] Purge cache impossible", eDel); }
                      analyserFichiers(files, true);""")

# 2) Moteur 3D : un volume peut etre pose SOUS le terrain (sous-sol, R-1)
remp("pose negative moteur",
"""        const poseY = typeof o.pose === "number" && o.pose > 0 ? o.pose : 0;
        if (poseY > 0) { grp.position.y = poseY; }""",
"""        const poseY = typeof o.pose === "number" ? o.pose : 0;
        if (Math.abs(poseY) > 0.01) { grp.position.y = poseY; }""")

# 3) Chemin analyse : garder une pose negative
remp("pose negative analyse",
"""            pose: (typeof o.pose_hauteur_m === "number" && o.pose_hauteur_m > 0) ? o.pose_hauteur_m : undefined,""",
"""            pose: (typeof o.pose_hauteur_m === "number" && Math.abs(o.pose_hauteur_m) > 0.01) ? o.pose_hauteur_m : undefined,""")

# 4) Le terrain devient translucide des qu un volume descend dessous
remp("sol translucide",
"""    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(120, 120),
      new THREE.MeshStandardMaterial({ color: 0x1a1f2e, roughness: 0.95, metalness: 0.0 })
    );""",
"""    const listeSol = Array.isArray(params.ouvrages) ? params.ouvrages : [];
    const aDuEnterre = listeSol.some(o => o && typeof o.pose === "number" && o.pose < -0.05) || (typeof params.pose === "number" && params.pose < -0.05);
    if (aDuEnterre) console.log("[DEVIA] Niveau enterre detecte : terrain rendu translucide");
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(120, 120),
      new THREE.MeshStandardMaterial({ color: 0x1a1f2e, roughness: 0.95, metalness: 0.0, transparent: aDuEnterre, opacity: aDuEnterre ? 0.25 : 1, depthWrite: (aDuEnterre === false) })
    );""")

# 5) L IA sait maintenant coder un niveau enterre
remp("prompt niveau enterre",
"""POSE EN HAUTEUR : pose_hauteur_m = altitude de POSE du volume au-dessus du sol (0 ou null = pose au sol) ;""",
"""POSE EN HAUTEUR OU EN PROFONDEUR : pose_hauteur_m = altitude de POSE du volume par rapport au terrain fini (0 ou null = pose au sol). Elle peut etre NEGATIVE : un sous-sol, un R-1, un niveau semi-enterre ou un garage en dessous se code avec pose_hauteur_m negatif egal a la profondeur de son plancher sous le terrain (ex un R-1 de 2.6 m de hauteur entierement enterre : pose_hauteur_m = -2.6). Un dossier qui montre un plan R-1 ou une coupe ou le terrain passe au-dessus du plancher bas a donc un volume de plus, avec sa propre hauteur et une pose negative. Un volume enterre partage l emprise du volume qui est au-dessus : c est normal et ce n est pas un double comptage ;""")

# 6) Le champ manuel accepte le signe moins
remp("titre champ pose",
'''title="hauteur de pose en metres (0 = au sol)"''',
'''title="hauteur de pose en metres (0 = au sol, valeur negative = niveau enterre, ex -2.6 pour un sous-sol)"''')

# 7) Bump de version
remp("version prompt",
'const versionPrompt = vh.toString(36) + "-p6v14";',
'const versionPrompt = vh.toString(36) + "-p6v15";')

open(F, "w", encoding="utf-8").write(src)
print("--- devia.jsx ecrit ---")
