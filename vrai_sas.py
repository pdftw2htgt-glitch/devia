# vrai_sas.py — LE CHANTIER SAS
# Volet 1 : vrai sas 3D = parois laterales en ossature bois complete (lisse basse
#           + montants 45x120 entraxe 60 + lisse haute) + murailleres + solives
#           + panneau OSB 22 au metre + etancheite + bandeaux de rive
# Volet 2 : VERROU corrections = "Verifier et enregistrer" stocke aussi tes valeurs
#           dans une case "corrections" qui survit aux re-analyses, purges et
#           mises a jour ; DEVIA la sert en priorite -> dossier identique a vie
import sys, shutil, datetime

F = "devia.jsx"
src = open(F, encoding="utf-8").read()

# ----- Volet 1 : remplacement de drawSasLiaison par 2 marqueurs -----
M0 = "  const drawSasLiaison = () => {"
M1 = "  const drawEtage = () => {"
i0 = src.find(M0)
i1 = src.find(M1)
if src.count(M0) != 1 or src.count(M1) != 1 or i1 <= i0 or i0 < 0:
    print("ABANDON — marqueurs sas : M0=" + str(src.count(M0)) + " M1=" + str(src.count(M1)))
    sys.exit(1)

NOUVELLE = r'''  const drawSasLiaison = () => {
    // Sas de liaison a toit plat : parois laterales en ossature bois complete
    // (lisse basse + montants 45x120 entraxe 60 + lisse haute), murailleres
    // d appui aux pignons, solives, panneau OSB 22, etancheite, bandeaux de rive
    const [soB, soH] = sec("Solive", 0.08, 0.20);
    const [ppB, ppH] = sec("Muraillere", 0.12, 0.32);
    const hToit = Math.max(Ht, 2.2);
    const yMur = hToit - ppH / 2;
    const ySolive = hToit - soH / 2;
    const xMur = L / 2 - ppB / 2;

    // ===== 2 MURAILLERES (aux pignons d appui sur les volumes voisins) =====
    setPiece("Muraillere");
    addBox(ppB, ppH, lg, xMur, yMur, 0, woodMat);
    addBox(ppB, ppH, lg, -xMur, yMur, 0, woodMat);

    // ===== SOLIVES (portee entre les murailleres, entraxe ~50 cm) =====
    setPiece("Solive");
    const portee = L - 2 * ppB;
    const nbSolives = Math.max(2, Math.round(lg / 0.5) + 1);
    for (let i = 0; i < nbSolives; i++) {
      const z = -lg/2 + soB/2 + (i / (nbSolives - 1)) * (lg - soB);
      addBox(portee, soH, soB, 0, ySolive, z, woodMat);
    }

    // ===== PAROIS LATERALES EN OSSATURE BOIS (lisses + montants entraxe 60) =====
    const [moB, moH] = sec("Montant", 0.045, 0.12);
    const [, liH] = sec("Lisse", 0.045, 0.12);
    const hHautOss = hToit - soH;
    const hMontant = Math.max(0.3, hHautOss - 2 * liH);
    const lOss = L - 2 * ppB;
    for (const sz of [-1, 1]) {
      const zParoi = sz * (lg / 2 - moH / 2);
      setPiece("Lisse");
      addBox(lOss, liH, moH, 0, liH / 2, zParoi, woodMat);
      addBox(lOss, liH, moH, 0, hHautOss - liH / 2, zParoi, woodMat);
      setPiece("Montant");
      const nbMont = Math.max(2, Math.round(lOss / 0.6) + 1);
      for (let i = 0; i < nbMont; i++) {
        const x = -lOss/2 + moB/2 + (i / (nbMont - 1)) * (lOss - moB);
        addBox(moB, hMontant, moH, x, liH + hMontant / 2, zParoi, woodMat);
      }
    }

    // ===== PANNEAU OSB 22 mm (au metre) + ETANCHEITE (membrane) =====
    setPiece("Panneau OSB");
    addBox(L, 0.022, lg, 0, hToit + 0.011, 0, woodMat);
    const etancheMat = new THREE.MeshStandardMaterial({ color: 0x2a2d33, roughness: 0.95 });
    const memb = new THREE.Mesh(new THREE.BoxGeometry(L, 0.006, lg), etancheMat);
    memb.position.set(0, hToit + 0.022 + 0.003, 0);
    scene.add(memb);

    // ===== BANDEAUX DE RIVE (gouttereaux) =====
    setPiece("Bandeau de rive");
    for (const sz of [-1, 1]) {
      addBox(L, 0.2, 0.027, 0, hToit - 0.05, sz * (lg / 2 + 0.02), woodMat);
    }
  };

'''

# ----- Volet 2 : verrou corrections (3 ancres) -----
A2 = r'''        const { data: ligneCache } = await supabase.from("analyses_plans").select("resultat").eq("empreinte", empreinte).eq("version", versionPrompt).limit(1).maybeSingle();
        if (ligneCache && ligneCache.resultat) jCache = ligneCache.resultat;'''
R2 = r'''        const { data: ligneCorr } = await supabase.from("analyses_plans").select("resultat").eq("empreinte", empreinte).eq("version", "corrections").limit(1).maybeSingle();
        if (ligneCorr && ligneCorr.resultat) {
          jCache = ligneCorr.resultat;
          console.log("[DEVIA] Corrections utilisateur servies (dossier verrouille par tes corrections)");
        } else {
          const { data: ligneCache } = await supabase.from("analyses_plans").select("resultat").eq("empreinte", empreinte).eq("version", versionPrompt).limit(1).maybeSingle();
          if (ligneCache && ligneCache.resultat) jCache = ligneCache.resultat;
        }'''

A3 = r'''        await supabase.from("analyses_plans").upsert({ user_id: uCor.id, empreinte: analyseEmpreinte, version: analyseVersionRef.current || "manuel", resultat: j2 }, { onConflict: "user_id,empreinte,version" });'''
R3 = r'''        await supabase.from("analyses_plans").upsert({ user_id: uCor.id, empreinte: analyseEmpreinte, version: analyseVersionRef.current || "manuel", resultat: j2 }, { onConflict: "user_id,empreinte,version" });
        await supabase.from("analyses_plans").upsert({ user_id: uCor.id, empreinte: analyseEmpreinte, version: "corrections", resultat: j2 }, { onConflict: "user_id,empreinte,version" });
        console.log("[DEVIA] Corrections enregistrees ET verrouillees (elles survivront aux re-analyses et mises a jour)");'''

A4 = r'''if (analyseEmpreinte) await supabase.from("analyses_plans").delete().eq("empreinte", analyseEmpreinte);'''
R4 = r'''if (analyseEmpreinte) await supabase.from("analyses_plans").delete().eq("empreinte", analyseEmpreinte).neq("version", "corrections");'''

paires = [("verrou lecture corrections", A2, R2), ("verrou ecriture corrections", A3, R3), ("purge epargne corrections", A4, R4)]

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
src = src[:i0] + NOUVELLE + src[i1:]
for nom, ancre, rempl in paires:
    src = src.replace(ancre, rempl)
open(F, "w", encoding="utf-8").write(src)
print("Fonction sas remplacee + 3 modifications verrou. Backup : " + F + ".bak_" + tag)
