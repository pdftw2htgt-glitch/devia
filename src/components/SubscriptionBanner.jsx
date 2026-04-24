// src/components/SubscriptionBanner.jsx
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
