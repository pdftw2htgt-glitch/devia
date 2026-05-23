// src/components/UserMenu.jsx
// Avatar + menu user integre dans le header DEVIA (style liquid glass)

import React, { useState, useEffect, useRef } from "react";
import { signOut } from "../lib/auth.js";

export default function UserMenu({ user, license, avatarUrl }) {
  const [open, setOpen] = useState(false);
  const [confirmLogout, setConfirmLogout] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    const t = setTimeout(() => document.addEventListener("click", handler), 50);
    return () => {
      clearTimeout(t);
      document.removeEventListener("click", handler);
    };
  }, [open]);

  const handleLogout = async () => {
    setOpen(false);
    setConfirmLogout(false);
    await signOut();
  };

  const initials = (user?.email || "?")
    .split("@")[0]
    .slice(0, 2)
    .toUpperCase();

  return (
    <>
      <div ref={menuRef} style={{ position: "relative" }}>
        <button onClick={() => setOpen(!open)} title="Mon compte"
          style={{
            background: avatarUrl ? "transparent" : "linear-gradient(135deg, rgba(240, 192, 64, 0.9) 0%, rgba(224, 160, 32, 0.9) 100%)",
            border: avatarUrl ? "2px solid rgba(240, 192, 64, 0.5)" : "1px solid rgba(255, 255, 255, 0.1)",
            color: "#0a0a0a",
            width: 34,
            height: 34,
            borderRadius: "50%",
            cursor: "pointer",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 700,
            fontSize: 12,
            letterSpacing: "0.01em",
            transition: "all 0.15s",
            boxShadow: open ? "0 4px 14px rgba(240, 192, 64, 0.35)" : "0 2px 8px rgba(0, 0, 0, 0.25)",
            padding: 0,
            overflow: "hidden"
          }}
          onMouseEnter={(e) => { if (!open) e.currentTarget.style.transform = "scale(1.05)"; }}
          onMouseLeave={(e) => { e.currentTarget.style.transform = "scale(1)"; }}>
          {avatarUrl ? (
            <img src={avatarUrl} alt="Avatar" style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: "50%" }} />
          ) : initials}
        </button>

        {open && (
          <div style={{
            position: "absolute",
            top: "calc(100% + 8px)",
            right: 0,
            background: "rgba(22, 25, 35, 0.96)",
            backdropFilter: "blur(24px) saturate(140%)",
            WebkitBackdropFilter: "blur(24px) saturate(140%)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderRadius: 14,
            padding: 6,
            minWidth: 280,
            boxShadow: "0 12px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,0.04) inset",
            zIndex: 1001
          }}>
            <div style={{
              padding: "12px 14px 10px 14px",
              borderBottom: "1px solid rgba(255, 255, 255, 0.05)"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
                <div style={{
                  width: 36, height: 36,
                  background: avatarUrl ? "transparent" : "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)",
                  border: avatarUrl ? "2px solid rgba(240, 192, 64, 0.4)" : "none",
                  borderRadius: "50%",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontWeight: 700,
                  fontSize: 13,
                  color: "#0a0a0a",
                  flexShrink: 0,
                  boxShadow: "0 2px 8px rgba(240, 192, 64, 0.2)",
                  overflow: "hidden"
                }}>
                  {avatarUrl ? (
                    <img src={avatarUrl} alt="Avatar" style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: "50%" }} />
                  ) : initials}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    color: "#e8eaf2",
                    fontSize: 12,
                    fontWeight: 600,
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis"
                  }}>{user?.email}</div>
                  <div style={{ color: "#7a7d92", fontSize: 10, marginTop: 2 }}>Compte connecte</div>
                </div>
              </div>
            </div>

            {(license?.license_key || license?.max_version) && (
              <div style={{
                padding: "10px 14px",
                borderBottom: "1px solid rgba(255, 255, 255, 0.05)",
                display: "grid",
                gap: 6
              }}>
                {license?.license_key && (
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                    <span style={{ color: "#7a7d92", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.04em", fontWeight: 500 }}>Licence</span>
                    <span style={{ color: "#e8eaf2", fontSize: 11, fontFamily: "Menlo, monospace", fontWeight: 600 }}>{license.license_key}</span>
                  </div>
                )}
                {license?.max_version && (
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                    <span style={{ color: "#7a7d92", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.04em", fontWeight: 500 }}>Version</span>
                    <span style={{ color: "#e8eaf2", fontSize: 11, fontWeight: 600 }}>{license.max_version}</span>
                  </div>
                )}
              </div>
            )}

            <div style={{ padding: 4 }}>
              <button onClick={() => setConfirmLogout(true)}
                style={{
                  width: "100%",
                  background: "transparent",
                  border: "none",
                  color: "#fca5a5",
                  textAlign: "left",
                  padding: "9px 11px",
                  fontSize: 13,
                  fontWeight: 500,
                  cursor: "pointer",
                  borderRadius: 8,
                  display: "flex",
                  alignItems: "center",
                  gap: 9,
                  transition: "all 0.12s"
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)"; e.currentTarget.style.color = "#ef4444"; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "#fca5a5"; }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
                Se deconnecter
              </button>
            </div>
          </div>
        )}
      </div>

      {confirmLogout && (
        <div style={{
          position: "fixed",
          top: 0, left: 0, right: 0, bottom: 0,
          background: "rgba(0, 0, 0, 0.55)",
          backdropFilter: "blur(8px)",
          WebkitBackdropFilter: "blur(8px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 2000,
          padding: 16
        }}
        onClick={(e) => { if (e.target === e.currentTarget) setConfirmLogout(false); }}>
          <div style={{
            background: "rgba(22, 25, 35, 0.95)",
            backdropFilter: "blur(24px) saturate(140%)",
            WebkitBackdropFilter: "blur(24px) saturate(140%)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderRadius: 20,
            padding: 28,
            maxWidth: 420,
            width: "100%",
            boxShadow: "0 24px 64px rgba(0, 0, 0, 0.4)"
          }}>
            <div style={{ display: "flex", alignItems: "start", gap: 14, marginBottom: 20 }}>
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: "rgba(240, 192, 64, 0.1)",
                border: "1px solid rgba(240, 192, 64, 0.25)",
                display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0
              }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
              </div>
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4, color: "#f5f6fa" }}>Se deconnecter ?</h2>
                <div style={{ color: "#9ca0b8", fontSize: 13, lineHeight: 1.55 }}>
                  Vous devrez vous reconnecter avec votre licence pour acceder a DEVIA.
                </div>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 14, paddingTop: 14, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
              <button onClick={() => setConfirmLogout(false)}
                style={{
                  background: "rgba(255, 255, 255, 0.04)",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                  color: "#e8eaf2",
                  borderRadius: 10,
                  padding: "10px 18px",
                  fontSize: 13,
                  fontWeight: 500,
                  cursor: "pointer"
                }}>
                Annuler
              </button>
              <button onClick={handleLogout}
                style={{
                  background: "#ef4444",
                  border: "1px solid #ef4444",
                  color: "#fff",
                  borderRadius: 10,
                  padding: "10px 18px",
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 7,
                  boxShadow: "0 4px 14px rgba(239, 68, 68, 0.25)"
                }}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
                Se deconnecter
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
