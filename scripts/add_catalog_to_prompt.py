#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEVIA - Etape 2.A.4 : Integrer les catalogues dans le prompt IA
Ajoute :
1. Choix du catalogue sur la page Devis (Marche / Mon catalogue)
2. Si Mon catalogue : option 'Completer avec marche' (cochee par defaut)
3. Construction de la liste des prix selon le choix
4. Injection dans le prompt systeme envoye a Claude
5. Indicateur dans le devis genere : quel catalogue a ete utilise

A lancer depuis ~/Desktop/devia :
    python3 add_catalog_to_prompt.py
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

backup_name = f"devia.jsx.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_before_catalog_to_prompt"
shutil.copy("devia.jsx", backup_name)
print(f"[OK] Backup cree : {backup_name}")

with open("devia.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# ================================================================
# MODIFICATION 1 : Ajouter les states pour le choix de catalogue
# ================================================================

old_editing_state = "const [editingCatalogId, setEditingCatalogId] = useState(null);"

if "catalogChoice" in content:
    print("[INFO] States catalogChoice deja presents, skip modification 1")
else:
    new_states = '''const [editingCatalogId, setEditingCatalogId] = useState(null);
  const [catalogChoice, setCatalogChoice] = useState("marche");
  const [completeWithMarket, setCompleteWithMarket] = useState(true);'''

    if old_editing_state not in content:
        print("ERREUR : impossible de trouver editingCatalogId state.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_editing_state, new_states, 1)
    print("[OK] States catalogChoice et completeWithMarket ajoutes")

# ================================================================
# MODIFICATION 2 : Modifier handleGenerate pour construire la liste de prix
# et l'injecter dans le prompt
# ================================================================

# On cherche la ligne du systemPrompt actuel (apres l'ajout DETECTION TYPE)
old_prompt_block = '''const systemPrompt = "Tu es DEVIA, expert charpente bois. Genere un devis professionnel EN FRANCAIS. " +
"DETECTION DU TYPE DE PROJET : analyse la description et choisis 1 valeur pour type_projet : " +
"'carport' (si carport, abri voiture, auvent ouvert sans murs, structure sur potaux), " +
"'charpente_trad' (charpente traditionnelle de maison, toit 2 pans avec murs), " +
"'hangar' (hangar agricole, batiment industriel, grand volume couvert), " +
"'abri' (abri jardin, abri petit volume), " +
"'autre' (si rien ne correspond clairement). " +'''

new_prompt_block = '''// Construction de la liste de prix selon le choix utilisateur
    let prixList = [];
    let catalogSource = "marche";
    if (catalogChoice === "marche") {
      prixList = marchePrix;
      catalogSource = "marche";
    } else if (catalogChoice === "perso") {
      if (completeWithMarket) {
        // Catalogue perso prioritaire, complete par marche pour les manquants
        prixList = [...catalogueEntreprise];
        const designationsPerso = new Set(catalogueEntreprise.map(p => (p.designation + "|" + (p.dimensions || "")).toLowerCase()));
        marchePrix.forEach(m => {
          const key = (m.designation + "|" + (m.dimensions || "")).toLowerCase();
          if (!designationsPerso.has(key)) {
            prixList.push(m);
          }
        });
        catalogSource = "perso+marche";
      } else {
        prixList = catalogueEntreprise;
        catalogSource = "perso";
      }
    }

    // Format compact pour le prompt (economiser les tokens)
    const prixListText = prixList.length > 0
      ? prixList.map(p => `- ${p.categorie} | ${p.designation} | ${p.dimensions || "-"} | ${p.unite} | ${Number(p.prix_ht).toFixed(2)} EUR`).join("\\n")
      : "Aucun catalogue fourni - estime les prix toi-meme.";

    const systemPrompt = "Tu es DEVIA, expert charpente bois. Genere un devis professionnel EN FRANCAIS. " +
"DETECTION DU TYPE DE PROJET : analyse la description et choisis 1 valeur pour type_projet : " +
"'carport' (si carport, abri voiture, auvent ouvert sans murs, structure sur potaux), " +
"'charpente_trad' (charpente traditionnelle de maison, toit 2 pans avec murs), " +
"'hangar' (hangar agricole, batiment industriel, grand volume couvert), " +
"'abri' (abri jardin, abri petit volume), " +
"'autre' (si rien ne correspond clairement). " +
"\\n\\nCATALOGUE DE PRIX A UTILISER (source: " + catalogSource + ") :\\n" + prixListText + "\\n\\n" +
"REGLES PRIX : 1) Pour chaque poste de devis, utilise EN PRIORITE un materiau du catalogue ci-dessus si disponible. " +
"2) Le prix unitaire HT doit correspondre exactement au prix du catalogue. " +
"3) Si un materiau necessaire n'existe pas dans le catalogue, estime le prix au mieux mais signale-le dans les notes. " +
"4) Adapte les quantites au projet decrit. " +'''

if "CATALOGUE DE PRIX A UTILISER" in content:
    print("[INFO] Prompt deja modifie pour utiliser le catalogue, skip modification 2")
else:
    if old_prompt_block not in content:
        print("ERREUR : impossible de trouver le prompt systeme.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_prompt_block, new_prompt_block, 1)
    print("[OK] Prompt enrichi avec le catalogue de prix")

# ================================================================
# MODIFICATION 3 : Stocker catalogSource dans le devis result
# ================================================================

# Apres setResult(parsed), on ajoute catalogSource au result
old_setresult = "setResult(parsed);"
new_setresult = '''setResult({ ...parsed, _catalogSource: catalogSource });'''

if "_catalogSource:" in content:
    print("[INFO] catalogSource deja stocke dans result, skip modification 3")
else:
    if old_setresult not in content:
        print("ATTENTION : ligne setResult(parsed) introuvable, skip")
    else:
        content = content.replace(old_setresult, new_setresult, 1)
        print("[OK] catalogSource stocke dans result")

# ================================================================
# MODIFICATION 4 : Ajouter le selecteur de catalogue avant le bouton Generer
# On l'ajoute juste avant le bouton "Generer le devis"
# ================================================================

old_generate_button = '''<button onClick={handleSubmit}'''

if "selecteur de catalogue" in content or "Catalogue a utiliser" in content:
    print("[INFO] Selecteur catalogue deja present, skip modification 4")
else:
    catalog_selector = '''{/* Selecteur de catalogue */}
              <div style={{ ...cardStyle, padding: 16, marginBottom: 16, background: "#0f1117" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                  <span style={{ fontSize: 16 }}>&#x1F4D6;</span>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>Catalogue a utiliser pour ce devis</div>
                </div>
                <div style={{ display: "grid", gap: 8 }}>
                  <label style={{ display: "flex", alignItems: "center", gap: 10, padding: 10, borderRadius: 6, background: catalogChoice === "marche" ? "#f0c04018" : "transparent", border: catalogChoice === "marche" ? "1px solid #f0c040" : "1px solid #1e2231", cursor: "pointer" }}>
                    <input type="radio" name="catalog" checked={catalogChoice === "marche"}
                      onChange={() => setCatalogChoice("marche")}
                      style={{ accentColor: "#f0c040" }} />
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600 }}>Catalogue marche DEVIA</div>
                      <div style={{ fontSize: 12, color: "#545870" }}>{marchePrix.length} materiaux - prix moyens du marche</div>
                    </div>
                  </label>
                  <label style={{ display: "flex", alignItems: "center", gap: 10, padding: 10, borderRadius: 6, background: catalogChoice === "perso" ? "#3ecf8e18" : "transparent", border: catalogChoice === "perso" ? "1px solid #3ecf8e" : "1px solid #1e2231", cursor: "pointer" }}>
                    <input type="radio" name="catalog" checked={catalogChoice === "perso"}
                      onChange={() => setCatalogChoice("perso")}
                      style={{ accentColor: "#3ecf8e" }} />
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600 }}>Mon catalogue d'entreprise</div>
                      <div style={{ fontSize: 12, color: "#545870" }}>{catalogueEntreprise.length} materiaux personnels</div>
                    </div>
                  </label>
                  {catalogChoice === "perso" && (
                    <label style={{ display: "flex", alignItems: "center", gap: 10, padding: "6px 10px", marginLeft: 28, fontSize: 13, cursor: "pointer", color: completeWithMarket ? "#e8eaf2" : "#545870" }}>
                      <input type="checkbox" checked={completeWithMarket}
                        onChange={(e) => setCompleteWithMarket(e.target.checked)}
                        style={{ accentColor: "#f0c040" }} />
                      <span>Completer les materiaux manquants avec les prix marche DEVIA</span>
                    </label>
                  )}
                </div>
              </div>

              ''' + old_generate_button

    if old_generate_button not in content:
        print("ERREUR : impossible de trouver le bouton Generer.")
        shutil.copy(backup_name, "devia.jsx")
        sys.exit(1)
    content = content.replace(old_generate_button, catalog_selector, 1)
    print("[OK] Selecteur de catalogue ajoute avant le bouton Generer")

# ================================================================
# MODIFICATION 5 : Afficher le badge catalogue utilise dans le devis genere
# Apres le titre du devis affiche
# ================================================================

old_devis_header = '''<h2 style={{ fontSize: 20, fontWeight: 700 }}>{result.projet ? result.projet.description : "Devis charpente"}</h2>
                <div style={{ color: "#545870", fontSize: 14 }}>{result.projet ? result.projet.commune : ""} - {new Date().toLocaleDateString("fr-FR")}</div>'''

new_devis_header = '''<h2 style={{ fontSize: 20, fontWeight: 700 }}>{result.projet ? result.projet.description : "Devis charpente"}</h2>
                <div style={{ color: "#545870", fontSize: 14, display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                  <span>{result.projet ? result.projet.commune : ""} - {new Date().toLocaleDateString("fr-FR")}</span>
                  {result._catalogSource && (
                    <span style={{
                      fontSize: 11,
                      fontWeight: 600,
                      padding: "2px 8px",
                      borderRadius: 12,
                      background: result._catalogSource === "perso" ? "#3ecf8e18" : (result._catalogSource === "perso+marche" ? "#a78bfa18" : "#f0c04018"),
                      color: result._catalogSource === "perso" ? "#3ecf8e" : (result._catalogSource === "perso+marche" ? "#a78bfa" : "#f0c040"),
                      border: "1px solid " + (result._catalogSource === "perso" ? "#3ecf8e44" : (result._catalogSource === "perso+marche" ? "#a78bfa44" : "#f0c04044"))
                    }}>
                      {result._catalogSource === "perso" ? "Catalogue perso" : (result._catalogSource === "perso+marche" ? "Perso + complement marche" : "Catalogue marche DEVIA")}
                    </span>
                  )}
                </div>'''

if "_catalogSource &&" in content:
    print("[INFO] Badge catalogue deja present dans le header, skip modification 5")
else:
    if old_devis_header not in content:
        print("ATTENTION : header devis non trouve, badge non ajoute (pas grave)")
    else:
        content = content.replace(old_devis_header, new_devis_header, 1)
        print("[OK] Badge catalogue utilise ajoute dans le header du devis")

# Ecrire
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("ETAPE 2.A.4 APPLIQUEE")
print("=" * 60)
print()
print("CE QUI A CHANGE :")
print("  1. Choix du catalogue sur la page Devis (Marche / Perso)")
print("  2. Option 'Completer avec marche' (cochee par defaut si Perso)")
print("  3. Le prompt IA recoit la liste des prix selon le choix")
print("  4. Claude utilise ces prix prioritairement dans le devis")
print("  5. Badge dans le devis genere : 'Catalogue marche', 'Perso', ou 'Perso + complement marche'")
print()
print("PROCHAINE ETAPE :")
print("  git add devia.jsx")
print("  git commit -m 'Catalogue de prix injecte dans le prompt IA'")
print("  git push")
print()
print("TESTS :")
print("  1. Sur la page Devis : verifier le selecteur de catalogue")
print("  2. Cas A : Marche DEVIA -> Generer un devis carport simple -> verifier badge marche")
print("  3. Cas B : Mon catalogue (vide ou peu rempli) sans completer -> prix peuvent etre faux")
print("  4. Cas C : Mon catalogue + completer avec marche -> devis complet avec mix")
print("  5. Verifier que les prix dans le devis correspondent EXACTEMENT au catalogue choisi")
print()
print(f"BACKUP : {backup_name}")
