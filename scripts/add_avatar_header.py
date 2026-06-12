#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - D.3 : Photo de profil dans le UserMenu du header
- UserMenu accepte avatarUrl en prop
- Affiche photo ronde si avatarUrl, sinon initiales (fallback)
- DeviaMain passe avatarUrl au UserMenu (synchro instant)
"""

import os
import sys
import shutil
from datetime import datetime

# ================================================================
# 1. Modifier src/components/UserMenu.jsx
# ================================================================
PATH_UM = "src/components/UserMenu.jsx"
if not os.path.exists(PATH_UM):
    print("ERREUR : UserMenu.jsx introuvable.")
    sys.exit(1)

backup_um = f"{PATH_UM}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_avatar"
shutil.copy(PATH_UM, backup_um)
print(f"[OK] Backup UserMenu : {backup_um}")

with open(PATH_UM, "r", encoding="utf-8") as f:
    um_content = f.read()

modifs = 0

# MOD UM-1 : Accepter avatarUrl en prop
old_signature = 'export default function UserMenu({ user, license }) {'
new_signature = 'export default function UserMenu({ user, license, avatarUrl }) {'

if "avatarUrl }" in um_content:
    print("[INFO] Prop avatarUrl deja en place")
elif old_signature in um_content:
    um_content = um_content.replace(old_signature, new_signature, 1)
    print("[OK] Prop avatarUrl ajoutee a UserMenu")
    modifs += 1
else:
    print("[ERREUR] Signature UserMenu non trouvee")
    sys.exit(1)

# MOD UM-2 : Bouton avatar dans le header - afficher la photo si avatarUrl
# On vise le bouton actuel qui affiche {initials}
old_button_avatar = '''        <button onClick={() => setOpen(!open)} title="Mon compte"
          style={{
            background: "linear-gradient(135deg, rgba(240, 192, 64, 0.9) 0%, rgba(224, 160, 32, 0.9) 100%)",
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
          onMouseLeave={(e) => { e.currentTarget.style.transform = "scale(1)"; }}>
          {initials}
        </button>'''

new_button_avatar = '''        <button onClick={() => setOpen(!open)} title="Mon compte"
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
        </button>'''

if "{avatarUrl ? (" in um_content and "alt=\"Avatar\"" in um_content:
    print("[INFO] Bouton avatar deja adapte")
elif old_button_avatar in um_content:
    um_content = um_content.replace(old_button_avatar, new_button_avatar, 1)
    print("[OK] Bouton avatar du header adapte (photo + fallback initiales)")
    modifs += 1
else:
    print("[WARN] Bouton avatar header non trouve")

# MOD UM-3 : Avatar dans le dropdown - aussi adapter
old_dropdown_avatar = '''                <div style={{
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
                </div>'''

new_dropdown_avatar = '''                <div style={{
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
                </div>'''

if "avatarUrl ? \"transparent\" : \"linear-gradient(135deg, #f0c040" in um_content:
    print("[INFO] Avatar dropdown deja adapte")
elif old_dropdown_avatar in um_content:
    um_content = um_content.replace(old_dropdown_avatar, new_dropdown_avatar, 1)
    print("[OK] Avatar dans le dropdown adapte")
    modifs += 1
else:
    print("[WARN] Avatar dropdown non trouve")

with open(PATH_UM, "w", encoding="utf-8") as f:
    f.write(um_content)

print(f"[OK] UserMenu.jsx mis a jour ({modifs} modifs)")

# ================================================================
# 2. Modifier devia.jsx : passer avatarUrl en prop au UserMenu
# ================================================================
if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_dj = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_avatar_in_header"
shutil.copy("devia.jsx", backup_dj)
print(f"[OK] Backup devia.jsx : {backup_dj}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs_dj = 0

# Cibler l'appel <UserMenu user={user} license={license} /> dans le header
old_call = '<UserMenu user={user} license={license} />'
new_call = '<UserMenu user={user} license={license} avatarUrl={avatarUrl} />'

if "avatarUrl={avatarUrl}" in content:
    print("[INFO] Prop avatarUrl deja passee a UserMenu")
elif old_call in content:
    content = content.replace(old_call, new_call, 1)
    print("[OK] Prop avatarUrl passee a UserMenu")
    modifs_dj += 1
else:
    print("[ERREUR] Appel UserMenu non trouve")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"TOTAL : {modifs + modifs_dj} MODIFICATIONS")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  UserMenu.jsx :")
print("    - Accepte avatarUrl en prop")
print("    - Affiche la photo si avatarUrl, sinon initiales (fallback)")
print("    - Bordure doree subtile autour de la photo")
print("    - Avatar du dropdown aussi adapte")
print("  devia.jsx :")
print("    - Passe avatarUrl au UserMenu")
print()
print("RESULTAT :")
print("  - Quand tu uploades une photo dans Compte -> avatar du header maj instantanement")
print("  - Quand tu supprimes -> retour aux initiales")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print()
print(f"BACKUPS : {backup_um}")
print(f"          {backup_dj}")
