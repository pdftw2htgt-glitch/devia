// src/hooks/useAuth.js
// Hook React pour suivre l'etat de connexion de l'utilisateur

import { useState, useEffect } from "react";
import { supabase } from "../lib/supabase.js";

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  // Arrivee par le lien "mot de passe oublie" : l adresse porte type=recovery tant que
  // Supabase ne l a pas lue, puis il emet PASSWORD_RECOVERY. On guette les deux.
  const [recovery, setRecovery] = useState(() =>
    (typeof window === "undefined") ? false : window.location.hash.indexOf("type=recovery") >= 0);

  useEffect(() => {
    // Recupere la session actuelle au chargement
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session ? session.user : null);
      setLoading(false);
    });

    // Ecoute les changements d'authentification (login, logout, refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (event === "PASSWORD_RECOVERY") setRecovery(true);
        setUser(session ? session.user : null);
        setLoading(false);
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  return { user, loading, recovery, finRecovery: () => setRecovery(false) };
}
