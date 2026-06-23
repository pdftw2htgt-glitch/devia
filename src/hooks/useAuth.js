// src/hooks/useAuth.js
// Hook React pour suivre l'etat de connexion de l'utilisateur

import { useState, useEffect } from "react";
import { supabase } from "../lib/supabase.js";

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Recupere la session actuelle au chargement
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session ? session.user : null);
      setLoading(false);
    });

    // Ecoute les changements d'authentification (login, logout, refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session ? session.user : null);
        setLoading(false);
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  return { user, loading };
}
