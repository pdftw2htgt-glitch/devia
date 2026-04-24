// src/lib/license.js
// Helpers pour interroger l'etat de la licence et activer une cle
// Utilise les fonctions SQL Supabase : check_my_license() et activate_my_license()

import { supabase } from "./supabase.js";

/**
 * Recupere l'etat de la licence de l'utilisateur connecte
 * Retourne un objet avec :
 *  - status : 'unauthenticated' | 'no_license' | 'ok'
 *  - license_key, installed_version, max_version, latest_version
 *  - subscription_status, subscription_type, subscription_expires_at
 *  - subscription_valid (boolean)
 *  - has_updates_available (boolean)
 */
export async function checkMyLicense() {
  const { data, error } = await supabase.rpc("check_my_license");
  if (error) {
    console.error("checkMyLicense error:", error);
    return { status: "error", error: error.message };
  }
  return data;
}

/**
 * Active une cle de licence pour l'utilisateur connecte
 * La cle passe d'orpheline (user_id NULL) a liee au user courant
 */
export async function activateLicense(key) {
  const cleanKey = (key || "").trim().toUpperCase();
  const { data, error } = await supabase.rpc("activate_my_license", {
    p_key: cleanKey,
  });
  if (error) {
    console.error("activateLicense error:", error);
    return { success: false, error: error.message };
  }
  return data;
}
