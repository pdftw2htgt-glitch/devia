#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Micro-etape 2.3b : Frontend du systeme de licence

Ce script cree :
  1. src/lib/license.js               -> Helpers pour check_my_license & activate_my_license
  2. src/hooks/useLicense.js          -> Hook React pour suivre l'etat de la licence
  3. src/components/ActivateLicense.jsx -> Ecran "Entre ta cle de licence"
  4. src/components/SubscriptionBanner.jsx -> Bandeau "Abonnement expire"
  5. src/components/UserMenu.jsx      -> Menu en haut a droite avec Deconnexion

Il modifie :
  - devia.jsx (racine) : ajoute le gate de licence apres le gate d'auth
                          + bandeau abonnement + menu utilisateur

A lancer depuis ~/Desktop/devia :
    python3 setup_license.py
"""

import os
import sys
import shutil
from datetime import datetime

# --- Verifications ---
if not os.path.exists("package.json"):
    print("ERREUR : package.json introuvable.")
    print("Lance ce script depuis ~/Desktop/devia")
    sys.exit(1)

if not os.path.exists("src/hooks/useAuth.js"):
    print("ERREUR : src/hooks/useAuth.js introuvable.")
    print("La micro-etape 2.2 doit avoir ete faite avant.")
    sys.exit(1)

print("Setup du systeme de licence DEVIA (2.3b)...")
print()

# --- 1. src/lib/license.js ---
license_js = '''// src/lib/license.js
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
'''

with open("src/lib/license.js", "w", encoding="utf-8") as f:
    f.write(license_js)
print("[OK] src/lib/license.js cree")

# --- 2. src/hooks/useLicense.js ---
useLicense_js = '''// src/hooks/useLicense.js
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
'''

with open("src/hooks/useLicense.js", "w", encoding="utf-8") as f:
    f.write(useLicense_js)
print("[OK] src/hooks/useLicense.js cree")

# --- 3. src/components/ActivateLicense.jsx ---
activate_jsx = '''// src/components/ActivateLicense.jsx
// Ecran d'activation de licence (affiche quand user connecte mais sans licence)

import React, { useState } from "react";
import { activateLicense } from "../lib/license.js";
import { signOut } from "../lib/auth.js";

export default function ActivateLicense({ onActivated, userEmail }) {
  const [key, setKey] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!key.trim()) {
      setError("Merci d'entrer ta cle de licence.");
      return;
    }

    setLoading(true);
    try {
      const result = await activateLicense(key);
      if (result.success) {
        // Succes : on previent le parent qui va refresh la licence
        if (onActivated) onActivated();
      } else {
        setError(result.message || "Erreur lors de l'activation.");
      }
    } catch (err) {
      setError("Erreur inattendue : " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await signOut();
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <div style={styles.logo}>DEVIA</div>
        <div style={styles.subtitle}>Activation de licence</div>

        <div style={styles.userBox}>
          Connecte en tant que <strong>{userEmail}</strong>
          <button onClick={handleLogout} style={styles.logoutLink}>
            (se deconnecter)
          </button>
        </div>

        <p style={styles.description}>
          Ton compte est cree, mais aucune licence DEVIA n'y est associee.
          Entre la cle de licence recue lors de ton achat pour acceder au logiciel.
        </p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Cle de licence</label>
          <input
            type="text"
            value={key}
            onChange={(e) => setKey(e.target.value.toUpperCase())}
            placeholder="DEVIA-2026-XXXX-XXXX-XXXX"
            style={styles.input}
            autoFocus
            required
          />

          {error && <div style={styles.error}>{error}</div>}

          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? "Verification..." : "Activer ma licence"}
          </button>
        </form>

        <div style={styles.help}>
          <strong>Pas encore de cle ?</strong> La cle t'a ete envoyee par email apres ton achat.
          Si tu ne la trouves pas, verifie tes spams ou contacte le support.
        </div>

        <div style={styles.footer}>
          DEVIA &copy; 2026 &mdash; Tous droits reserves
        </div>
      </div>
    </div>
  );
}

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
    maxWidth: "480px",
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
    marginBottom: "24px",
  },
  userBox: {
    background: "#f5f5f5",
    padding: "10px 14px",
    borderRadius: "8px",
    fontSize: "13px",
    color: "#555",
    textAlign: "center",
    marginBottom: "20px",
  },
  logoutLink: {
    background: "none",
    border: "none",
    color: "#4a6cf7",
    fontSize: "12px",
    cursor: "pointer",
    textDecoration: "underline",
    marginLeft: "6px",
    padding: 0,
  },
  description: {
    fontSize: "14px",
    color: "#555",
    lineHeight: "1.5",
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
  },
  input: {
    padding: "14px",
    fontSize: "16px",
    fontFamily: "Menlo, Monaco, Courier New, monospace",
    border: "1px solid #ddd",
    borderRadius: "8px",
    outline: "none",
    textAlign: "center",
    letterSpacing: "1px",
  },
  button: {
    marginTop: "16px",
    padding: "14px",
    fontSize: "15px",
    fontWeight: "600",
    color: "#fff",
    background: "#1a1a2e",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
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
  help: {
    marginTop: "24px",
    padding: "12px 14px",
    background: "#f0f7ff",
    border: "1px solid #cfe2ff",
    borderRadius: "8px",
    fontSize: "12px",
    color: "#456",
    lineHeight: "1.5",
  },
  footer: {
    marginTop: "30px",
    fontSize: "11px",
    color: "#aaa",
    textAlign: "center",
  },
};
'''

with open("src/components/ActivateLicense.jsx", "w", encoding="utf-8") as f:
    f.write(activate_jsx)
print("[OK] src/components/ActivateLicense.jsx cree")

# --- 4. src/components/SubscriptionBanner.jsx ---
banner_jsx = '''// src/components/SubscriptionBanner.jsx
// Bandeau en haut de l'app si abonnement expire ou problemes

import React from "react";

export default function SubscriptionBanner({ license }) {
  if (!license || license.status !== "ok") return null;

  // Cas 1 : abonnement expire
  if (!license.subscription_valid && license.subscription_status !== "none") {
    return (
      <div style={styles.warning}>
        <strong>Abonnement de maintenance expire</strong>
        {" "}&mdash; Tu utilises la version {license.max_version}.
        Renouvelle ton abonnement pour acceder aux derniers updates et corrections.
      </div>
    );
  }

  // Cas 2 : jamais eu d'abonnement, mais une nouvelle version existe
  if (license.subscription_status === "none" && license.has_updates_available) {
    return (
      <div style={styles.info}>
        Une nouvelle version de DEVIA est disponible (v{license.latest_version}).
        Souscris a un abonnement de maintenance pour y acceder.
      </div>
    );
  }

  // Cas 3 : tout va bien, pas de bandeau
  return null;
}

const styles = {
  warning: {
    background: "#fff3cd",
    color: "#856404",
    borderBottom: "1px solid #ffeaa7",
    padding: "10px 20px",
    fontSize: "13px",
    textAlign: "center",
    fontFamily: "-apple-system, sans-serif",
  },
  info: {
    background: "#e7f3ff",
    color: "#004085",
    borderBottom: "1px solid #b8daff",
    padding: "10px 20px",
    fontSize: "13px",
    textAlign: "center",
    fontFamily: "-apple-system, sans-serif",
  },
};
'''

with open("src/components/SubscriptionBanner.jsx", "w", encoding="utf-8") as f:
    f.write(banner_jsx)
print("[OK] src/components/SubscriptionBanner.jsx cree")

# --- 5. src/components/UserMenu.jsx ---
usermenu_jsx = '''// src/components/UserMenu.jsx
// Petit menu en haut a droite avec info user + bouton deconnexion

import React, { useState } from "react";
import { signOut } from "../lib/auth.js";

export default function UserMenu({ user, license }) {
  const [open, setOpen] = useState(false);

  const handleLogout = async () => {
    if (confirm("Se deconnecter de DEVIA ?")) {
      await signOut();
    }
  };

  const initials = (user?.email || "?")
    .split("@")[0]
    .slice(0, 2)
    .toUpperCase();

  return (
    <div style={styles.wrapper}>
      <button onClick={() => setOpen(!open)} style={styles.trigger}>
        <div style={styles.avatar}>{initials}</div>
      </button>

      {open && (
        <>
          <div style={styles.overlay} onClick={() => setOpen(false)} />
          <div style={styles.menu}>
            <div style={styles.email}>{user?.email}</div>
            {license?.license_key && (
              <div style={styles.license}>
                Licence : <span style={styles.licenseKey}>{license.license_key}</span>
              </div>
            )}
            {license?.max_version && (
              <div style={styles.version}>Version {license.max_version}</div>
            )}
            <div style={styles.divider} />
            <button onClick={handleLogout} style={styles.logoutBtn}>
              Se deconnecter
            </button>
          </div>
        </>
      )}
    </div>
  );
}

const styles = {
  wrapper: {
    position: "fixed",
    top: "16px",
    right: "16px",
    zIndex: 1000,
    fontFamily: "-apple-system, sans-serif",
  },
  trigger: {
    background: "none",
    border: "none",
    padding: 0,
    cursor: "pointer",
  },
  avatar: {
    width: "40px",
    height: "40px",
    borderRadius: "50%",
    background: "#1a1a2e",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "600",
    fontSize: "14px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
  },
  overlay: {
    position: "fixed",
    inset: 0,
    zIndex: 999,
  },
  menu: {
    position: "absolute",
    top: "50px",
    right: 0,
    background: "#fff",
    borderRadius: "10px",
    padding: "16px",
    minWidth: "260px",
    boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
    border: "1px solid #eee",
    zIndex: 1001,
  },
  email: {
    fontSize: "14px",
    fontWeight: "600",
    color: "#1a1a2e",
    marginBottom: "8px",
    wordBreak: "break-all",
  },
  license: {
    fontSize: "12px",
    color: "#666",
    marginBottom: "4px",
  },
  licenseKey: {
    fontFamily: "Menlo, monospace",
    fontSize: "11px",
    color: "#1a1a2e",
    fontWeight: "600",
  },
  version: {
    fontSize: "11px",
    color: "#888",
  },
  divider: {
    height: "1px",
    background: "#eee",
    margin: "12px -16px",
  },
  logoutBtn: {
    width: "100%",
    padding: "10px",
    background: "#f5f5f5",
    border: "1px solid #ddd",
    borderRadius: "6px",
    fontSize: "13px",
    color: "#c33",
    cursor: "pointer",
    fontWeight: "600",
  },
};
'''

with open("src/components/UserMenu.jsx", "w", encoding="utf-8") as f:
    f.write(usermenu_jsx)
print("[OK] src/components/UserMenu.jsx cree")

# --- 6. Patch devia.jsx ---
print()
print("Patching devia.jsx pour integrer le gate de licence...")

# Backup
backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_2.3b"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Ajouter les nouveaux imports apres les imports existants de la 2.2
new_imports = '''import { useLicense } from "./src/hooks/useLicense.js";
import ActivateLicense from "./src/components/ActivateLicense.jsx";
import SubscriptionBanner from "./src/components/SubscriptionBanner.jsx";
import UserMenu from "./src/components/UserMenu.jsx";
'''

# On cherche la ligne import Login et on ajoute nos imports juste apres le dernier import de 2.2
marker = 'import { signOut } from "./src/lib/auth.js";'
if marker in content:
    content = content.replace(marker, marker + "\n" + new_imports.rstrip())
    print("[OK] Nouveaux imports ajoutes")
else:
    print("ATTENTION : marqueur d'import introuvable. Patch imports non applique.")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

# 2. Remplacer le wrapper DeviaAuthGate de la 2.2 par une version etendue qui gere aussi la licence
old_wrapper = '''function DeviaAuthGate() {
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
}'''

new_wrapper = '''function DeviaAuthGate() {
  const { user, loading: authLoading } = useAuth();
  const { license, loading: licenseLoading, refresh: refreshLicense } = useLicense();

  // Spinner pendant le chargement initial
  if (authLoading || (user && licenseLoading)) {
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

  // Pas connecte -> ecran login
  if (!user) {
    return <Login />;
  }

  // Connecte mais pas de licence -> ecran d'activation
  if (!license || license.status === "no_license") {
    return (
      <ActivateLicense
        userEmail={user.email}
        onActivated={refreshLicense}
      />
    );
  }

  // Tout est OK : afficher l'app avec bandeau abonnement + menu user
  return (
    <>
      <SubscriptionBanner license={license} />
      <UserMenu user={user} license={license} />
      <DeviaMain />
    </>
  );
}'''

if old_wrapper in content:
    content = content.replace(old_wrapper, new_wrapper)
    print("[OK] Wrapper DeviaAuthGate mis a jour pour le gate de licence")
else:
    print("ATTENTION : wrapper DeviaAuthGate introuvable.")
    print("Le fichier devia.jsx a peut-etre ete modifie manuellement entre 2.2 et 2.3b.")
    shutil.copy(backup_name, "devia.jsx")
    sys.exit(1)

# Sauvegarde
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("Micro-etape 2.3b : fichiers crees et devia.jsx patche !")
print("=" * 60)
print()
print("NOUVELLE STRUCTURE :")
print("  src/lib/supabase.js       (existant)")
print("  src/lib/auth.js           (existant)")
print("  src/lib/license.js        (NOUVEAU)")
print("  src/hooks/useAuth.js      (existant)")
print("  src/hooks/useLicense.js   (NOUVEAU)")
print("  src/components/Login.jsx           (existant)")
print("  src/components/ActivateLicense.jsx (NOUVEAU)")
print("  src/components/SubscriptionBanner.jsx (NOUVEAU)")
print("  src/components/UserMenu.jsx        (NOUVEAU)")
print("  devia.jsx                 (MODIFIE : gate de licence ajoute)")
print()
print("PROCHAINE COMMANDE : npm run dev")
print("  -> Connecte-toi")
print("  -> Tu verras l'ecran 'Activation de licence'")
print("  -> Colle ta cle de test : DEVIA-2026-L5V8-28SS-5774")
print("  -> Tu devrais acceder a DEVIA avec menu user en haut a droite")
