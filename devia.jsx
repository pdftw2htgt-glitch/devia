import { useState, useRef, useEffect, useCallback } from "react";
import * as THREE from "three";
// ─── THEME ───────────────────────────────────────────────────────────────────
const T = {
bg:"#08090c", surface:"#0f1117", card:"#13161f", border:"#1e2231",
accent:"#f0c040", accentLo:"#f0c04018", text:"#e8eaf2", muted:"#545870",
dim:"#2a2e40", wood:"#c4894a", woodDk:"#8b5e2e", ok:"#3ecf8e",
blue:"#60a5fa", purple:"#a78bfa", orange:"#f97316", red:"#ef4444",
};
// ─── ZONES EUROCODE ──────────────────────────────────────────────────────────
const ZONES_DB = {
"paris":{neige:"A1",vent:"2",sismique:"1",pays:"FR"},"ile-de-france":{neige:"A1",vent:"2",s
"lyon":{neige:"A2",vent:"2",sismique:"1",pays:"FR"},"marseille":{neige:"A1",vent:"3",sismiq
"bordeaux":{neige:"A1",vent:"2",sismique:"2",pays:"FR"},"toulouse":{neige:"A2",vent:"2",sis
"nantes":{neige:"A1",vent:"3",sismique:"1",pays:"FR"},"strasbourg":{neige:"B1",vent:"1",sis
"lille":{neige:"A1",vent:"3",sismique:"1",pays:"FR"},"nice":{neige:"A2",vent:"3",sismique:"
"grenoble":{neige:"C1",vent:"2",sismique:"4",pays:"FR"},"clermont":{neige:"B2",vent:"2",sis
"limoges":{neige:"A2",vent:"2",sismique:"2",pays:"FR"},"rennes":{neige:"A1",vent:"3",sismiq
"rouen":{neige:"A1",vent:"3",sismique:"1",pays:"FR"},"dijon":{neige:"B1",vent:"1",sismique:
"metz":{neige:"B1",vent:"1",sismique:"2",pays:"FR"},"nancy":{neige:"B1",vent:"1",sismique:"
"reims":{neige:"A2",vent:"2",sismique:"1",pays:"FR"},"le havre":{neige:"A1",vent:"4",sismiq
"brest":{neige:"A1",vent:"4",sismique:"1",pays:"FR"},"toulon":{neige:"A1",vent:"3",sismique
"montpellier":{neige:"A1",vent:"3",sismique:"3",pays:"FR"},"perpignan":{neige:"A1",vent:"4"
"pau":{neige:"B1",vent:"2",sismique:"4",pays:"FR"},"bayonne":{neige:"A2",vent:"3",sismique:
"chamonix":{neige:"C2",vent:"2",sismique:"4",pays:"FR"},"annecy":{neige:"C1",vent:"2",sismi
"chambery":{neige:"C1",vent:"2",sismique:"4",pays:"FR"},"ajaccio":{neige:"A1",vent:"3",sism
"bastia":{neige:"A2",vent:"3",sismique:"3",pays:"FR"},"martinique":{neige:"—",vent:"4",sism
"guadeloupe":{neige:"—",vent:"4",sismique:"5",pays:"FR-DOM"},"reunion":{neige:"—",vent:"4",
"bruxelles":{neige:"—",vent:"3",sismique:"1",pays:"BE"},"liege":{neige:"A1",vent:"2",sismiq
"geneve":{neige:"B1",vent:"2",sismique:"2",pays:"CH"},"lausanne":{neige:"B1",vent:"2",sismi
"zurich":{neige:"C1",vent:"2",sismique:"2",pays:"CH"},"bale":{neige:"B1",vent:"1",sismique:
"luxembourg":{neige:"B1",vent:"2",sismique:"1",pays:"LU"},
};
const CHARGES_NEIGE={"A1":a=>a<=200?0.20:a<=500?0.35:0.45,"A2":a=>a<=200?0.25:a<=500?0.40:0.5
const PRESSION_VENT={"1":280,"2":400,"3":500,"4":700};
const ACCEL_SISMIQUE={"1":0.4,"2":0.7,"3":1.1,"4":1.6,"5":3.0};
function getZones(commune,altitude=100){
if(!commune)return null;
const key=commune.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").trim();
let zone=ZONES_DB[key];
if(!zone){const f=Object.keys(ZONES_DB).find(k=>key.includes(k)||k.includes(key));zone=f?ZO
if(!zone)return null;
const alt=parseInt(altitude)||100;
return{...zone,altitude:alt,sk:CHARGES_NEIGE[zone.neige]?CHARGES_NEIGE[zone.neige](alt):0,q
}
// ─── QUESTIONS INTELLIGENTES ─────────────────────────────────────────────────
const QUESTIONS_CONFIG = [
{id:"type",label:"Type de charpente",options:["2 pans traditionnelle","4 pans / croupe","Fe
{id:"couverture",label:"Type de couverture",options:["Tuiles canal","Tuiles mécaniques","Ar
{id:"essence",label:"Essence de bois",options:["Douglas","Épicéa","Chêne","Pin sylvestre","
{id:"combles",label:"Combles",options:["Combles perdus","Combles aménageables","Sans comble
];
function getMissingQuestions(prompt){return QUESTIONS_CONFIG.filter(q=>!q.detect.test(prompt)
// ─── 3D VIEWER ───────────────────────────────────────────────────────────────
function Viewer3D({params,active}){
const mountRef=useRef(null),frameRef=useRef(null);
const rotRef=useRef({theta:0.7,phi:0.45,r:16}),dragRef=useRef({down:false,lx:0,ly:0});
const build=useCallback(()=>{
const scene=new THREE.Scene();
scene.background=new THREE.Color(T.bg);scene.fog=new THREE.FogExp2(T.bg,0.04);
scene.add(new THREE.GridHelper(40,40,"#141824","#111420"));
const{w=8,l=12,h=3,pente=35}=params;
const rise=(w/2)*Math.tan((pente*Math.PI)/180);
const mat=c=>new THREE.MeshStandardMaterial({color:c,roughness:0.82,metalness:0.04});
const box=(W,H,D,m)=>new THREE.Mesh(new THREE.BoxGeometry(W,H,D),mat(m));
const add=m=>scene.add(m);
const wm=new THREE.MeshStandardMaterial({color:"#1a2040",transparent:true,opacity:0.28,ro
[[w,h,0.08,0,h/2,-l/2],[w,h,0.08,0,h/2,l/2],[0.08,h,l,-w/2,h/2,0],[0.08,h,l,w/2,h/2,0]].f
[-w/2+0.08,w/2-0.08].forEach(x=>{const m=box(0.14,0.14,l,T.wood);m.position.set(x,h,0);ad
const fg=box(0.14,0.14,l,T.woodDk);fg.position.set(0,h+rise,0);add(fg);
const rLen=Math.sqrt((w/2)**2+rise**2)+0.4,rAng=Math.atan2(rise,w/2),nR=Math.ceil(l/0.55)
for(let i=0;i<=nR;i++){const z=-l/2+(i/nR)*l;[-1,1].forEach(s=>{const r=box(0.07,0.11,rLe
[0.25,0.5,0.75].forEach(t=>{const px=(w/2)*(1-t),py=h+rise*t;[-1,1].forEach(s=>{const p=b
for(let i=0;i<=nR;i+=3){const z=-l/2+(i/nR)*l;const e=box(w-0.2,0.14,0.1,T.woodDk);e.posi
const rm=new THREE.MeshStandardMaterial({color:"#1c2850",transparent:true,opacity:0.22,si
[-1,1].forEach(s=>{const rf=new THREE.Mesh(new THREE.PlaneGeometry(rLen+0.2,l),rm);rf.rot
scene.add(new THREE.AmbientLight("#b0c8e0",0.65));
const sun=new THREE.DirectionalLight("#fff4d0",1.5);sun.position.set(12,20,8);add(sun);
return scene;
},[params]);
useEffect(()=>{
if(!mountRef.current||!active)return;
const W=mountRef.current.clientWidth,H=mountRef.current.clientHeight;
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(W,H);renderer.setPixelRatio(window.devicePixelRatio);
mountRef.current.appendChild(renderer.domElement);
const camera=new THREE.PerspectiveCamera(44,W/H,0.1,200);
const scene=build();
const tick=()=>{frameRef.current=requestAnimationFrame(tick);const{theta,phi,r}=rotRef.cu
tick();
const onDown=e=>{dragRef.current={down:true,lx:e.clientX,ly:e.clientY};};
const onUp=()=>{dragRef.current.down=false;};
const onMove=e=>{if(!dragRef.current.down)return;rotRef.current.theta-=(e.clientX-dragRef
const onWheel=e=>{rotRef.current.r=Math.max(5,Math.min(35,rotRef.current.r+e.deltaY*0.02)
const onResize=()=>{if(!mountRef.current)return;const W=mountRef.current.clientWidth,H=mo
renderer.domElement.addEventListener("mousedown",onDown);window.addEventListener("mouseup
return()=>{cancelAnimationFrame(frameRef.current);renderer.domElement.removeEventListener
},[build,active]);
return(<div style={{position:"relative",width:"100%",height:"100%"}}><div ref={mountRef} st
}
// ─── DEVIS TABLE ──────────────────────────────────────────────────────────────
function DevisTable({devis}){
if(!devis?.lignes)return null;
return(
<div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:12}}>
<div style={{display:"flex",color:T.muted,borderBottom:`1px solid ${T.border}`,paddingB
<span style={{flex:3}}>DÉSIGNATION</span><span style={{flex:1,textAlign:"right"}}>QTÉ
</div>
{devis.lignes.map((l,i)=>(
<div key={i} style={{display:"flex",padding:"6px 0",borderBottom:`1px solid ${T.borde
<span style={{flex:3,color:T.text,lineHeight:1.4}}>{l.designation}</span>
<span style={{flex:1,textAlign:"right",color:T.muted}}>{l.quantite}</span>
<span style={{flex:"0 0 40px",textAlign:"right",color:T.muted}}>{l.unite}</span>
<span style={{flex:1,textAlign:"right",color:T.text}}>{l.prixUnitaire?.toFixed(2)}<
<span style={{flex:1,textAlign:"right",color:T.accent,fontWeight:600}}>{l.total?.to
</div>
))}
<div style={{marginTop:16,paddingTop:12,borderTop:`1px solid ${T.border}`}}>
{[["Sous-total HT",devis.sousTotal,T.muted],["TVA 20%",devis.tva,T.muted],["TOTAL TTC
<div key={label} style={{display:"flex",justifyContent:"space-between",marginBottom
<span>{label}</span><span>{val?.toFixed(2)} €</span>
</div>
))}
</div>
</div>
{devis.notes&&<div style={{marginTop:14,padding:"10px 14px",background:T.accentLo,borde
);
}
// ─── FEUILLE DE CALCUL ────────────────────────────────────────────────────────
function FeuilleCalcTable({calc}){
if(!calc)return(<div style={{color:T.muted,fontSize:13,textAlign:"center",padding:"40px 0"}
return(
<div style={{fontFamily:"'JetBrains Mono',monospace"}}>
{calc.charges&&(
<div style={{marginBottom:24}}>
<div style={{fontSize:11,color:T.blue,textTransform:"uppercase",letterSpacing:"0.1e
{calc.charges.map((c,i)=>(
<div key={i} style={{display:"flex",justifyContent:"space-between",padding:"5px 0
<span style={{color:T.muted}}>{c.label}</span><span style={{color:T.text}}>{c.v
</div>
))}
</div>
)}
{calc.elements&&(
<div style={{marginBottom:24}}>
<div style={{fontSize:11,color:T.purple,textTransform:"uppercase",letterSpacing:"0.
{calc.elements.map((e,i)=>(
<div key={i} style={{marginBottom:12,padding:"12px 16px",background:T.surface,bor
<div style={{color:T.text,fontWeight:600,marginBottom:8,fontSize:13}}>{e.elemen
{[["Section retenue",e.section,true],["Contrainte de flexion",`${e.contrainte}
<div key={label} style={{display:"flex",justifyContent:"space-between",paddin
<span style={{color:T.muted}}>{label}</span><span style={{color:hi?T.accent
</div>
))}
</div>
</div>
<div style={{marginTop:8,padding:"5px 12px",background:parseFloat(e.coefficient
{parseFloat(e.coefficient)<=1?"Section vérifiée ✓":"Section insuffisante — re
))}
</div>
)}
{calc.assemblages&&(
<div style={{marginBottom:24}}>
<div style={{fontSize:11,color:T.orange,textTransform:"uppercase",letterSpacing:"0.
{calc.assemblages.map((a,i)=>(
<div key={i} style={{display:"flex",justifyContent:"space-between",padding:"5px 0
<span style={{color:T.muted}}>{a.type}</span><span style={{color:T.text}}>{a.sp
</div>
))}
</div>
)}
{calc.conclusion&&(
<div style={{padding:"14px 18px",background:`${T.ok}11`,border:`1px solid ${T.ok}33`,
<div style={{color:T.ok,fontWeight:600,marginBottom:4}}>Conclusion technique</div>
{calc.conclusion}
</div>
)}
</div>
);
}
// ─── FILE PILL ────────────────────────────────────────────────────────────────
function FilePill({file,onRemove}){
return(
<div style={{display:"flex",alignItems:"center",gap:8,padding:"6px 12px",background:T.car
<span>{file.type.startsWith("image/")?" ":" "}</span>
<span style={{maxWidth:120,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap
<button onClick={onRemove} style={{background:"none",border:"none",color:T.muted,cursor
</div>
);
}
// ─── PAGE PROJETS ─────────────────────────────────────────────────────────────
function PageProjets({projets,onOpen,onDelete}){
return(
<div style={{flex:1,overflowY:"auto",padding:40}}>
<div style={{maxWidth:800,margin:"0 auto"}}>
<div style={{fontSize:22,fontWeight:700,letterSpacing:"-0.03em",marginBottom:6}}>Mes
<div style={{color:T.muted,fontSize:13,marginBottom:32}}>Historique de vos devis géné
{projets.length===0?(
<div style={{textAlign:"center",padding:"80px 0",color:T.muted}}>
<div style={{fontSize:40,marginBottom:16}}> </div>
<div style={{fontSize:15,color:T.text,marginBottom:8}}>Aucun projet pour le momen
<div style={{fontSize:13}}>Générez votre premier devis pour le voir apparaître ic
</div>
):(
<div style={{display:"flex",flexDirection:"column",gap:12}}>
{projets.map((p,i)=>(
<div key={i} style={{background:T.card,border:`1px solid ${T.border}`,borderRad
onClick={()=>onOpen(p)} onMouseEnter={e=>e.currentTarget.style.borderColor=T.
<div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-s
<div>
<div style={{fontWeight:600,fontSize:14,marginBottom:4}}>{p.description}<
<div style={{fontSize:12,color:T.muted}}>{p.date} · {p.commune||"Commune
</div>
<div style={{display:"flex",alignItems:"center",gap:10}}>
<div style={{fontSize:15,fontWeight:700,color:T.accent}}>{p.devis?.totalT
<button onClick={e=>{e.stopPropagation();onDelete(i);}} style={{backgroun
</div>
</div>
{p.params&&(
<div style={{display:"flex",gap:8,marginTop:10,flexWrap:"wrap"}}>
{[`${p.params.w}×${p.params.l}m`,`Pente ${p.params.pente}°`,`Mur ${p.para
<span key={tag} style={{padding:"3px 10px",background:T.surface,border:
))}
</div>
)}
</div>
))}
</div>
)}
</div>
</div>
);
}
// ─── PAGE PARAMETRES ──────────────────────────────────────────────────────────
function PageParametres({settings,onSave}){
const [form,setForm]=useState(settings);
const inp={width:"100%",background:T.surface,border:`1px solid ${T.border}`,borderRadius:8,
return(
<div style={{flex:1,overflowY:"auto",padding:40}}>
<div style={{maxWidth:600,margin:"0 auto"}}>
<div style={{fontSize:22,fontWeight:700,letterSpacing:"-0.03em",marginBottom:6}}>Para
<div style={{color:T.muted,fontSize:13,marginBottom:32}}>Personnalisez DEVIA pour vot
{[
{section:"Votre entreprise",fields:[{key:"nomEntreprise",label:"Nom de l'entreprise
{section:"Tarifs par défaut",fields:[{key:"tauxHoraire",label:"Taux horaire main d'
{section:"Mentions légales",fields:[{key:"validite",label:"Validité du devis (jours
].map(({section,fields})=>(
<div key={section} style={{marginBottom:28}}>
<div style={{fontSize:11,color:T.accent,textTransform:"uppercase",letterSpacing:"
<div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,pad
{fields.map(({key,label,placeholder})=>(
<div key={key}>
<label style={{fontSize:11,color:T.muted,display:"block",marginBottom:5,tex
{key==="mentionsLegales"
?<textarea style={{...inp,minHeight:80,resize:"vertical"}} value={form[ke
:<input style={inp} value={form[key]||""} onChange={e=>setForm(f=>({...f,
}
</div>
))}
</div>
</div>
))}
<button onClick={()=>onSave(form)} style={{width:"100%",padding:"13px 0",background:T
Enregistrer les paramètres
</button>
</div>
</div>
);
}
// ─── PAGE COMPTE ──────────────────────────────────────────────────────────────
function PageCompte(){
return(
<div style={{flex:1,overflowY:"auto",padding:40}}>
<div style={{maxWidth:600,margin:"0 auto"}}>
<div style={{fontSize:22,fontWeight:700,letterSpacing:"-0.03em",marginBottom:6}}>Mon
<div style={{color:T.muted,fontSize:13,marginBottom:32}}>Informations et abonnement</
<div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,padding
<div style={{fontSize:11,color:T.accent,textTransform:"uppercase",letterSpacing:"0.
<div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marg
<div><div style={{fontSize:18,fontWeight:700}}>Plan Gratuit</div><div style={{fon
<div style={{padding:"6px 16px",background:`${T.ok}18`,border:`1px solid ${T.ok}3
</div>
{["Génération de devis illimitée","Modélisation 3D interactive","Zones Eurocodes in
<div key={f} style={{display:"flex",gap:10,alignItems:"center",fontSize:13,color:
<span style={{color:T.ok}}>✓</span>{f}
</div>
))}
</div>
<div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,padding
<div style={{fontSize:11,color:T.accent,textTransform:"uppercase",letterSpacing:"0.
<div style={{display:"flex",gap:12}}>
{[["Devis générés","—"],["Ce mois","—"],["Valeur totale","—"]].map(([l,v])=>(
<div key={l} style={{flex:1,padding:"14px 16px",background:T.surface,borderRadi
<div style={{fontSize:22,fontWeight:700,color:T.accent,marginBottom:4}}>{v}</
<div style={{fontSize:11,color:T.muted}}>{l}</div>
</div>
))}
</div>
</div>
</div>
</div>
);
}
// ─── MAIN ─────────────────────────────────────────────────────────────────────
export default function Devia(){
const [page,setPage]=useState("home");
const [prompt,setPrompt]=useState("");
const [files,setFiles]=useState([]);
const [state,setState]=useState("idle");
const [result,setResult]=useState(null);
const [tab,setTab]=useState("devis");
const [errMsg,setErrMsg]=useState("");
const [commune,setCommune]=useState("");
const [altitude,setAltitude]=useState("100");
const [zones,setZones]=useState(null);
const [missingQ,setMissingQ]=useState([]);
const [answers,setAnswers]=useState({});
const [projets,setProjets]=useState([]);
const [settings,setSettings]=useState({nomEntreprise:"",siret:"",adresse:"",telephone:"",em
const [savedMsg,setSavedMsg]=useState(false);
const fileRef=useRef(null),textRef=useRef(null);
useEffect(()=>{if(textRef.current){textRef.current.style.height="auto";textRef.current.styl
useEffect(()=>{if(commune.trim().length>2)setZones(getZones(commune,altitude));else setZone
const addFiles=list=>{const arr=Array.from(list).filter(f=>f.type.startsWith("image/")||f.t
const onDrop=e=>{e.preventDefault();addFiles(e.dataTransfer.files);};
const toBase64=file=>new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.re
const checkAndGenerate=()=>{
if(!prompt.trim())return;
const missing=getMissingQuestions(prompt);
if(missing.length>0){setMissingQ(missing);setState("questions");return;}
doGenerate({});
};
const doGenerate=async(extraAnswers)=>{
setState("loading");setErrMsg("");
const allAnswers={...answers,...extraAnswers};
try{
const content=[];
for(const f of files){if(f.type.startsWith("image/")){const data=await toBase64(f);cont
const zonesInfo=zones?`DONNÉES GÉOGRAPHIQUES (Eurocodes) : Commune ${commune}, Altitude
const answersText=Object.entries(allAnswers).map(([k,v])=>`- ${k}: ${v}`).join("\n");
content.push({type:"text",text:`Tu es un bureau d'études charpente bois expert Eurocode
Description : ${prompt}
${answersText?`Précisions :\n${answersText}`:""}
${zonesInfo}
Réponds UNIQUEMENT en JSON valide :
{
"description": "résumé court",
"params": { "w": 8, "l": 12, "h": 3, "pente": 35 },
"devis": {
"lignes": [{ "designation": "...", "quantite": 12.5, "unite": "ml", "prixUnitaire": 8.50,
"sousTotal": 0, "tva": 0, "totalTTC": 0, "notes": "..."
},
"calcul": {
"charges": [{ "label": "Charge permanente", "valeur": "0.45", "unite": "kN/m²" }],
"elements": [{ "element": "Chevron 60×180mm", "section": "60×180 mm", "contrainte": "8.2"
"assemblages": [{ "type": "Sabot chevron/panne", "specification": "Simpson LBV 60×180" }]
"conclusion": "Structure vérifiée sous toutes les combinaisons réglementaires."
}
}
Prix marché français 2024. Sections dimensionnées selon charges réelles.`});
const res=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/j
const data=await res.json();
const raw=data.content?.map(b=>b.text||"").join("").trim();
const clean=raw.replace(/```json|```/g,"").trim();
const parsed=JSON.parse(clean);
const projet={...parsed,zones,commune,date:new Date().toLocaleDateString("fr-FR",{day:"
setResult(projet);
setProjets(prev=>[projet,...prev].slice(0,50));
setState("done");setTab("devis");
}catch(e){
console.error(e);
setErrMsg("Une erreur est survenue. Vérifiez que le proxy API est bien configuré setState("error");
sur Ve
}
};
const reset=()=>{setState("idle");setResult(null);setPrompt("");setFiles([]);setCommune("")
const navBtn=(id,label)=>(
<button key={id} onClick={()=>setPage(id)} style={{padding:"7px 16px",background:page===i
{label}
</button>
);
return(
<div style={{minHeight:"100vh",background:T.bg,color:T.text,fontFamily:"'Inter',system-ui
{/* HEADER */}
<header style={{display:"flex",alignItems:"center",justifyContent:"space-between",paddi
<div style={{display:"flex",alignItems:"center",gap:12,cursor:"pointer"}} onClick={()
<div style={{width:36,height:36,background:T.accent,borderRadius:10,display:"flex",
<div>
<div style={{fontWeight:700,fontSize:17,letterSpacing:"-0.03em",color:T.text}}>DE
<div style={{fontSize:10,color:T.muted,letterSpacing:"0.08em",textTransform:"uppe
</div>
</div>
<div style={{display:"flex",gap:8}}>
{navBtn("projets","Mes projets")}
{navBtn("parametres","Paramètres")}
{navBtn("compte","Mon compte")}
</div>
</header>
{/* PAGES */}
{page==="projets"&&<PageProjets projets={projets} onOpen={p=>{setResult(p);setState("do
{page==="parametres"&&<PageParametres settings={settings} onSave={s=>{setSettings(s);se
{page==="compte"&&<PageCompte/>}
{savedMsg&&<div style={{position:"fixed",bottom:24,right:24,padding:"12px 20px",backgro
{/* HOME */}
{page==="home"&&(
<>
<div style={{flex:state==="done"?0:1,padding:"60px 32px 40px",display:"flex",flexDi
{state==="idle"&&(
<>
<div style={{fontSize:52,fontWeight:700,letterSpacing:"-0.04em",textAlign:"ce
Estimez votre charpente<br/><span style={{color:T.accent}}>en quelques seco
</div>
<div style={{color:T.muted,fontSize:16,textAlign:"center",marginBottom:40,let
Décrivez votre projet — DEVIA génère un devis détaillé, une modélisation 3D
</div>
</>
)}
<div style={{width:"100%",maxWidth:760,background:T.card,border:`1.5px solid ${st
<textarea ref={textRef} value={prompt} onChange={e=>setPrompt(e.target.value)}
placeholder="Décrivez votre projet : type de charpente, dimensions approximat
style={{width:"100%",minHeight:80,maxHeight:220,background:"none",border:"non
<div style={{display:"flex",gap:10,padding:"0 16px 12px",borderBottom:`1px soli
<div style={{flex:2,position:"relative"}}>
<input value={commune} onChange={e=>setCommune(e.target.value)} placeholder
{zones&&<div style={{position:"absolute",right:10,top:"50%",transform:"tran
</div>
<input value={altitude} onChange={e=>setAltitude(e.target.value)} placeholder
</div>
{zones&&(
<div style={{display:"flex",gap:8,padding:"10px 16px",flexWrap:"wrap",borderB
{[["Neige",`Zone ${zones.neige} — ${zones.sk} kN/m²`,"#60a5fa"],["Vent",`Zo
<div key={l} style={{padding:"4px 12px",background:`${c}14`,border:`1px s
<span style={{color:c,fontWeight:600}}>{l}</span><span style={{color:T.
</div>
))}
</div>
)}
{files.length>0&&<div style={{display:"flex",flexWrap:"wrap",gap:8,padding:"0 1
<div style={{display:"flex",alignItems:"center",justifyContent:"space-between",
<div style={{display:"flex",gap:8}}>
<button onClick={()=>fileRef.current?.click()} style={{padding:"7px 14px",b
<input ref={fileRef} type="file" multiple accept="image/*,application/pdf"
</div>
<div style={{display:"flex",alignItems:"center",gap:12}}>
<span style={{fontSize:11,color:T.muted}}>Ctrl + Entrée</span>
<button onClick={checkAndGenerate} disabled={state==="loading"||!prompt.tri
style={{padding:"9px 22px",background:state==="loading"||!prompt.trim()?T
{state==="loading"?"Analyse en cours…":"Générer le devis"}
</button>
</div>
</div>
</div>
{errMsg&&<div style={{marginTop:12,color:"#e05555",fontSize:12,textAlign:"center"
{state==="idle"&&<div onDrop={onDrop} onDragOver={e=>e.preventDefault()} style={{
</div>
{/* QUESTIONS */}
{state==="questions"&&(
<div style={{flex:1,display:"flex",alignItems:"center",justifyContent:"center",pa
<div style={{maxWidth:560,width:"100%",background:T.card,border:`1px solid ${T.
<div style={{fontSize:16,fontWeight:700,marginBottom:6}}>Quelques précisions<
<div style={{color:T.muted,fontSize:13,marginBottom:24}}>Pour générer un devi
{missingQ.map(q=>(
<div key={q.id} style={{marginBottom:20}}>
<div style={{fontSize:12,color:T.accent,textTransform:"uppercase",letterS
<div style={{display:"flex",flexWrap:"wrap",gap:8}}>
{q.options.map(opt=>(
<button key={opt} onClick={()=>setAnswers(a=>({...a,[q.label]:opt}))}
style={{padding:"8px 16px",background:answers[q.label]===opt?T.acce
{opt}
</button>
))}
</div>
</div>
))}
<div style={{display:"flex",gap:10,marginTop:8}}>
<button onClick={()=>setState("idle")} style={{flex:1,padding:"11px 0",back
<button onClick={()=>doGenerate(answers)} style={{flex:2,padding:"11px 0",b
</div>
</div>
</div>
)}
{/* RÉSULTATS */}
{state==="done"&&result&&(
<div style={{flex:1,display:"flex",flexDirection:"column",overflow:"hidden"}}>
<div style={{display:"flex",alignItems:"center",borderBottom:`1px solid ${T.bor
{[["devis","Devis estimatif"],["3d","Modélisation 3D"],["calcul","Feuille de
<button key={id} onClick={()=>setTab(id)} style={{padding:"14px 22px",backg
))}
<div style={{marginLeft:"auto",fontSize:12,color:T.muted}}>{result.descriptio
<button onClick={reset} style={{marginLeft:16,padding:"6px 16px",background:"
Date()
</div>
<div style={{flex:1,overflow:"hidden",display:"flex"}}>
{tab==="devis"&&(
<div style={{flex:1,overflowY:"auto",padding:"40px 0"}}>
<div style={{maxWidth:700,margin:"0 auto",padding:"0 32px"}}>
<div style={{display:"flex",justifyContent:"space-between",alignItems:"
<div>
<div style={{fontSize:26,fontWeight:800,letterSpacing:"-0.04em"}}>D
<div style={{color:T.muted,fontSize:13,marginTop:2}}>N° {new </div>
<div style={{padding:"8px 16px",background:T.accentLo,borderRadius:20
<span style={{color:T.accent,fontSize:12,fontWeight:600}}>Devis gén
</div>
</div>
{settings.nomEntreprise&&(
<div style={{background:T.card,border:`1px solid ${T.border}`,borderR
<div style={{fontSize:11,color:T.accent,textTransform:"uppercase",l
<div style={{fontWeight:600}}>{settings.nomEntreprise}</div>
{settings.adresse&&<div style={{color:T.muted,fontSize:13}}>{settin
{settings.telephone&&<div style={{color:T.muted,fontSize:13}}>{sett
</div>
)}
<div style={{background:T.card,border:`1px solid ${T.border}`,borderRad
<div style={{fontSize:11,color:T.accent,textTransform:"uppercase",let
<div style={{color:T.text,fontSize:14,lineHeight:1.6}}>{result.descri
{result.params&&(
<div style={{display:"flex",gap:10,marginTop:12,flexWrap:"wrap"}}>
{[["Largeur",`${result.params.w}m`],["Longueur",`${result.params.
<div key={k} style={{padding:"6px 14px",background:T.surface,bo
<span style={{color:T.muted}}>{k} : </span><span style={{colo
</div>
))}
</div>
)}
</div>
{result.zones&&(
<div style={{background:T.card,border:`1px solid ${T.border}`,borderR
<div style={{fontSize:11,color:T.accent,textTransform:"uppercase",l
<div style={{display:"flex",gap:10,flexWrap:"wrap"}}>
{[["Neige EN 1991-1-3",`Zone ${result.zones.neige}`,`sk = ${resul
<div key={label} style={{flex:"1 1 140px",padding:"12px 16px",b
<div style={{fontSize:10,color:T.muted,marginBottom:4,textTra
<div style={{color,fontWeight:700,fontSize:15,marginBottom:2}
<div style={{color:T.muted,fontSize:11}}>{val}</div>
</div>
))}
</div>
</div>
)}
<div style={{background:T.card,border:`1px solid ${T.border}`,borderRad
<DevisTable devis={result.devis}/>
</div>
{settings.mentionsLegales&&<div style={{marginTop:16,padding:"12px 16px
<div style={{marginTop:20,display:"flex",gap:10,justifyContent:"flex-en
<button onClick={()=>window.print()} style={{padding:"10px 20px",back
<button style={{padding:"10px 20px",background:T.accent,border:"none"
</div>
</div>
</div>
)}
{tab==="3d"&&<div style={{flex:1,position:"relative"}}><Viewer3D params={resu
{tab==="calcul"&&(
<div style={{flex:1,overflowY:"auto",padding:"40px 0"}}>
<div style={{maxWidth:700,margin:"0 auto",padding:"0 32px"}}>
<div style={{fontSize:22,fontWeight:700,letterSpacing:"-0.03em",marginB
<div style={{color:T.muted,fontSize:13,marginBottom:24}}>Justification
<div style={{background:T.card,border:`1px solid ${T.border}`,borderRad
<FeuilleCalcTable calc={result.calcul}/>
</div>
<div style={{marginTop:16,display:"flex",justifyContent:"flex-end"}}>
<button onClick={()=>window.print()} style={{padding:"10px 20px",back
</div>
</div>
</div>
)}
</div>
</div>
)}
{state==="loading"&&(
<div style={{flex:1,display:"flex",flexDirection:"column",alignItems:"center",jus
<div style={{width:56,height:56,border:`3px solid ${T.border}`,borderTop:`3px s
<div style={{color:T.muted,fontSize:14}}>Analyse du projet en cours, veuillez p
</div>
)}
</>
)}
<style>{`
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;
*{box-sizing:border-box;margin:0;padding:0;}
body{background:${T.bg};}
@keyframes spin{to{transform:rotate(360deg)}}
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:${T.surface};}
::-webkit-scrollbar-thumb{background:${T.dim};border-radius:3px;}
textarea::placeholder,input::placeholder{color:${T.muted};}
`}</style>
</div>
);
}
