#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Modif 6 : Estimations temps fabrication + pose
- Modifie le prompt IA pour qu'il retourne temps_fabrication_h et temps_pose_h
- Ajoute une CARD "Estimation temps" dans le devis genere
- Affichage : 2 colonnes (Fabrication / Pose) + total
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_temps_estim"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Modifier le prompt IA pour demander les temps
# On ajoute la consigne juste apres l'exemple de format JSON
# ================================================================

# On cible la fin du prompt (la ligne "Genere 12 a 18 postes...")
old_prompt_end = '"Genere 12 a 18 postes realistes avec prix marche francais 2024. IMPORTANT: Reponds UNIQUEMENT avec le JSON, rien d autre.";'

new_prompt_end = '''"Genere 12 a 18 postes realistes avec prix marche francais 2024. " +
"ESTIMATION TEMPS : Tu DOIS aussi estimer le temps de fabrication en atelier (debit, assemblage des pieces) et le temps de pose sur chantier (montage de la charpente) en HEURES. " +
"Base tes estimations sur la complexite du projet, la surface, le type de charpente, le nombre de pieces. " +
"Pour une charpente traditionnelle standard : compter environ 0.8-1.2h de fabrication par m2 + 0.5-0.8h de pose par m2. " +
"Pour un carport simple : 0.4-0.6h fabrication par m2 + 0.3-0.5h pose par m2. " +
"Pour un hangar : 0.3-0.5h fabrication par m2 + 0.2-0.4h pose par m2. " +
"Ajuste selon les specificites (pente forte, combles amenages, essence difficile = +20%). " +
"AJOUTE ces 2 valeurs dans le JSON apres totaux : \\"temps_fabrication_h\\":XX, \\"temps_pose_h\\":XX (entiers). " +
"IMPORTANT: Reponds UNIQUEMENT avec le JSON, rien d autre.";'''

if "temps_fabrication_h" in content:
    print("[INFO] Prompt deja modifie")
elif old_prompt_end in content:
    content = content.replace(old_prompt_end, new_prompt_end, 1)
    print("[OK] Prompt IA modifie pour demander temps_fabrication_h et temps_pose_h")
    modifs += 1
else:
    print("[ERREUR] Fin du prompt non trouvee")
    sys.exit(1)

# ================================================================
# MOD 2 : Mettre a jour l'exemple JSON dans le prompt
# pour que l'IA voie les nouveaux champs
# ================================================================

old_json_example = '\'"totaux":{"totalHT":12000,"tva":2400,"totalTTC":14400},"notes":["Note 1"]}. \''

new_json_example = '\'"totaux":{"totalHT":12000,"tva":2400,"totalTTC":14400},"temps_fabrication_h":24,"temps_pose_h":16,"notes":["Note 1"]}. \''

if '"temps_fabrication_h":24' in content:
    print("[INFO] Exemple JSON deja modifie")
elif old_json_example in content:
    content = content.replace(old_json_example, new_json_example, 1)
    print("[OK] Exemple JSON dans le prompt mis a jour")
    modifs += 1
else:
    print("[WARN] Exemple JSON non trouve")

# ================================================================
# MOD 3 : Ajouter la CARD "Estimation temps" apres le bloc des totaux
# On cible le </div> qui ferme le bloc des totaux
# Strategie : on ajoute la card juste avant la <FeuilleCalcTable ...>
# car FeuilleCalcTable est apres les totaux
# ================================================================

old_feuille_marker = '                <FeuilleCalcTable devisData={result.projet || {}} zoneData={zoneInfo} />'

new_with_card = '''                {/* Card Estimation temps fabrication + pose */}
                {(result.temps_fabrication_h !== undefined || result.temps_pose_h !== undefined) && (() => {
                  const fab = Number(result.temps_fabrication_h) || 0;
                  const pose = Number(result.temps_pose_h) || 0;
                  const total = fab + pose;
                  return (
                    <div style={{
                      background: "linear-gradient(135deg, rgba(96, 165, 250, 0.08), rgba(167, 139, 250, 0.04))",
                      border: "1px solid rgba(96, 165, 250, 0.18)",
                      borderRadius: 16,
                      padding: 20,
                      marginBottom: 16,
                      backdropFilter: "blur(24px) saturate(140%)",
                      WebkitBackdropFilter: "blur(24px) saturate(140%)"
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                        <div style={{
                          width: 32, height: 32, borderRadius: 8,
                          background: "rgba(96, 165, 250, 0.12)",
                          border: "1px solid rgba(96, 165, 250, 0.2)",
                          display: "flex", alignItems: "center", justifyContent: "center"
                        }}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                          </svg>
                        </div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 14, color: "#e8eaf2" }}>Estimation temps</div>
                          <div style={{ color: "#7a7d92", fontSize: 12 }}>Fabrication atelier + pose chantier</div>
                        </div>
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
                        {/* Fabrication */}
                        <div style={{
                          background: "rgba(255, 255, 255, 0.025)",
                          border: "1px solid rgba(255, 255, 255, 0.05)",
                          borderRadius: 12,
                          padding: 14
                        }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 8 }}>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#fb923c" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/>
                            </svg>
                            <span style={{ color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase" }}>Fabrication</span>
                          </div>
                          <div style={{ fontSize: 22, fontWeight: 700, color: "#e8eaf2", letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums" }}>
                            {fab}<span style={{ fontSize: 13, color: "#7a7d92", fontWeight: 500, marginLeft: 4 }}>h</span>
                          </div>
                          <div style={{ color: "#545870", fontSize: 11, marginTop: 4 }}>Atelier</div>
                        </div>
                        {/* Pose */}
                        <div style={{
                          background: "rgba(255, 255, 255, 0.025)",
                          border: "1px solid rgba(255, 255, 255, 0.05)",
                          borderRadius: 12,
                          padding: 14
                        }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 8 }}>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                            </svg>
                            <span style={{ color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase" }}>Pose</span>
                          </div>
                          <div style={{ fontSize: 22, fontWeight: 700, color: "#e8eaf2", letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums" }}>
                            {pose}<span style={{ fontSize: 13, color: "#7a7d92", fontWeight: 500, marginLeft: 4 }}>h</span>
                          </div>
                          <div style={{ color: "#545870", fontSize: 11, marginTop: 4 }}>Chantier</div>
                        </div>
                        {/* Total */}
                        <div style={{
                          background: "linear-gradient(135deg, rgba(240, 192, 64, 0.1), rgba(240, 192, 64, 0.03))",
                          border: "1px solid rgba(240, 192, 64, 0.25)",
                          borderRadius: 12,
                          padding: 14
                        }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 8 }}>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                            </svg>
                            <span style={{ color: "#f0c040", fontSize: 10, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase" }}>Total</span>
                          </div>
                          <div style={{ fontSize: 22, fontWeight: 700, color: "#f0c040", letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums" }}>
                            {total}<span style={{ fontSize: 13, color: "#a8841f", fontWeight: 500, marginLeft: 4 }}>h</span>
                          </div>
                          <div style={{ color: "#a8841f", fontSize: 11, marginTop: 4 }}>{Math.ceil(total / 8)} jour(s) - 8h</div>
                        </div>
                      </div>
                    </div>
                  );
                })()}

                <FeuilleCalcTable devisData={result.projet || {}} zoneData={zoneInfo} />'''

if "Card Estimation temps fabrication" in content:
    print("[INFO] Card Estimation deja en place")
elif old_feuille_marker in content:
    content = content.replace(old_feuille_marker, new_with_card, 1)
    print("[OK] Card Estimation temps ajoutee avant FeuilleCalcTable")
    modifs += 1
else:
    print("[ERREUR] Marqueur FeuilleCalcTable non trouve")
    sys.exit(1)

# ================================================================
# MOD 4 : Sauvegarder temps_fabrication_h et temps_pose_h en BDD
# Quand on save un projet, on doit aussi sauvegarder ces valeurs
# Mais comme ils sont deja dans devis_data (JSON), pas besoin de modif BDD
# ================================================================

print("[INFO] Pas de modif BDD necessaire (temps stockes dans devis_data JSON)")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Prompt IA modifie pour estimer temps_fabrication_h + temps_pose_h")
print("  2. Exemple JSON du prompt mis a jour")
print("  3. Card 'Estimation temps' ajoutee en haut du devis genere")
print()
print("RATIOS UTILISES PAR L'IA :")
print("  - Charpente traditionnelle : 0.8-1.2h fabrication + 0.5-0.8h pose / m2")
print("  - Carport simple : 0.4-0.6h fabrication + 0.3-0.5h pose / m2")
print("  - Hangar : 0.3-0.5h fabrication + 0.2-0.4h pose / m2")
print("  - Specificites (pente forte, combles, essence dure) : +20%")
print()
print("AFFICHAGE :")
print("  Card en haut du devis avec 3 colonnes :")
print("  [Fabrication: XXh] [Pose: XXh] [Total: XXh = X jour(s)]")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
