// src/components/LicenceExpiree.jsx
// Ecran affiche quand une licence TEMPORAIRE est arrivee a echeance.
//
// RIEN N EST SUPPRIME : le compte, la cle et les projets restent en base. Il suffit de
// repousser subscription_expires_at pour que l acces revienne au prochain chargement.
// C est la difference avec l ancienne "seule coupure possible", qui etait d effacer la
// ligne de licences - et qui faisait perdre le rattachement de la cle au compte.

import React from "react";
import { signOut } from "../lib/auth.js";

export default function LicenceExpiree({ userEmail, echeance, cle }) {
  let dateLisible = "";
  try {
    dateLisible = new Date(echeance).toLocaleDateString("fr-FR", {
      day: "numeric", month: "long", year: "numeric",
    });
  } catch (e) {
    dateLisible = "";
  }

  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <div style={styles.logo}>DEVIA</div>
        <div style={styles.subtitle}>Devis de charpente assistes par IA</div>

        <div style={styles.bandeau}>Votre licence temporaire a expire</div>

        <p style={styles.texte}>
          L acces d essai rattache a ce compte a pris fin
          {dateLisible === "" ? "" : " le " + dateLisible}.
        </p>
        <p style={styles.texte}>
          Votre compte, vos projets et vos devis sont conserves : rien n a ete supprime.
          Ils vous sont rendus des la reactivation de la licence.
        </p>
        <p style={styles.texteFort}>
          Contactez DEVIA pour prolonger votre essai ou souscrire.
        </p>

        <div style={styles.userBox}>
          {userEmail}{cle === undefined || cle === null || cle === "" ? "" : " - " + cle}
        </div>

        <button style={styles.lien} onClick={() => { signOut(); }}>
          Se deconnecter
        </button>
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
  bandeau: {
    background: "#fdf0e3",
    border: "1px solid #f0c040",
    color: "#8a5a00",
    borderRadius: "10px",
    padding: "14px 16px",
    fontSize: "16px",
    fontWeight: "700",
    textAlign: "center",
    marginBottom: "20px",
  },
  texte: {
    fontSize: "14px",
    lineHeight: "1.6",
    color: "#555",
    textAlign: "center",
    margin: "0 0 12px 0",
  },
  texteFort: {
    fontSize: "14px",
    lineHeight: "1.6",
    color: "#1a1a2e",
    fontWeight: "600",
    textAlign: "center",
    margin: "0 0 20px 0",
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
  lien: {
    display: "block",
    width: "100%",
    background: "transparent",
    border: "none",
    color: "#888",
    fontSize: "13px",
    cursor: "pointer",
    padding: "8px",
  },
};
