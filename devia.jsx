import { useState, useRef, useEffect } from "react";
import * as THREE from "three";
import { useAuth } from "./src/hooks/useAuth.js";
import Login from "./src/components/Login.jsx";
import { signOut } from "./src/lib/auth.js";
import { supabase } from "./src/lib/supabase.js";
import { useLicense } from "./src/hooks/useLicense.js";
import ActivateLicense from "./src/components/ActivateLicense.jsx";
import SubscriptionBanner from "./src/components/SubscriptionBanner.jsx";
import UserMenu from "./src/components/UserMenu.jsx";

const T = {
bg: "#08090c", surface: "#0f1117", card: "#13161f", border: "#1e2231",
accent: "#f0c040", accentLo: "#f0c04018", text: "#e8eaf2", muted: "#545870",
dim: "#2a2e40", ok: "#3ecf8e", blue: "#60a5fa", red: "#ef4444",
purple: "#a78bfa", orange: "#f97316",
};

const ZONES_DB = {
"paris": { neige: "A1", vent: "2", sismique: "1" },
"lyon": { neige: "A2", vent: "2", sismique: "1" },
"marseille": { neige: "A1", vent: "3", sismique: "2" },
"bordeaux": { neige: "A1", vent: "2", sismique: "2" },
"toulouse": { neige: "A2", vent: "2", sismique: "3" },
"nantes": { neige: "A1", vent: "2", sismique: "1" },
"strasbourg": { neige: "B1", vent: "1", sismique: "3" },
"lille": { neige: "A1", vent: "3", sismique: "1" },
"nice": { neige: "A2", vent: "3", sismique: "3" },
"grenoble": { neige: "B2", vent: "1", sismique: "4" },
"rennes": { neige: "A1", vent: "2", sismique: "1" },
"rouen": { neige: "A1", vent: "3", sismique: "1" },
"dijon": { neige: "B1", vent: "1", sismique: "2" },
"nancy": { neige: "B1", vent: "1", sismique: "2" },
"reims": { neige: "A2", vent: "2", sismique: "1" },
"toulon": { neige: "A1", vent: "3", sismique: "2" },
"brest": { neige: "A1", vent: "4", sismique: "1" },
"montpellier": { neige: "A1", vent: "3", sismique: "3" },
"bayonne": { neige: "A3", vent: "2", sismique: "3" },
"pau": { neige: "B1", vent: "2", sismique: "4" },
"chamonix": { neige: "C1", vent: "2", sismique: "4" },
"annecy": { neige: "C1", vent: "2", sismique: "4" },
"bruxelles": { neige: "A1", vent: "2", sismique: "0" },
"lausanne": { neige: "C1", vent: "2", sismique: "2" },
"geneve": { neige: "B2", vent: "2", sismique: "2" },
"luxembourg": { neige: "A2", vent: "2", sismique: "1" },
};

function getZone(commune, altitude) {
const key = commune.toLowerCase().trim();
let zone = null;
for (const k of Object.keys(ZONES_DB)) {
if (key.includes(k) || k.includes(key)) { zone = ZONES_DB[k]; break; }
}
if (!zone) zone = { neige: "A2", vent: "2", sismique: "1" };
const nl = zone.neige.match(/([A-D])(\d?)/);
const nL = nl ? nl[1] : "A";
const nC = nl ? parseInt(nl[2] || "1") : 1;
const altNum = parseInt(altitude) || 200;
const neigeBase = { A: { 1: 0.45, 2: 0.45, 3: 0.55 }, B: { 1: 0.65, 2: 0.90 }, C: { 1: 1.40, 2: 1.70 }, D: { 0: 2.30 } };
let sk = (neigeBase[nL] || {})[nC] || 0.65;
if (altNum > 200) sk = sk * (1 + ((altNum - 200) / 800) * 1.5);
const vb0 = { "1": 22, "2": 25, "3": 28, "4": 32 }[zone.vent] || 25;
const qb = (1.25 * vb0 * vb0) / 2000;
const ag = { "0": 0, "1": 0.07, "2": 0.10, "3": 0.15, "4": 0.20 }[zone.sismique] || 0.07;
return { ...zone, sk: Math.round(sk * 100) / 100, qb: Math.round(qb * 100) / 100, ag };
}

function Viewer3D({ params }) {
  const mountRef = useRef(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const w = mountRef.current.clientWidth;
    const h = mountRef.current.clientHeight;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.shadowMap.enabled = true;
    mountRef.current.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 200);
    camera.position.set(12, 8, 12);

    scene.add(new THREE.AmbientLight(0xffffff, 0.4));
    const sun = new THREE.DirectionalLight(0xfff8e7, 1.2);
    sun.position.set(10, 20, 10);
    sun.castShadow = true;
    scene.add(sun);

    const L = params.longueur || 8;
    const lg = params.largeur || 6;
    const H = params.hauteur || 3;
    const pente = params.pente || 35;
    const typeProjet = params.type_projet || "charpente_trad";

    const woodMat = new THREE.MeshLambertMaterial({ color: 0xc4894a });
    const roofMat = new THREE.MeshLambertMaterial({ color: 0x8b6355, side: THREE.DoubleSide });
    const wallMat = new THREE.MeshLambertMaterial({ color: 0xf0ece0, transparent: true, opacity: 0.2, side: THREE.DoubleSide });

    const addBox = (sx, sy, sz, px, py, pz, mat, rot) => {
      const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), mat || woodMat);
      m.position.set(px, py, pz);
      if (rot) m.rotation.set(...rot);
      m.castShadow = true;
      scene.add(m);
    };

    // ============================================================
    // FONCTION : dessine une charpente traditionnelle (2 pans)
    // ============================================================
    const drawCharpenteTrad = () => {
      const hf = lg / 2 * Math.tan((pente * Math.PI) / 180);

      // Murs (4 cotes)
      [
        [L, H, 0.15, 0, H/2, lg/2],
        [L, H, 0.15, 0, H/2, -lg/2],
        [0.15, H, lg, -L/2, H/2, 0],
        [0.15, H, lg, L/2, H/2, 0]
      ].forEach(([sx, sy, sz, px, py, pz]) => addBox(sx, sy, sz, px, py, pz, wallMat));

      // Fermes
      const nb = Math.max(2, Math.ceil(L / 2.5));
      for (let i = 0; i <= nb; i++) {
        const x = -L/2 + (i/nb) * L;
        const ang = Math.atan(hf / (lg/2));
        const pl = (lg/2) / Math.cos(ang);
        addBox(pl, 0.12, 0.12, x, H + hf/2, lg/4, woodMat, [ang, 0, 0]);
        addBox(pl, 0.12, 0.12, x, H + hf/2, -lg/4, woodMat, [-ang, 0, 0]);
        addBox(0.12, hf + 0.1, 0.12, x, H + hf/2, 0);
      }

      // Faitage
      addBox(L + 0.4, 0.14, 0.14, 0, H + hf, 0);

      // Toiture (2 pans)
      const ang = Math.atan(hf / (lg/2));
      const pl = (lg/2) / Math.cos(ang);
      const rg = new THREE.PlaneGeometry(L + 0.6, pl + 0.2);
      const r1 = new THREE.Mesh(rg, roofMat);
      r1.position.set(0, H + hf/2, lg/4);
      r1.rotation.x = ang - Math.PI/2;
      scene.add(r1);
      const r2 = new THREE.Mesh(rg, roofMat);
      r2.position.set(0, H + hf/2, -lg/4);
      r2.rotation.x = -(ang - Math.PI/2);
      scene.add(r2);
    };

    // ============================================================
    // FONCTION : dessine un carport (1 pente + potaux + pas de murs)
    // ============================================================
    const drawCarport = () => {
      // Carport : la pente descend de l'ARRIERE (Z=+lg/2, haut) vers l'AVANT (Z=-lg/2, bas)
      // C'est l'inverse du fix precedent.
      const denivele = lg * Math.tan((pente * Math.PI) / 180);
      const Hbas = H;
      const Hhaut = H + denivele;

      // 4 POTAUX
      // AVANT (Z negatif, cube ROUGE) = potaux BAS
      // ARRIERE (Z positif, cube BLEU) = potaux HAUTS
      const sectionPotau = 0.18;
      // Potau avant gauche (BAS)
      addBox(sectionPotau, Hbas, sectionPotau, -L/2, Hbas/2, -lg/2);
      // Potau avant droit (BAS)
      addBox(sectionPotau, Hbas, sectionPotau, L/2, Hbas/2, -lg/2);
      // Potau arriere gauche (HAUT)
      addBox(sectionPotau, Hhaut, sectionPotau, -L/2, Hhaut/2, lg/2);
      // Potau arriere droit (HAUT)
      addBox(sectionPotau, Hhaut, sectionPotau, L/2, Hhaut/2, lg/2);

      // 2 SABLIERES
      // Sabliere avant (en bas)
      addBox(L + 0.3, 0.16, 0.16, 0, Hbas, -lg/2);
      // Sabliere arriere (en haut)
      addBox(L + 0.3, 0.16, 0.16, 0, Hhaut, lg/2);

      // PANNES (entre sablieres, suivent la pente)
      const nbPannes = 3;
      for (let i = 0; i < nbPannes; i++) {
        const t = i / (nbPannes - 1); // 0 a 1
        const z = -lg/2 + t * lg;       // de avant a arriere
        const y = Hbas + t * denivele;  // de bas a haut (pente montante avant->arriere)
        addBox(L + 0.3, 0.14, 0.14, 0, y, z);
      }

      // CHEVRONS (sens largeur, en pente)
      const nbChevrons = Math.max(3, Math.ceil(L / 1.0));
      const ang = Math.atan(denivele / lg);
      const longueurChevron = lg / Math.cos(ang);
      for (let i = 0; i <= nbChevrons; i++) {
        const x = -L/2 + (i / nbChevrons) * L;
        const yCentre = Hbas + denivele/2;
        // Rotation X positive pour pente avant bas -> arriere haut
        addBox(0.10, 0.10, longueurChevron + 0.2, x, yCentre, 0, woodMat, [ang, 0, 0]);
      }

      // TOITURE (1 seul pan, rotation sur axe X au lieu de Z)
      // Le toit est tourne dans l'autre dimension par rapport a la structure
      const rg = new THREE.PlaneGeometry(longueurChevron + 0.3, L + 0.4);
      const roof = new THREE.Mesh(rg, roofMat);
      roof.position.set(0, Hbas + denivele/2 + 0.1, 0);
      // Combinaison de rotations pour que le toit penche cote gauche/droite
      roof.rotation.z = ang;
      roof.rotation.y = Math.PI/2;
      scene.add(roof);

    };

    // ============================================================
    // SWITCH : choisir la fonction selon type_projet
    // ============================================================
    if (typeProjet === "carport") {
      drawCarport();
    } else {
      drawCharpenteTrad();
    }

    // SOL (commun a tous les types)
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(30, 30),
      new THREE.MeshLambertMaterial({ color: 0x1a1f2e })
    );
    ground.rotation.x = -Math.PI/2;
    scene.add(ground);

    // ANIMATION (rotation camera)
    let angle = 0, animId;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      angle += 0.005;
      camera.position.x = Math.cos(angle) * 16;
      camera.position.z = Math.sin(angle) * 16;
      // Centre de la camera : adapter selon type
      const yCentre = typeProjet === "carport"
        ? H + (lg * Math.tan((pente * Math.PI) / 180)) / 2
        : H/2 + (lg/2 * Math.tan((pente * Math.PI) / 180)) / 2;
      camera.lookAt(0, yCentre, 0);
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(animId);
      renderer.dispose();
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current)
        mountRef.current.removeChild(renderer.domElement);
    };
  }, [params]);

  return <div ref={mountRef} style={{ width: "100%", height: "100%", borderRadius: 8 }} />;
}

const QUESTIONS = {
type: {
label: "Type de charpente",
options: [
{ val: "fermette", label: "Fermette industrielle", icon: "🏭" },
{ val: "traditionnelle", label: "Charpente traditionnelle", icon: "🪵" },
{ val: "lamelle", label: "Lamelle-colle", icon: "✨" },
{ val: "metalique", label: "Charpente metallique", icon: "⚙️" },
],
},
couverture: {
label: "Type de couverture",
options: [
{ val: "tuile_terre", label: "Tuile terre cuite", icon: "🟤" },
{ val: "tuile_beton", label: "Tuile beton", icon: "⬜" },
{ val: "ardoise", label: "Ardoise naturelle", icon: "🔲" },
{ val: "bac_acier", label: "Bac acier", icon: "📐" },
],
},
essence: {
label: "Essence du bois",
options: [
{ val: "sapin", label: "Sapin / Epicea", icon: "🌲" },
{ val: "pin", label: "Pin Maritime", icon: "🌳" },
{ val: "douglas", label: "Douglas", icon: "🌲" },
{ val: "chene", label: "Chene", icon: "🌳" },
],
},
combles: {
label: "Utilisation des combles",
options: [
{ val: "perdus", label: "Combles perdus", icon: "📦" },
{ val: "amenageables", label: "Amenageables", icon: "🏠" },
{ val: "amenages", label: "Amenages", icon: "🛋️" },
],
},
};

function QuestionsScreen({ detected, onValidate }) {
const [answers, setAnswers] = useState({});
const missing = Object.keys(QUESTIONS).filter(k => !detected[k]);
const allAnswered = missing.every(k => answers[k]);
return (
<div style={{ padding: 24, maxWidth: 600, margin: "0 auto" }}>
<div style={{ textAlign: "center", marginBottom: 28 }}>
<div style={{ fontSize: 40, marginBottom: 8 }}>🤔</div>
<div style={{ fontSize: 20, fontWeight: 700, color: "#e8eaf2" }}>Quelques precisions</div>
<div style={{ color: "#545870", fontSize: 14, marginTop: 4 }}>Pour un devis precis, quelques informations manquantes</div>
</div>
{missing.map(key => (
<div key={key} style={{ marginBottom: 20 }}>
<div style={{ color: "#545870", fontSize: 13, marginBottom: 10, textTransform: "uppercase", letterSpacing: 1 }}>{QUESTIONS[key].label}</div>
<div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
{QUESTIONS[key].options.map(opt => (
<button key={opt.val} onClick={() => setAnswers(prev => ({ ...prev, [key]: opt.val }))}
style={{
background: answers[key] === opt.val ? "#f0c04018" : "#13161f",
border: answers[key] === opt.val ? "1px solid #f0c040" : "1px solid #1e2231",
borderRadius: 8, padding: "12px 10px", cursor: "pointer",
color: answers[key] === opt.val ? "#f0c040" : "#e8eaf2",
textAlign: "left", display: "flex", alignItems: "center", gap: 8, fontSize: 14,
}}>
<span style={{ fontSize: 20 }}>{opt.icon}</span>{opt.label}
</button>
))}
</div>
</div>
))}
<button onClick={() => onValidate({ ...detected, ...answers })} disabled={!allAnswered}
style={{
width: "100%", padding: 14, borderRadius: 8, border: "none",
background: allAnswered ? "#f0c040" : "#2a2e40",
color: allAnswered ? "#000" : "#545870",
fontWeight: 700, fontSize: 15, cursor: allAnswered ? "pointer" : "not-allowed", marginTop: 8,
}}>
Generer le devis
</button>
</div>
);
}

function FeuilleCalcTable({ devisData, zoneData }) {
const largeur = devisData.largeur || 6;
const sk = zoneData ? zoneData.sk : 0.65;
const qb = zoneData ? zoneData.qb : 0.39;
const ag = zoneData ? zoneData.ag : 0.07;
const q_neige = sk * 0.8;
const q_vent = qb * 1.5 * 0.8;
const q_totale = q_neige + q_vent * 0.6 + 0.35 + 0.15;
const portee = largeur / 2;
const moment = (q_totale * portee * portee) / 8;
const section_requise = Math.sqrt((moment * 1000000 * 6) / 24) / 10;
const section_choisie = Math.ceil(section_requise / 25) * 25;
const rows = [
{ cat: "Charges permanentes", item: "Couverture", val: "0.35 kN/m2", ok: true },
{ cat: "Charges permanentes", item: "Charpente propre", val: "0.15 kN/m2", ok: true },
{ cat: "Charges climatiques", item: "Neige sk", val: sk.toFixed(2) + " kN/m2", ok: true },
{ cat: "Charges climatiques", item: "Neige appliquee", val: q_neige.toFixed(2) + " kN/m2", ok: true },
{ cat: "Charges climatiques", item: "Vent qb", val: qb.toFixed(2) + " kN/m2", ok: true },
{ cat: "Charges climatiques", item: "Vent applique", val: q_vent.toFixed(2) + " kN/m2", ok: true },
{ cat: "Combinaisons ELU", item: "Charge totale", val: q_totale.toFixed(2) + " kN/m2", ok: true },
{ cat: "Verification EC5", item: "Portee de calcul", val: portee.toFixed(2) + " m", ok: true },
{ cat: "Verification EC5", item: "Moment flechissant", val: moment.toFixed(2) + " kN.m", ok: true },
{ cat: "Verification EC5", item: "Section requise", val: section_requise.toFixed(0) + " mm", ok: true },
{ cat: "Verification EC5", item: "Section choisie", val: section_choisie + "x" + section_choisie + " mm", ok: section_choisie >= section_requise },
{ cat: "Sismique", item: "Acceleration ag", val: ag + " g", ok: ag < 0.15 },
{ cat: "Assemblages", item: "Connecteurs", val: "Simpson Strong-Tie", ok: true },
{ cat: "Assemblages", item: "Visserie inox A4", val: "8x120 mm / 300 mm", ok: true },
];
let lastCat = "";
return (
<div style={{ fontFamily: "monospace", fontSize: 13 }}>
<div style={{ marginBottom: 16, padding: 12, background: "#f0c04018", borderRadius: 8, border: "1px solid #f0c040" }}>
<span style={{ color: "#f0c040", fontWeight: 700 }}>Note : </span>
<span style={{ color: "#545870" }}>Calculs preliminaires EN 1990/1991/1995. A valider par un bureau d etudes.</span>
</div>
<table style={{ width: "100%", borderCollapse: "collapse" }}>
<thead>
<tr style={{ background: "#2a2e40" }}>
{["Categorie", "Parametre", "Valeur", "Statut"].map(h => (
<th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "#545870", fontSize: 11, textTransform: "uppercase" }}>{h}</th>
))}
</tr>
</thead>
<tbody>
{rows.map((r, i) => {
const showCat = r.cat !== lastCat;
lastCat = r.cat;
return (
<tr key={i} style={{ borderBottom: "1px solid #1e2231", background: i % 2 === 0 ? "transparent" : "#0f1117" }}>
<td style={{ padding: "7px 12px", color: showCat ? "#60a5fa" : "transparent", fontSize: 12, fontWeight: 600 }}>{r.cat}</td>
<td style={{ padding: "7px 12px", color: "#e8eaf2" }}>{r.item}</td>
<td style={{ padding: "7px 12px", color: "#f0c040" }}>{r.val}</td>
<td style={{ padding: "7px 12px", color: r.ok ? "#3ecf8e" : "#ef4444", fontSize: 16 }}>{r.ok ? "OK" : "!!"}</td>
</tr>
);
})}
</tbody>
</table>
<div style={{ marginTop: 16, padding: 12, background: "#13161f", borderRadius: 8, border: "1px solid #3ecf8e" }}>
<span style={{ color: "#3ecf8e", fontWeight: 700 }}>Conclusion : </span>
<span style={{ color: "#e8eaf2" }}>Section {section_choisie}x{section_choisie} mm en C24 - espacement fermes 2.0 m.</span>
</div>
</div>
);
}

function Badge({ children, color }) {
return (
<span style={{ background: color + "22", color: color, border: "1px solid " + color + "44", borderRadius: 4, padding: "2px 8px", fontSize: 12, fontWeight: 600 }}>
{children}
</span>
);
}

function DeviaMain() {
const [activeTab, setActiveTab] = useState("devis");
const [prompt, setPrompt] = useState("");
const [commune, setCommune] = useState("");
const [altitude, setAltitude] = useState("200");
const [files, setFiles] = useState([]);
const [loading, setLoading] = useState(false);
const [result, setResult] = useState(null);
const [error, setError] = useState(null);
const [view3DParams, setView3DParams] = useState({ longueur: 8, largeur: 6, hauteur: 3, pente: 35 });
const [activeResultTab, setActiveResultTab] = useState("devis");
const [showQuestions, setShowQuestions] = useState(false);
const [detectedParams, setDetectedParams] = useState({});
const [projects, setProjects] = useState([]);
  const [marchePrix, setMarchePrix] = useState([]);
  const [catalogueEntreprise, setCatalogueEntreprise] = useState([]);
  const [activeCatalogTab, setActiveCatalogTab] = useState("marche");
  const [loadingCatalogues, setLoadingCatalogues] = useState(false);
  const [showAddCatalogModal, setShowAddCatalogModal] = useState(false);
  const [catalogForm, setCatalogForm] = useState({
    categorie: "Charpente",
    categorieAutre: "",
    designation: "",
    dimensions: "",
    unite: "ml",
    prix_ht: "",
    notes: "",
  });
  const [catalogFormError, setCatalogFormError] = useState(null);
  const [savingCatalog, setSavingCatalog] = useState(false);
  const [editingCatalogId, setEditingCatalogId] = useState(null);
  const [catalogChoice, setCatalogChoice] = useState("marche");
  const [completeWithMarket, setCompleteWithMarket] = useState(true);

  // Charge les projets de l'utilisateur depuis Supabase au demarrage
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;
        const { data, error } = await supabase
          .from("projects")
          .select("*")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false });
        if (error) {
          console.error("Erreur chargement projets:", error);
          return;
        }
        if (data) {
          const formatted = data.map(p => ({
            id: p.id,
            nom: p.nom,
            commune: p.commune || "",
            date: p.created_at ? p.created_at.split("T")[0] : "",
            ttc: p.total_ttc || 0,
            dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m",
            devis_data: p.devis_data,
            zone_data: p.zone_data,
          }));
          setProjects(formatted);
        }
      } catch (e) {
        console.error("Erreur loadProjects:", e);
      }
    };
    loadProjects();
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
  }, []);

const [params, setParams] = useState({
entreprise: "", siret: "", adresse: "",
tauxHoraire: 55, tva: 20, marge: 25,
mentions: "Devis valable 30 jours.",
});
const fileInputRef = useRef(null);

const detectParams = (text) => {
const out = {};
if (/fermette|industriel/i.test(text)) out.type = "fermette";
else if (/traditionn/i.test(text)) out.type = "traditionnelle";
else if (/lamell/i.test(text)) out.type = "lamelle";
else if (/metal/i.test(text)) out.type = "metalique";
if (/tuile.*terre|terre.*cuite/i.test(text)) out.couverture = "tuile_terre";
else if (/tuile.*beton/i.test(text)) out.couverture = "tuile_beton";
else if (/ardoise/i.test(text)) out.couverture = "ardoise";
else if (/bac.*acier/i.test(text)) out.couverture = "bac_acier";
if (/sapin|epicea/i.test(text)) out.essence = "sapin";
else if (/douglas/i.test(text)) out.essence = "douglas";
else if (/chene/i.test(text)) out.essence = "chene";
else if (/pin/i.test(text)) out.essence = "pin";
if (/perdus/i.test(text)) out.combles = "perdus";
else if (/amenages/i.test(text)) out.combles = "amenages";
else if (/amenageable/i.test(text)) out.combles = "amenageables";
const dims = text.match(/(\d+)[x](\d+)/);
if (dims) { out.longueur = parseInt(dims[1]); out.largeur = parseInt(dims[2]); }
const surf = text.match(/(\d+)\s*m2/);
if (surf) out.surface = parseInt(surf[1]);
const pt = text.match(/(\d+)\s*deg/);
if (pt) out.pente = parseInt(pt[1]);
return out;
};

const handleGenerate = async (finalParams) => {
setShowQuestions(false);
setLoading(true);
setError(null);
const zoneInfo = getZone(commune, altitude);
// Construction de la liste de prix selon le choix utilisateur
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
      ? prixList.map(p => `- ${p.categorie} | ${p.designation} | ${p.dimensions || "-"} | ${p.unite} | ${Number(p.prix_ht).toFixed(2)} EUR`).join("\n")
      : "Aucun catalogue fourni - estime les prix toi-meme.";

    const systemPrompt = "Tu es DEVIA, expert charpente bois. Genere un devis professionnel EN FRANCAIS. " +
"DETECTION DU TYPE DE PROJET : analyse la description et choisis 1 valeur pour type_projet : " +
"'carport' (si carport, abri voiture, auvent ouvert sans murs, structure sur potaux), " +
"'charpente_trad' (charpente traditionnelle de maison, toit 2 pans avec murs), " +
"'hangar' (hangar agricole, batiment industriel, grand volume couvert), " +
"'abri' (abri jardin, abri petit volume), " +
"'autre' (si rien ne correspond clairement). " +
"\n\nCATALOGUE DE PRIX A UTILISER (source: " + catalogSource + ") :\n" + prixListText + "\n\n" +
(catalogSource === "perso" ?
  // MODE STRICT : que le catalogue perso, pas d'invention
  "REGLES PRIX (MODE STRICT - CATALOGUE PERSO UNIQUEMENT) : " +
  "1) INTERDICTION ABSOLUE d'inventer un prix ou de creer un poste pour un materiau qui n'est PAS dans le catalogue ci-dessus. " +
  "2) Tu DOIS uniquement creer des postes correspondant aux materiaux LISTES dans le catalogue. " +
  "3) Le prix unitaire HT doit correspondre EXACTEMENT au prix du catalogue. " +
  "4) Si tu n'as pas assez de materiaux pour faire un devis complet (par exemple, pas de tuiles, pas de fixations), ne genere QUE les postes pour lesquels tu as un materiau dans le catalogue. " +
  "5) Le devis sera donc PARTIEL. C'est ok et voulu. " +
  "6) Adapte les quantites au projet decrit. " +
  "7) Dans le tableau 'notes' du JSON, AJOUTE en premiere note : 'Devis partiel : seuls les materiaux de votre catalogue sont inclus. Les postes manquants doivent etre completes manuellement ou en activant l option Completer avec marche.' " +
  "8) Genere entre 3 et 8 postes (selon le nombre de materiaux disponibles). "
  :
  // MODE NORMAL : avec complement marche
  "REGLES PRIX : 1) Pour chaque poste de devis, utilise EN PRIORITE un materiau du catalogue ci-dessus si disponible. " +
  "2) Le prix unitaire HT doit correspondre exactement au prix du catalogue. " +
  "3) Si un materiau necessaire n'existe pas dans le catalogue, estime le prix au mieux mais signale-le dans les notes. " +
  "4) Adapte les quantites au projet decrit. "
) +
"Type=" + (finalParams.type || "traditionnelle") + ", Couverture=" + (finalParams.couverture || "tuile_terre") + ", Essence=" + (finalParams.essence || "sapin") + ", Combles=" + (finalParams.combles || "perdus") + ". " +
"Commune=" + commune + ", Altitude=" + altitude + "m, Zone neige=" + zoneInfo.neige + " sk=" + zoneInfo.sk + "kN/m2, Vent=" + zoneInfo.vent + " qb=" + zoneInfo.qb + "kN/m2. " +
(finalParams.longueur ? "Dimensions=" + finalParams.longueur + "x" + finalParams.largeur + "m. " : "") +
(finalParams.pente ? "Pente=" + finalParams.pente + "deg. " : "") +
"Reponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans backticks, sans texte avant ou apres. Format exact : " +
'{"projet":{"description":"texte","commune":"' + commune + '","longueur":10,"largeur":8,"hauteur":3,"pente":35,"surface":80,' +
'"type":"' + (finalParams.type || "traditionnelle") + '","couverture":"' + (finalParams.couverture || "tuile_terre") + '",' +
'"essence":"' + (finalParams.essence || "sapin") + '","combles":"' + (finalParams.combles || "perdus") + '",' +
'"type_projet":"carport_OU_charpente_trad_OU_hangar_OU_abri_OU_autre"},' +
'"postes":[{"categorie":"Charpente","designation":"Exemple","unite":"ml","quantite":10,"prixUnitaireHT":45,"totalHT":450}],' +
'"totaux":{"totalHT":12000,"tva":2400,"totalTTC":14400},"notes":["Note 1"]}. ' +
"Genere 12 a 18 postes realistes avec prix marche francais 2024. IMPORTANT: Reponds UNIQUEMENT avec le JSON, rien d autre.";
try {
const response = await fetch("/api/chat", {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({
model: "claude-sonnet-4-20250514",
max_tokens: 4000,
system: systemPrompt,
messages: [{ role: "user", content: prompt }],
}),
});

  if (!response.ok) {
    const errText = await response.text();
    throw new Error("Erreur serveur " + response.status + " : " + errText.substring(0, 150));
  }

  const data = await response.json();

  // Extraction robuste du texte
  const text = (data.content && data.content[0] && data.content[0].text)
    ? data.content[0].text
    : "";

  if (!text) {
    throw new Error("Reponse vide du serveur. Verifie la cle API dans Vercel.");
  }

  // Nettoyage : supprime les backticks markdown si presents
  const clean = text.replace(/\x60\x60\x60json|\x60\x60\x60/g, "").trim();

  // Extraction du JSON
  const jsonMatch = clean.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    throw new Error("Reponse inattendue : " + clean.substring(0, 120));
  }

  const parsed = JSON.parse(jsonMatch[0]);

  setResult({ ...parsed, _catalogSource: catalogSource });
  if (parsed.projet) {
    const p = parsed.projet;
    setView3DParams({
        longueur: p.longueur || 10,
        largeur: p.largeur || 8,
        hauteur: p.hauteur || 3,
        pente: p.pente || 35,
        type_projet: p.type_projet || "autre"
      });
      console.log("[DEVIA] Type de projet detecte par l'IA :", p.type_projet || "non specifie");
    (async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        const totalTTC = parsed.totaux ? parsed.totaux.totalTTC : 0;
        const totalHT = parsed.totaux ? parsed.totaux.totalHT : 0;
        if (user) {
          const newProject = {
            user_id: user.id,
            nom: p.description || "Nouveau projet",
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
          };
          const { data: inserted, error: insertError } = await supabase
            .from("projects")
            .insert(newProject)
            .select()
            .single();
          if (insertError) {
            console.error("Erreur sauvegarde projet:", insertError);
            setProjects(prev => [{ id: Date.now(), nom: p.description || "Nouveau projet", commune: p.commune || commune, date: new Date().toISOString().split("T")[0], ttc: totalTTC, dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m" }, ...prev]);
          } else if (inserted) {
            setProjects(prev => [{
              id: inserted.id,
              nom: inserted.nom,
              commune: inserted.commune || "",
              date: inserted.created_at ? inserted.created_at.split("T")[0] : "",
              ttc: inserted.total_ttc || 0,
              dims: (inserted.longueur || "?") + "x" + (inserted.largeur || "?") + "m",
              devis_data: inserted.devis_data,
            }, ...prev]);
          }
        } else {
          setProjects(prev => [{ id: Date.now(), nom: p.description || "Nouveau projet", commune: p.commune || commune, date: new Date().toISOString().split("T")[0], ttc: totalTTC, dims: (p.longueur || "?") + "x" + (p.largeur || "?") + "m" }, ...prev]);
        }
      } catch (e) {
        console.error("Erreur sauvegarde:", e);
      }
    })();
  }
  setActiveResultTab("devis");
} catch (e) {
  setError("Erreur : " + e.message);
} finally {
  setLoading(false);
}

};

const loadProjectDetails = (project) => {
    if (!project.devis_data) {
      setError("Donnees du devis non disponibles pour ce projet.");
      return;
    }
    setResult(project.devis_data);
    if (project.devis_data.projet) {
      const p = project.devis_data.projet;
      setView3DParams({
        longueur: p.longueur || 10,
        largeur: p.largeur || 8,
        hauteur: p.hauteur || 3,
        pente: p.pente || 35
      });
    }
    setActiveResultTab("devis");
    setActiveTab("devis");
    setError(null);
  };

  const deleteProject = async (projectId, projectNom) => {
    const confirmed = window.confirm("Supprimer le projet \"" + projectNom + "\" ? Cette action est irreversible.");
    if (!confirmed) return;
    try {
      const { error } = await supabase.from("projects").delete().eq("id", projectId);
      if (error) {
        console.error("Erreur suppression:", error);
        alert("Erreur lors de la suppression : " + error.message);
        return;
      }
      setProjects(prev => prev.filter(p => p.id !== projectId));
    } catch (e) {
      console.error("Erreur deleteProject:", e);
      alert("Erreur lors de la suppression");
    }
  };

  const resetCatalogForm = () => {
    setCatalogForm({
      categorie: "Charpente",
      categorieAutre: "",
      designation: "",
      dimensions: "",
      unite: "ml",
      prix_ht: "",
      notes: "",
    });
    setCatalogFormError(null);
    setEditingCatalogId(null);
  };

  const openEditCatalogModal = (material) => {
    const isStandardCat = ["Charpente", "Bardage", "Couverture", "Isolation", "Quincaillerie", "Main d'oeuvre"].includes(material.categorie);
    setCatalogForm({
      categorie: isStandardCat ? material.categorie : "Autre",
      categorieAutre: isStandardCat ? "" : material.categorie,
      designation: material.designation || "",
      dimensions: material.dimensions || "",
      unite: material.unite || "ml",
      prix_ht: material.prix_ht ? String(material.prix_ht) : "",
      notes: material.notes || "",
    });
    setEditingCatalogId(material.id);
    setCatalogFormError(null);
    setShowAddCatalogModal(true);
  };

  const handleDeleteMaterial = async (material) => {
    const confirmed = window.confirm("Supprimer le materiau \"" + material.designation + "\" ? Cette action est irreversible.");
    if (!confirmed) return;
    try {
      const { error } = await supabase
        .from("catalogue_entreprise")
        .delete()
        .eq("id", material.id);
      if (error) {
        console.error("Erreur suppression catalogue:", error);
        alert("Erreur lors de la suppression : " + error.message);
        return;
      }
      setCatalogueEntreprise(prev => prev.filter(m => m.id !== material.id));
    } catch (e) {
      console.error("Erreur handleDeleteMaterial:", e);
      alert("Erreur inattendue lors de la suppression.");
    }
  };

  const handleAddMaterial = async () => {
    setCatalogFormError(null);

    // Validations
    const categorieFinal = catalogForm.categorie === "Autre"
      ? catalogForm.categorieAutre.trim()
      : catalogForm.categorie;
    if (!categorieFinal) {
      setCatalogFormError("La categorie est obligatoire.");
      return;
    }
    if (!catalogForm.designation.trim()) {
      setCatalogFormError("La designation est obligatoire.");
      return;
    }
    const prixHt = parseFloat(catalogForm.prix_ht);
    if (isNaN(prixHt) || prixHt < 0) {
      setCatalogFormError("Le prix HT doit etre un nombre positif.");
      return;
    }
    if (!catalogForm.unite) {
      setCatalogFormError("L'unite est obligatoire.");
      return;
    }

    setSavingCatalog(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        setCatalogFormError("Vous devez etre connecte.");
        setSavingCatalog(false);
        return;
      }
      const newRow = {
        user_id: user.id,
        categorie: categorieFinal,
        designation: catalogForm.designation.trim(),
        dimensions: catalogForm.dimensions.trim() || null,
        unite: catalogForm.unite,
        prix_ht: prixHt,
        notes: catalogForm.notes.trim() || null,
      };
      if (editingCatalogId) {
        // MODE MODIFICATION
        const { data: updated, error } = await supabase
          .from("catalogue_entreprise")
          .update(newRow)
          .eq("id", editingCatalogId)
          .select()
          .single();
        if (error) {
          console.error("Erreur update catalogue:", error);
          setCatalogFormError("Erreur : " + error.message);
          setSavingCatalog(false);
          return;
        }
        // Mise a jour locale
        setCatalogueEntreprise(prev => prev.map(m => m.id === editingCatalogId ? updated : m));
      } else {
        // MODE AJOUT
        const { data: inserted, error } = await supabase
          .from("catalogue_entreprise")
          .insert(newRow)
          .select()
          .single();
        if (error) {
          console.error("Erreur insertion catalogue:", error);
          setCatalogFormError("Erreur : " + error.message);
          setSavingCatalog(false);
          return;
        }
        setCatalogueEntreprise(prev => [inserted, ...prev]);
      }
      setShowAddCatalogModal(false);
      resetCatalogForm();
    } catch (e) {
      console.error("Erreur handleAddMaterial:", e);
      setCatalogFormError("Erreur inattendue : " + e.message);
    } finally {
      setSavingCatalog(false);
    }
  };

  const handleSubmit = () => {
if (!prompt.trim()) return;
const detected = detectParams(prompt);
const missingKeys = Object.keys(QUESTIONS).filter(k => !detected[k]);
if (missingKeys.length > 0) { setDetectedParams(detected); setShowQuestions(true); }
else handleGenerate(detected);
};

const zoneInfo = commune ? getZone(commune, altitude) : null;
// === DEVIA Design System v2 - Liquid Glass ===
// Cards translucides avec backdrop-filter, bordures ultra-fines, plus d'espace
const cardStyle = {
  background: "rgba(22, 25, 35, 0.55)",
  backdropFilter: "blur(24px) saturate(140%)",
  WebkitBackdropFilter: "blur(24px) saturate(140%)",
  border: "1px solid rgba(255, 255, 255, 0.06)",
  borderRadius: 16,
  padding: 24,
  marginBottom: 16,
  boxShadow: "0 1px 0 rgba(255,255,255,0.03) inset, 0 8px 32px rgba(0,0,0,0.25)"
};
const inputStyle = {
  width: "100%",
  background: "rgba(255, 255, 255, 0.03)",
  border: "1px solid rgba(255, 255, 255, 0.08)",
  borderRadius: 10,
  padding: "12px 16px",
  color: "#e8eaf2",
  fontSize: 14,
  outline: "none",
  boxSizing: "border-box",
  fontFamily: "inherit",
  transition: "border-color 0.15s, background 0.15s"
};
const btnPrimary = {
  background: "#f0c040",
  color: "#0a0a0a",
  border: "1px solid #f0c040",
  borderRadius: 999,
  padding: "11px 24px",
  cursor: "pointer",
  fontSize: 14,
  fontWeight: 600,
  letterSpacing: "0.01em",
  boxShadow: "0 4px 14px rgba(240, 192, 64, 0.18)",
  transition: "transform 0.1s, box-shadow 0.15s"
};
const btnSecondary = {
  background: "rgba(255, 255, 255, 0.04)",
  backdropFilter: "blur(16px)",
  WebkitBackdropFilter: "blur(16px)",
  color: "#e8eaf2",
  border: "1px solid rgba(255, 255, 255, 0.08)",
  borderRadius: 999,
  padding: "11px 24px",
  cursor: "pointer",
  fontSize: 14,
  fontWeight: 500,
  letterSpacing: "0.01em",
  transition: "background 0.15s, border-color 0.15s"
};

return (
<div style={{ minHeight: "100vh", background: "radial-gradient(ellipse at top, rgba(30, 35, 50, 0.4) 0%, #08090c 50%), #08090c", color: "#e8eaf2", fontFamily: "Inter, sans-serif" }}>
<style>{`
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-feature-settings: "ss01", "cv11"; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; letter-spacing: -0.005em; }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }
    input:focus, select:focus, textarea:focus { border-color: rgba(240,192,64,0.4) !important; background: rgba(255,255,255,0.05) !important; }
    button:active { transform: scale(0.97); }
    .devia-page { animation: fadeInUp 0.35s ease-out; }
    .devia-bg-noise { background-image: radial-gradient(at 0% 0%, rgba(240, 192, 64, 0.04) 0px, transparent 40%), radial-gradient(at 100% 100%, rgba(96, 165, 250, 0.03) 0px, transparent 40%); }
  `}</style>

  <header style={{
    background: "rgba(8, 9, 12, 0.7)",
    backdropFilter: "blur(20px) saturate(180%)",
    WebkitBackdropFilter: "blur(20px) saturate(180%)",
    borderBottom: "1px solid rgba(255,255,255,0.05)",
    padding: "0 28px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    height: 64,
    position: "sticky",
    top: 0,
    zIndex: 100
  }}>
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <img
        src="/logo-devia.jpeg"
        alt="DEVIA"
        style={{
          width: 32,
          height: 32,
          borderRadius: 9,
          objectFit: "cover",
          boxShadow: "0 2px 8px rgba(0,0,0,0.3)"
        }}
      />
      <span style={{ fontWeight: 700, fontSize: 15, letterSpacing: "-0.01em" }}>DEVIA</span>
      <span style={{ color: "#545870", fontSize: 11, fontWeight: 500, marginLeft: 4, paddingLeft: 12, borderLeft: "1px solid rgba(255,255,255,0.08)" }}>Devis charpente IA</span>
    </div>
    <nav style={{
      display: "flex",
      gap: 2,
      background: "rgba(255,255,255,0.03)",
      border: "1px solid rgba(255,255,255,0.06)",
      borderRadius: 999,
      padding: 4
    }}>
      {[{ id: "devis", label: "Devis" }, { id: "projets", label: "Projets" }, { id: "catalogue", label: "Catalogue" }, { id: "parametres", label: "Parametres" }, { id: "compte", label: "Compte" }].map(tab => (
        <button key={tab.id} onClick={() => setActiveTab(tab.id)}
          style={{
            background: activeTab === tab.id ? "rgba(255,255,255,0.08)" : "transparent",
            border: "none",
            color: activeTab === tab.id ? "#ffffff" : "#7a7d92",
            borderRadius: 999,
            padding: "7px 16px",
            cursor: "pointer",
            fontSize: 13,
            fontWeight: activeTab === tab.id ? 600 : 500,
            letterSpacing: "-0.005em",
            transition: "all 0.15s",
            boxShadow: activeTab === tab.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
          }}
          onMouseEnter={(e) => { if (activeTab !== tab.id) e.currentTarget.style.color = "#d0d2dc"; }}
          onMouseLeave={(e) => { if (activeTab !== tab.id) e.currentTarget.style.color = "#7a7d92"; }}>
          {tab.label}
        </button>
      ))}
    </nav>
  </header>

  <main className="devia-page devia-bg-noise" style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 20px" }}>

    {activeTab === "devis" && (
      <div>
        {showQuestions ? (
          <div style={cardStyle}><QuestionsScreen detected={detectedParams} onValidate={handleGenerate} /></div>
        ) : !result ? (
          <div>
            <div style={{ textAlign: "center", marginBottom: 40, paddingTop: 16 }}>
              <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 12, letterSpacing: "-0.02em", lineHeight: 1.1 }}>Generez votre devis <span style={{ background: "linear-gradient(135deg, #f0c040 0%, #e0a020 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>charpente</span></h1>
              <p style={{ color: "#7a7d92", fontSize: 15, maxWidth: 520, margin: "0 auto", lineHeight: 1.55 }}>Decrivez votre projet en langage naturel. DEVIA genere un devis professionnel et une visualisation 3D.</p>
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
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 8, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Documents <span style={{ color: "#545870", textTransform: "none", fontWeight: 400 }}>(max 5)</span></label>
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
                  {error}
                </div>
              )}
              {/* Selecteur de catalogue - v2 cards elegantes */}
              <div style={{ marginBottom: 20 }}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 12, marginBottom: 12, fontWeight: 500, letterSpacing: "0.02em", textTransform: "uppercase" }}>Catalogue a utiliser pour ce devis</label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  {/* Card MARCHE */}
                  <div onClick={() => setCatalogChoice("marche")}
                    style={{
                      position: "relative",
                      padding: 16,
                      borderRadius: 12,
                      background: catalogChoice === "marche" ? "rgba(240, 192, 64, 0.06)" : "rgba(255, 255, 255, 0.02)",
                      border: catalogChoice === "marche" ? "1px solid rgba(240, 192, 64, 0.45)" : "1px solid rgba(255, 255, 255, 0.06)",
                      cursor: "pointer",
                      transition: "all 0.18s",
                      boxShadow: catalogChoice === "marche" ? "0 0 0 3px rgba(240, 192, 64, 0.08), inset 0 0 0 1px rgba(240, 192, 64, 0.1)" : "none"
                    }}
                    onMouseEnter={(e) => { if (catalogChoice !== "marche") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.035)"; } }}
                    onMouseLeave={(e) => { if (catalogChoice !== "marche") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)"; } }}>
                    <div style={{ display: "flex", alignItems: "start", gap: 10, marginBottom: 6 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: 8,
                        background: catalogChoice === "marche" ? "linear-gradient(135deg, rgba(240, 192, 64, 0.25), rgba(240, 192, 64, 0.1))" : "rgba(255, 255, 255, 0.04)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        flexShrink: 0,
                        transition: "background 0.18s"
                      }}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={catalogChoice === "marche" ? "#f0c040" : "#7a7d92"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <div style={{ fontSize: 13, fontWeight: 600, color: catalogChoice === "marche" ? "#f5f6fa" : "#d0d2dc" }}>Marche DEVIA</div>
                          {catalogChoice === "marche" && (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: "auto" }}>
                              <path d="M20 6L9 17l-5-5"/>
                            </svg>
                          )}
                        </div>
                        <div style={{ fontSize: 11, color: "#7a7d92", marginTop: 2 }}>{marchePrix.length} materiaux du marche</div>
                      </div>
                    </div>
                  </div>
                  {/* Card PERSO */}
                  <div onClick={() => setCatalogChoice("perso")}
                    style={{
                      position: "relative",
                      padding: 16,
                      borderRadius: 12,
                      background: catalogChoice === "perso" ? "rgba(62, 207, 142, 0.06)" : "rgba(255, 255, 255, 0.02)",
                      border: catalogChoice === "perso" ? "1px solid rgba(62, 207, 142, 0.45)" : "1px solid rgba(255, 255, 255, 0.06)",
                      cursor: "pointer",
                      transition: "all 0.18s",
                      boxShadow: catalogChoice === "perso" ? "0 0 0 3px rgba(62, 207, 142, 0.08), inset 0 0 0 1px rgba(62, 207, 142, 0.1)" : "none"
                    }}
                    onMouseEnter={(e) => { if (catalogChoice !== "perso") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.035)"; } }}
                    onMouseLeave={(e) => { if (catalogChoice !== "perso") { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)"; } }}>
                    <div style={{ display: "flex", alignItems: "start", gap: 10, marginBottom: 6 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: 8,
                        background: catalogChoice === "perso" ? "linear-gradient(135deg, rgba(62, 207, 142, 0.25), rgba(62, 207, 142, 0.1))" : "rgba(255, 255, 255, 0.04)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        flexShrink: 0,
                        transition: "background 0.18s"
                      }}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={catalogChoice === "perso" ? "#3ecf8e" : "#7a7d92"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                          <circle cx="12" cy="7" r="4" />
                        </svg>
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <div style={{ fontSize: 13, fontWeight: 600, color: catalogChoice === "perso" ? "#f5f6fa" : "#d0d2dc" }}>Mon catalogue</div>
                          {catalogChoice === "perso" && (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: "auto" }}>
                              <path d="M20 6L9 17l-5-5"/>
                            </svg>
                          )}
                        </div>
                        <div style={{ fontSize: 11, color: "#7a7d92", marginTop: 2 }}>{catalogueEntreprise.length} materiaux personnels</div>
                      </div>
                    </div>
                  </div>
                </div>
                {catalogChoice === "perso" && (
                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "10px 14px",
                    marginTop: 10,
                    fontSize: 13,
                    cursor: "pointer",
                    background: "rgba(240, 192, 64, 0.04)",
                    border: "1px solid rgba(240, 192, 64, 0.18)",
                    borderRadius: 10,
                    color: completeWithMarket ? "#e8eaf2" : "#9ca0b8",
                    transition: "all 0.15s"
                  }}>
                    <input type="checkbox" checked={completeWithMarket}
                      onChange={(e) => setCompleteWithMarket(e.target.checked)}
                      style={{ accentColor: "#f0c040", width: 16, height: 16, cursor: "pointer" }} />
                    <span>Completer les materiaux manquants avec les prix marche DEVIA</span>
                  </label>
                )}
              </div>

              <button onClick={handleSubmit} disabled={loading || !prompt.trim() || !commune.trim()}
                style={{
                  ...btnPrimary,
                  width: "100%",
                  padding: "16px 24px",
                  fontSize: 15,
                  fontWeight: 700,
                  letterSpacing: "0.01em",
                  marginTop: 8,
                  opacity: loading || !prompt.trim() || !commune.trim() ? 0.45 : 1,
                  cursor: loading || !prompt.trim() || !commune.trim() ? "not-allowed" : "pointer",
                  boxShadow: loading || !prompt.trim() || !commune.trim() ? "none" : "0 8px 24px rgba(240, 192, 64, 0.28), 0 2px 6px rgba(240, 192, 64, 0.15)",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 10
                }}
                onMouseEnter={(e) => { if (!loading && prompt.trim() && commune.trim()) { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 12px 32px rgba(240, 192, 64, 0.35), 0 4px 8px rgba(240, 192, 64, 0.2)"; } }}
                onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = loading || !prompt.trim() || !commune.trim() ? "none" : "0 8px 24px rgba(240, 192, 64, 0.28), 0 2px 6px rgba(240, 192, 64, 0.15)"; }}>
                {loading ? (
                  <>
                    <span style={{ display: "inline-block", width: 14, height: 14, border: "2px solid rgba(10,10,10,0.25)", borderTopColor: "#0a0a0a", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                    <span>Analyse en cours...</span>
                  </>
                ) : (
                  <>
                    <span>Generer le devis</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M5 12h14M13 5l7 7-7 7"/>
                    </svg>
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div style={{ marginBottom: 24 }}>
              <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between", gap: 16, marginBottom: 14, flexWrap: "wrap" }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6, flexWrap: "wrap" }}>
                    <h2 style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-0.015em", lineHeight: 1.2 }}>{result.projet ? result.projet.description : "Devis charpente"}</h2>
                    {result._catalogSource && (
                      <span style={{
                        fontSize: 10,
                        fontWeight: 600,
                        padding: "3px 9px",
                        borderRadius: 999,
                        letterSpacing: "0.02em",
                        textTransform: "uppercase",
                        background: result._catalogSource === "perso" ? "rgba(62, 207, 142, 0.1)" : (result._catalogSource === "perso+marche" ? "rgba(167, 139, 250, 0.1)" : "rgba(240, 192, 64, 0.1)"),
                        color: result._catalogSource === "perso" ? "#3ecf8e" : (result._catalogSource === "perso+marche" ? "#a78bfa" : "#f0c040"),
                        border: "1px solid " + (result._catalogSource === "perso" ? "rgba(62, 207, 142, 0.3)" : (result._catalogSource === "perso+marche" ? "rgba(167, 139, 250, 0.3)" : "rgba(240, 192, 64, 0.3)")),
                        display: "inline-flex", alignItems: "center", gap: 5
                      }}>
                        <span style={{ width: 5, height: 5, borderRadius: "50%", background: result._catalogSource === "perso" ? "#3ecf8e" : (result._catalogSource === "perso+marche" ? "#a78bfa" : "#f0c040") }}></span>
                        {result._catalogSource === "perso" ? "Catalogue perso" : (result._catalogSource === "perso+marche" ? "Perso + marche" : "Marche DEVIA")}
                      </span>
                    )}
                  </div>
                  <div style={{ color: "#7a7d92", fontSize: 13, display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                    {result.projet && result.projet.commune && (<>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
                      </svg>
                      <span>{result.projet.commune}</span>
                      <span style={{ opacity: 0.4 }}>&bull;</span>
                    </>)}
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                    <span>{new Date().toLocaleDateString("fr-FR")}</span>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
                  <button style={btnSecondary} onClick={() => { setResult(null); setPrompt(""); }}>Nouveau</button>
                  <button style={btnPrimary}>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                      </svg>
                      PDF
                    </span>
                  </button>
                </div>
              </div>
              {result._catalogSource === "perso" && (
                <div style={{ padding: 14, background: "rgba(249, 115, 22, 0.06)", border: "1px solid rgba(249, 115, 22, 0.25)", borderRadius: 12, display: "flex", alignItems: "start", gap: 12 }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 2 }}>
                    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "#fb923c", marginBottom: 3 }}>Devis partiel</div>
                    <div style={{ fontSize: 12, color: "#fdba74", lineHeight: 1.5 }}>
                      Ce devis ne contient que les materiaux presents dans votre catalogue d&apos;entreprise.
                      Pour un devis complet, cochez &quot;Completer avec marche&quot; lors de la prochaine generation.
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div style={{ display: "inline-flex", gap: 2, marginBottom: 20, background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 999, padding: 4 }}>
              {[{ id: "devis", label: "Devis" }, { id: "3d", label: "Vue 3D" }, { id: "calcul", label: "Calcul" }].map(t => (
                <button key={t.id} onClick={() => setActiveResultTab(t.id)}
                  style={{
                    background: activeResultTab === t.id ? "rgba(255,255,255,0.08)" : "transparent",
                    border: "none",
                    color: activeResultTab === t.id ? "#ffffff" : "#7a7d92",
                    borderRadius: 999,
                    padding: "7px 18px",
                    cursor: "pointer",
                    fontSize: 13,
                    fontWeight: activeResultTab === t.id ? 600 : 500,
                    letterSpacing: "-0.005em",
                    transition: "all 0.15s",
                    boxShadow: activeResultTab === t.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
                  }}
                  onMouseEnter={(e) => { if (activeResultTab !== t.id) e.currentTarget.style.color = "#d0d2dc"; }}
                  onMouseLeave={(e) => { if (activeResultTab !== t.id) e.currentTarget.style.color = "#7a7d92"; }}>
                  {t.label}
                </button>
              ))}
            </div>

            {activeResultTab === "devis" && result.projet && (
              <div style={cardStyle}>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 24 }}>
                  {[
                    { label: "Surface", val: (result.projet.surface || "?") + "m²" },
                    { label: "Dimensions", val: (result.projet.longueur || "?") + "×" + (result.projet.largeur || "?") + "m" },
                    { label: "Pente", val: (result.projet.pente || "?") + "°" },
                    { label: "Type", val: result.projet.type || "?" }
                  ].map(info => (
                    <div key={info.label} style={{
                      background: "rgba(255, 255, 255, 0.02)",
                      borderRadius: 12,
                      padding: "14px 16px",
                      border: "1px solid rgba(255, 255, 255, 0.05)",
                      transition: "border-color 0.15s"
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.05)"; }}>
                      <div style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 6 }}>{info.label}</div>
                      <div style={{ color: "#f5f6fa", fontWeight: 700, fontSize: 18, letterSpacing: "-0.01em" }}>{info.val}</div>
                    </div>
                  ))}
                </div>
                <div style={{ borderRadius: 12, overflow: "hidden", border: "1px solid rgba(255, 255, 255, 0.05)", marginBottom: 20 }}>
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ background: "rgba(255, 255, 255, 0.025)", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                        {[
                          { label: "Categorie", align: "left" },
                          { label: "Designation", align: "left" },
                          { label: "U", align: "left" },
                          { label: "Qte", align: "right" },
                          { label: "PU HT", align: "right" },
                          { label: "Total HT", align: "right" }
                        ].map(h => (
                          <th key={h.label} style={{ padding: "12px 16px", textAlign: h.align, color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>{h.label}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(result.postes || []).map((p, i) => (
                        <tr key={i} style={{ borderBottom: i < (result.postes || []).length - 1 ? "1px solid rgba(255, 255, 255, 0.04)" : "none", transition: "background 0.12s" }}
                          onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.025)"; }}
                          onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                          <td style={{ padding: "12px 16px", fontSize: 13 }}>
                            <span style={{ color: "#60a5fa", fontSize: 11, fontWeight: 600, padding: "3px 8px", background: "rgba(96, 165, 250, 0.08)", borderRadius: 999, letterSpacing: "0.02em" }}>{p.categorie}</span>
                          </td>
                          <td style={{ padding: "12px 16px", color: "#e8eaf2", fontSize: 13, fontWeight: 500 }}>{p.designation}</td>
                          <td style={{ padding: "12px 16px", color: "#7a7d92", fontSize: 13 }}>{p.unite}</td>
                          <td style={{ padding: "12px 16px", color: "#d0d2dc", fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{p.quantite}</td>
                          <td style={{ padding: "12px 16px", color: "#d0d2dc", fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{p.prixUnitaireHT ? p.prixUnitaireHT.toLocaleString("fr-FR") : 0} <span style={{ color: "#545870", fontSize: 11 }}>EUR</span></td>
                          <td style={{ padding: "12px 16px", color: "#f0c040", fontWeight: 600, fontSize: 13, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{p.totalHT ? p.totalHT.toLocaleString("fr-FR") : 0} <span style={{ color: "#a8841f", fontSize: 11 }}>EUR</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <div style={{
                    background: "linear-gradient(135deg, rgba(240, 192, 64, 0.04) 0%, rgba(255, 255, 255, 0.02) 100%)",
                    border: "1px solid rgba(240, 192, 64, 0.15)",
                    borderRadius: 14,
                    padding: "18px 22px",
                    minWidth: 280,
                    boxShadow: "0 4px 16px rgba(0, 0, 0, 0.2)"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                      <span style={{ color: "#7a7d92", fontSize: 12, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Total HT</span>
                      <span style={{ color: "#e8eaf2", fontSize: 14, fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>{result.totaux ? result.totaux.totalHT.toLocaleString("fr-FR") : 0} <span style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500 }}>EUR</span></span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, paddingBottom: 14, borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                      <span style={{ color: "#7a7d92", fontSize: 12, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>TVA</span>
                      <span style={{ color: "#e8eaf2", fontSize: 14, fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>{result.totaux ? result.totaux.tva.toLocaleString("fr-FR") : 0} <span style={{ color: "#7a7d92", fontSize: 11, fontWeight: 500 }}>EUR</span></span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                      <span style={{ color: "#f0c040", fontSize: 13, fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase" }}>Total TTC</span>
                      <span style={{
                        color: "#f0c040",
                        fontWeight: 700,
                        fontSize: 24,
                        fontVariantNumeric: "tabular-nums",
                        letterSpacing: "-0.02em",
                        textShadow: "0 0 24px rgba(240, 192, 64, 0.25)"
                      }}>{result.totaux ? result.totaux.totalTTC.toLocaleString("fr-FR") : 0} <span style={{ fontSize: 14, fontWeight: 600 }}>EUR</span></span>
                    </div>
                  </div>
                </div>
                {result.notes && result.notes.length > 0 && (
                  <div style={{ marginTop: 20, padding: 18, background: "rgba(255, 255, 255, 0.02)", borderRadius: 12, border: "1px solid rgba(255, 255, 255, 0.05)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca0b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
                      </svg>
                      <div style={{ color: "#9ca0b8", fontSize: 11, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Notes techniques</div>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                      {result.notes.map((n, i) => (
                        <div key={i} style={{ color: "#d0d2dc", fontSize: 13, lineHeight: 1.55, paddingLeft: 14, position: "relative" }}>
                          <span style={{ position: "absolute", left: 0, top: 8, width: 4, height: 4, borderRadius: "50%", background: "#7a7d92" }}></span>
                          {n}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeResultTab === "3d" && (
              <div style={{ ...cardStyle, height: 420, padding: 0, overflow: "hidden" }}>
                <Viewer3D params={view3DParams} />
              </div>
            )}

            {activeResultTab === "calcul" && (
              <div style={cardStyle}>
                <FeuilleCalcTable devisData={result.projet || {}} zoneData={zoneInfo} />
              </div>
            )}
          </div>
        )}
      </div>
    )}

    {activeTab === "projets" && (
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Mes projets</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>Retrouvez tous vos devis sauvegardes</div>
          </div>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 6,
            background: "rgba(96, 165, 250, 0.08)",
            border: "1px solid rgba(96, 165, 250, 0.2)",
            borderRadius: 999,
            padding: "6px 14px",
            fontSize: 12,
            fontWeight: 600,
            color: "#60a5fa"
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#60a5fa" }}></span>
            {projects.length} devis
          </div>
        </div>
        {projects.length === 0 ? (
          <div style={{ ...cardStyle, textAlign: "center", padding: "48px 24px" }}>
            <div style={{
              width: 56, height: 56, borderRadius: 14,
              background: "rgba(255, 255, 255, 0.03)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              display: "inline-flex", alignItems: "center", justifyContent: "center",
              marginBottom: 16
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
              </svg>
            </div>
            <div style={{ color: "#e8eaf2", fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Aucun projet pour l&apos;instant</div>
            <div style={{ color: "#7a7d92", fontSize: 13, maxWidth: 360, margin: "0 auto", lineHeight: 1.5 }}>Generez votre premier devis depuis l&apos;onglet Devis et il apparaitra ici.</div>
          </div>
        ) : (
          <div style={{ display: "grid", gap: 10 }}>
            {projects.map(p => (
              <div key={p.id} style={{
                ...cardStyle,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: "pointer",
                marginBottom: 0,
                padding: 18,
                transition: "all 0.18s",
                gap: 14
              }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = "rgba(240, 192, 64, 0.4)";
                  e.currentTarget.style.background = "rgba(240, 192, 64, 0.025)";
                  const deleteBtn = e.currentTarget.querySelector(".devia-delete-btn");
                  if (deleteBtn) deleteBtn.style.opacity = "1";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)";
                  e.currentTarget.style.background = "rgba(22, 25, 35, 0.55)";
                  const deleteBtn = e.currentTarget.querySelector(".devia-delete-btn");
                  if (deleteBtn) deleteBtn.style.opacity = "0.4";
                }}
                onClick={() => loadProjectDetails(p)}>
                <div style={{ display: "flex", alignItems: "center", gap: 14, flex: 1, minWidth: 0 }}>
                  <div style={{
                    width: 44, height: 44,
                    background: "linear-gradient(135deg, rgba(240, 192, 64, 0.18), rgba(240, 192, 64, 0.06))",
                    border: "1px solid rgba(240, 192, 64, 0.15)",
                    borderRadius: 11,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0
                  }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                    </svg>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: 15, color: "#e8eaf2", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", marginBottom: 3 }}>{p.nom}</div>
                    <div style={{ color: "#7a7d92", fontSize: 12, display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
                        </svg>
                        {p.commune || "?"}
                      </span>
                      <span style={{ opacity: 0.4 }}>&bull;</span>
                      <span>{p.dims}</span>
                      <span style={{ opacity: 0.4 }}>&bull;</span>
                      <span>{new Date(p.date).toLocaleDateString("fr-FR")}</span>
                    </div>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 12, flexShrink: 0 }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: "#f0c040", fontWeight: 700, fontSize: 17, fontVariantNumeric: "tabular-nums", letterSpacing: "-0.01em" }}>
                      {p.ttc.toLocaleString("fr-FR")} <span style={{ fontSize: 12, fontWeight: 600 }}>EUR</span>
                    </div>
                    <div style={{ color: "#7a7d92", fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase" }}>TTC</div>
                  </div>
                  <button
                    className="devia-delete-btn"
                    onClick={(e) => { e.stopPropagation(); deleteProject(p.id, p.nom); }}
                    title="Supprimer ce projet"
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
                      justifyContent: "center",
                      opacity: 0.4
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)"; e.currentTarget.style.borderColor = "rgba(239, 68, 68, 0.4)"; e.currentTarget.style.color = "#ef4444"; e.currentTarget.style.opacity = "1"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.color = "#7a7d92"; }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    )}

    {activeTab === "catalogue" && (
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Catalogue</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>Gerez les prix de reference utilises pour vos devis</div>
          </div>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 6,
            background: "rgba(96, 165, 250, 0.08)",
            border: "1px solid rgba(96, 165, 250, 0.2)",
            borderRadius: 999,
            padding: "6px 14px",
            fontSize: 12,
            fontWeight: 600,
            color: "#60a5fa"
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#60a5fa" }}></span>
            {activeCatalogTab === "marche" ? marchePrix.length + " materiaux" : catalogueEntreprise.length + " materiaux"}
          </div>
        </div>

        {/* Onglets internes - style pills */}
        <div style={{ display: "inline-flex", gap: 2, marginBottom: 24, background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 999, padding: 4 }}>
          {[
            { id: "marche", label: "Marche DEVIA", color: "#f0c040" },
            { id: "perso", label: "Mon catalogue", color: "#3ecf8e" }
          ].map(t => (
            <button key={t.id} onClick={() => setActiveCatalogTab(t.id)}
              style={{
                background: activeCatalogTab === t.id ? "rgba(255,255,255,0.08)" : "transparent",
                border: "none",
                color: activeCatalogTab === t.id ? "#ffffff" : "#7a7d92",
                borderRadius: 999,
                padding: "8px 18px",
                cursor: "pointer",
                fontSize: 13,
                fontWeight: activeCatalogTab === t.id ? 600 : 500,
                letterSpacing: "-0.005em",
                transition: "all 0.15s",
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                boxShadow: activeCatalogTab === t.id ? "0 1px 0 rgba(255,255,255,0.06) inset" : "none"
              }}
              onMouseEnter={(e) => { if (activeCatalogTab !== t.id) e.currentTarget.style.color = "#d0d2dc"; }}
              onMouseLeave={(e) => { if (activeCatalogTab !== t.id) e.currentTarget.style.color = "#7a7d92"; }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: activeCatalogTab === t.id ? t.color : "#3a3d4f", transition: "background 0.15s" }}></span>
              {t.label}
            </button>
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
                <div style={{
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
                        <div style={{ borderRadius: 12, overflow: "hidden", border: "1px solid rgba(255, 255, 255, 0.05)", background: "rgba(255, 255, 255, 0.015)" }}>
                          <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                              <tr style={{ background: "rgba(255, 255, 255, 0.025)", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                                <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Designation</th>
                                <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Dimensions</th>
                                <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Unite</th>
                                <th style={{ padding: "12px 16px", textAlign: "right", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Prix HT</th>
                              </tr>
                            </thead>
                            <tbody>
                              {items.map((m, i) => (
                                <tr key={m.id} style={{ borderBottom: i < items.length - 1 ? "1px solid rgba(255, 255, 255, 0.04)" : "none", transition: "background 0.12s" }}
                                  onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.025)"; }}
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                                  <td style={{ padding: "12px 16px", fontSize: 13, color: "#e8eaf2", fontWeight: 500 }}>{m.designation}</td>
                                  <td style={{ padding: "12px 16px", fontSize: 13, color: "#9ca0b8" }}>{m.dimensions || "—"}</td>
                                  <td style={{ padding: "12px 16px", fontSize: 13, color: "#7a7d92" }}>{m.unite}</td>
                                  <td style={{ padding: "12px 16px", textAlign: "right", fontSize: 13, color: "#f0c040", fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>
                                    {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} <span style={{ color: "#a8841f", fontSize: 11 }}>EUR</span>
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
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, gap: 12 }}>
                  <div style={{
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
                  </div>
                  <button
                    onClick={() => { resetCatalogForm(); setShowAddCatalogModal(true); }}
                    style={{
                      background: "#f0c040",
                      color: "#0a0a0a",
                      border: "1px solid #f0c040",
                      borderRadius: 999,
                      padding: "11px 20px",
                      cursor: "pointer",
                      fontSize: 13,
                      fontWeight: 700,
                      letterSpacing: "0.01em",
                      whiteSpace: "nowrap",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 8,
                      boxShadow: "0 4px 14px rgba(240, 192, 64, 0.22)",
                      transition: "transform 0.1s, box-shadow 0.15s"
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 8px 20px rgba(240, 192, 64, 0.3)"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 4px 14px rgba(240, 192, 64, 0.22)"; }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    Ajouter un materiau
                  </button>
                </div>
                {catalogueEntreprise.length === 0 ? (
                  <div style={{ ...cardStyle, textAlign: "center", padding: "48px 24px" }}>
                    <div style={{
                      width: 56, height: 56, borderRadius: 14,
                      background: "rgba(255, 255, 255, 0.03)",
                      border: "1px solid rgba(255, 255, 255, 0.06)",
                      display: "inline-flex", alignItems: "center", justifyContent: "center",
                      marginBottom: 16
                    }}>
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7a7d92" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/>
                      </svg>
                    </div>
                    <div style={{ color: "#e8eaf2", fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Aucun materiau dans votre catalogue</div>
                    <div style={{ color: "#7a7d92", fontSize: 13, maxWidth: 360, margin: "0 auto", lineHeight: 1.5 }}>Cliquez sur &quot;Ajouter un materiau&quot; pour creer votre premier prix personnalise.</div>
                  </div>
                ) : (
                  <div style={{ ...cardStyle, padding: 0, overflow: "hidden" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead>
                        <tr style={{ background: "rgba(255, 255, 255, 0.025)", borderBottom: "1px solid rgba(255, 255, 255, 0.06)" }}>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Categorie</th>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Designation</th>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Dimensions</th>
                          <th style={{ padding: "12px 16px", textAlign: "left", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Unite</th>
                          <th style={{ padding: "12px 16px", textAlign: "right", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Prix HT</th>
                          <th style={{ padding: "12px 16px", textAlign: "right", color: "#7a7d92", fontSize: 10, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase" }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {catalogueEntreprise.map((m, i) => (
                          <tr key={m.id} style={{ borderBottom: i < catalogueEntreprise.length - 1 ? "1px solid rgba(255, 255, 255, 0.04)" : "none", transition: "background 0.12s" }}
                            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.025)"; }}
                            onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}>
                            <td style={{ padding: "12px 16px", fontSize: 13 }}>
                              <span style={{ color: "#60a5fa", fontSize: 11, fontWeight: 600, padding: "3px 8px", background: "rgba(96, 165, 250, 0.08)", borderRadius: 999, letterSpacing: "0.02em" }}>{m.categorie}</span>
                            </td>
                            <td style={{ padding: "12px 16px", fontSize: 13, color: "#e8eaf2", fontWeight: 500 }}>{m.designation}</td>
                            <td style={{ padding: "12px 16px", fontSize: 13, color: "#9ca0b8" }}>{m.dimensions || "—"}</td>
                            <td style={{ padding: "12px 16px", fontSize: 13, color: "#7a7d92" }}>{m.unite}</td>
                            <td style={{ padding: "12px 16px", textAlign: "right", fontSize: 13, color: "#3ecf8e", fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>
                              {m.prix_ht ? Number(m.prix_ht).toFixed(2) : "0.00"} <span style={{ color: "#1f7a4c", fontSize: 11 }}>EUR</span>
                            </td>
                            <td style={{ padding: "8px 12px", textAlign: "right" }}>
                              <div style={{ display: "flex", gap: 6, justifyContent: "flex-end" }}>
                                <button
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
                                  onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.06)"; e.currentTarget.style.color = "#7a7d92"; }}>
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                  </svg>
                                </button>
                                <button
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
                                </button>
                              </div>
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

    {activeTab === "parametres" && (
      <div>
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Parametres</h2>
          <div style={{ color: "#7a7d92", fontSize: 13 }}>Configurez votre entreprise et vos tarifs par defaut</div>
        </div>

        {/* Section Informations entreprise */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(240, 192, 64, 0.1)",
              border: "1px solid rgba(240, 192, 64, 0.2)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f0c040" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 21h18M5 21V7l8-4v18M19 21V11l-6-4"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="9" y1="12" x2="9.01" y2="12"/><line x1="9" y1="15" x2="9.01" y2="15"/><line x1="9" y1="18" x2="9.01" y2="18"/>
              </svg>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: "#e8eaf2" }}>Informations entreprise</div>
              <div style={{ color: "#7a7d92", fontSize: 12 }}>Ces informations apparaitront sur vos devis</div>
            </div>
          </div>
          {[{ label: "Nom de l'entreprise", key: "entreprise" }, { label: "SIRET", key: "siret" }, { label: "Adresse", key: "adresse" }].map(f => (
            <div key={f.key} style={{ marginBottom: 14 }}>
              <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>{f.label}</label>
              <input value={params[f.key]} onChange={e => setParams(prev => ({ ...prev, [f.key]: e.target.value }))} style={inputStyle} />
            </div>
          ))}
        </div>

        {/* Section Tarification */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(62, 207, 142, 0.1)",
              border: "1px solid rgba(62, 207, 142, 0.2)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3ecf8e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
              </svg>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: "#e8eaf2" }}>Tarification par defaut</div>
              <div style={{ color: "#7a7d92", fontSize: 12 }}>Ces valeurs s&apos;appliquent automatiquement a vos devis</div>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
            {[
              { label: "Taux horaire", key: "tauxHoraire", suffix: "EUR/h" },
              { label: "TVA", key: "tva", suffix: "%" },
              { label: "Marge", key: "marge", suffix: "%" }
            ].map(f => (
              <div key={f.key}>
                <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>{f.label} <span style={{ color: "#7a7d92", fontWeight: 400, textTransform: "none" }}>({f.suffix})</span></label>
                <input type="number" value={params[f.key]} onChange={e => setParams(prev => ({ ...prev, [f.key]: parseFloat(e.target.value) }))} style={inputStyle} />
              </div>
            ))}
          </div>
        </div>

        {/* Section Mentions legales */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: "rgba(96, 165, 250, 0.1)",
              border: "1px solid rgba(96, 165, 250, 0.2)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
              </svg>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: "#e8eaf2" }}>Mentions legales</div>
              <div style={{ color: "#7a7d92", fontSize: 12 }}>Texte affiche en bas de vos devis</div>
            </div>
          </div>
          <textarea value={params.mentions} onChange={e => setParams(prev => ({ ...prev, mentions: e.target.value }))} rows={3} style={{ ...inputStyle, resize: "vertical", lineHeight: 1.6 }} />
        </div>

        {/* Bouton Sauvegarder */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
          <button style={{
            ...btnPrimary,
            padding: "12px 28px",
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            boxShadow: "0 4px 14px rgba(240, 192, 64, 0.22)",
            transition: "transform 0.1s, box-shadow 0.15s"
          }}
          onMouseEnter={(e) => { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 8px 20px rgba(240, 192, 64, 0.3)"; }}
          onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 4px 14px rgba(240, 192, 64, 0.22)"; }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>
            </svg>
            Sauvegarder
          </button>
        </div>
      </div>
    )}

    {activeTab === "compte" && (
      <div>
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.02em", marginBottom: 4 }}>Mon compte</h2>
          <div style={{ color: "#7a7d92", fontSize: 13 }}>Apercu de votre activite DEVIA</div>
        </div>

        {/* Card Identite + Plan */}
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
            <div style={{
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
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: 700, fontSize: 18, color: "#e8eaf2", marginBottom: 6, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {params.entreprise || "Mon entreprise"}
              </div>
              <div style={{
                display: "inline-flex", alignItems: "center", gap: 6,
                background: "rgba(62, 207, 142, 0.1)",
                border: "1px solid rgba(62, 207, 142, 0.25)",
                borderRadius: 999,
                padding: "4px 11px",
                fontSize: 11,
                fontWeight: 600,
                color: "#3ecf8e",
                letterSpacing: "0.02em",
                textTransform: "uppercase"
              }}>
                <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#3ecf8e" }}></span>
                Plan Pro
              </div>
            </div>
          </div>

          {/* 3 stats */}
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
          </div>
        </div>
      </div>
    )}

  </main>

  {showAddCatalogModal && (
    <div style={{
        position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0, 0, 0, 0.55)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 1000, padding: 16,
        animation: "fadeInUp 0.18s ease-out"
      }}
      onClick={(e) => { if (e.target === e.currentTarget) { setShowAddCatalogModal(false); resetCatalogForm(); } }}>
      <div style={{
        background: "rgba(22, 25, 35, 0.95)",
        backdropFilter: "blur(24px) saturate(140%)",
        WebkitBackdropFilter: "blur(24px) saturate(140%)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        borderRadius: 20,
        padding: 28,
        maxWidth: 560,
        width: "100%",
        maxHeight: "90vh",
        overflowY: "auto",
        boxShadow: "0 24px 64px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,0.04) inset"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: 24, gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.015em", marginBottom: 4 }}>{editingCatalogId ? "Modifier un materiau" : "Ajouter un materiau"}</h2>
            <div style={{ color: "#7a7d92", fontSize: 13 }}>{editingCatalogId ? "Mettez a jour les informations" : "Ajoutez un prix a votre catalogue personnel"}</div>
          </div>
          <button onClick={() => { setShowAddCatalogModal(false); resetCatalogForm(); }}
            style={{
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              color: "#7a7d92",
              cursor: "pointer",
              borderRadius: 10,
              padding: 8,
              flexShrink: 0,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.15s"
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)"; e.currentTarget.style.color = "#e8eaf2"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255, 255, 255, 0.04)"; e.currentTarget.style.color = "#7a7d92"; }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div style={{ display: "grid", gap: 14 }}>
          {/* Categorie */}
          <div>
            <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Categorie <span style={{ color: "#f0c040" }}>*</span></label>
            <select value={catalogForm.categorie}
              onChange={(e) => setCatalogForm({ ...catalogForm, categorie: e.target.value })}
              style={{ ...inputStyle, cursor: "pointer" }}>
              <option value="Charpente">Charpente</option>
              <option value="Bardage">Bardage</option>
              <option value="Couverture">Couverture</option>
              <option value="Isolation">Isolation</option>
              <option value="Quincaillerie">Quincaillerie</option>
              <option value="Main d'oeuvre">Main d'oeuvre</option>
              <option value="Autre">Autre (champ libre)</option>
            </select>
            {catalogForm.categorie === "Autre" && (
              <input type="text" value={catalogForm.categorieAutre}
                onChange={(e) => setCatalogForm({ ...catalogForm, categorieAutre: e.target.value })}
                placeholder="Nom de votre categorie..."
                style={{ ...inputStyle, marginTop: 8 }} />
            )}
          </div>

          {/* Designation */}
          <div>
            <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Designation <span style={{ color: "#f0c040" }}>*</span></label>
            <input type="text" value={catalogForm.designation}
              onChange={(e) => setCatalogForm({ ...catalogForm, designation: e.target.value })}
              placeholder="Ex: Chevron sapin C24, Tuile mecanique, Vis 6x180..."
              style={inputStyle} />
          </div>

          {/* Dimensions et Unite */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Dimensions</label>
              <input type="text" value={catalogForm.dimensions}
                onChange={(e) => setCatalogForm({ ...catalogForm, dimensions: e.target.value })}
                placeholder="Ex: 75x175 mm"
                style={inputStyle} />
            </div>
            <div>
              <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Unite <span style={{ color: "#f0c040" }}>*</span></label>
              <select value={catalogForm.unite}
                onChange={(e) => setCatalogForm({ ...catalogForm, unite: e.target.value })}
                style={{ ...inputStyle, cursor: "pointer" }}>
                <option value="ml">ml (metre lineaire)</option>
                <option value="m2">m2 (metre carre)</option>
                <option value="m3">m3 (metre cube)</option>
                <option value="u">u (unite)</option>
                <option value="kg">kg (kilo)</option>
                <option value="h">h (heure)</option>
                <option value="forfait">forfait</option>
              </select>
            </div>
          </div>

          {/* Prix HT */}
          <div>
            <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Prix HT <span style={{ color: "#7a7d92", fontWeight: 400, textTransform: "none" }}>(EUR)</span> <span style={{ color: "#f0c040" }}>*</span></label>
            <input type="number" step="0.01" min="0" value={catalogForm.prix_ht}
              onChange={(e) => setCatalogForm({ ...catalogForm, prix_ht: e.target.value })}
              placeholder="Ex: 12.50"
              style={inputStyle} />
          </div>

          {/* Notes */}
          <div>
            <label style={{ display: "block", color: "#9ca0b8", fontSize: 11, marginBottom: 8, fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase" }}>Notes <span style={{ color: "#7a7d92", fontWeight: 400, textTransform: "none" }}>(optionnel)</span></label>
            <input type="text" value={catalogForm.notes}
              onChange={(e) => setCatalogForm({ ...catalogForm, notes: e.target.value })}
              placeholder="Ex: Fournisseur X, classe C24..."
              style={inputStyle} />
          </div>

          {catalogFormError && (
            <div style={{
              background: "rgba(239, 68, 68, 0.08)",
              border: "1px solid rgba(239, 68, 68, 0.25)",
              borderRadius: 10,
              padding: 14,
              color: "#fca5a5",
              fontSize: 13,
              display: "flex",
              alignItems: "start",
              gap: 10
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <div>{catalogFormError}</div>
            </div>
          )}

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 12, paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.05)" }}>
            <button onClick={() => { setShowAddCatalogModal(false); resetCatalogForm(); }}
              disabled={savingCatalog}
              style={{ ...btnSecondary, opacity: savingCatalog ? 0.5 : 1 }}>
              Annuler
            </button>
            <button onClick={handleAddMaterial}
              disabled={savingCatalog}
              style={{
                ...btnPrimary,
                padding: "11px 22px",
                opacity: savingCatalog ? 0.7 : 1,
                cursor: savingCatalog ? "not-allowed" : "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                boxShadow: savingCatalog ? "none" : "0 4px 14px rgba(240, 192, 64, 0.25)"
              }}>
              {savingCatalog ? (
                <>
                  <span style={{ display: "inline-block", width: 13, height: 13, border: "2px solid rgba(10,10,10,0.25)", borderTopColor: "#0a0a0a", borderRadius: "50%", animation: "spin 0.7s linear infinite" }}></span>
                  <span>{editingCatalogId ? "Sauvegarde..." : "Ajout en cours..."}</span>
                </>
              ) : (
                <>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    {editingCatalogId ? <polyline points="20 6 9 17 4 12"/> : <><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></>}
                  </svg>
                  {editingCatalogId ? "Enregistrer" : "Ajouter"}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )}
</div>

);
}


// ============================================================
// DEVIA - Gate d'authentification (Micro-etape 2.2)
// Ce wrapper affiche Login si l'utilisateur n'est pas connecte.
// Il ne verifie PAS encore la licence (c'est la micro-etape 2.3).
// ============================================================

function DeviaAuthGate() {
  const { user, loading: authLoading } = useAuth();
  const { license, loading: licenseLoading, refresh: refreshLicense } = useLicense();

  // Spinner pendant le chargement initial
  if (authLoading || (user && licenseLoading)) {
    return (
      <div style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#1a1a2e",
        color: "#fff",
        fontFamily: "-apple-system, sans-serif",
        fontSize: "14px",
      }}>
        Chargement...
      </div>
    );
  }

  // Pas connecte -> ecran login
  if (!user) {
    return <Login />;
  }

  // Connecte mais pas de licence -> ecran d'activation
  if (!license || license.status === "no_license") {
    return (
      <ActivateLicense
        userEmail={user.email}
        onActivated={refreshLicense}
      />
    );
  }

  // Tout est OK : afficher l'app avec bandeau abonnement + menu user
  return (
    <>
      <SubscriptionBanner license={license} />
      <UserMenu user={user} license={license} />
      <DeviaMain />
    </>
  );
}

export default DeviaAuthGate;
