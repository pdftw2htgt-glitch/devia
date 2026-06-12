#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Micro-etape 2.2 : Systeme de login Supabase Auth

Ce script cree :
  1. src/lib/auth.js         -> Helpers Supabase Auth (signIn, signUp, signOut)
  2. src/hooks/useAuth.js    -> Hook React pour suivre l'etat de connexion
  3. src/components/Login.jsx -> Composant ecran de login / inscription

Il modifie :
  - devia.jsx (racine) : ajoute le gate de login en haut du composant

A lancer depuis ~/Desktop/devia :
    python3 setup_login.py
"""

import os
import sys
import shutil
from datetime import datetime

# --- Verifications prealables ---
if not os.path.exists("package.json"):
    print("ERREUR : package.json introuvable.")
    print("Lance ce script depuis ~/Desktop/devia")
    sys.exit(1)

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable a la racine.")
    sys.exit(1)

if not os.path.exists("src/lib/supabase.js"):
    print("ERREUR : src/lib/supabase.js introuvable.")
    print("La micro-etape 2.1 doit avoir ete faite avant.")
    sys.exit(1)

print("Setup du systeme de login DEVIA...")
print()

# --- Creer les dossiers necessaires ---
os.makedirs("src/hooks", exist_ok=True)
os.makedirs("src/components", exist_ok=True)
print("[OK] Dossiers src/hooks/ et src/components/ crees")

# --- 1. src/lib/auth.js ---
auth_js = '''// src/lib/auth.js
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
'''

with open("src/lib/auth.js", "w", encoding="utf-8") as f:
    f.write(auth_js)
print("[OK] src/lib/auth.js cree")

# --- 2. src/hooks/useAuth.js ---
useauth_js = '''// src/hooks/useAuth.js
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
'''

with open("src/hooks/useAuth.js", "w", encoding="utf-8") as f:
    f.write(useauth_js)
print("[OK] src/hooks/useAuth.js cree")

# --- 3. src/components/Login.jsx ---
login_jsx = '''// src/components/Login.jsx
// Ecran de connexion / inscription pour DEVIA

import React, { useState } from "react";
import { signIn, signUp, resetPassword } from "../lib/auth.js";

export default function Login() {
  const [mode, setMode] = useState("signin"); // "signin" | "signup" | "reset"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setInfo("");

    if (!email || (mode !== "reset" && !password)) {
      setError("Merci de remplir tous les champs.");
      return;
    }

    if (mode === "signup" && password.length < 8) {
      setError("Le mot de passe doit faire au moins 8 caracteres.");
      return;
    }

    setLoading(true);

    try {
      if (mode === "signin") {
        const { error } = await signIn(email, password);
        if (error) {
          if (error.message.includes("Invalid login")) {
            setError("Email ou mot de passe incorrect.");
          } else if (error.message.includes("Email not confirmed")) {
            setError("Email non confirme. Verifie ta boite mail.");
          } else {
            setError(error.message);
          }
        }
        // Si succes : le hook useAuth detectera le changement et affichera DEVIA
      } else if (mode === "signup") {
        const { error } = await signUp(email, password);
        if (error) {
          if (error.message.includes("already registered")) {
            setError("Cet email est deja inscrit. Essaye de te connecter.");
          } else {
            setError(error.message);
          }
        } else {
          setInfo("Compte cree ! Verifie ta boite mail pour confirmer ton adresse, puis connecte-toi.");
          setMode("signin");
        }
      } else if (mode === "reset") {
        const { error } = await resetPassword(email);
        if (error) {
          setError(error.message);
        } else {
          setInfo("Email de reinitialisation envoye. Verifie ta boite mail.");
        }
      }
    } catch (err) {
      setError("Erreur inattendue : " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const title = mode === "signin" ? "Connexion" : mode === "signup" ? "Creer un compte" : "Mot de passe oublie";
  const buttonLabel = mode === "signin" ? "Se connecter" : mode === "signup" ? "Creer mon compte" : "Envoyer le lien";

  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <div style={styles.logo}>DEVIA</div>
        <div style={styles.subtitle}>Logiciel professionnel de devis charpente</div>

        <h2 style={styles.title}>{title}</h2>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="votre@email.com"
            style={styles.input}
            autoComplete="email"
            required
          />

          {mode !== "reset" && (
            <>
              <label style={styles.label}>Mot de passe</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={mode === "signup" ? "Minimum 8 caracteres" : ""}
                style={styles.input}
                autoComplete={mode === "signup" ? "new-password" : "current-password"}
                required
              />
            </>
          )}

          {error && <div style={styles.error}>{error}</div>}
          {info && <div style={styles.info}>{info}</div>}

          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? "Chargement..." : buttonLabel}
          </button>
        </form>

        <div style={styles.links}>
          {mode === "signin" && (
            <>
              <button type="button" onClick={() => { setMode("signup"); setError(""); setInfo(""); }} style={styles.linkBtn}>
                Pas encore de compte ? Creer un compte
              </button>
              <button type="button" onClick={() => { setMode("reset"); setError(""); setInfo(""); }} style={styles.linkBtn}>
                Mot de passe oublie ?
              </button>
            </>
          )}
          {mode === "signup" && (
            <button type="button" onClick={() => { setMode("signin"); setError(""); setInfo(""); }} style={styles.linkBtn}>
              Deja un compte ? Se connecter
            </button>
          )}
          {mode === "reset" && (
            <button type="button" onClick={() => { setMode("signin"); setError(""); setInfo(""); }} style={styles.linkBtn}>
              Retour a la connexion
            </button>
          )}
        </div>

        <div style={styles.footer}>
          DEVIA &copy; 2026 &mdash; Tous droits reserves
        </div>
      </div>
    </div>
  );
}

// Styles inline (pas besoin de CSS externe)
const styles = {
  wrapper: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
    padding: "20px",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  },
  card: {
    background: "#ffffff",
    borderRadius: "16px",
    padding: "40px",
    width: "100%",
    maxWidth: "420px",
    boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
  },
  logo: {
    fontSize: "32px",
    fontWeight: "800",
    textAlign: "center",
    color: "#1a1a2e",
    letterSpacing: "2px",
  },
  subtitle: {
    fontSize: "13px",
    textAlign: "center",
    color: "#888",
    marginTop: "4px",
    marginBottom: "32px",
  },
  title: {
    fontSize: "22px",
    fontWeight: "600",
    color: "#1a1a2e",
    marginBottom: "20px",
    textAlign: "center",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "6px",
  },
  label: {
    fontSize: "13px",
    fontWeight: "600",
    color: "#555",
    marginTop: "12px",
  },
  input: {
    padding: "12px 14px",
    fontSize: "15px",
    border: "1px solid #ddd",
    borderRadius: "8px",
    outline: "none",
    transition: "border-color 0.2s",
  },
  button: {
    marginTop: "20px",
    padding: "14px",
    fontSize: "15px",
    fontWeight: "600",
    color: "#fff",
    background: "#1a1a2e",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    transition: "background 0.2s",
  },
  error: {
    marginTop: "12px",
    padding: "10px 14px",
    background: "#fee",
    color: "#c33",
    fontSize: "13px",
    borderRadius: "6px",
    border: "1px solid #fcc",
  },
  info: {
    marginTop: "12px",
    padding: "10px 14px",
    background: "#efe",
    color: "#2a7",
    fontSize: "13px",
    borderRadius: "6px",
    border: "1px solid #cfc",
  },
  links: {
    marginTop: "20px",
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    alignItems: "center",
  },
  linkBtn: {
    background: "none",
    border: "none",
    color: "#4a6cf7",
    fontSize: "13px",
    cursor: "pointer",
    textDecoration: "underline",
    padding: "4px",
  },
  footer: {
    marginTop: "30px",
    fontSize: "11px",
    color: "#aaa",
    textAlign: "center",
  },
};
'''

with open("src/components/Login.jsx", "w", encoding="utf-8") as f:
    f.write(login_jsx)
print("[OK] src/components/Login.jsx cree")

# --- 4. Patch de devia.jsx pour brancher le login ---
print()
print("Patching devia.jsx pour integrer le gate de login...")

# Backup du fichier au cas ou
backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# Detection : le fichier utilise export default function Devia() ? export default Devia ? const Devia = ?
# On cherche les imports existants pour savoir ou ajouter les notres
# et on cherche le debut du composant pour injecter le gate

# Strategie : ajouter nos imports juste apres le dernier import React existant
import_block = '''import { useAuth } from "./src/hooks/useAuth.js";
import Login from "./src/components/Login.jsx";
import { signOut } from "./src/lib/auth.js";
'''

# Cherche la derniere ligne d'import au debut du fichier
lines = content.split("\n")
last_import_idx = -1
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("import "):
        last_import_idx = i
    elif stripped and not stripped.startswith("//") and not stripped.startswith("/*"):
        # Premiere ligne non-import, non-commentaire, non-vide -> on s'arrete
        if last_import_idx >= 0:
            break

if last_import_idx < 0:
    print("ERREUR : Aucun import React trouve dans devia.jsx")
    print("Restauration du backup...")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

# Injecte nos imports apres le dernier import existant
lines.insert(last_import_idx + 1, import_block.rstrip())
content = "\n".join(lines)

# Maintenant : injecter le gate AU DEBUT du composant principal
# On cherche "export default function Devia" ou "function Devia(" ou "const Devia ="
# Strategie simple : on wrappe tout le composant dans un gate.
# Pour ne pas casser la structure du composant, on cree un wrapper DeviaApp
# qui gere le gate, et on renomme l'existant en DeviaMain.

# Plus simple encore : on cherche la premiere occurrence de "export default" et on
# insere notre logique juste apres. Mais c'est risque.

# Approche ROBUSTE : on cree un NOUVEAU default export a la fin qui wrappe l'existant.
# On cherche "export default function Devia" ou "export default Devia"

wrapper_code = '''

// ============================================================
// DEVIA - Gate d'authentification (Micro-etape 2.2)
// Ce wrapper affiche Login si l'utilisateur n'est pas connecte.
// Il ne verifie PAS encore la licence (c'est la micro-etape 2.3).
// ============================================================

function DeviaAuthGate() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#1a1a2e",
        color: "#fff",
        fontFamily: "-apple-system, sans-serif",
        fontSize: "14px",
      }}>
        Chargement...
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return <DeviaMain />;
}
'''

# On cherche "export default function Devia(" ou "export default Devia" ou equivalent
# et on renomme Devia -> DeviaMain, puis on ajoute notre wrapper, puis un nouveau export default

renamed = False

# Cas 1 : export default function Devia() { ... }
if "export default function Devia(" in content:
    content = content.replace(
        "export default function Devia(",
        "function DeviaMain("
    )
    content += wrapper_code
    content += "\nexport default DeviaAuthGate;\n"
    renamed = True
    print("[OK] Pattern 'export default function Devia' detecte et patche")

# Cas 2 : function Devia() { ... } puis plus loin : export default Devia;
elif "export default Devia;" in content and "function Devia(" in content:
    content = content.replace("function Devia(", "function DeviaMain(")
    content = content.replace("export default Devia;", "export default DeviaAuthGate;")
    content += wrapper_code
    renamed = True
    print("[OK] Pattern 'function Devia + export default Devia' detecte et patche")

# Cas 3 : const Devia = () => { ... } puis export default Devia;
elif "const Devia =" in content and "export default Devia;" in content:
    content = content.replace("const Devia =", "const DeviaMain =")
    content = content.replace("export default Devia;", "export default DeviaAuthGate;")
    content += wrapper_code
    renamed = True
    print("[OK] Pattern 'const Devia + export default Devia' detecte et patche")

# Cas 4 : export default function sans nom explicite
elif "export default function" in content and "Devia" not in content:
    # Remplacer export default function par function DeviaMain
    content = content.replace("export default function", "function DeviaMain", 1)
    content += wrapper_code
    content += "\nexport default DeviaAuthGate;\n"
    renamed = True
    print("[OK] Pattern 'export default function (anonyme)' detecte et patche")

if not renamed:
    print()
    print("ATTENTION : Impossible de detecter automatiquement le pattern du composant principal.")
    print("Aucune modification appliquee a devia.jsx.")
    print()
    print("Tu devras modifier le fichier manuellement. Cherche la ligne qui contient")
    print("'export default' avec 'Devia' et envoie-la a Claude pour un patch manuel.")
    # On ne sauvegarde pas, et on garde le backup
else:
    with open("devia.jsx", "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] devia.jsx patche avec succes")

print()
print("=" * 60)
print("Micro-etape 2.2 : fichiers crees !")
print("=" * 60)
print()
print("STRUCTURE RESULTANTE :")
print("  src/lib/supabase.js       (deja existant)")
print("  src/lib/auth.js           (NOUVEAU)")
print("  src/hooks/useAuth.js      (NOUVEAU)")
print("  src/components/Login.jsx  (NOUVEAU)")
print("  devia.jsx                 (MODIFIE : gate d'auth ajoute)")
print(f"  {backup_name} (backup de devia.jsx avant modif)")
print()
print("PROCHAINE COMMANDE : npm run dev")
print("  -> Doit afficher l'ecran de login au lieu de l'app DEVIA")
