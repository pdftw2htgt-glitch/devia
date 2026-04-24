// src/components/Login.jsx
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
