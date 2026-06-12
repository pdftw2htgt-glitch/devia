#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix bugs tokens/CO2 : utiliser table usage_logs
- Etape B : insert usage_logs apres chaque generation + maj state local
- Etape C : stats calculees depuis usage_logs (pas projects)
- Charge usageLogs au demarrage
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_usage_logs"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter le state usageLogs
# ================================================================
old_state = 'const [showInfosEntreprise, setShowInfosEntreprise] = useState(false);'
new_state = '''const [showInfosEntreprise, setShowInfosEntreprise] = useState(false);
  const [usageLogs, setUsageLogs] = useState([]);'''

if "const [usageLogs" in content:
    print("[INFO] State usageLogs deja present")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] State usageLogs ajoute")
    modifs += 1
else:
    print("[ERREUR] State showInfosEntreprise non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Charger usage_logs au demarrage (apres loadGroupes)
# ================================================================
old_loadgroupes_end = '''    loadGroupes();
  }, []);'''

new_with_loadlogs = '''    loadGroupes();

    // Chargement de l'historique de consommation
    const loadUsageLogs = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;
        const { data, error } = await supabase
          .from("usage_logs")
          .select("*")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false });
        if (error) {
          console.error("Erreur chargement usage_logs:", error);
          return;
        }
        if (data) setUsageLogs(data);
      } catch (e) {
        console.error("Erreur loadUsageLogs:", e);
      }
    };
    loadUsageLogs();
  }, []);'''

if "const loadUsageLogs = async" in content:
    print("[INFO] loadUsageLogs deja present")
elif old_loadgroupes_end in content:
    content = content.replace(old_loadgroupes_end, new_with_loadlogs, 1)
    print("[OK] loadUsageLogs ajoute au demarrage")
    modifs += 1
else:
    print("[ERREUR] Fin loadGroupes non trouvee")
    sys.exit(1)

# ================================================================
# MOD 3 : Apres insert projet, inserer aussi dans usage_logs
# + ajouter au state local pour eviter le refresh F5
# On cible la zone apres insert avec succes
# ================================================================

# On vise la fin du bloc 'else if (inserted)' ou apres l'insert reussi
# La logique : juste apres l'insert reussi, on insert dans usage_logs

# On va viser le else if (inserted) {
old_else_inserted = '''const { data: inserted, error: insertError } = await supabase
            .from("projects")
            .insert(newProject)
            .select()
            .single();
          if (insertError) {'''

new_else_inserted = '''const tokensIn = (data.usage && data.usage.input_tokens) || 0;
          const tokensOut = (data.usage && data.usage.output_tokens) || 0;

          const { data: inserted, error: insertError } = await supabase
            .from("projects")
            .insert(newProject)
            .select()
            .single();
          if (insertError) {'''

if "const tokensIn = (data.usage" in content:
    print("[INFO] Variables tokensIn/Out deja en place")
elif old_else_inserted in content:
    content = content.replace(old_else_inserted, new_else_inserted, 1)
    print("[OK] Variables tokensIn/tokensOut declarees avant insert")
    modifs += 1
else:
    print("[WARN] Bloc insert non trouve exactement")

# Maintenant on ajoute l'insert dans usage_logs APRES l'insert reussi
# On cible la branche 'else if (inserted)'
# La structure typique : } else if (inserted) { ... setProjects... }

# On cherche le pattern : } else if (inserted) {
old_branch = '''} else if (inserted) {'''

# On va inserer l'insert usage_logs juste apres cette ligne
# Mais il faut etre prudent - on inserer dans le PREMIER match seulement
# pour eviter d'inserer dans plusieurs endroits

if "// Insert usage_logs" not in content:
    if old_branch in content:
        # Trouve la position du premier match
        idx = content.index(old_branch)
        # Insere apres
        insert_text = '''} else if (inserted) {
            // Insert usage_logs : historique de consommation (survit a la suppression du projet)
            (async () => {
              try {
                const { data: logData, error: logError } = await supabase
                  .from("usage_logs")
                  .insert({
                    user_id: user.id,
                    tokens_in: tokensIn,
                    tokens_out: tokensOut,
                    model: "claude-sonnet-4-20250514",
                    project_id: inserted.id,
                  })
                  .select()
                  .single();
                if (logError) {
                  console.error("Erreur insert usage_logs:", logError);
                } else if (logData) {
                  // Maj du state local immediatement (pas besoin de refresh)
                  setUsageLogs(prev => [logData, ...prev]);
                }
              } catch (e) {
                console.error("Erreur usage_logs async:", e);
              }
            })();'''
        content = content.replace(old_branch, insert_text, 1)
        print("[OK] Insert usage_logs ajoute apres l'insert projet")
        modifs += 1
    else:
        print("[WARN] Branche 'else if (inserted)' non trouvee")
else:
    print("[INFO] Insert usage_logs deja en place")

# ================================================================
# MOD 4 : Remplacer le calcul des stats pour utiliser usageLogs
# au lieu de calculer depuis projects
# ================================================================

# On vise la calcul de tokensTotal/tokensMonth dans le bloc 5 stats
old_calc = '''            const tokensTotal = projects.reduce((sum, p) => sum + (p.tokens_in || 0) + (p.tokens_out || 0), 0);
            const tokensMonth = projetsThisMonth.reduce((sum, p) => sum + (p.tokens_in || 0) + (p.tokens_out || 0), 0);'''

new_calc = '''            // Tokens calcules depuis usage_logs (survit a la suppression de projets)
            const tokensTotal = usageLogs.reduce((sum, l) => sum + (l.tokens_in || 0) + (l.tokens_out || 0), 0);
            const logsThisMonth = usageLogs.filter(l => {
              if (!l.created_at) return false;
              const d = new Date(l.created_at);
              return d.getMonth() === thisMonth && d.getFullYear() === thisYear;
            });
            const tokensMonth = logsThisMonth.reduce((sum, l) => sum + (l.tokens_in || 0) + (l.tokens_out || 0), 0);'''

if "// Tokens calcules depuis usage_logs" in content:
    print("[INFO] Calcul stats deja base sur usageLogs")
elif old_calc in content:
    content = content.replace(old_calc, new_calc, 1)
    print("[OK] Stats Tokens/CO2 calculees depuis usage_logs (et non plus projects)")
    modifs += 1
else:
    print("[ERREUR] Bloc calcul tokensTotal non trouve")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. State usageLogs ajoute")
print("  2. loadUsageLogs() au demarrage")
print("  3. Apres chaque insert projet reussi :")
print("     - Insert aussi dans usage_logs")
print("     - Maj du state usageLogs immediatement (FIX bug refresh)")
print("  4. Stats Tokens/CO2 calculees depuis usage_logs (FIX bug suppression)")
print()
print("RESULTAT :")
print("  - Bug 1 : plus besoin de F5 apres une generation")
print("  - Bug 2 : la suppression d'un projet ne touche plus les stats")
print()
print("COMMENT TESTER :")
print("  1. npm run build")
print("  2. Recharger Safari")
print("  3. Va sur Compte -> verifie que tu vois deja les tokens existants")
print("     (les anciens logs migres depuis projects)")
print("  4. Genere un NOUVEAU devis")
print("  5. Reviens sur Compte -> tokens monte IMMEDIATEMENT (sans F5)")
print("  6. Supprime ce projet depuis Projets")
print("  7. Reviens sur Compte -> tokens reste IDENTIQUE (pas de baisse)")
print()
print(f"BACKUP : {backup_name}")
