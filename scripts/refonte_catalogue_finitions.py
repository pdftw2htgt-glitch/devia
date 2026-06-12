#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 3.B.2 : Finitions Catalogue
Refait :
1. Card d'intro 'Catalogue marche DEVIA' (icone SVG info)
2. Card d'intro 'Mon catalogue d'entreprise' (icone SVG ampoule)
3. Boutons Modifier/Supprimer (icones SVG + hover plus marque)

A lancer depuis ~/Desktop/devia :
    python3 refonte_catalogue_finitions.py

Apres : npm run build
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_catalogue_finitions"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MOD 1 : Card d'intro Marche DEVIA
# ================================================================

old_intro_marche = '''<div style={{ ...cardStyle, padding: 16, marginBottom: 16, background: "#0f1117", borderColor: "#60a5fa44" }}>
                  <div style={{ display: "flex", alignItems: "start", gap: 12 }}>
                    <div style={{ fontSize: 20 }}>&#x2139;&#xFE0F;</div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>Catalogue marche DEVIA</div>
                      <div style={{ color: "#545870", fontSize: 13, lineHeight: 1.5 }}>
                        Prix moyens du marche francais 2026, mis a jour regulierement par DEVIA.
                        Vos prix dans 'Mon catalogue' ont la priorite sur ces references.
                      </div>
                    </div>
                  </div>
                </div>'''

new_intro_marche = '''<div style={{
                  padding: 16,
                  marginBottom: 16,
                  background: "rgba(96, 165, 250, 0.04)",
                  border: "1px solid rgba(96, 165, 250, 0.18)",
                  borderRadius: 12,
                  display: "flex",
                  alignItems: "start",
                  gap: 12
                }}>
                  <div style={{
                    width: 32, height: 32, borderRadius: 8,
                    background: "rgba(96, 165, 250, 0.12)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0
                  }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
                    </svg>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4, color: "#e8eaf2" }}>Catalogue marche DEVIA</div>
                    <div style={{ color: "#9ca0b8", fontSize: 13, lineHeight: 1.55 }}>
                      Prix moyens du marche francais 2026, mis a jour regulierement par DEVIA.
                      Vos prix dans &quot;Mon catalogue&quot; ont la priorite sur ces references.
                    </div>
                  </div>
                </div>'''

if 'background: "rgba(96, 165, 250, 0.04)"' in content and 'Catalogue marche DEVIA' in content:
    print("[INFO] Card intro Marche deja refondue")
elif old_intro_marche in content:
    content = content.replace(old_intro_marche, new_intro_marche, 1)
    print("[OK] Card intro Marche DEVIA refondue (icone SVG info)")
else:
    print("[ERREUR] Card intro Marche non trouvee.")
    sys.exit(1)

# ================================================================
# MOD 2 : Card d'intro Mon catalogue
# ================================================================

old_intro_perso = '''<div style={{ ...cardStyle, padding: 16, background: "#0f1117", borderColor: "#3ecf8e44", flex: 1, marginBottom: 0 }}>
                    <div style={{ display: "flex", alignItems: "start", gap: 12 }}>
                      <div style={{ fontSize: 20 }}>&#x1F4A1;</div>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>Mon catalogue d'entreprise</div>
                        <div style={{ color: "#545870", fontSize: 13, lineHeight: 1.5 }}>
                          Vos prix personnels, prioritaires sur le catalogue marche.
                        </div>
                      </div>
                    </div>
                  </div>'''

new_intro_perso = '''<div style={{
                    padding: 16,
                    background: "rgba(62, 207, 142, 0.04)",
                    border: "1px solid rgba(62, 207, 142, 0.18)",
                    borderRadius: 12,
                    flex: 1,
                    display: "flex",
                    alignItems: "start",
                    gap: 12
                  }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: 8,
                      background: "rgba(62, 207, 142, 0.12)",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      flexShrink: 0
                    }}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 21h6"/><path d="M12 17v4"/><path d="M12 3a6 6 0 016 6c0 3-2 4-3 6H9c-1-2-3-3-3-6a6 6 0 016-6z"/>
                      </svg>
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4, color: "#e8eaf2" }}>Mon catalogue d&apos;entreprise</div>
                      <div style={{ color: "#9ca0b8", fontSize: 13, lineHeight: 1.55 }}>
                        Vos prix personnels, prioritaires sur le catalogue marche.
                      </div>
                    </div>
                  </div>'''

if 'background: "rgba(62, 207, 142, 0.04)"' in content and 'Mon catalogue d' in content:
    print("[INFO] Card intro Perso deja refondue")
elif old_intro_perso in content:
    content = content.replace(old_intro_perso, new_intro_perso, 1)
    print("[OK] Card intro Mon catalogue refondue (icone SVG ampoule)")
else:
    print("[WARN] Card intro Perso non trouvee exactement")

# ================================================================
# MOD 3 : Boutons Modifier / Supprimer
# ================================================================

old_btn_modifier = '''<button
                                  onClick={() => openEditCatalogModal(m)}
                                  title="Modifier"
                                  style={{ background: "transparent", border: "1px solid #2a2e40", color: "#60a5fa", borderRadius: 6, padding: "4px 10px", cursor: "pointer", fontSize: 12, fontWeight: 600, transition: "all 0.15s" }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "#60a5fa18"; e.currentTarget.style.borderColor = "#60a5fa"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "#2a2e40"; }}>'''

new_btn_modifier = '''<button
                                  onClick={() => openEditCatalogModal(m)}
                                  title="Modifier"
                                  style={{
                                    background: "transparent",
                                    border: "1px solid rgba(255, 255, 255, 0.06)",
                                    color: "#7a7d92",
                                    borderRadius: 8,
                                    padding: "6px 8px",
                                    cursor: "pointer",
                                    transition: "all 0.15s",
                                    display: "inline-flex",
                                    alignItems: "center",
                                    justifyContent: "center"
                                  }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(96, 165, 250, 0.1)"; e.currentTarget.style.borderColor = "rgba(96, 165, 250, 0.4)"; e.currentTarget.style.color = "#60a5fa"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.color = "#7a7d92"; }}>'''

# Le bouton modifier - on remplace aussi son contenu (Modifier -> SVG)
old_btn_modifier_full = old_btn_modifier + '''
                                  Modifier
                                </button>'''

new_btn_modifier_full = new_btn_modifier + '''
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                  </svg>
                                </button>'''

if 'M18.5 2.5a2.121 2.121 0 013 3L12 15' in content:
    print("[INFO] Bouton Modifier deja refondu")
elif old_btn_modifier_full in content:
    content = content.replace(old_btn_modifier_full, new_btn_modifier_full, 1)
    print("[OK] Bouton Modifier refondu (icone crayon SVG)")
else:
    print("[WARN] Bouton Modifier non trouve exactement")

# Bouton Supprimer
old_btn_supprimer = '''<button
                                  onClick={() => handleDeleteMaterial(m)}
                                  title="Supprimer"
                                  style={{ background: "transparent", border: "1px solid #2a2e40", color: "#ef4444", borderRadius: 6, padding: "4px 10px", cursor: "pointer", fontSize: 12, fontWeight: 600, transition: "all 0.15s" }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "#ef444418"; e.currentTarget.style.borderColor = "#ef4444"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "#2a2e40"; }}>
                                  Supprimer
                                </button>'''

new_btn_supprimer = '''<button
                                  onClick={() => handleDeleteMaterial(m)}
                                  title="Supprimer"
                                  style={{
                                    background: "transparent",
                                    border: "1px solid rgba(255, 255, 255, 0.06)",
                                    color: "#7a7d92",
                                    borderRadius: 8,
                                    padding: "6px 8px",
                                    cursor: "pointer",
                                    transition: "all 0.15s",
                                    display: "inline-flex",
                                    alignItems: "center",
                                    justifyContent: "center"
                                  }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)"; e.currentTarget.style.borderColor = "rgba(239, 68, 68, 0.4)"; e.currentTarget.style.color = "#ef4444"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.color = "#7a7d92"; }}>
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                                  </svg>
                                </button>'''

if 'polyline points="3 6 5 6 21 6"' in content:
    print("[INFO] Bouton Supprimer deja refondu")
elif old_btn_supprimer in content:
    content = content.replace(old_btn_supprimer, new_btn_supprimer, 1)
    print("[OK] Bouton Supprimer refondu (icone poubelle SVG)")
else:
    print("[WARN] Bouton Supprimer non trouve exactement")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 3.B.2 APPLIQUEE - Finitions Catalogue")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Card intro Marche DEVIA :")
print("     - Icone SVG info dans un carre bleu translucide")
print("     - Texte plus lisible")
print("  2. Card intro Mon catalogue :")
print("     - Icone SVG ampoule dans un carre vert translucide")
print("     - Texte plus lisible")
print("  3. Boutons Modifier/Supprimer (tableau Mon catalogue) :")
print("     - Texte remplace par icones SVG (crayon + poubelle)")
print("     - Tres discrets au repos (gris)")
print("     - Au hover :")
print("       - Modifier : bleu vif")
print("       - Supprimer : rouge vif")
print()
print("PROCHAINE ETAPE :")
print("  npm run build")
print("  Si OK :")
print("    git add devia.jsx")
print("    git commit -m 'Refonte design Session 3.B.2 - Finitions catalogue'")
print("    git push")
print()
print(f"BACKUP : {backup_name}")
