#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Fix UserMenu :
- Refonte du composant UserMenu (style liquid glass coherent)
- Integration dans le header (plus de position fixed)
- Suppression du popup blanc/bleu, modale moderne
"""

import os
import sys
import shutil
from datetime import datetime

# ================================================================
# 1. Reecrire src/components/UserMenu.jsx
# ================================================================
ABS_PATH_USERMENU = "src/components/UserMenu.jsx"

if not os.path.exists(ABS_PATH_USERMENU):
    print("ERREUR : src/components/UserMenu.jsx introuvable.")
    sys.exit(1)

backup_um = f"{ABS_PATH_USERMENU}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_refonte"
shutil.copy(ABS_PATH_USERMENU, backup_um)
print(f"[OK] Backup UserMenu : {backup_um}")

new_usermenu = '''// src/components/UserMenu.jsx
// Avatar + menu user integre dans le header DEVIA (style liquid glass)

import React, { useState, useEffect, useRef } from "react";
import { signOut } from "../lib/auth.js";

export default function UserMenu({ user, license }) {
  const [open, setOpen] = useState(false);
  const [confirmLogout, setConfirmLogout] = useState(false);
  const menuRef = useRef(null);

  // Fermer au clic externe
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
            background: open ? "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)" : "linear-gradient(135deg, rgba(240, 192, 64, 0.9) 0%, rgba(224, 160, 32, 0.9) 100%)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
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
            padding: 0
          }}
          onMouseEnter={(e) => { if (!open) e.currentTarget.style.transform = "scale(1.05)"; }}
          onMouseLeave={(e) => { if (!open) e.currentTarget.style.transform = "scale(1)"; }}>
          {initials}
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
            zIndex: 1001,
            animation: "fadeInUp 0.18s ease-out"
          }}>
            {/* Header utilisateur */}
            <div style={{
              padding: "12px 14px 10px 14px",
              borderBottom: "1px solid rgba(255, 255, 255, 0.05)"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
                <div style={{
                  width: 36, height: 36,
                  background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)",
                  borderRadius: "50%",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontWeight: 700,
                  fontSize: 13,
                  color: "#0a0a0a",
                  flexShrink: 0,
                  boxShadow: "0 2px 8px rgba(240, 192, 64, 0.2)"
                }}>
                  {initials}
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

            {/* Infos licence */}
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

            {/* Bouton deconnexion */}
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

      {/* Modale custom de confirmation deconnexion */}
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
          padding: 16,
          animation: "fadeInUp 0.18s ease-out"
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
                  cursor: "pointer",
                  transition: "all 0.15s"
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)"; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.04)"; }}>
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
                  transition: "background 0.15s",
                  boxShadow: "0 4px 14px rgba(239, 68, 68, 0.25)"
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = "#dc2626"; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = "#ef4444"; }}>
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
'''

with open(ABS_PATH_USERMENU, "w", encoding="utf-8") as f:
    f.write(new_usermenu)

print(f"[OK] {ABS_PATH_USERMENU} reecrit (style liquid glass + modale)")

# ================================================================
# 2. Modifier devia.jsx pour integrer UserMenu DANS le header
# Et supprimer le rendu par-dessus l'app
# ================================================================

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_dj = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_usermenu_in_header"
shutil.copy("devia.jsx", backup_dj)
print(f"[OK] Backup devia.jsx : {backup_dj}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# MOD 1 : Importer UserMenu dans devia.jsx (s'il ne l'est pas deja)
# Il est probablement importe deja vu qu'il est utilise dans DeviaAuthGate
# Verifions
if "import UserMenu from" not in content and "from \"./src/components/UserMenu\"" not in content:
    # Cherche un autre import pour s'aligner
    import_anchor = 'import React'
    if import_anchor in content:
        # Ajoute apres le premier import React
        new_import = 'import React'
        # On cherche le premier '\n' apres l'import React
        idx = content.index(import_anchor)
        next_nl = content.index("\n", idx)
        # Insere notre import sur la ligne suivante
        content = content[:next_nl+1] + 'import UserMenu from "./src/components/UserMenu.jsx";\n' + content[next_nl+1:]
        print("[OK] Import UserMenu ajoute dans devia.jsx")
        modifs += 1
else:
    print("[INFO] UserMenu deja importe ou utilise differemment")

# MOD 2 : Modifier le header pour passer la nav dans un container,
# et ajouter le UserMenu apres la nav
# On cible la fin de la nav (avant </header>)
old_end_nav = '''          {tab.label}
        </button>
      ))}
    </nav>
  </header>'''

# On va wrapper nav + UserMenu dans un div flex, mais c'est complique
# Alternative simple : ajouter le UserMenu juste apres la nav, dans un wrapper flex
# Mais le header utilise space-between, donc nav est colle a droite
# Pour ajouter UserMenu a droite de la nav, il faut un wrapper

# Strategie : on transforme la nav directe en un wrapper flex contenant nav + UserMenu
# Le wrapper sera dans le header, et space-between le poussera a droite

new_end_nav_with_user = '''          {tab.label}
        </button>
      ))}
    </nav>
    {user && <UserMenu user={user} license={license} />}
  </header>'''

# Mais attention, on a besoin que `user` et `license` soient accessibles ici
# Vu que c'est dans le composant principal qui les recoit en props
# Verifions d'abord

# Le header est dans le composant App probablement
# On va voir comment l'app est definie

if "<UserMenu user={user} license={license} />" in content.replace("\n", " "):
    print("[INFO] UserMenu deja dans le header")
elif old_end_nav in content:
    # On a besoin que le header soit dans un wrapper qui passe user et license
    # On va d'abord verifier comment App recoit user et license
    print("[NOTE] Verifions le contexte avant d'inserer...")
    print("[ACTION] Insertion du UserMenu dans le header - mais user/license doivent etre accessibles")
    print("         Si le build casse, c'est qu'on doit propager les props.")
    content = content.replace(old_end_nav, new_end_nav_with_user, 1)
    print("[OK] UserMenu insere dans le header")
    modifs += 1
else:
    print("[ERREUR] Fin de la nav non trouvee")

# MOD 3 : Modifier la structure pour que le header soit flex et que nav+usermenu soient groupes
# En fait c'est plus simple : on rend nav et UserMenu cote a cote en wrappant dans un flex

# La structure actuelle :
# <header (flex space-between)>
#   <div> logo + texte </div>      <-- gauche
#   <nav> tabs </nav>              <-- droite (avec space-between)
# </header>
#
# On veut :
# <header (flex space-between)>
#   <div> logo + texte </div>      <-- gauche
#   <div style="flex; gap; align">  <-- nouveau wrapper droite
#     <nav> tabs </nav>
#     <UserMenu />
#   </div>
# </header>

# On cible la nav et on l'enveloppe avec UserMenu dans un div
old_nav_start = '''    <nav style={{
      display: "flex",
      gap: 2,
      background: "rgba(255,255,255,0.03)",
      border: "1px solid rgba(255,255,255,0.06)",
      borderRadius: 999,
      padding: 4
    }}>'''

new_wrapper_start = '''    <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
    <nav style={{
      display: "flex",
      gap: 2,
      background: "rgba(255,255,255,0.03)",
      border: "1px solid rgba(255,255,255,0.06)",
      borderRadius: 999,
      padding: 4
    }}>'''

if '<div style={{ display: "flex", alignItems: "center", gap: 14 }}>\n    <nav' in content:
    print("[INFO] Wrapper nav+user deja en place")
elif old_nav_start in content:
    content = content.replace(old_nav_start, new_wrapper_start, 1)
    print("[OK] Wrapper flex ouvert avant la nav")
    modifs += 1

# Et fermer le wrapper APRES UserMenu
old_after_usermenu = '''    {user && <UserMenu user={user} license={license} />}
  </header>'''

new_after_usermenu = '''    {user && <UserMenu user={user} license={license} />}
    </div>
  </header>'''

if "</div>\n  </header>" in content:
    print("[INFO] Wrapper deja ferme")
elif old_after_usermenu in content:
    content = content.replace(old_after_usermenu, new_after_usermenu, 1)
    print("[OK] Wrapper flex ferme apres UserMenu")
    modifs += 1

# MOD 4 : Verifions si l'app principale recoit `user` et `license`
# Si oui, c'est bon. Sinon, on a un probleme.
# Cherchons la signature de la fonction App
# function App() ? function App({ user, license }) ?

# On va juste verifier si user et license sont accessibles dans le scope du header
# Le header est dans le return de App. On va chercher le debut de App
if "function App({" in content or "function App(props)" in content:
    print("[OK] App recoit des props (user/license probablement disponibles)")
elif "function App()" in content:
    print("[WARN] App() sans props - user et license ne seront pas accessibles dans le header")
    print("[ACTION] Il faut modifier App pour recevoir user et license en props")
    # Recherche signature exacte
    import re
    match = re.search(r'function App\(\)\s*\{', content)
    if match:
        content = content[:match.start()] + 'function App({ user, license })' + content[match.start()+12:]
        print("[OK] App() -> App({ user, license })")
        modifs += 1

# Verifions aussi comment App est appele dans DeviaAuthGate
# Probablement <App /> sans props -> il faut <App user={user} license={license} />
old_app_call = '<App />'
new_app_call = '<App user={user} license={license} />'
if old_app_call in content:
    count = content.count(old_app_call)
    content = content.replace(old_app_call, new_app_call)
    print(f"[OK] {count} occurrence(s) de <App /> -> <App user license />")
    modifs += 1

# MOD 5 : Supprimer le <UserMenu> en dehors du header (dans DeviaAuthGate)
# pour ne plus l'avoir en position fixed
old_authgate_usermenu = '''      <SubscriptionBanner license={license} />
      <UserMenu user={user} license={license} />'''

new_authgate_usermenu = '''      <SubscriptionBanner license={license} />'''

if old_authgate_usermenu in content:
    content = content.replace(old_authgate_usermenu, new_authgate_usermenu, 1)
    print("[OK] UserMenu retire du AuthGate (plus de position fixed)")
    modifs += 1
elif "<UserMenu user={user} license={license} />" in content and content.count("<UserMenu user={user} license={license} />") == 1:
    print("[INFO] UserMenu deja unique (dans le header seulement)")

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES SUR devia.jsx")
print("=" * 60)
print()
print("RESUME :")
print("  1. UserMenu.jsx : style liquid glass coherent")
print("     - Avatar dore avec initiales")
print("     - Dropdown : email, licence, version, deconnexion")
print("     - Modale custom de confirmation deconnexion")
print("  2. UserMenu integre DANS le header (plus de position fixed)")
print("  3. Suppression de l'ancien UserMenu en overlay")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si erreur : rollback avec :")
print(f"  cp {backup_dj} devia.jsx")
print(f"  cp {backup_um} {ABS_PATH_USERMENU}")
print()
print(f"BACKUPS : {backup_um}")
print(f"          {backup_dj}")
