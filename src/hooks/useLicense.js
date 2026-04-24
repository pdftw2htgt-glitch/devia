// src/hooks/useLicense.js
// Hook React pour suivre l'etat de la licence en temps reel

import { useState, useEffect, useCallback } from "react";
import { checkMyLicense } from "../lib/license.js";
import { supabase } from "../lib/supabase.js";

export function useLicense() {
  const [license, setLicense] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    const result = await checkMyLicense();
    setLicense(result);
    setLoading(false);
  }, []);

  useEffect(() => {
    refresh();

    // Recharge la licence quand l'auth change (login/logout)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(() => {
      refresh();
    });

    return () => subscription.unsubscribe();
  }, [refresh]);

  return { license, loading, refresh };
}
