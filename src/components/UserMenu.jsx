// src/components/UserMenu.jsx
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
