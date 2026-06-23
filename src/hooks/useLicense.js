// src/hooks/useLicense.js
// Hook React pour suivre l'etat de la licence en temps reel

import { useState, useEffect, useCallback } from "react";
import { checkMyLicense } from "../lib/license.js";
import { supabase } from "../lib/supabase.js";

export function useLicense() {
  const [license, setLicense] = useState(null);
  const [loading, setLoading] = useState(true);

  // refresh avec option silencieuse : silent=true ne touche pas a "loading"
  // (evite de demonter l'app a chaque refresh de token / passage plein ecran)
  const refresh = useCallback(async (silent) => {
    if (!silent) setLoading(true);
    const result = await checkMyLicense();
    setLicense(result);
    if (!silent) setLoading(false);
  }, []);

  useEffect(() => {
    // chargement initial : avec loading
    refresh();

    // Changements d'auth ulterieurs : refresh SILENCIEUX (ne demonte pas l'app)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event) => {
      console.log("[DEVIA LICENSE] event =", event);
      if (event === "SIGNED_IN" || event === "SIGNED_OUT") {
        refresh();
      } else {
        refresh(true);
      }
    });

    return () => subscription.unsubscribe();
  }, [refresh]);

  return { license, loading, refresh };
}
