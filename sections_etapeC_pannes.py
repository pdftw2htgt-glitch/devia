#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEVIA - Sections etape C : injecter section EC5 dans les pannes 3D (hangar), avec fallback"""
import shutil
from datetime import datetime

content = open("devia.jsx", encoding="utf-8").read()
modifs = 0
def apply(old, new, label):
    global content, modifs
    n = content.count(old)
    if n == 1:
        content = content.replace(old, new, 1); print(f"[OK] {label}"); modifs += 1
    elif n == 0: print(f"[WARN] {label} : NON trouve")
    else: print(f"[WARN] {label} : {n}x ambigu -> ignore")

backup = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_sectionsC"
shutil.copy("devia.jsx", backup)
print(f"[OK] Backup : {backup}")

# 1) Ajouter le helper sec() au debut de buildScene3D (apres la lecture de pente)
apply(
    '''  const typeProjet = params.type_projet || "charpente_trad";

  // Options : couleurs (peuvent varier pour le PDF vs interactif)''',
    '''  const typeProjet = params.type_projet || "charpente_trad";

  // Helper sections EC5 : si opts.sections[nom] existe, l'utilise (mm->m), sinon fallback
  // sectionMode choisit mini ou conseillee
  const secMode = (opts && opts.sectionMode) || "conseillee";
  const sec = (nom, wDef, hDef) => {
    const dim = opts && opts.sections && opts.sections[nom];
    if (dim && dim[secMode]) return [dim[secMode].b / 1000, dim[secMode].h / 1000];
    return [wDef, hDef];
  };

  // Options : couleurs (peuvent varier pour le PDF vs interactif)''',
    "Helper sec() dans buildScene3D"
)

# 2) Pannes hangar : faitiere + intermediaires
apply(
    '''    addBox(L + 0.5, 0.16, 0.16, 0, yFait, 0, woodMat);
    const nbPannesParPan = 2;
    for (let p = 1; p <= nbPannesParPan; p++) {
      const t = p / (nbPannesParPan + 1);
      const yPanne = Ht + hf * t;
      const zPanne = (lg/2) * (1 - t);
      addBox(L + 0.4, 0.12, 0.12, 0, yPanne, zPanne, woodMat);
      addBox(L + 0.4, 0.12, 0.12, 0, yPanne, -zPanne, woodMat);
    }''',
    '''    const [pfw, pfh] = sec("Panne faitiere", 0.16, 0.16);
    addBox(L + 0.5, pfw, pfh, 0, yFait, 0, woodMat);
    const nbPannesParPan = 2;
    const [pw, ph] = sec("Panne", 0.12, 0.12);
    for (let p = 1; p <= nbPannesParPan; p++) {
      const t = p / (nbPannesParPan + 1);
      const yPanne = Ht + hf * t;
      const zPanne = (lg/2) * (1 - t);
      addBox(L + 0.4, pw, ph, 0, yPanne, zPanne, woodMat);
      addBox(L + 0.4, pw, ph, 0, yPanne, -zPanne, woodMat);
    }''',
    "Pannes hangar avec section EC5"
)

# 3) Passer sections + sectionMode depuis Viewer3D
apply(
    '''    // Construction de la scene via fonction commune
    const buildResultViewer = buildScene3D(scene, params, { couverture: params.couverture, mode: params.mode3D });
    if (onMetreRef.current && buildResultViewer.metre) {
      onMetreRef.current(agregerMetre(buildResultViewer.metre, buildResultViewer.densiteBois || 450), buildResultViewer.metre);
    }''',
    '''    // Construction de la scene via fonction commune
    // 1er passage : sans sections (pour obtenir le metre)
    const preBuild = buildScene3D(scene, params, { couverture: params.couverture, mode: params.mode3D });
    // calcul des sections EC5 a partir du metre obtenu
    let sectionsEC5 = {};
    try {
      const agg = agregerMetre(preBuild.metre, preBuild.densiteBois || 450);
      sectionsEC5 = calculerSectionsCharpente(agg, params, params.sk);
    } catch (e) { sectionsEC5 = {}; }
    // 2e passage : on vide la scene des meshes et on redessine avec les sections
    // (simple : on retire tous les Mesh ajoutes par le 1er passage)
    const toRemove = [];
    scene.traverse((o) => { if (o.isMesh) toRemove.push(o); });
    toRemove.forEach((o) => { scene.remove(o); if (o.geometry) o.geometry.dispose(); });
    const buildResultViewer = buildScene3D(scene, params, {
      couverture: params.couverture, mode: params.mode3D,
      sections: sectionsEC5, sectionMode: params.sectionMode || "conseillee",
    });
    if (onMetreRef.current && buildResultViewer.metre) {
      onMetreRef.current(agregerMetre(buildResultViewer.metre, buildResultViewer.densiteBois || 450), buildResultViewer.metre);
    }''',
    "Double passage + injection sections dans Viewer3D"
)

# 4) Ajouter sectionMode aux dependances du useEffect (pour redessiner au toggle)
apply(
    "  }, [params.longueur, params.largeur, params.hauteur, params.pente, params.type_projet, params.couverture, params.mode3D]);",
    "  }, [params.longueur, params.largeur, params.hauteur, params.pente, params.type_projet, params.couverture, params.mode3D, params.sectionMode]);",
    "sectionMode dans les deps useEffect"
)

# 5) Passer sectionMode dans les params de Viewer3D (cote rendu)
apply(
    "<Viewer3D params={{ ...view3DParams, mode3D }} onMetre={(agg, brut) => { setMetreData(agg); setMetreBrut(brut); }} />",
    "<Viewer3D params={{ ...view3DParams, mode3D, sectionMode, sk: zoneInfo ? zoneInfo.sk : 0.45 }} onMetre={(agg, brut) => { setMetreData(agg); setMetreBrut(brut); }} />",
    "sectionMode + sk passes a Viewer3D"
)

open("devia.jsx", "w", encoding="utf-8").write(content)
print()
print("="*60); print(f"{modifs} MODIFICATION(S) APPLIQUEE(S)"); print("="*60)
print(f"BACKUP : {backup}")
