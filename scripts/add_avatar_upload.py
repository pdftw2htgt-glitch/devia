#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Etape D.2 : Photo de profil sur page Compte
- State avatarUrl + hover state
- Chargement profile au demarrage
- Overlay 'Modifier la photo' au hover de l'avatar
- Upload Supabase Storage + update profiles.avatar_url
- Bouton 'Supprimer' si avatar existe
- Affichage photo a la place des initiales
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_avatar_upload"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter les states avatar
# ================================================================

old_state = 'const [showInfosEntreprise, setShowInfosEntreprise] = useState(false);'
new_state = '''const [showInfosEntreprise, setShowInfosEntreprise] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState(null);
  const [avatarHover, setAvatarHover] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const avatarFileInputRef = useRef(null);'''

if "const [avatarUrl, setAvatarUrl]" in content:
    print("[INFO] State avatar deja present")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("[OK] States avatar ajoutes")
    modifs += 1
else:
    print("[ERREUR] State showInfosEntreprise non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Charger profile (avatar_url) au demarrage
# ================================================================

old_loadlogs_end = '''    loadUsageLogs();
  }, []);'''

new_with_loadprofile = '''    loadUsageLogs();

    // Chargement du profil (avatar)
    const loadProfile = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;
        const { data, error } = await supabase
          .from("profiles")
          .select("avatar_url")
          .eq("user_id", user.id)
          .maybeSingle();
        if (error) {
          console.error("Erreur chargement profile:", error);
          return;
        }
        if (data && data.avatar_url) setAvatarUrl(data.avatar_url);
      } catch (e) {
        console.error("Erreur loadProfile:", e);
      }
    };
    loadProfile();
  }, []);'''

if "const loadProfile = async" in content:
    print("[INFO] loadProfile deja present")
elif old_loadlogs_end in content:
    content = content.replace(old_loadlogs_end, new_with_loadprofile, 1)
    print("[OK] loadProfile ajoute au demarrage")
    modifs += 1
else:
    print("[WARN] Fin loadUsageLogs non trouvee")

# ================================================================
# MOD 3 : Ajouter les fonctions handleAvatarUpload et handleAvatarDelete
# On les ajoute apres handleRenameProject
# ================================================================

# On vise un marqueur stable : la fin de handleRenameProject
# Plus simple : avant 'const assignProjectToGroup'
old_marker = 'const assignProjectToGroup = async (projectId, groupeId) => {'

new_with_avatar_fns = '''const handleAvatarUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validation
    if (!file.type.startsWith("image/")) {
      alert("Veuillez selectionner une image");
      return;
    }
    if (file.size > 2097152) {
      alert("L'image est trop grande (2 Mo maximum)");
      return;
    }

    setUploadingAvatar(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        alert("Vous devez etre connecte");
        setUploadingAvatar(false);
        return;
      }

      // Supprimer les anciens avatars de l'utilisateur
      const { data: existingFiles } = await supabase.storage
        .from("avatars")
        .list(user.id + "/");
      if (existingFiles && existingFiles.length > 0) {
        const pathsToRemove = existingFiles.map(f => user.id + "/" + f.name);
        await supabase.storage.from("avatars").remove(pathsToRemove);
      }

      // Upload nouveau fichier
      const ext = file.name.split(".").pop().toLowerCase();
      const filePath = user.id + "/avatar." + ext;
      const { error: uploadError } = await supabase.storage
        .from("avatars")
        .upload(filePath, file, { upsert: true, cacheControl: "0" });

      if (uploadError) {
        console.error("Erreur upload avatar:", uploadError);
        alert("Erreur lors de l'upload");
        setUploadingAvatar(false);
        return;
      }

      // Recuperer l'URL publique
      const { data: { publicUrl } } = supabase.storage
        .from("avatars")
        .getPublicUrl(filePath);

      // Ajouter cachebuster pour forcer le refresh
      const publicUrlWithBuster = publicUrl + "?t=" + Date.now();

      // Update profile
      const { error: updateError } = await supabase
        .from("profiles")
        .upsert({ user_id: user.id, avatar_url: publicUrlWithBuster, updated_at: new Date().toISOString() }, { onConflict: "user_id" });

      if (updateError) {
        console.error("Erreur update profile:", updateError);
        alert("Photo uploadee mais erreur de sauvegarde");
        setUploadingAvatar(false);
        return;
      }

      setAvatarUrl(publicUrlWithBuster);
      setUploadingAvatar(false);
    } catch (e) {
      console.error("Erreur handleAvatarUpload:", e);
      alert("Erreur inattendue");
      setUploadingAvatar(false);
    }
  };

  const handleAvatarDelete = async () => {
    if (!confirm("Supprimer la photo de profil ?")) return;
    setUploadingAvatar(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // Supprimer du Storage
      const { data: existingFiles } = await supabase.storage
        .from("avatars")
        .list(user.id + "/");
      if (existingFiles && existingFiles.length > 0) {
        const pathsToRemove = existingFiles.map(f => user.id + "/" + f.name);
        await supabase.storage.from("avatars").remove(pathsToRemove);
      }

      // Update profile (avatar_url = null)
      await supabase
        .from("profiles")
        .upsert({ user_id: user.id, avatar_url: null, updated_at: new Date().toISOString() }, { onConflict: "user_id" });

      setAvatarUrl(null);
      setUploadingAvatar(false);
    } catch (e) {
      console.error("Erreur handleAvatarDelete:", e);
      setUploadingAvatar(false);
    }
  };

  const assignProjectToGroup = async (projectId, groupeId) => {'''

if "const handleAvatarUpload" in content:
    print("[INFO] Fonctions avatar deja presentes")
elif old_marker in content:
    content = content.replace(old_marker, new_with_avatar_fns, 1)
    print("[OK] Fonctions handleAvatarUpload + handleAvatarDelete ajoutees")
    modifs += 1
else:
    print("[ERREUR] assignProjectToGroup non trouve")
    sys.exit(1)

# ================================================================
# MOD 4 : Remplacer l'avatar M E par la photo (ou initiales fallback)
# avec overlay hover pour modifier
# ================================================================

old_avatar_block = '''            <div style={{
              width: 56, height: 56,
              background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)",
              borderRadius: 14,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 22,
              fontWeight: 700,
              color: "#0a0a0a",
              boxShadow: "0 4px 14px rgba(240, 192, 64, 0.25)",
              flexShrink: 0
            }}>
              {(params.entreprise || "M E").split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase()}
            </div>'''

new_avatar_block = '''            <div
              style={{
                position: "relative",
                width: 56, height: 56,
                flexShrink: 0,
                cursor: uploadingAvatar ? "wait" : "pointer"
              }}
              onMouseEnter={() => setAvatarHover(true)}
              onMouseLeave={() => setAvatarHover(false)}
              onClick={() => { if (!uploadingAvatar && avatarFileInputRef.current) avatarFileInputRef.current.click(); }}>
              {avatarUrl ? (
                <img src={avatarUrl} alt="Avatar"
                  style={{
                    width: 56, height: 56,
                    borderRadius: 14,
                    objectFit: "cover",
                    boxShadow: "0 4px 14px rgba(240, 192, 64, 0.25)",
                    border: "2px solid rgba(240, 192, 64, 0.4)"
                  }}
                  onError={(e) => { e.target.style.display = "none"; }}
                />
              ) : (
                <div style={{
                  width: 56, height: 56,
                  background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)",
                  borderRadius: 14,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 22,
                  fontWeight: 700,
                  color: "#0a0a0a",
                  boxShadow: "0 4px 14px rgba(240, 192, 64, 0.25)"
                }}>
                  {(params.entreprise || "M E").split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase()}
                </div>
              )}
              {/* Overlay au hover */}
              {(avatarHover || uploadingAvatar) && (
                <div style={{
                  position: "absolute",
                  inset: 0,
                  background: "rgba(0, 0, 0, 0.55)",
                  borderRadius: 14,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  backdropFilter: "blur(2px)",
                  transition: "opacity 0.18s"
                }}>
                  {uploadingAvatar ? (
                    <span style={{ display: "inline-block", width: 18, height: 18, border: "2px solid rgba(255,255,255,0.25)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                  ) : (
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
                      <circle cx="12" cy="13" r="4"/>
                    </svg>
                  )}
                </div>
              )}
              {/* Input file cache */}
              <input
                ref={avatarFileInputRef}
                type="file"
                accept="image/*"
                onChange={handleAvatarUpload}
                style={{ display: "none" }}
              />
              {/* Bouton supprimer (si photo et hover) */}
              {avatarUrl && avatarHover && !uploadingAvatar && (
                <button onClick={(e) => { e.stopPropagation(); handleAvatarDelete(); }}
                  title="Supprimer la photo"
                  style={{
                    position: "absolute",
                    top: -6, right: -6,
                    width: 22, height: 22, borderRadius: "50%",
                    background: "#ef4444",
                    border: "2px solid #0a0a0a",
                    color: "#fff",
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    padding: 0,
                    boxShadow: "0 2px 6px rgba(0, 0, 0, 0.3)"
                  }}>
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              )}
            </div>'''

if 'ref={avatarFileInputRef}' in content:
    print("[INFO] Avatar dynamique deja en place")
elif old_avatar_block in content:
    content = content.replace(old_avatar_block, new_avatar_block, 1)
    print("[OK] Avatar dynamique (photo + hover + upload + delete) ajoute")
    modifs += 1
else:
    print("[ERREUR] Bloc avatar non trouve")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. States avatarUrl, avatarHover, uploadingAvatar + ref input file")
print("  2. loadProfile() au demarrage (recupere avatar_url)")
print("  3. handleAvatarUpload + handleAvatarDelete")
print("  4. Avatar sur page Compte :")
print("     - Affiche la photo si avatarUrl, sinon initiales (fallback)")
print("     - Au hover : overlay sombre + icone appareil photo")
print("     - Click : ouvre selecteur de fichier")
print("     - Bouton X rouge en haut-droite si photo presente")
print("     - Spinner pendant l'upload")
print()
print("COMMENT TESTER :")
print("  1. npm run build")
print("  2. Va sur Compte")
print("  3. Hover sur l'avatar dore -> overlay 'appareil photo'")
print("  4. Click -> selectionne une image (max 2 Mo)")
print("  5. Spinner pendant l'upload")
print("  6. La photo apparait immediatement")
print("  7. Hover -> petit X rouge en haut-droite pour supprimer")
print()
print(f"BACKUP : {backup_name}")
