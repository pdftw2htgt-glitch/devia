#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Etape 2.A.3.a : Onglet Catalogue (affichage seul)
Ajoute :
1. Onglet 'Catalogue' au menu (entre Projets et Parametres)
2. States React pour les 2 catalogues
3. useEffect pour charger les donnees Supabase
4. Vue Catalogue avec 2 onglets internes (Marche / Mon catalogue)
5. Tableaux groupes par categorie

PAS ENCORE : ajout, modification, suppression (etapes 2.A.3.b et c)

A lancer depuis ~/Desktop/devia :
    python3 add_catalogue_view.py
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

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_catalogue_view"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MODIFICATION 1 : Ajouter Catalogue au menu (ligne 686)
# ================================================================

old_menu = '''{[{ id: "devis", label: "Devis" }, { id: "projets", label: "Projets" }, { id: "parametres", label: "Parametres" }, { id: "compte", label: "Compte" }].map(tab => ('''

new_menu = '''{[{ id: "devis", label: "Devis" }, { id: "projets", label: "Projets" }, { id: "catalogue", label: "Catalogue" }, { id: "parametres", label: "Parametres" }, { id: "compte", label: "Compte" }].map(tab => ('''

if 'id: "catalogue"' in content:
    print("[INFO] Onglet Catalogue deja present dans le menu, skip modification 1")
else:
    if old_menu not in content:
        print("ERREUR : impossible de trouver le menu existant.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_menu, new_menu, 1)
    print("[OK] Onglet 'Catalogue' ajoute au menu")

# ================================================================
# MODIFICATION 2 : Ajouter les states pour catalogues
# On les ajoute juste apres const [projects, setProjects] = useState([]);
# ================================================================

old_projects_state_marker = "const [projects, setProjects] = useState([]);"

if "marchePrix" in content and "setMarchePrix" in content:
    print("[INFO] States catalogues deja presents, skip modification 2")
else:
    new_states = '''const [projects, setProjects] = useState([]);
  const [marchePrix, setMarchePrix] = useState([]);
  const [catalogueEntreprise, setCatalogueEntreprise] = useState([]);
  const [activeCatalogTab, setActiveCatalogTab] = useState("marche");
  const [loadingCatalogues, setLoadingCatalogues] = useState(false);'''

    if old_projects_state_marker not in content:
        print("ERREUR : impossible de trouver le useState projects.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_projects_state_marker, new_states, 1)
    print("[OK] States catalogues ajoutes")

# ================================================================
# MODIFICATION 3 : Ajouter useEffect pour charger les catalogues
# On l'ajoute juste apres le useEffect loadProjects
# ================================================================

old_loadprojects_end = '''    loadProjects();
  }, []);'''

if "loadCatalogues" in content:
    print("[INFO] useEffect loadCatalogues deja present, skip modification 3")
else:
    new_loadcatalogues = '''    loadProjects();
  }, []);

  // Charge les 2 catalogues depuis Supabase
  useEffect(() => {
    const loadCatalogues = async () => {
      setLoadingCatalogues(true);
      try {
        // Catalogue marche DEVIA (lecture seule, accessible a tous)
        const { data: marcheData, error: marcheError } = await supabase
          .from("marche_prix")
          .select("*")
          .eq("actif", true)
          .order("categorie")
          .order("designation");
        if (marcheError) {
          console.error("Erreur chargement marche_prix:", marcheError);
        } else if (marcheData) {
          setMarchePrix(marcheData);
        }

        // Catalogue entreprise (perso a l'utilisateur)
        const { data: { user } } = await supabase.auth.getUser();
        if (user) {
          const { data: persoData, error: persoError } = await supabase
            .from("catalogue_entreprise")
            .select("*")
            .eq("user_id", user.id)
            .eq("actif", true)
            .order("categorie")
            .order("designation");
          if (persoError) {
            console.error("Erreur chargement catalogue_entreprise:", persoError);
          } else if (persoData) {
            setCatalogueEntreprise(persoData);
          }
        }
      } catch (e) {
        console.error("Erreur loadCatalogues:", e);
      } finally {
        setLoadingCatalogues(false);
      }
    };
    loadCatalogues();
  }, []);'''

    if old_loadprojects_end not in content:
        print("ERREUR : impossible de trouver la fin de loadProjects useEffect.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_loadprojects_end, new_loadcatalogues, 1)
    print("[OK] useEffect loadCatalogues ajoute")

# ================================================================
# MODIFICATION 4 : Ajouter la vue Catalogue
# On l'insere juste avant {activeTab === "parametres" && (
# ================================================================

old_parametres_marker = '{activeTab === "parametres" && ('

if 'activeTab === "catalogue"' in content:
    print("[INFO] Vue Catalogue deja presente, skip modification 4")
else:
    new_catalogue_view = '''{activeTab === "catalogue" && (
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700 }}>Catalogue</h2>
          <Badge color="#60a5fa">
            {activeCatalogTab === "marche" ? marchePrix.length + " materiaux" : catalogueEntreprise.length + " materiaux"}
          </Badge>
        </div>

        {/* Onglets internes */}
        <div style={{ display: "flex", gap: 4, marginBottom: 20, borderBottom: "1px solid #1e2231" }}>
          {[
            { id: "marche", label: "Marche DEVIA", icon: "&#x1F4CA;" },
            { id: "perso", label: "Mon catalogue", icon: "&#x1F4DD;" }
          ].map(t => (
            <button key={t.id} onClick={() => setActiveCatalogTab(t.id)}
              style={{
                background: "transparent",
                border: "none",
                borderBottom: activeCatalogTab === t.id ? "2px solid #f0c040" : "2px solid transparent",
                color: activeCatalogTab === t.id ? "#f0c040" : "#545870",
                cursor: "pointer",
                padding: "10px 18px",
                fontSize: 14,
                fontWeight: activeCatalogTab === t.id ? 600 : 400,
                transition: "all 0.15s"
              }}
              dangerouslySetInnerHTML={{ __html: t.icon + " " + t.label }} />
          ))}
        </div>

        {loadingCatalogues ? (
          <div style={{ ...cardStyle, textAlign: "center", padding: 40, color: "#545870" }}>
            Chargement du catalogue...
          </div>
        ) : (
          <>
            {/* TAB MARCHE DEVIA */}
            {activeCatalogTab === "marche" && (
              <>
                <div style={{ ...cardStyle, padding: 16, marginBottom: 16, background: "#0f1117", borderColor: "#60a5fa44" }}>
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
                </div>
                {(() => {
                  const grouped = marchePrix.reduce((acc, m) => {
                    if (!acc[m.categorie]) acc[m.categorie] = [];
                    acc[m.categorie].push(m);
                    return acc;
                  }, {});
                  const orderedCats = ["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie", "Main d'oeuvre"];
                  const icons = {
                    "Charpente": "&#x1FAB5;",
                    "Bardage": "&#x1F3E0;",
                    "Couverture": "&#x1F7EB;",
                    "Isolation": "&#x1F9CA;",
                    "Quincaillerie": "&#x1F529;",
                    "Main d'oeuvre": "&#x1F477;"
                  };
                  return orderedCats.map(cat => {
                    const items = grouped[cat] || [];
                    if (items.length === 0) return null;
                    return (
                      <div key={cat} style={{ marginBottom: 24 }}>
                        <h3 style={{ fontSize: 15, fontWeight: 700, color: "#f0c040", marginBottom: 10, display: "flex", alignItems: "center", gap: 8 }}>
                          <span dangerouslySetInnerHTML={{ __html: icons[cat] || "" }} />
                          {cat} <span style={{ color: "#545870", fontWeight: 400, fontSize: 13 }}>({items.length})</span>
                        </h3>
                        <div style={{ ...cardStyle, padding: 0, overflow: "hidden" }}>
                          <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                              <tr style={{ background: "#0f1117" }}>
                                <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Designation</th>
                                <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Dimensions</th>
                                <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Unite</th>
                                <th style={{ padding: "10px 12px", textAlign: "right", color: "#545870", fontSize: 12, fontWeight: 600 }}>Prix HT</th>
                              </tr>
                            </thead>
                            <tbody>
                              {items.map((m, i) => (
                                <tr key={m.id} style={{ borderTop: "1px solid #1e2231", background: i % 2 === 0 ? "transparent" : "#0f111740" }}>
                                  <td style={{ padding: "10px 12px", fontSize: 13 }}>{m.designation}</td>
                                  <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.dimensions || "-"}</td>
                                  <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.unite}</td>
                                  <td style={{ padding: "10px 12px", textAlign: "right", fontSize: 13, color: "#f0c040", fontWeight: 600 }}>
                                    {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} EUR
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    );
                  });
                })()}
              </>
            )}

            {/* TAB MON CATALOGUE */}
            {activeCatalogTab === "perso" && (
              <>
                <div style={{ ...cardStyle, padding: 16, marginBottom: 16, background: "#0f1117", borderColor: "#3ecf8e44" }}>
                  <div style={{ display: "flex", alignItems: "start", gap: 12 }}>
                    <div style={{ fontSize: 20 }}>&#x1F4A1;</div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>Mon catalogue d'entreprise</div>
                      <div style={{ color: "#545870", fontSize: 13, lineHeight: 1.5 }}>
                        Vos prix personnels, prioritaires sur le catalogue marche.
                        Ajout et modification disponibles prochainement.
                      </div>
                    </div>
                  </div>
                </div>
                {catalogueEntreprise.length === 0 ? (
                  <div style={{ ...cardStyle, textAlign: "center", padding: 40 }}>
                    <div style={{ fontSize: 40, marginBottom: 12 }}>&#x1F4DD;</div>
                    <div style={{ color: "#545870", marginBottom: 8 }}>Aucun materiau dans votre catalogue.</div>
                    <div style={{ color: "#545870", fontSize: 13 }}>Bientot vous pourrez ajouter vos propres prix.</div>
                  </div>
                ) : (
                  <div style={{ ...cardStyle, padding: 0, overflow: "hidden" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead>
                        <tr style={{ background: "#0f1117" }}>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Categorie</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Designation</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Dimensions</th>
                          <th style={{ padding: "10px 12px", textAlign: "left", color: "#545870", fontSize: 12, fontWeight: 600 }}>Unite</th>
                          <th style={{ padding: "10px 12px", textAlign: "right", color: "#545870", fontSize: 12, fontWeight: 600 }}>Prix HT</th>
                        </tr>
                      </thead>
                      <tbody>
                        {catalogueEntreprise.map((m, i) => (
                          <tr key={m.id} style={{ borderTop: "1px solid #1e2231", background: i % 2 === 0 ? "transparent" : "#0f111740" }}>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#60a5fa" }}>{m.categorie}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13 }}>{m.designation}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.dimensions || "-"}</td>
                            <td style={{ padding: "10px 12px", fontSize: 13, color: "#545870" }}>{m.unite}</td>
                            <td style={{ padding: "10px 12px", textAlign: "right", fontSize: 13, color: "#3ecf8e", fontWeight: 600 }}>
                              {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} EUR
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    )}

    ''' + old_parametres_marker

    if old_parametres_marker not in content:
        print("ERREUR : impossible de trouver le bloc parametres.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_parametres_marker, new_catalogue_view, 1)
    print("[OK] Vue Catalogue ajoutee")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("ETAPE 2.A.3.a APPLIQUEE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Onglet 'Catalogue' ajoute au menu principal")
print("  2. States React : marchePrix, catalogueEntreprise, activeCatalogTab")
print("  3. Chargement automatique des 2 catalogues depuis Supabase")
print("  4. Vue Catalogue avec 2 onglets internes :")
print("     - Marche DEVIA : 34 materiaux groupes par categorie (lecture seule)")
print("     - Mon catalogue : message 'Aucun materiau' (vide pour l'instant)")
print()
print("PROCHAINE ETAPE :")
print("  git add devia.jsx")
print("  git commit -m 'Ajout onglet Catalogue (affichage seul)'")
print("  git push")
print()
print("TESTS :")
print("  1. Aller sur devia-iota.vercel.app")
print("  2. Cliquer sur l'onglet 'Catalogue' (nouveau)")
print("  3. Voir les 34 materiaux marche DEVIA groupes par categorie")
print("  4. Cliquer sur 'Mon catalogue' (vide)")
print()
print(f"BACKUP : {backup_name}")
