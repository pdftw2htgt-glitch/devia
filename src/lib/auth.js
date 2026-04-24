// src/lib/auth.js
// Helpers d'authentification Supabase pour DEVIA

import { supabase } from "./supabase.js";

/**
 * Inscription d'un nouvel utilisateur
 * Supabase enverra automatiquement un email de confirmation
 */
export async function signUp(email, password) {
  const { data, error } = await supabase.auth.signUp({
    email: email.trim().toLowerCase(),
    password: password,
  });
  return { data, error };
}

/**
 * Connexion d'un utilisateur existant
 */
export async function signIn(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email: email.trim().toLowerCase(),
    password: password,
  });
  return { data, error };
}

/**
 * Deconnexion de l'utilisateur courant
 */
export async function signOut() {
  const { error } = await supabase.auth.signOut();
  return { error };
}

/**
 * Envoi d'un email de reinitialisation de mot de passe
 */
export async function resetPassword(email) {
  const { data, error } = await supabase.auth.resetPasswordForEmail(
    email.trim().toLowerCase()
  );
  return { data, error };
}

/**
 * Recupere l'utilisateur actuellement connecte (ou null)
 */
export async function getCurrentUser() {
  const { data: { user } } = await supabase.auth.getUser();
  return user;
}
