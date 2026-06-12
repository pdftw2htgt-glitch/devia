#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Etape B.2 : Stockage tokens + refonte section stats Compte
- Ajoute tokens_in / tokens_out a l'insert Supabase
- Charge ces colonnes au demarrage
- Refonte grille 3 -> 5 colonnes responsive
- Stats : Devis ce mois, Total, Jours abo, Tokens (cumul + mois), CO2 (cumul + mois)
- CO2 estime : ~0.000175 g par token (entree + sortie)
"""

import os
import sys
import shutil
from datetime import datetime

if not os.path.exists("devia.jsx"):
    print("ERREUR : devia.jsx introuvable.")
    sys.exit(1)

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_tokens_stats"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

modifs = 0

# ================================================================
# MOD 1 : Ajouter tokens_in / tokens_out dans l'insert Supabase
# ================================================================

old_insert = '''const newProject = {
            user_id: user.id,
            nom: nomProjet.trim() || p.description || "Nouveau projet",
            commune: p.commune || commune,
            longueur: p.longueur || null,
            largeur: p.largeur || null,
            hauteur: p.hauteur || null,
            pente: p.pente || null,
            surface: p.surface || null,
            type_charpente: p.type || null,
            total_ttc: totalTTC,
            total_ht: totalHT,
            devis_data: parsed,
          };'''

new_insert = '''const newProject = {
            user_id: user.id,
            nom: nomProjet.trim() || p.description || "Nouveau projet",
            commune: p.commune || commune,
            longueur: p.longueur || null,
            largeur: p.largeur || null,
            hauteur: p.hauteur || null,
            pente: p.pente || null,
            surface: p.surface || null,
            type_charpente: p.type || null,
            total_ttc: totalTTC,
            total_ht: totalHT,
            devis_data: parsed,
            tokens_in: (data.usage && data.usage.input_tokens) || 0,
            tokens_out: (data.usage && data.usage.output_tokens) || 0,
          };'''

if "tokens_in: (data.usage" in content:
    print("[INFO] Insert tokens deja en place")
elif old_insert in content:
    content = content.replace(old_insert, new_insert, 1)
    print("[OK] Tokens ajoutes a l'insert Supabase")
    modifs += 1
else:
    print("[ERREUR] Insert newProject non trouve")
    sys.exit(1)

# ================================================================
# MOD 2 : Charger les tokens dans loadProjects (formatted)
# ================================================================

old_formatted = '''const formatted = data.map(p => ({
            id: p.id,
            nom: p.nom,
            commune: p.commune || "",
            date: p.created_at ? p.created_at.split("T")[0] : "",
            ttc: p.total_ttc || 0,
            dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m",
            devis_data: p.devis_data,
            zone_data: p.zone_data,
            groupe_id: p.groupe_id || null,
          }));'''

new_formatted = '''const formatted = data.map(p => ({
            id: p.id,
            nom: p.nom,
            commune: p.commune || "",
            date: p.created_at ? p.created_at.split("T")[0] : "",
            ttc: p.total_ttc || 0,
            dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m",
            devis_data: p.devis_data,
            zone_data: p.zone_data,
            groupe_id: p.groupe_id || null,
            tokens_in: p.tokens_in || 0,
            tokens_out: p.tokens_out || 0,
            created_at: p.created_at,
          }));'''

if "tokens_in: p.tokens_in" in content:
    print("[INFO] Chargement tokens deja en place")
elif old_formatted in content:
    content = content.replace(old_formatted, new_formatted, 1)
    print("[OK] Chargement tokens + created_at ajoute dans loadProjects")
    modifs += 1
else:
    print("[WARN] Bloc formatted non trouve, le chargement des tokens echoue")

# ================================================================
# MOD 3 : Refonte de la grille des 3 stats -> 5 stats responsive
# ================================================================

# On vise la grille 3 stats existante (le grand bloc qu'on a vu)
old_stats_block = '''          {/* 3 stats */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>
            {[
              {
                label: "Devis ce mois",
                val: projects.length,
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 11H7v8h2v-8zm6 0h-2v8h2v-8zM11 11v8h2v-8h-2zM4 7h16M5 7v14h14V7M9 4h6v3H9z"/></svg>,
                color: "#60a5fa"
              },
              {
                label: "Total generes",
                val: projects.length,
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>,
                color: "#3ecf8e"
              },
              {
                label: "Jours restants",
                val: "23",
                icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>,
                color: "#a78bfa"
              }
            ].map(s => (
              <div key={s.label} style={{
                background: "rgba(255, 255, 255, 0.02)",
                borderRadius: 12,
                padding: 16,
                border: "1px solid rgba(255, 255, 255, 0.05)",
                transition: "border-color 0.15s"
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)"; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.05)"; }}>
                <div style={{
                  width: 32, height: 32, borderRadius: 8,
                  background: "rgba(255, 255, 255, 0.04)",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                  display: "inline-flex", alignItems: "center", justifyContent: "center",
                  marginBottom: 10
                }}>
                  {s.icon}
                </div>
                <div style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 4 }}>{s.label}</div>
                <div style={{ fontSize: 24, fontWeight: 700, color: "#f5f6fa", letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums" }}>{s.val}</div>
              </div>
            ))}
          </div>'''

new_stats_block = '''          {/* 5 stats responsive */}
          {(() => {
            // Calculs
            const now = new Date();
            const thisMonth = now.getMonth();
            const thisYear = now.getFullYear();
            const projetsThisMonth = projects.filter(p => {
              if (!p.created_at) return false;
              const d = new Date(p.created_at);
              return d.getMonth() === thisMonth && d.getFullYear() === thisYear;
            });
            const tokensTotal = projects.reduce((sum, p) => sum + (p.tokens_in || 0) + (p.tokens_out || 0), 0);
            const tokensMonth = projetsThisMonth.reduce((sum, p) => sum + (p.tokens_in || 0) + (p.tokens_out || 0), 0);
            // CO2 : approximation Anthropic ~ 0.000175 g par token (cumul in+out)
            const co2TotalG = tokensTotal * 0.000175;
            const co2MonthG = tokensMonth * 0.000175;
            const formatTokens = (n) => n >= 1000000 ? (n / 1000000).toFixed(1) + "M" : n >= 1000 ? (n / 1000).toFixed(1) + "k" : String(n);
            const formatCO2 = (g) => g >= 1000 ? (g / 1000).toFixed(2) + " kg" : g.toFixed(1) + " g";

            const stats = [
              {
                label: "Devis ce mois",
                val: projetsThisMonth.length,
                sub: null,
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 11H7v8h2v-8zm6 0h-2v8h2v-8zM11 11v8h2v-8h-2zM4 7h16M5 7v14h14V7M9 4h6v3H9z"/></svg>,
                color: "#60a5fa"
              },
              {
                label: "Total devis",
                val: projects.length,
                sub: null,
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>,
                color: "#3ecf8e"
              },
              {
                label: "Jours abo",
                val: "23",
                sub: null,
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>,
                color: "#a78bfa"
              },
              {
                label: "Tokens IA",
                val: formatTokens(tokensTotal),
                sub: tokensMonth > 0 ? formatTokens(tokensMonth) + " ce mois" : "0 ce mois",
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
                color: "#f0c040"
              },
              {
                label: "Empreinte CO2",
                val: formatCO2(co2TotalG),
                sub: co2MonthG > 0 ? formatCO2(co2MonthG) + " ce mois" : "0 g ce mois",
                icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C7 8 17 8 17 8z"/></svg>,
                color: "#3ecf8e"
              }
            ];

            return (
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
                gap: 10
              }}>
                {stats.map(s => (
                  <div key={s.label} style={{
                    background: "rgba(255, 255, 255, 0.02)",
                    borderRadius: 12,
                    padding: 14,
                    border: "1px solid rgba(255, 255, 255, 0.05)",
                    transition: "border-color 0.15s",
                    display: "flex",
                    flexDirection: "column"
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)"; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.05)"; }}>
                    <div style={{
                      width: 28, height: 28, borderRadius: 7,
                      background: "rgba(255, 255, 255, 0.04)",
                      border: "1px solid rgba(255, 255, 255, 0.06)",
                      display: "inline-flex", alignItems: "center", justifyContent: "center",
                      marginBottom: 10
                    }}>
                      {s.icon}
                    </div>
                    <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: 4 }}>{s.label}</div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: "#f5f6fa", letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums", lineHeight: 1.1 }}>{s.val}</div>
                    {s.sub && (
                      <div style={{ marginTop: 6, color: "#545870", fontSize: 10, fontVariantNumeric: "tabular-nums" }}>{s.sub}</div>
                    )}
                  </div>
                ))}
              </div>
            );
          })()}'''

if "5 stats responsive" in content:
    print("[INFO] Refonte stats deja en place")
elif old_stats_block in content:
    content = content.replace(old_stats_block, new_stats_block, 1)
    print("[OK] Refonte 3 -> 5 stats responsive (Tokens + CO2)")
    modifs += 1
else:
    print("[ERREUR] Bloc 3 stats non trouve exactement")
    sys.exit(1)

with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print(f"{modifs} MODIFICATIONS APPLIQUEES")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Tokens stockes dans Supabase a chaque generation de devis")
print("     - tokens_in = data.usage.input_tokens")
print("     - tokens_out = data.usage.output_tokens")
print("  2. Tokens charges dans loadProjects (avec created_at)")
print("  3. Grille refondue : 3 -> 5 stats responsive")
print("     - Devis ce mois (calcule sur created_at)")
print("     - Total devis")
print("     - Jours abo (23 en dur pour l'instant)")
print("     - Tokens IA (cumul + sous-ligne ce mois)")
print("     - Empreinte CO2 (~0.000175 g/token, cumul + mois)")
print("  4. Grille auto-fit : 5 colonnes desktop / 2-3 mobile")
print("  5. Format intelligent : 1.2k / 1.5M, et g/kg pour CO2")
print()
print("COMMENT TESTER :")
print("  1. npm run build")
print("  2. Recharger Safari")
print("  3. Va sur Compte")
print("  4. Section stats : tu vois 5 cards")
print("  5. Pour l'instant tokens = 0 (anciens projets sans tokens stockes)")
print("  6. Genere un NOUVEAU devis -> tokens stockes")
print("  7. Reviens sur Compte -> les chiffres montent !")
print()
print("NOTE : les 17 anciens projets ont tokens=0 (par defaut SQL)")
print("       Seuls les nouveaux devis remonteront leurs tokens.")
print()
print(f"BACKUP : {backup_name}")
