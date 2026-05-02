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
const w = mountRef.current.clientWidth, h = mountRef.current.clientHeight;
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
const L = params.longueur || 8, lg = params.largeur || 6, H = params.hauteur || 3;
const pente = params.pente || 35;
const hf = lg / 2 * Math.tan((pente * Math.PI) / 180);
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
[[L, H, 0.15, 0, H/2, lg/2],[L, H, 0.15, 0, H/2, -lg/2],[0.15, H, lg, -L/2, H/2, 0],[0.15, H, lg, L/2, H/2, 0]]
.forEach(([sx,sy,sz,px,py,pz]) => addBox(sx,sy,sz,px,py,pz,wallMat));
const nb = Math.max(2, Math.ceil(L / 2.5));
for (let i = 0; i <= nb; i++) {
const x = -L/2 + (i/nb)*L;
const ang = Math.atan(hf / (lg/2));
const pl = (lg/2) / Math.cos(ang);
addBox(pl, 0.12, 0.12, x, H+hf/2, lg/4, woodMat, [ang,0,0]);
addBox(pl, 0.12, 0.12, x, H+hf/2, -lg/4, woodMat, [-ang,0,0]);
addBox(0.12, hf+0.1, 0.12, x, H+hf/2, 0);
}
addBox(L+0.4, 0.14, 0.14, 0, H+hf, 0);
const ang = Math.atan(hf / (lg/2));
const pl = (lg/2) / Math.cos(ang);
const rg = new THREE.PlaneGeometry(L+0.6, pl+0.2);
const r1 = new THREE.Mesh(rg, roofMat);
r1.position.set(0, H+hf/2, lg/4);
r1.rotation.x = ang - Math.PI/2;
scene.add(r1);
const r2 = new THREE.Mesh(rg, roofMat);
r2.position.set(0, H+hf/2, -lg/4);
r2.rotation.x = -(ang - Math.PI/2);
scene.add(r2);
const ground = new THREE.Mesh(new THREE.PlaneGeometry(30,30), new THREE.MeshLambertMaterial({ color: 0x1a1f2e }));
ground.rotation.x = -Math.PI/2;
scene.add(ground);
let angle = 0, animId;
const animate = () => {
animId = requestAnimationFrame(animate);
angle += 0.005;
camera.position.x = Math.cos(angle) * 16;
camera.position.z = Math.sin(angle) * 16;
camera.lookAt(0, H/2+hf/2, 0);
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
const systemPrompt = "Tu es DEVIA, expert charpente bois. Genere un devis professionnel EN FRANCAIS. " +
"Type=" + (finalParams.type || "traditionnelle") + ", Couverture=" + (finalParams.couverture || "tuile_terre") + ", Essence=" + (finalParams.essence || "sapin") + ", Combles=" + (finalParams.combles || "perdus") + ". " +
"Commune=" + commune + ", Altitude=" + altitude + "m, Zone neige=" + zoneInfo.neige + " sk=" + zoneInfo.sk + "kN/m2, Vent=" + zoneInfo.vent + " qb=" + zoneInfo.qb + "kN/m2. " +
(finalParams.longueur ? "Dimensions=" + finalParams.longueur + "x" + finalParams.largeur + "m. " : "") +
(finalParams.pente ? "Pente=" + finalParams.pente + "deg. " : "") +
"Reponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans backticks, sans texte avant ou apres. Format exact : " +
'{"projet":{"description":"texte","commune":"' + commune + '","longueur":10,"largeur":8,"hauteur":3,"pente":35,"surface":80,' +
'"type":"' + (finalParams.type || "traditionnelle") + '","couverture":"' + (finalParams.couverture || "tuile_terre") + '",' +
'"essence":"' + (finalParams.essence || "sapin") + '","combles":"' + (finalParams.combles || "perdus") + '"},' +
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

  setResult(parsed);
  if (parsed.projet) {
    const p = parsed.projet;
    setView3DParams({ longueur: p.longueur || 10, largeur: p.largeur || 8, hauteur: p.hauteur || 3, pente: p.pente || 35 });
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

  const handleSubmit = () => {
if (!prompt.trim()) return;
const detected = detectParams(prompt);
const missingKeys = Object.keys(QUESTIONS).filter(k => !detected[k]);
if (missingKeys.length > 0) { setDetectedParams(detected); setShowQuestions(true); }
else handleGenerate(detected);
};

const zoneInfo = commune ? getZone(commune, altitude) : null;
const cardStyle = { background: "#13161f", border: "1px solid #1e2231", borderRadius: 12, padding: 20, marginBottom: 16 };
const inputStyle = { width: "100%", background: "#0f1117", border: "1px solid #1e2231", borderRadius: 8, padding: "10px 14px", color: "#e8eaf2", fontSize: 14, outline: "none", boxSizing: "border-box", fontFamily: "inherit" };
const btnPrimary = { background: "#f0c040", color: "#000", border: "1px solid #f0c040", borderRadius: 8, padding: "10px 20px", cursor: "pointer", fontSize: 14, fontWeight: 600 };
const btnSecondary = { background: "#0f1117", color: "#e8eaf2", border: "1px solid #1e2231", borderRadius: 8, padding: "10px 20px", cursor: "pointer", fontSize: 14, fontWeight: 600 };

return (
<div style={{ minHeight: "100vh", background: "#08090c", color: "#e8eaf2", fontFamily: "Inter, sans-serif" }}>
<style>{"* { box-sizing: border-box; margin: 0; padding: 0; } @keyframes spin { to { transform: rotate(360deg); } } ::-webkit-scrollbar { width: 5px; } ::-webkit-scrollbar-track { background: #0f1117; } ::-webkit-scrollbar-thumb { background: #2a2e40; border-radius: 3px; }"}</style>

  <header style={{ background: "#0f1117", borderBottom: "1px solid #1e2231", padding: "0 24px", display: "flex", alignItems: "center", justifyContent: "space-between", height: 56 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div style={{ width: 32, height: 32, background: "#f0c040", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>⚡</div>
      <span style={{ fontWeight: 800, fontSize: 16 }}>DEVIA</span>
      <span style={{ color: "#545870", fontSize: 12 }}>Devis charpente IA</span>
    </div>
    <nav style={{ display: "flex", gap: 4 }}>
      {[{ id: "devis", label: "Devis" }, { id: "projets", label: "Projets" }, { id: "parametres", label: "Parametres" }, { id: "compte", label: "Compte" }].map(tab => (
        <button key={tab.id} onClick={() => setActiveTab(tab.id)}
          style={{ background: activeTab === tab.id ? "#f0c04018" : "transparent", border: activeTab === tab.id ? "1px solid #f0c040" : "1px solid transparent", color: activeTab === tab.id ? "#f0c040" : "#545870", borderRadius: 6, padding: "6px 14px", cursor: "pointer", fontSize: 14, fontWeight: activeTab === tab.id ? 600 : 400 }}>
          {tab.label}
        </button>
      ))}
    </nav>
  </header>

  <main style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 16px" }}>

    {activeTab === "devis" && (
      <div>
        {showQuestions ? (
          <div style={cardStyle}><QuestionsScreen detected={detectedParams} onValidate={handleGenerate} /></div>
        ) : !result ? (
          <div>
            <div style={{ textAlign: "center", marginBottom: 32 }}>
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
                  {error}
                </div>
              )}
              <button onClick={handleSubmit} disabled={loading || !prompt.trim() || !commune.trim()}
                style={{ ...btnPrimary, width: "100%", padding: 14, fontSize: 15, opacity: loading || !prompt.trim() || !commune.trim() ? 0.5 : 1, cursor: loading || !prompt.trim() || !commune.trim() ? "not-allowed" : "pointer" }}>
                {loading ? "⏳ Analyse en cours..." : "Generer le devis"}
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
              <div>
                <h2 style={{ fontSize: 20, fontWeight: 700 }}>{result.projet ? result.projet.description : "Devis charpente"}</h2>
                <div style={{ color: "#545870", fontSize: 14 }}>{result.projet ? result.projet.commune : ""} - {new Date().toLocaleDateString("fr-FR")}</div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button style={btnSecondary} onClick={() => { setResult(null); setPrompt(""); }}>Nouveau</button>
                <button style={btnPrimary}>PDF</button>
              </div>
            </div>
            <div style={{ display: "flex", gap: 8, marginBottom: 16, borderBottom: "1px solid #1e2231" }}>
              {[{ id: "devis", label: "Devis" }, { id: "3d", label: "Vue 3D" }, { id: "calcul", label: "Calcul" }].map(t => (
                <button key={t.id} onClick={() => setActiveResultTab(t.id)}
                  style={{ background: activeResultTab === t.id ? "#0f1117" : "transparent", border: activeResultTab === t.id ? "1px solid #1e2231" : "1px solid transparent", borderBottom: activeResultTab === t.id ? "2px solid #f0c040" : "2px solid transparent", color: activeResultTab === t.id ? "#e8eaf2" : "#545870", padding: "8px 16px", cursor: "pointer", fontSize: 14, fontWeight: activeResultTab === t.id ? 600 : 400, borderRadius: "6px 6px 0 0" }}>
                  {t.label}
                </button>
              ))}
            </div>

            {activeResultTab === "devis" && result.projet && (
              <div style={cardStyle}>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 }}>
                  {[
                    { label: "Surface", val: (result.projet.surface || "?") + "m2" },
                    { label: "Dimensions", val: (result.projet.longueur || "?") + "x" + (result.projet.largeur || "?") + "m" },
                    { label: "Pente", val: (result.projet.pente || "?") + " deg" },
                    { label: "Type", val: result.projet.type || "?" }
                  ].map(info => (
                    <div key={info.label} style={{ background: "#0f1117", borderRadius: 8, padding: 12, border: "1px solid #1e2231" }}>
                      <div style={{ color: "#545870", fontSize: 12 }}>{info.label}</div>
                      <div style={{ color: "#f0c040", fontWeight: 700, fontSize: 16, marginTop: 2 }}>{info.val}</div>
                    </div>
                  ))}
                </div>
                <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: 20 }}>
                  <thead>
                    <tr style={{ background: "#2a2e40" }}>
                      {["Categorie", "Designation", "U", "Qte", "PU HT", "Total HT"].map(h => (
                        <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "#545870", fontSize: 12 }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(result.postes || []).map((p, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid #1e2231", background: i % 2 === 0 ? "transparent" : "#0f1117" }}>
                        <td style={{ padding: "8px 12px", color: "#60a5fa", fontSize: 13 }}>{p.categorie}</td>
                        <td style={{ padding: "8px 12px", color: "#e8eaf2", fontSize: 13 }}>{p.designation}</td>
                        <td style={{ padding: "8px 12px", color: "#545870", fontSize: 13 }}>{p.unite}</td>
                        <td style={{ padding: "8px 12px", color: "#e8eaf2", fontSize: 13 }}>{p.quantite}</td>
                        <td style={{ padding: "8px 12px", color: "#e8eaf2", fontSize: 13 }}>{p.prixUnitaireHT ? p.prixUnitaireHT.toLocaleString("fr-FR") : 0} EUR</td>
                        <td style={{ padding: "8px 12px", color: "#f0c040", fontWeight: 600, fontSize: 13 }}>{p.totalHT ? p.totalHT.toLocaleString("fr-FR") : 0} EUR</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <div style={{ background: "#0f1117", border: "1px solid #1e2231", borderRadius: 10, padding: 16, minWidth: 220 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8, color: "#545870" }}>
                      <span>Total HT</span><span style={{ color: "#e8eaf2" }}>{result.totaux ? result.totaux.totalHT.toLocaleString("fr-FR") : 0} EUR</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12, color: "#545870" }}>
                      <span>TVA</span><span style={{ color: "#e8eaf2" }}>{result.totaux ? result.totaux.tva.toLocaleString("fr-FR") : 0} EUR</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700, fontSize: 18, color: "#f0c040", borderTop: "1px solid #1e2231", paddingTop: 12 }}>
                      <span>Total TTC</span><span>{result.totaux ? result.totaux.totalTTC.toLocaleString("fr-FR") : 0} EUR</span>
                    </div>
                  </div>
                </div>
                {result.notes && result.notes.length > 0 && (
                  <div style={{ marginTop: 16, padding: 14, background: "#0f1117", borderRadius: 8, border: "1px solid #1e2231" }}>
                    <div style={{ color: "#545870", fontSize: 12, marginBottom: 8, textTransform: "uppercase" }}>Notes techniques</div>
                    {result.notes.map((n, i) => <div key={i} style={{ color: "#e8eaf2", fontSize: 13, marginBottom: 4 }}>{n}</div>)}
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
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700 }}>Mes projets</h2>
          <Badge color="#60a5fa">{projects.length} devis</Badge>
        </div>
        {projects.length === 0 ? (
          <div style={{ ...cardStyle, textAlign: "center", padding: 40 }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>📁</div>
            <div style={{ color: "#545870" }}>Aucun projet pour l instant. Generez votre premier devis !</div>
          </div>
        ) : (
          <div style={{ display: "grid", gap: 12 }}>
            {projects.map(p => (
              <div key={p.id} style={{ ...cardStyle, display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer", marginBottom: 0, transition: "border 0.15s" }}
                onMouseEnter={(e) => e.currentTarget.style.border = "1px solid #f0c040"}
                onMouseLeave={(e) => e.currentTarget.style.border = "1px solid #1e2231"}
                onClick={() => loadProjectDetails(p)}>
                <div style={{ display: "flex", alignItems: "center", gap: 16, flex: 1 }}>
                  <div style={{ width: 44, height: 44, background: "#f0c04018", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22 }}>🏠</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 15 }}>{p.nom}</div>
                    <div style={{ color: "#545870", fontSize: 13 }}>{p.commune} - {p.dims} - {new Date(p.date).toLocaleDateString("fr-FR")}</div>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: "#f0c040", fontWeight: 700, fontSize: 18 }}>{p.ttc.toLocaleString("fr-FR")} EUR</div>
                    <div style={{ color: "#545870", fontSize: 12 }}>TTC</div>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteProject(p.id, p.nom); }}
                    title="Supprimer ce projet"
                    style={{ background: "transparent", border: "1px solid #2a2e40", color: "#ef4444", borderRadius: 6, padding: "6px 10px", cursor: "pointer", fontSize: 13, fontWeight: 600, transition: "all 0.15s" }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = "#ef444418"; e.currentTarget.style.borderColor = "#ef4444"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "#2a2e40"; }}>
                    Supprimer
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    )}

    {activeTab === "parametres" && (
      <div>
        <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20 }}>Parametres</h2>
        <div style={cardStyle}>
          <div style={{ fontWeight: 600, marginBottom: 16, color: "#f0c040" }}>Informations entreprise</div>
          {[{ label: "Nom de l entreprise", key: "entreprise" }, { label: "SIRET", key: "siret" }, { label: "Adresse", key: "adresse" }].map(f => (
            <div key={f.key} style={{ marginBottom: 14 }}>
              <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>{f.label}</label>
              <input value={params[f.key]} onChange={e => setParams(prev => ({ ...prev, [f.key]: e.target.value }))} style={inputStyle} />
            </div>
          ))}
        </div>
        <div style={cardStyle}>
          <div style={{ fontWeight: 600, marginBottom: 16, color: "#f0c040" }}>Tarification</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
            {[{ label: "Taux horaire EUR/h", key: "tauxHoraire" }, { label: "TVA %", key: "tva" }, { label: "Marge %", key: "marge" }].map(f => (
              <div key={f.key}>
                <label style={{ display: "block", color: "#545870", fontSize: 13, marginBottom: 6 }}>{f.label}</label>
                <input type="number" value={params[f.key]} onChange={e => setParams(prev => ({ ...prev, [f.key]: parseFloat(e.target.value) }))} style={inputStyle} />
              </div>
            ))}
          </div>
        </div>
        <div style={cardStyle}>
          <div style={{ fontWeight: 600, marginBottom: 16, color: "#f0c040" }}>Mentions legales</div>
          <textarea value={params.mentions} onChange={e => setParams(prev => ({ ...prev, mentions: e.target.value }))} rows={3} style={{ ...inputStyle, resize: "vertical" }} />
        </div>
        <button style={{ ...btnPrimary, padding: "12px 24px" }}>Sauvegarder</button>
      </div>
    )}

    {activeTab === "compte" && (
      <div>
        <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20 }}>Mon compte</h2>
        <div style={cardStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
            <div style={{ width: 56, height: 56, background: "#f0c040", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28 }}>👤</div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 18 }}>{params.entreprise || "Mon entreprise"}</div>
              <Badge color="#3ecf8e">Plan Pro</Badge>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
            {[{ label: "Devis ce mois", val: projects.length, icon: "📋" }, { label: "Total generes", val: projects.length, icon: "📁" }, { label: "Jours restants", val: "23", icon: "📅" }].map(s => (
              <div key={s.label} style={{ background: "#0f1117", borderRadius: 8, padding: 16, border: "1px solid #1e2231", textAlign: "center" }}>
                <div style={{ fontSize: 28, marginBottom: 8 }}>{s.icon}</div>
                <div style={{ fontSize: 24, fontWeight: 700, color: "#f0c040" }}>{s.val}</div>
                <div style={{ color: "#545870", fontSize: 13 }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )}

  </main>
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
