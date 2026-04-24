// src/components/ActivateLicense.jsx
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
