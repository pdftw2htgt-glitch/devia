#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix : persistance des parametres entreprise
- Au demarrage : charge params depuis Supabase (profiles.params)
- Au changement : sauvegarde auto avec debounce (800ms)
- Indicator visuel "Sauvegarde..."
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_params_persist"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter states pour la sauvegarde + ref de debounce
# Apres la definition de params
# ================================================================

old_params_block = '''const [params, setParams] = useState({
entreprise: "", siret: "", adresse: "",
tauxHoraire: 55, tva: 20, marge: 25,
mentions: "Devis valable 30 jours.",
});
const fileInputRef = useRef(null);'''

new_params_block = '''const [params, setParams] = useState({
entreprise: "", siret: "", adresse: "",
tauxHoraire: 55, tva: 20, marge: 25,
mentions: "Devis valable 30 jours.",
});
const [paramsLoaded, setParamsLoaded] = useState(false);
const [paramsSaving, setParamsSaving] = useState(false);
const [paramsSavedAt, setParamsSavedAt] = useState(null);
const paramsSaveTimerRef = useRef(null);
const fileInputRef = useRef(null);'''

if "paramsLoaded" in content:
    print("[INFO] States persistance deja ajoutes")
elif old_params_block in content:
    content = content.replace(old_params_block, new_params_block, 1)
    print("[OK] States paramsLoaded/Saving/SavedAt + timer ref ajoutes")
    modifs += 1
else:
    print("[ERREUR] Bloc params non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Ajouter useEffect pour charger les params au demarrage
# Et un autre useEffect pour sauvegarder en debounced
# On les place juste avant detectParams
# ================================================================

old_detect_marker = 'const detectParams = (text) => {'

new_with_persist = '''// Charger les params depuis Supabase au demarrage
useEffect(() => {
  const loadParams = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) { setParamsLoaded(true); return; }
      const { data, error } = await supabase
        .from("profiles")
        .select("params")
        .eq("user_id", user.id)
        .maybeSingle();
      if (error) {
        console.error("Erreur chargement params :", error);
        setParamsLoaded(true);
        return;
      }
      if (data && data.params && Object.keys(data.params).length > 0) {
        setParams(prev => ({ ...prev, ...data.params }));
      }
      setParamsLoaded(true);
    } catch (e) {
      console.error("Erreur loadParams :", e);
      setParamsLoaded(true);
    }
  };
  loadParams();
}, []);

// Sauvegarde automatique des params dans Supabase avec debounce
useEffect(() => {
  if (!paramsLoaded) return; // Ne pas sauvegarder pendant le chargement initial
  if (paramsSaveTimerRef.current) clearTimeout(paramsSaveTimerRef.current);
  paramsSaveTimerRef.current = setTimeout(async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      setParamsSaving(true);
      const { error } = await supabase
        .from("profiles")
        .upsert({
          user_id: user.id,
          params: params,
          updated_at: new Date().toISOString()
        }, { onConflict: "user_id" });
      if (error) {
        console.error("Erreur sauvegarde params :", error);
        setParamsSaving(false);
        return;
      }
      setParamsSavedAt(new Date());
      setTimeout(() => setParamsSaving(false), 300);
    } catch (e) {
      console.error("Erreur saveParams :", e);
      setParamsSaving(false);
    }
  }, 800); // Debounce 800ms
  return () => {
    if (paramsSaveTimerRef.current) clearTimeout(paramsSaveTimerRef.current);
  };
}, [params, paramsLoaded]);

const detectParams = (text) => {'''

if "loadParams" in content:
    print("[INFO] useEffect persistance deja en place")
elif old_detect_marker in content:
    content = content.replace(old_detect_marker, new_with_persist, 1)
    print("[OK] useEffect de chargement + sauvegarde auto ajoutes")
    modifs += 1
else:
    print("[ERREUR] detectParams non trouve")
    sys.exit(1)

# ================================================================
# MOD 3 : Ajouter un indicateur visuel "Sauvegarde..." dans la page Parametres
# On le met juste apres le titre "Parametres"
# ================================================================

old_param_title = '''<h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Paramètres</h2>
          <div style={{ color: "#7a7d92", fontSize: 13 }}>Configurez votre entreprise et vos tarifs par défaut</div>
        </div>'''

new_param_title = '''<h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Paramètres</h2>
          <div style={{ color: "#7a7d92", fontSize: 13, display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            <span>Configurez votre entreprise et vos tarifs par défaut</span>
            {paramsSaving && (
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "#f0c040", fontSize: 12 }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ animation: "spin 1s linear infinite" }}>
                  <path d="M21 12a9 9 0 11-6.219-8.56"/>
                </svg>
                Sauvegarde...
              </span>
            )}
            {!paramsSaving && paramsSavedAt && (
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "#3ecf8e", fontSize: 12 }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                Enregistré
              </span>
            )}
          </div>
        </div>'''

if "paramsSaving && (" in content:
    print("[INFO] Indicateur visuel deja en place")
elif old_param_title in content:
    content = content.replace(old_param_title, new_param_title, 1)
    print("[OK] Indicateur visuel 'Sauvegarde...' / 'Enregistre' ajoute")
    modifs += 1
else:
    print("[WARN] Titre Parametres non trouve exactement")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. States ajoutes : paramsLoaded, paramsSaving, paramsSavedAt, paramsSaveTimerRef")
print("  2. useEffect : charge params depuis Supabase (profiles.params)")
print("  3. useEffect : sauvegarde auto avec debounce 800ms")
print("  4. Indicateur visuel 'Sauvegarde...' (or) puis 'Enregistre' (vert)")
print()
print("COMPORTEMENT :")
print("  - Au demarrage : charge les params, attend que ce soit fini")
print("  - Quand tu modifies un champ : attend 800ms puis sauve dans Supabase")
print("  - Indicator visuel : 'Sauvegarde...' puis 'Enregistre' (3 sec)")
print("  - Si tu refresh la page : les params sont recharges automatiquement")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUP : {backup_name}")
