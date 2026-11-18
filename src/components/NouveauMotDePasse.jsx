// src/components/NouveauMotDePasse.jsx
// Ecran affiche quand on arrive par le lien "mot de passe oublie" recu par e-mail.
// Le lien ouvre une session de recuperation : on choisit le nouveau mot de passe AVANT
// d entrer dans le logiciel. Sans cet ecran, le lien connectait la personne sans jamais
// lui faire changer son mot de passe.

import React, { useState } from "react";
import { supabase } from "../lib/supabase.js";

export default function NouveauMotDePasse({ email, onFini }) {
  const [mdp, setMdp] = useState("");
  const [mdp2, setMdp2] = useState("");
  const [erreur, setErreur] = useState("");
  const [enCours, setEnCours] = useState(false);
  const [fait, setFait] = useState(false);

  const valider = async (e) => {
    e.preventDefault();
    setErreur("");
    if (mdp.length < 12 || /[a-zA-Z]/.test(mdp) === false || /[0-9]/.test(mdp) === false) {
      setErreur("12 caracteres minimum, avec des lettres et des chiffres.");
      return;
    }
    if ((mdp === mdp2) === false) {
      setErreur("Les deux mots de passe ne sont pas identiques.");
      return;
    }
    setEnCours(true);
    const { error } = await supabase.auth.updateUser({ password: mdp });
    setEnCours(false);
    if (error) {
      setErreur("Le mot de passe n'a pas pu etre change : " + error.message);
      return;
    }
    setFait(true);
    // Le lien de recuperation laisse son jeton dans l adresse : on la nettoie.
    window.history.replaceState(null, "", window.location.pathname);
  };

  return (
    <div style={s.page}>
      <div style={s.carte}>
        <div style={s.logo}>DEVIA</div>
        <h1 style={s.titre}>{fait ? "Mot de passe change" : "Nouveau mot de passe"}</h1>
        {fait ? (
          <>
            <p style={s.texte}>Votre nouveau mot de passe est enregistre. Il sert aussi sur le site DEVIA.</p>
            <button type="button" onClick={onFini} style={s.bouton}>Ouvrir DEVIA</button>
          </>
        ) : (
          <form onSubmit={valider}>
            <p style={s.texte}>Compte : <strong>{email}</strong></p>
            <label style={s.label} htmlFor="nmdp1">Nouveau mot de passe</label>
            <input id="nmdp1" type="password" value={mdp} onChange={(e) => setMdp(e.target.value)}
              autoComplete="new-password" placeholder="12 caracteres minimum, lettres et chiffres" style={s.champ} required />
            <label style={s.label} htmlFor="nmdp2">Confirmer le mot de passe</label>
            <input id="nmdp2" type="password" value={mdp2} onChange={(e) => setMdp2(e.target.value)}
              autoComplete="new-password" style={s.champ} required />
            {erreur === "" ? null : <div style={s.erreur}>{erreur}</div>}
            <button type="submit" disabled={enCours} style={s.bouton}>
              {enCours ? "Enregistrement..." : "Enregistrer le mot de passe"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

const s = {
  page: {
    minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
    background: "#1a1a2e", fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", padding: 16,
  },
  carte: {
    width: "100%", maxWidth: 400, background: "#fff", borderRadius: 14, padding: "32px 28px",
    boxShadow: "0 12px 40px rgba(0,0,0,0.35)",
  },
  logo: { fontWeight: 800, fontSize: 22, letterSpacing: 1, color: "#1a1a2e", marginBottom: 6 },
  titre: { fontSize: 18, fontWeight: 600, color: "#1a1a2e", margin: "0 0 18px" },
  texte: { fontSize: 14, color: "#555", lineHeight: 1.5, margin: "0 0 16px" },
  label: { display: "block", fontSize: 13, color: "#555", marginBottom: 6 },
  champ: {
    width: "100%", boxSizing: "border-box", padding: "11px 12px", fontSize: 15, border: "1px solid #d0d0d8",
    borderRadius: 8, marginBottom: 14,
  },
  erreur: { fontSize: 13, color: "#c33", margin: "0 0 12px" },
  bouton: {
    width: "100%", padding: "12px 0", fontSize: 15, fontWeight: 600, color: "#fff", background: "#4a6cf7",
    border: "none", borderRadius: 8, cursor: "pointer",
  },
};
