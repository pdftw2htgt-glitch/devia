#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Session 2.A : Refonte du formulaire d'entree Devis
Modifie le bloc 'activeTab === devis' / !result pour :
1. Hero plus elegant (pas d'emoji, typo plus grande)
2. Card formulaire avec inputs plus aerees
3. Badges climatiques refondus
4. Zone upload plus moderne
5. Style errors plus discret

Aucun changement fonctionnel.
A lancer depuis ~/Desktop/devia :
    python3 refonte_devis_form.py
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("package.json"):
    print("ERREUR : package.json introuvable. Lance depuis ~/Desktop/devia")
    sys.exit(1)

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_devis_form"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MODIFICATION 1 : Hero + Card formulaire (description + commune + altitude + badges + upload)
# ================================================================

old_block = '''<div style={{ textAlign: "center", marginBottom: 32 }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>🏗️</div>
              <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>Generez votre devis charpente</h1>
              <p style={{ color: "#545870", fontSize: 15 }}>Decrivez votre projet - DEVIA genere un devis professionnel et une visualisation 3D</p>
            </div>
            <div style={cardStyle}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Description du projet</label>
                <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
                  placeholder="Ex: Charpente traditionnelle en sapin pour maison de 10x8m, tuile terre cuite, pente 35 deg, combles amenageables..."
                  rows={4} style={{ ...inputStyle, resize: "vertical", lineHeight: 1.6 }} />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
                <div>
                  <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Commune</label>
                  <input value={commune} onChange={e => setCommune(e.target.value)} placeholder="Lyon, Grenoble, Paris..." style={inputStyle} />
                </div>
                <div>
                  <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Altitude (m)</label>
                  <input value={altitude} onChange={e => setAltitude(e.target.value)} type="number" placeholder="200" style={inputStyle} />
                </div>
              </div>
              {zoneInfo && (
                <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
                  <Badge color="#60a5fa">Neige {zoneInfo.neige} - {zoneInfo.sk} kN/m2</Badge>
                  <Badge color="#a78bfa">Vent {zoneInfo.vent} - {zoneInfo.qb} kN/m2</Badge>
                  <Badge color="#f97316">Sismique {zoneInfo.sismique} - {zoneInfo.ag}g</Badge>
                </div>
              )}
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>Documents - max 5</label>
                <div onClick={() => fileInputRef.current && fileInputRef.current.click()}
                  style={{ border: "2px dashed #1e2231", borderRadius: 8, padding: 20, textAlign: "center", cursor: "pointer", color: "#545870" }}>
                  <div style={{ fontSize: 24, marginBottom: 6 }}>📎</div>
                  <div style={{ fontSize: 13 }}>Cliquez pour ajouter des fichiers</div>
                  {files.length > 0 && (
                    <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "center" }}>
                      {files.map((f, i) => <Badge key={i} color="#60a5fa">{f.name}</Badge>)}
                    </div>
                  )}
                </div>
                <input ref={fileInputRef} type="file" multiple accept="image/*,.pdf"
                  onChange={e => setFiles(prev => [...prev, ...Array.from(e.target.files || [])].slice(0, 5))}
                  style={{ display: "none" }} />
              </div>
              {error && (
                <div style={{ background: "#ef444420", border: "1px solid #ef4444", borderRadius: 8, padding: 12, marginBottom: 16, color: "#ef4444", fontSize: 14 }}>
                  {error}'''

new_block = '''<div style={{ textAlign: "center", marginBottom: 40, paddingTop: 16 }}>
              <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 12, letterSpacing: "-0.02em", lineHeight: 1.1 }}>
                Generez votre devis <span style={{ background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>charpente</span>
              </h1>
              <p style={{ color: "#7a7d92", fontSize: 15, maxWidth: 520, margin: "0 auto", lineHeight: 1.55 }}>
                Decrivez votre projet en langage naturel. DEVIA genere un devis professionnel et une visualisation 3D.
              </p>
            </div>
            <div style={cardStyle}>
              <div style={{ marginBottom: 20 }}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Description du projet</label>
                <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
                  placeholder="Ex: Charpente traditionnelle en sapin pour maison de 10x8m, tuile terre cuite, pente 35 deg, combles amenageables..."
                  rows={5} style={{ ...inputStyle, resize: "vertical", lineHeight: 1.6, fontSize: 14 }} />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 20 }}>
                <div>
                  <label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Commune</label>
                  <input value={commune} onChange={e => setCommune(e.target.value)} placeholder="Lyon, Grenoble, Paris..." style={inputStyle} />
                </div>
                <div>
                  <label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Altitude <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>(m)</span></label>
                  <input value={altitude} onChange={e => setAltitude(e.target.value)} type="number" placeholder="200" style={inputStyle} />
                </div>
              </div>
              {zoneInfo && (
                <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
                  <div style={{ background: "rgba(96, 165, 250, 0.08)", border: "1px solid rgba(96, 165, 250, 0.18)", borderRadius: 999, padding: "5px 12px", fontSize: 12, color: "#60a5fa", fontWeight: 500, display: "inline-flex", alignItems: "center", gap: 6 }}>
                    <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#60a5fa" }}></span>
                    Neige {zoneInfo.neige} <span style={{ opacity: 0.7 }}>{zoneInfo.sk} kN/m2</span>
                  </div>
                  <div style={{ background: "rgba(167, 139, 250, 0.08)", border: "1px solid rgba(167, 139, 250, 0.18)", borderRadius: 999, padding: "5px 12px", fontSize: 12, color: "#a78bfa", fontWeight: 500, display: "inline-flex", alignItems: "center", gap: 6 }}>
                    <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#a78bfa" }}></span>
                    Vent {zoneInfo.vent} <span style={{ opacity: 0.7 }}>{zoneInfo.qb} kN/m2</span>
                  </div>
                  <div style={{ background: "rgba(249, 115, 22, 0.08)", border: "1px solid rgba(249, 115, 22, 0.18)", borderRadius: 999, padding: "5px 12px", fontSize: 12, color: "#f97316", fontWeight: 500, display: "inline-flex", alignItems: "center", gap: 6 }}>
                    <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#f97316" }}></span>
                    Sismique {zoneInfo.sismique} <span style={{ opacity: 0.7 }}>{zoneInfo.ag}g</span>
                  </div>
                </div>
              )}
              <div style={{ marginBottom: 20 }}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Documents <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>(max 5)</span></label>
                <div onClick={() => fileInputRef.current && fileInputRef.current.click()}
                  style={{ border: "1.5px dashed rgba(255,255,255,0.12)", background: "rgba(255,255,255,0.02)", borderRadius: 12, padding: 24, textAlign: "center", cursor: "pointer", color: "#7a7d92", transition: "all 0.15s" }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(240,192,64,0.3)"; e.currentTarget.style.background = "rgba(240,192,64,0.03)"; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.12)"; e.currentTarget.style.background = "rgba(255,255,255,0.02)"; }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ marginBottom: 8, opacity: 0.7 }}>
                    <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
                  </svg>
                  <div style={{ fontSize: 13, fontWeight: 500 }}>Cliquez pour ajouter des fichiers</div>
                  <div style={{ fontSize: 11, color: "#545870", marginTop: 4 }}>Images ou PDF</div>
                  {files.length > 0 && (
                    <div style={{ marginTop: 12, display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "center" }}>
                      {files.map((f, i) => (
                        <div key={i} style={{ background: "rgba(96, 165, 250, 0.1)", border: "1px solid rgba(96, 165, 250, 0.2)", borderRadius: 999, padding: "4px 10px", fontSize: 11, color: "#60a5fa" }}>
                          {f.name}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <input ref={fileInputRef} type="file" multiple accept="image/*,.pdf"
                  onChange={e => setFiles(prev => [...prev, ...Array.from(e.target.files || [])].slice(0, 5))}
                  style={{ display: "none" }} />
              </div>
              {error && (
                <div style={{ background: "rgba(239, 68, 68, 0.08)", border: "1px solid rgba(239, 68, 68, 0.25)", borderRadius: 10, padding: 14, marginBottom: 20, color: "#fca5a5", fontSize: 13, display: "flex", alignItems: "start", gap: 10 }}>
                  <span style={{ flexShrink: 0, marginTop: 1 }}>&#x26A0;&#xFE0F;</span>
                  <div>{error}'''

if "WebkitBackgroundClip" in content and "Generez votre devis" in content:
    print("[INFO] Formulaire devis deja refondu, skip")
else:
    if old_block not in content:
        print("ERREUR : impossible de trouver le bloc formulaire actuel.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_block, new_block, 1)
    print("[OK] Formulaire devis refondu : hero, inputs, badges, upload, errors")

# ================================================================
# MODIFICATION 2 : Fermeture du bloc error (le </div> qui suit {error})
# Le bloc original a juste {error} sans wrapper, on a ajoute un <div> autour
# donc il faut adapter le </div> de fermeture pour qu'il y en ait 2
# ================================================================

# On cherche le pattern {error}\n                </div> juste apres l'ajout
old_error_close = '''                  {error}
                </div>
              )}'''

new_error_close = '''                  {error}</div>
                </div>
              )}'''

# Application apres modification 1 : le nouveau code contient le pattern
# pour preserver la structure
if old_error_close in content:
    content = content.replace(old_error_close, new_error_close, 1)
    print("[OK] Fermeture bloc error ajustee")
else:
    print("[INFO] Pas besoin d'ajuster fermeture error (deja correct ou structure differente)")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("SESSION 2.A APPLIQUEE - Formulaire entree Devis")
print("=" * 60)
print()
print("CE QUI A CHANGE VISUELLEMENT :")
print("  1. Titre : 'Generez votre devis CHARPENTE' avec gradient jaune sur 'charpente'")
print("  2. Emoji 🏗️ supprime (look + pro)")
print("  3. Sous-titre : plus narratif et lisible")
print("  4. Labels : MAJUSCULES, plus petites, plus subtiles (style pro)")
print("  5. Badges climatiques : pills arrondies avec point colore (style screenshots)")
print("  6. Zone upload : icone trombone fine SVG + texte secondaire")
print("  7. Hover sur zone upload : bord jaune subtil")
print("  8. Erreur : icone warning + fond plus discret")
print()
print("CE QUI N'A PAS CHANGE :")
print("  - Aucun comportement modifie")
print("  - Aucun state touche")
print("  - Selecteur catalogue + bouton Generer : Session 2.B")
print("  - Affichage du devis genere : Session 2.B")
print()
print("PROCHAINE ETAPE :")
print("  git add devia.jsx")
print("  git commit -m 'Refonte design Session 2.A - Formulaire Devis'")
print("  git push")
print()
print("TESTS :")
print("  1. Page Devis : voir le nouveau hero avec 'charpente' en gradient jaune")
print("  2. Cliquer dans description : focus jaune subtil sur la textarea")
print("  3. Taper une commune connue : badges climatiques avec design pill")
print("  4. Hover sur zone upload : bord jaune apparait")
print()
print(f"BACKUP : {backup_name}")
