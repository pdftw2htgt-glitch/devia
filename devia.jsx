import { useState, useRef, useEffect, useCallback } from “react”;
import * as THREE from “three”;

// ─── THEME ───────────────────────────────────────────────────────────────────
const T = {
bg:”#08090c”, surface:”#0f1117”, card:”#13161f”, border:”#1e2231”,
accent:”#f0c040”, accentLo:”#f0c04018”, text:”#e8eaf2”, muted:”#545870”,
dim:”#2a2e40”, wood:”#c4894a”, woodDk:”#8b5e2e”, ok:”#3ecf8e”,
blue:”#60a5fa”, purple:”#a78bfa”, orange:”#f97316”, red:”#ef4444”,
};

// ─── ZONES EUROCODE ──────────────────────────────────────────────────────────
const ZONES_DB = {
“paris”:{neige:“A1”,vent:“2”,sismique:“1”,pays:“FR”},“ile-de-france”:{neige:“A1”,vent:“2”,sismique:“1”,pays:“FR”},
“lyon”:{neige:“A2”,vent:“2”,sismique:“1”,pays:“FR”},“marseille”:{neige:“A1”,vent:“3”,sismique:“2”,pays:“FR”},
“bordeaux”:{neige:“A1”,vent:“2”,sismique:“2”,pays:“FR”},“toulouse”:{neige:“A2”,vent:“2”,sismique:“3”,pays:“FR”},
“nantes”:{neige:“A1”,vent:“3”,sismique:“1”,pays:“FR”},“strasbourg”:{neige:“B1”,vent:“1”,sismique:“3”,pays:“FR”},
“lille”:{neige:“A1”,vent:“3”,sismique:“1”,pays:“FR”},“nice”:{neige:“A2”,vent:“3”,sismique:“4”,pays:“FR”},
“grenoble”:{neige:“C1”,vent:“2”,sismique:“4”,pays:“FR”},“clermont”:{neige:“B2”,vent:“2”,sismique:“2”,pays:“FR”},
“limoges”:{neige:“A2”,vent:“2”,sismique:“2”,pays:“FR”},“rennes”:{neige:“A1”,vent:“3”,sismique:“1”,pays:“FR”},
“rouen”:{neige:“A1”,vent:“3”,sismique:“1”,pays:“FR”},“dijon”:{neige:“B1”,vent:“1”,sismique:“1”,pays:“FR”},
“metz”:{neige:“B1”,vent:“1”,sismique:“2”,pays:“FR”},“nancy”:{neige:“B1”,vent:“1”,sismique:“2”,pays:“FR”},
“reims”:{neige:“A2”,vent:“2”,sismique:“1”,pays:“FR”},“le havre”:{neige:“A1”,vent:“4”,sismique:“1”,pays:“FR”},
“brest”:{neige:“A1”,vent:“4”,sismique:“1”,pays:“FR”},“toulon”:{neige:“A1”,vent:“3”,sismique:“3”,pays:“FR”},
“montpellier”:{neige:“A1”,vent:“3”,sismique:“3”,pays:“FR”},“perpignan”:{neige:“A1”,vent:“4”,sismique:“4”,pays:“FR”},
“pau”:{neige:“B1”,vent:“2”,sismique:“4”,pays:“FR”},“bayonne”:{neige:“A2”,vent:“3”,sismique:“4”,pays:“FR”},
“chamonix”:{neige:“C2”,vent:“2”,sismique:“4”,pays:“FR”},“annecy”:{neige:“C1”,vent:“2”,sismique:“4”,pays:“FR”},
“chambery”:{neige:“C1”,vent:“2”,sismique:“4”,pays:“FR”},“ajaccio”:{neige:“A1”,vent:“3”,sismique:“3”,pays:“FR”},
“bastia”:{neige:“A2”,vent:“3”,sismique:“3”,pays:“FR”},“martinique”:{neige:”—”,vent:“4”,sismique:“5”,pays:“FR-DOM”},
“guadeloupe”:{neige:”—”,vent:“4”,sismique:“5”,pays:“FR-DOM”},“reunion”:{neige:”—”,vent:“4”,sismique:“2”,pays:“FR-DOM”},
“bruxelles”:{neige:”—”,vent:“3”,sismique:“1”,pays:“BE”},“liege”:{neige:“A1”,vent:“2”,sismique:“2”,pays:“BE”},
“geneve”:{neige:“B1”,vent:“2”,sismique:“2”,pays:“CH”},“lausanne”:{neige:“B1”,vent:“2”,sismique:“2”,pays:“CH”},
“zurich”:{neige:“C1”,vent:“2”,sismique:“2”,pays:“CH”},“bale”:{neige:“B1”,vent:“1”,sismique:“3”,pays:“CH”},
“luxembourg”:{neige:“B1”,vent:“2”,sismique:“1”,pays:“LU”},
};
const CHARGES_NEIGE={“A1”:a=>a<=200?0.20:a<=500?0.35:0.45,“A2”:a=>a<=200?0.25:a<=500?0.40:0.55,“B1”:a=>a<=200?0.45:a<=500?0.65:0.90,“B2”:a=>a<=200?0.55:a<=500?0.80:1.10,“C1”:a=>a<=200?0.65:a<=500?1.00:1.50,“C2”:a=>a<=200?0.90:a<=500?1.40:2.10,”—”:()=>0};
const PRESSION_VENT={“1”:280,“2”:400,“3”:500,“4”:700};
const ACCEL_SISMIQUE={“1”:0.4,“2”:0.7,“3”:1.1,“4”:1.6,“5”:3.0};
function getZones(commune,altitude=100){
if(!commune)return null;
const key=commune.toLowerCase().normalize(“NFD”).replace(/[\u0300-\u036f]/g,””).trim();
let zone=ZONES_DB[key];
if(!zone){const f=Object.keys(ZONES_DB).find(k=>key.includes(k)||k.includes(key));zone=f?ZONES_DB[f]:null;}
if(!zone)return null;
const alt=parseInt(altitude)||100;
return{…zone,altitude:alt,sk:CHARGES_NEIGE[zone.neige]?CHARGES_NEIGE[zone.neige](alt):0,qb:PRESSION_VENT[zone.vent]||400,ag:ACCEL_SISMIQUE[zone.sismique]||0.4};
}

// ─── QUESTIONS INTELLIGENTES ─────────────────────────────────────────────────
const QUESTIONS_CONFIG = [
{id:“type”,label:“Type de charpente”,options:[“2 pans traditionnelle”,“4 pans / croupe”,“Fermettes industrielles”,“Charpente plate / terrasse”,“Carport / auvent”,“Véranda / extension”],detect:/2\s*pan|4\s*pan|croupe|fermette|terrasse|carport|veranda|extension/i},
{id:“couverture”,label:“Type de couverture”,options:[“Tuiles canal”,“Tuiles mécaniques”,“Ardoise naturelle”,“Bac acier”,“Zinc”,“EPDM / membrane”],detect:/tuile|ardoise|bac acier|zinc|epdm|membrane|couverture/i},
{id:“essence”,label:“Essence de bois”,options:[“Douglas”,“Épicéa”,“Chêne”,“Pin sylvestre”,“Lamellé-collé GL24”,“Lamellé-collé GL28”],detect:/douglas|epicea|epinette|chene|pin|lamelle|essenc/i},
{id:“combles”,label:“Combles”,options:[“Combles perdus”,“Combles aménageables”,“Sans combles”],detect:/comble|amenag|perdu/i},
];
function getMissingQuestions(prompt){return QUESTIONS_CONFIG.filter(q=>!q.detect.test(prompt));}

// ─── 3D VIEWER ───────────────────────────────────────────────────────────────
function Viewer3D({params,active}){
const mountRef=useRef(null),frameRef=useRef(null);
const rotRef=useRef({theta:0.7,phi:0.45,r:16}),dragRef=useRef({down:false,lx:0,ly:0});
const build=useCallback(()=>{
const scene=new THREE.Scene();
scene.background=new THREE.Color(T.bg);scene.fog=new THREE.FogExp2(T.bg,0.04);
scene.add(new THREE.GridHelper(40,40,”#141824”,”#111420”));
const{w=8,l=12,h=3,pente=35}=params;
const rise=(w/2)*Math.tan((pente*Math.PI)/180);
const mat=c=>new THREE.MeshStandardMaterial({color:c,roughness:0.82,metalness:0.04});
const box=(W,H,D,m)=>new THREE.Mesh(new THREE.BoxGeometry(W,H,D),mat(m));
const add=m=>scene.add(m);
const wm=new THREE.MeshStandardMaterial({color:”#1a2040”,transparent:true,opacity:0.28,roughness:1});
[[w,h,0.08,0,h/2,-l/2],[w,h,0.08,0,h/2,l/2],[0.08,h,l,-w/2,h/2,0],[0.08,h,l,w/2,h/2,0]].forEach(([W,H,D,x,y,z])=>{const m=new THREE.Mesh(new THREE.BoxGeometry(W,H,D),wm);m.position.set(x,y,z);add(m);});
[-w/2+0.08,w/2-0.08].forEach(x=>{const m=box(0.14,0.14,l,T.wood);m.position.set(x,h,0);add(m);});
const fg=box(0.14,0.14,l,T.woodDk);fg.position.set(0,h+rise,0);add(fg);
const rLen=Math.sqrt((w/2)**2+rise**2)+0.4,rAng=Math.atan2(rise,w/2),nR=Math.ceil(l/0.55)+1;
for(let i=0;i<=nR;i++){const z=-l/2+(i/nR)*l;[-1,1].forEach(s=>{const r=box(0.07,0.11,rLen,T.wood);r.rotation.z=s*rAng;r.position.set(s*(w/4-0.1),h+rise/2,z);add(r);});}
[0.25,0.5,0.75].forEach(t=>{const px=(w/2)*(1-t),py=h+rise*t;[-1,1].forEach(s=>{const p=box(0.12,0.12,l,T.woodDk);p.position.set(s*px,py,0);add(p);});});
for(let i=0;i<=nR;i+=3){const z=-l/2+(i/nR)*l;const e=box(w-0.2,0.14,0.1,T.woodDk);e.position.set(0,h+0.08,z);add(e);}
const rm=new THREE.MeshStandardMaterial({color:”#1c2850”,transparent:true,opacity:0.22,side:THREE.DoubleSide});
[-1,1].forEach(s=>{const rf=new THREE.Mesh(new THREE.PlaneGeometry(rLen+0.2,l),rm);rf.rotation.z=-s*rAng;rf.position.set(s*(w/4-0.1),h+rise/2,0);add(rf);});
scene.add(new THREE.AmbientLight(”#b0c8e0”,0.65));
const sun=new THREE.DirectionalLight(”#fff4d0”,1.5);sun.position.set(12,20,8);add(sun);
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
const tick=()=>{frameRef.current=requestAnimationFrame(tick);const{theta,phi,r}=rotRef.current;camera.position.set(r*Math.sin(theta)*Math.cos(phi),r*Math.sin(phi),r*Math.cos(theta)*Math.cos(phi));camera.lookAt(0,2,0);renderer.render(scene,camera);};
tick();
const onDown=e=>{dragRef.current={down:true,lx:e.clientX,ly:e.clientY};};
const onUp=()=>{dragRef.current.down=false;};
const onMove=e=>{if(!dragRef.current.down)return;rotRef.current.theta-=(e.clientX-dragRef.current.lx)*0.01;rotRef.current.phi=Math.max(0.1,Math.min(1.4,rotRef.current.phi+(e.clientY-dragRef.current.ly)*0.01));dragRef.current={down:true,lx:e.clientX,ly:e.clientY};};
const onWheel=e=>{rotRef.current.r=Math.max(5,Math.min(35,rotRef.current.r+e.deltaY*0.02));};
const onResize=()=>{if(!mountRef.current)return;const W=mountRef.current.clientWidth,H=mountRef.current.clientHeight;camera.aspect=W/H;camera.updateProjectionMatrix();renderer.setSize(W,H);};
renderer.domElement.addEventListener(“mousedown”,onDown);window.addEventListener(“mouseup”,onUp);window.addEventListener(“mousemove”,onMove);renderer.domElement.addEventListener(“wheel”,onWheel,{passive:true});window.addEventListener(“resize”,onResize);
return()=>{cancelAnimationFrame(frameRef.current);renderer.domElement.removeEventListener(“mousedown”,onDown);window.removeEventListener(“mouseup”,onUp);window.removeEventListener(“mousemove”,onMove);renderer.domElement.removeEventListener(“wheel”,onWheel);window.removeEventListener(“resize”,onResize);renderer.dispose();if(mountRef.current&&renderer.domElement.parentNode===mountRef.current)mountRef.current.removeChild(renderer.domElement);};
},[build,active]);
return(<div style={{position:“relative”,width:“100%”,height:“100%”}}><div ref={mountRef} style={{width:“100%”,height:“100%”}}/><div style={{position:“absolute”,bottom:14,left:14,fontSize:11,color:T.muted,fontFamily:“monospace”,background:`${T.bg}cc`,padding:“4px 10px”,borderRadius:20}}>Cliquer-glisser pour orienter · Molette pour zoomer</div></div>);
}

// ─── DEVIS TABLE ──────────────────────────────────────────────────────────────
function DevisTable({devis}){
if(!devis?.lignes)return null;
return(
<div style={{fontFamily:”‘JetBrains Mono’,monospace”,fontSize:12}}>
<div style={{display:“flex”,color:T.muted,borderBottom:`1px solid ${T.border}`,paddingBottom:8,marginBottom:4,fontSize:11,letterSpacing:“0.06em”}}>
<span style={{flex:3}}>DÉSIGNATION</span><span style={{flex:1,textAlign:“right”}}>QTÉ</span><span style={{flex:“0 0 40px”,textAlign:“right”}}>U.</span><span style={{flex:1,textAlign:“right”}}>P.U.</span><span style={{flex:1,textAlign:“right”}}>TOTAL</span>
</div>
{devis.lignes.map((l,i)=>(
<div key={i} style={{display:“flex”,padding:“6px 0”,borderBottom:`1px solid ${T.border}33`,alignItems:“center”}}>
<span style={{flex:3,color:T.text,lineHeight:1.4}}>{l.designation}</span>
<span style={{flex:1,textAlign:“right”,color:T.muted}}>{l.quantite}</span>
<span style={{flex:“0 0 40px”,textAlign:“right”,color:T.muted}}>{l.unite}</span>
<span style={{flex:1,textAlign:“right”,color:T.text}}>{l.prixUnitaire?.toFixed(2)}</span>
<span style={{flex:1,textAlign:“right”,color:T.accent,fontWeight:600}}>{l.total?.toFixed(2)}</span>
</div>
))}
<div style={{marginTop:16,paddingTop:12,borderTop:`1px solid ${T.border}`}}>
{[[“Sous-total HT”,devis.sousTotal,T.muted],[“TVA 20%”,devis.tva,T.muted],[“TOTAL TTC”,devis.totalTTC,T.accent]].map(([label,val,color])=>(
<div key={label} style={{display:“flex”,justifyContent:“space-between”,marginBottom:6,color,fontWeight:label===“TOTAL TTC”?700:400,fontSize:label===“TOTAL TTC”?15:12}}>
<span>{label}</span><span>{val?.toFixed(2)} €</span>
</div>
))}
</div>
{devis.notes&&<div style={{marginTop:14,padding:“10px 14px”,background:T.accentLo,borderLeft:`3px solid ${T.accent}55`,borderRadius:4,color:T.muted,fontSize:11,lineHeight:1.7}}>{devis.notes}</div>}
</div>
);
}

// ─── FEUILLE DE CALCUL ────────────────────────────────────────────────────────
function FeuilleCalcTable({calc}){
if(!calc)return(<div style={{color:T.muted,fontSize:13,textAlign:“center”,padding:“40px 0”}}>Aucune feuille de calcul disponible pour ce projet.</div>);
return(
<div style={{fontFamily:”‘JetBrains Mono’,monospace”}}>
{calc.charges&&(
<div style={{marginBottom:24}}>
<div style={{fontSize:11,color:T.blue,textTransform:“uppercase”,letterSpacing:“0.1em”,marginBottom:12,paddingBottom:6,borderBottom:`1px solid ${T.border}`}}>Charges appliquées — Eurocodes</div>
{calc.charges.map((c,i)=>(
<div key={i} style={{display:“flex”,justifyContent:“space-between”,padding:“5px 0”,borderBottom:`1px solid ${T.border}22`,fontSize:12}}>
<span style={{color:T.muted}}>{c.label}</span><span style={{color:T.text}}>{c.valeur} {c.unite}</span>
</div>
))}
</div>
)}
{calc.elements&&(
<div style={{marginBottom:24}}>
<div style={{fontSize:11,color:T.purple,textTransform:“uppercase”,letterSpacing:“0.1em”,marginBottom:12,paddingBottom:6,borderBottom:`1px solid ${T.border}`}}>Vérification des éléments — EC5</div>
{calc.elements.map((e,i)=>(
<div key={i} style={{marginBottom:12,padding:“12px 16px”,background:T.surface,borderRadius:10,border:`1px solid ${T.border}`}}>
<div style={{color:T.text,fontWeight:600,marginBottom:8,fontSize:13}}>{e.element}</div>
{[[“Section retenue”,e.section,true],[“Contrainte de flexion”,`${e.contrainte} MPa`,false],[“Résistance admissible”,`${e.resistance} MPa`,false],[“Coefficient d’utilisation”,e.coefficient,false]].map(([label,val,hi])=>(
<div key={label} style={{display:“flex”,justifyContent:“space-between”,padding:“4px 0”,fontSize:12}}>
<span style={{color:T.muted}}>{label}</span><span style={{color:hi?T.accent:T.text,fontWeight:hi?600:400}}>{val}</span>
</div>
))}
<div style={{marginTop:8,padding:“5px 12px”,background:parseFloat(e.coefficient)<=1?`${T.ok}18`:`${T.red}18`,border:`1px solid ${parseFloat(e.coefficient)<=1?T.ok:T.red}33`,borderRadius:6,fontSize:11,color:parseFloat(e.coefficient)<=1?T.ok:T.red,textAlign:“center”}}>
{parseFloat(e.coefficient)<=1?“Section vérifiée ✓”:“Section insuffisante — renforcement requis ✗”}
</div>
</div>
))}
</div>
)}
{calc.assemblages&&(
<div style={{marginBottom:24}}>
<div style={{fontSize:11,color:T.orange,textTransform:“uppercase”,letterSpacing:“0.1em”,marginBottom:12,paddingBottom:6,borderBottom:`1px solid ${T.border}`}}>Assemblages & connecteurs</div>
{calc.assemblages.map((a,i)=>(
<div key={i} style={{display:“flex”,justifyContent:“space-between”,padding:“5px 0”,borderBottom:`1px solid ${T.border}22`,fontSize:12}}>
<span style={{color:T.muted}}>{a.type}</span><span style={{color:T.text}}>{a.specification}</span>
</div>
))}
</div>
)}
{calc.conclusion&&(
<div style={{padding:“14px 18px”,background:`${T.ok}11`,border:`1px solid ${T.ok}33`,borderRadius:10,color:T.muted,fontSize:12,lineHeight:1.7}}>
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
<div style={{display:“flex”,alignItems:“center”,gap:8,padding:“6px 12px”,background:T.card,border:`1px solid ${T.border}`,borderRadius:20,fontSize:12,color:T.text}}>
<span>{file.type.startsWith(“image/”)?“🖼”:“📄”}</span>
<span style={{maxWidth:120,overflow:“hidden”,textOverflow:“ellipsis”,whiteSpace:“nowrap”}}>{file.name}</span>
<button onClick={onRemove} style={{background:“none”,border:“none”,color:T.muted,cursor:“pointer”,fontSize:14,lineHeight:1,padding:0}}>×</button>
</div>
);
}

// ─── PAGE PROJETS ─────────────────────────────────────────────────────────────
function PageProjets({projets,onOpen,onDelete}){
return(
<div style={{flex:1,overflowY:“auto”,padding:40}}>
<div style={{maxWidth:800,margin:“0 auto”}}>
<div style={{fontSize:22,fontWeight:700,letterSpacing:”-0.03em”,marginBottom:6}}>Mes projets</div>
<div style={{color:T.muted,fontSize:13,marginBottom:32}}>Historique de vos devis générés</div>
{projets.length===0?(
<div style={{textAlign:“center”,padding:“80px 0”,color:T.muted}}>
<div style={{fontSize:40,marginBottom:16}}>📋</div>
<div style={{fontSize:15,color:T.text,marginBottom:8}}>Aucun projet pour le moment</div>
<div style={{fontSize:13}}>Générez votre premier devis pour le voir apparaître ici</div>
</div>
):(
<div style={{display:“flex”,flexDirection:“column”,gap:12}}>
{projets.map((p,i)=>(
<div key={i} style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,padding:“20px 24px”,cursor:“pointer”,transition:“border 0.2s”}}
onClick={()=>onOpen(p)} onMouseEnter={e=>e.currentTarget.style.borderColor=T.accent} onMouseLeave={e=>e.currentTarget.style.borderColor=T.border}>
<div style={{display:“flex”,justifyContent:“space-between”,alignItems:“flex-start”}}>
<div>
<div style={{fontWeight:600,fontSize:14,marginBottom:4}}>{p.description}</div>
<div style={{fontSize:12,color:T.muted}}>{p.date} · {p.commune||“Commune non renseignée”}</div>
</div>
<div style={{display:“flex”,alignItems:“center”,gap:10}}>
<div style={{fontSize:15,fontWeight:700,color:T.accent}}>{p.devis?.totalTTC?.toFixed(0)} €</div>
<button onClick={e=>{e.stopPropagation();onDelete(i);}} style={{background:“none”,border:“none”,color:T.muted,cursor:“pointer”,fontSize:16,padding:“2px 6px”}}>×</button>
</div>
</div>
{p.params&&(
<div style={{display:“flex”,gap:8,marginTop:10,flexWrap:“wrap”}}>
{[`${p.params.w}×${p.params.l}m`,`Pente ${p.params.pente}°`,`Mur ${p.params.h}m`].map(tag=>(
<span key={tag} style={{padding:“3px 10px”,background:T.surface,border:`1px solid ${T.border}`,borderRadius:20,fontSize:11,color:T.muted}}>{tag}</span>
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
const inp={width:“100%”,background:T.surface,border:`1px solid ${T.border}`,borderRadius:8,color:T.text,padding:“10px 14px”,fontSize:13,fontFamily:“inherit”,outline:“none”,boxSizing:“border-box”};
return(
<div style={{flex:1,overflowY:“auto”,padding:40}}>
<div style={{maxWidth:600,margin:“0 auto”}}>
<div style={{fontSize:22,fontWeight:700,letterSpacing:”-0.03em”,marginBottom:6}}>Paramètres</div>
<div style={{color:T.muted,fontSize:13,marginBottom:32}}>Personnalisez DEVIA pour votre entreprise</div>
{[
{section:“Votre entreprise”,fields:[{key:“nomEntreprise”,label:“Nom de l’entreprise”,placeholder:“Charpentes Martin SARL”},{key:“siret”,label:“SIRET”,placeholder:“XXX XXX XXX XXXXX”},{key:“adresse”,label:“Adresse”,placeholder:“12 rue des Artisans, 75001 Paris”},{key:“telephone”,label:“Téléphone”,placeholder:“06 XX XX XX XX”},{key:“email”,label:“Email”,placeholder:“contact@charpentes.fr”}]},
{section:“Tarifs par défaut”,fields:[{key:“tauxHoraire”,label:“Taux horaire main d’œuvre (€/h)”,placeholder:“45”},{key:“tauxTVA”,label:“Taux TVA (%)”,placeholder:“20”},{key:“marge”,label:“Marge bénéficiaire (%)”,placeholder:“15”}]},
{section:“Mentions légales”,fields:[{key:“validite”,label:“Validité du devis (jours)”,placeholder:“30”},{key:“mentionsLegales”,label:“Mentions légales”,placeholder:“Devis valable 30 jours. Acompte de 30% à la commande…”}]},
].map(({section,fields})=>(
<div key={section} style={{marginBottom:28}}>
<div style={{fontSize:11,color:T.accent,textTransform:“uppercase”,letterSpacing:“0.1em”,marginBottom:14}}>{section}</div>
<div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,padding:20,display:“flex”,flexDirection:“column”,gap:12}}>
{fields.map(({key,label,placeholder})=>(
<div key={key}>
<label style={{fontSize:11,color:T.muted,display:“block”,marginBottom:5,textTransform:“uppercase”,letterSpacing:“0.05em”}}>{label}</label>
{key===“mentionsLegales”
?<textarea style={{…inp,minHeight:80,resize:“vertical”}} value={form[key]||””} onChange={e=>setForm(f=>({…f,[key]:e.target.value}))} placeholder={placeholder}/>
:<input style={inp} value={form[key]||””} onChange={e=>setForm(f=>({…f,[key]:e.target.value}))} placeholder={placeholder}/>
}
</div>
))}
</div>
</div>
))}
<button onClick={()=>onSave(form)} style={{width:“100%”,padding:“13px 0”,background:T.accent,border:“none”,borderRadius:10,color:”#0a0800”,fontWeight:700,fontSize:14,cursor:“pointer”}}>
Enregistrer les paramètres
</button>
</div>
</div>
);
}

// ─── PAGE COMPTE ──────────────────────────────────────────────────────────────
function PageCompte(){
return(
<div style={{flex:1,overflowY:“auto”,padding:40}}>
<div style={{maxWidth:600,margin:“0 auto”}}>
<div style={{fontSize:22,fontWeight:700,letterSpacing:”-0.03em”,marginBottom:6}}>Mon compte</div>
<div style={{color:T.muted,fontSize:13,marginBottom:32}}>Informations et abonnement</div>
<div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,padding:24,marginBottom:20}}>
<div style={{fontSize:11,color:T.accent,textTransform:“uppercase”,letterSpacing:“0.1em”,marginBottom:14}}>Abonnement actuel</div>
<div style={{display:“flex”,justifyContent:“space-between”,alignItems:“center”,marginBottom:20}}>
<div><div style={{fontSize:18,fontWeight:700}}>Plan Gratuit</div><div style={{fontSize:13,color:T.muted,marginTop:4}}>Accès à toutes les fonctionnalités de base</div></div>
<div style={{padding:“6px 16px”,background:`${T.ok}18`,border:`1px solid ${T.ok}33`,borderRadius:20,color:T.ok,fontSize:12,fontWeight:600}}>Actif</div>
</div>
{[“Génération de devis illimitée”,“Modélisation 3D interactive”,“Zones Eurocodes intégrées”,“Feuille de calcul technique EC5”,“Historique des projets”].map(f=>(
<div key={f} style={{display:“flex”,gap:10,alignItems:“center”,fontSize:13,color:T.muted,marginBottom:6}}>
<span style={{color:T.ok}}>✓</span>{f}
</div>
))}
</div>
<div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,padding:24}}>
<div style={{fontSize:11,color:T.accent,textTransform:“uppercase”,letterSpacing:“0.1em”,marginBottom:14}}>Statistiques</div>
<div style={{display:“flex”,gap:12}}>
{[[“Devis générés”,”—”],[“Ce mois”,”—”],[“Valeur totale”,”—”]].map(([l,v])=>(
<div key={l} style={{flex:1,padding:“14px 16px”,background:T.surface,borderRadius:10,border:`1px solid ${T.border}`,textAlign:“center”}}>
<div style={{fontSize:22,fontWeight:700,color:T.accent,marginBottom:4}}>{v}</div>
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
const [page,setPage]=useState(“home”);
const [prompt,setPrompt]=useState(””);
const [files,setFiles]=useState([]);
const [state,setState]=useState(“idle”);
const [result,setResult]=useState(null);
const [tab,setTab]=useState(“devis”);
const [errMsg,setErrMsg]=useState(””);
const [commune,setCommune]=useState(””);
const [altitude,setAltitude]=useState(“100”);
const [zones,setZones]=useState(null);
const [missingQ,setMissingQ]=useState([]);
const [answers,setAnswers]=useState({});
const [projets,setProjets]=useState([]);
const [settings,setSettings]=useState({nomEntreprise:””,siret:””,adresse:””,telephone:””,email:””,tauxHoraire:“45”,tauxTVA:“20”,marge:“15”,validite:“30”,mentionsLegales:””});
const [savedMsg,setSavedMsg]=useState(false);
const fileRef=useRef(null),textRef=useRef(null);

useEffect(()=>{if(textRef.current){textRef.current.style.height=“auto”;textRef.current.style.height=textRef.current.scrollHeight+“px”;}},[ prompt]);
useEffect(()=>{if(commune.trim().length>2)setZones(getZones(commune,altitude));else setZones(null);},[commune,altitude]);

const addFiles=list=>{const arr=Array.from(list).filter(f=>f.type.startsWith(“image/”)||f.type===“application/pdf”);setFiles(prev=>[…prev,…arr].slice(0,5));};
const onDrop=e=>{e.preventDefault();addFiles(e.dataTransfer.files);};
const toBase64=file=>new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.result.split(”,”)[1]);r.onerror=rej;r.readAsDataURL(file);});

const checkAndGenerate=()=>{
if(!prompt.trim())return;
const missing=getMissingQuestions(prompt);
if(missing.length>0){setMissingQ(missing);setState(“questions”);return;}
doGenerate({});
};

const doGenerate=async(extraAnswers)=>{
setState(“loading”);setErrMsg(””);
const allAnswers={…answers,…extraAnswers};
try{
const content=[];
for(const f of files){if(f.type.startsWith(“image/”)){const data=await toBase64(f);content.push({type:“image”,source:{type:“base64”,media_type:f.type,data}});}}
const zonesInfo=zones?`DONNÉES GÉOGRAPHIQUES (Eurocodes) : Commune ${commune}, Altitude ${zones.altitude}m, Zone neige ${zones.neige} sk=${zones.sk}kN/m², Zone vent ${zones.vent} qb=${zones.qb}Pa, Zone sismique ${zones.sismique} ag=${zones.ag}%g`:`Valeurs moyennes françaises.`;
const answersText=Object.entries(allAnswers).map(([k,v])=>`- ${k}: ${v}`).join(”\n”);
content.push({type:“text”,text:`Tu es un bureau d'études charpente bois expert Eurocodes. Description : ${prompt} ${answersText?`Précisions :\n${answersText}`:””}
${zonesInfo}

Réponds UNIQUEMENT en JSON valide :
{
“description”: “résumé court”,
“params”: { “w”: 8, “l”: 12, “h”: 3, “pente”: 35 },
“devis”: {
“lignes”: [{ “designation”: “…”, “quantite”: 12.5, “unite”: “ml”, “prixUnitaire”: 8.50, “total”: 106.25 }],
“sousTotal”: 0, “tva”: 0, “totalTTC”: 0, “notes”: “…”
},
“calcul”: {
“charges”: [{ “label”: “Charge permanente”, “valeur”: “0.45”, “unite”: “kN/m²” }],
“elements”: [{ “element”: “Chevron 60×180mm”, “section”: “60×180 mm”, “contrainte”: “8.2”, “resistance”: “14.0”, “coefficient”: “0.59” }],
“assemblages”: [{ “type”: “Sabot chevron/panne”, “specification”: “Simpson LBV 60×180” }],
“conclusion”: “Structure vérifiée sous toutes les combinaisons réglementaires.”
}
}
Prix marché français 2024. Sections dimensionnées selon charges réelles.`});

```
  const res=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({messages:[{role:"user",content}]})});
  const data=await res.json();
  const raw=data.content?.map(b=>b.text||"").join("").trim();
  const clean=raw.replace(/```json|```/g,"").trim();
  const parsed=JSON.parse(clean);
  const projet={...parsed,zones,commune,date:new Date().toLocaleDateString("fr-FR",{day:"numeric",month:"long",year:"numeric"}),id:Date.now()};
  setResult(projet);
  setProjets(prev=>[projet,...prev].slice(0,50));
  setState("done");setTab("devis");
}catch(e){
  console.error(e);
  setErrMsg("Une erreur est survenue. Vérifiez que le proxy API est bien configuré sur Vercel.");
  setState("error");
}
```

};

const reset=()=>{setState(“idle”);setResult(null);setPrompt(””);setFiles([]);setCommune(””);setAltitude(“100”);setZones(null);setMissingQ([]);setAnswers({});};

const navBtn=(id,label)=>(
<button key={id} onClick={()=>setPage(id)} style={{padding:“7px 16px”,background:page===id?T.accentLo:“none”,border:`1px solid ${page===id?T.accent:T.border}`,borderRadius:20,color:page===id?T.accent:T.muted,fontSize:12,cursor:“pointer”,transition:“all 0.2s”}}>
{label}
</button>
);

return(
<div style={{minHeight:“100vh”,background:T.bg,color:T.text,fontFamily:”‘Inter’,system-ui,sans-serif”,display:“flex”,flexDirection:“column”}}>

```
  {/* HEADER */}
  <header style={{display:"flex",alignItems:"center",justifyContent:"space-between",padding:"18px 32px",borderBottom:`1px solid ${T.border}`,background:T.surface,position:"sticky",top:0,zIndex:100}}>
    <div style={{display:"flex",alignItems:"center",gap:12,cursor:"pointer"}} onClick={()=>{setPage("home");reset();}}>
      <div style={{width:36,height:36,background:T.accent,borderRadius:10,display:"flex",alignItems:"center",justifyContent:"center",fontSize:18,fontWeight:900,color:"#0a0800"}}>D</div>
      <div>
        <div style={{fontWeight:700,fontSize:17,letterSpacing:"-0.03em",color:T.text}}>DEVIA</div>
        <div style={{fontSize:10,color:T.muted,letterSpacing:"0.08em",textTransform:"uppercase",marginTop:-1}}>Estimation & Modélisation · Charpente</div>
      </div>
    </div>
    <div style={{display:"flex",gap:8}}>
      {navBtn("projets","Mes projets")}
      {navBtn("parametres","Paramètres")}
      {navBtn("compte","Mon compte")}
    </div>
  </header>

  {/* PAGES */}
  {page==="projets"&&<PageProjets projets={projets} onOpen={p=>{setResult(p);setState("done");setPage("home");}} onDelete={i=>setProjets(prev=>prev.filter((_,j)=>j!==i))}/>}
  {page==="parametres"&&<PageParametres settings={settings} onSave={s=>{setSettings(s);setSavedMsg(true);setTimeout(()=>setSavedMsg(false),2500);}}/>}
  {page==="compte"&&<PageCompte/>}
  {savedMsg&&<div style={{position:"fixed",bottom:24,right:24,padding:"12px 20px",background:T.ok,color:"#0a1a0a",borderRadius:10,fontWeight:600,fontSize:13,zIndex:999}}>Paramètres enregistrés ✓</div>}

  {/* HOME */}
  {page==="home"&&(
    <>
      <div style={{flex:state==="done"?0:1,padding:"60px 32px 40px",display:"flex",flexDirection:"column",alignItems:"center",transition:"all 0.4s",background:state==="done"?"none":`radial-gradient(ellipse 80% 60% at 50% 0%, ${T.accentLo}, transparent)`}}>
        {state==="idle"&&(
          <>
            <div style={{fontSize:52,fontWeight:700,letterSpacing:"-0.04em",textAlign:"center",lineHeight:1.08,marginBottom:16,color:T.text}}>
              Estimez votre charpente<br/><span style={{color:T.accent}}>en quelques secondes.</span>
            </div>
            <div style={{color:T.muted,fontSize:16,textAlign:"center",marginBottom:40,letterSpacing:"-0.01em"}}>
              Décrivez votre projet — DEVIA génère un devis détaillé, une modélisation 3D et une feuille de calcul technique.
            </div>
          </>
        )}

        <div style={{width:"100%",maxWidth:760,background:T.card,border:`1.5px solid ${state==="error"?"#e05555":T.border}`,borderRadius:20,overflow:"hidden",boxShadow:`0 0 60px ${T.accentLo}`}}>
          <textarea ref={textRef} value={prompt} onChange={e=>setPrompt(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"&&(e.metaKey||e.ctrlKey))checkAndGenerate();}}
            placeholder="Décrivez votre projet : type de charpente, dimensions approximatives, essence de bois souhaitée, contraintes particulières…"
            style={{width:"100%",minHeight:80,maxHeight:220,background:"none",border:"none",outline:"none",color:T.text,fontSize:15,padding:"20px 22px 10px",resize:"none",fontFamily:"inherit",lineHeight:1.7,boxSizing:"border-box"}}/>
          <div style={{display:"flex",gap:10,padding:"0 16px 12px",borderBottom:`1px solid ${T.border}`}}>
            <div style={{flex:2,position:"relative"}}>
              <input value={commune} onChange={e=>setCommune(e.target.value)} placeholder="Commune (ex : Grenoble, Bruxelles…)" style={{width:"100%",background:T.surface,border:`1px solid ${zones?"#3ecf8e44":T.border}`,borderRadius:10,color:T.text,padding:"9px 14px",fontSize:13,fontFamily:"inherit",outline:"none",boxSizing:"border-box"}}/>
              {zones&&<div style={{position:"absolute",right:10,top:"50%",transform:"translateY(-50%)",width:8,height:8,borderRadius:"50%",background:T.ok}}/>}
            </div>
            <input value={altitude} onChange={e=>setAltitude(e.target.value)} placeholder="Altitude (m)" type="number" style={{flex:1,background:T.surface,border:`1px solid ${T.border}`,borderRadius:10,color:T.text,padding:"9px 14px",fontSize:13,fontFamily:"inherit",outline:"none",boxSizing:"border-box"}}/>
          </div>
          {zones&&(
            <div style={{display:"flex",gap:8,padding:"10px 16px",flexWrap:"wrap",borderBottom:`1px solid ${T.border}`}}>
              {[["Neige",`Zone ${zones.neige} — ${zones.sk} kN/m²`,"#60a5fa"],["Vent",`Zone ${zones.vent} — ${zones.qb} Pa`,"#a78bfa"],["Sismique",`Zone ${zones.sismique} — ${zones.ag}%g`,"#f97316"],["Altitude",`${zones.altitude} m`,"#3ecf8e"]].map(([l,v,c])=>(
                <div key={l} style={{padding:"4px 12px",background:`${c}14`,border:`1px solid ${c}33`,borderRadius:20,fontSize:11,display:"flex",gap:6}}>
                  <span style={{color:c,fontWeight:600}}>{l}</span><span style={{color:T.muted}}>{v}</span>
                </div>
              ))}
            </div>
          )}
          {files.length>0&&<div style={{display:"flex",flexWrap:"wrap",gap:8,padding:"0 16px 12px"}}>{files.map((f,i)=><FilePill key={i} file={f} onRemove={()=>setFiles(fs=>fs.filter((_,j)=>j!==i))}/>)}</div>}
          <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",padding:"10px 16px",borderTop:`1px solid ${T.border}`}}>
            <div style={{display:"flex",gap:8}}>
              <button onClick={()=>fileRef.current?.click()} style={{padding:"7px 14px",background:T.surface,border:`1px solid ${T.border}`,borderRadius:20,color:T.muted,fontSize:12,cursor:"pointer"}}>Joindre un fichier</button>
              <input ref={fileRef} type="file" multiple accept="image/*,application/pdf" style={{display:"none"}} onChange={e=>addFiles(e.target.files)}/>
            </div>
            <div style={{display:"flex",alignItems:"center",gap:12}}>
              <span style={{fontSize:11,color:T.muted}}>Ctrl + Entrée</span>
              <button onClick={checkAndGenerate} disabled={state==="loading"||!prompt.trim()}
                style={{padding:"9px 22px",background:state==="loading"||!prompt.trim()?T.dim:T.accent,border:"none",borderRadius:20,color:state==="loading"||!prompt.trim()?T.muted:"#0a0800",fontWeight:700,fontSize:13,cursor:state==="loading"||!prompt.trim()?"not-allowed":"pointer",transition:"all 0.2s"}}>
                {state==="loading"?"Analyse en cours…":"Générer le devis"}
              </button>
            </div>
          </div>
        </div>
        {errMsg&&<div style={{marginTop:12,color:"#e05555",fontSize:12,textAlign:"center",maxWidth:600}}>{errMsg}</div>}
        {state==="idle"&&<div onDrop={onDrop} onDragOver={e=>e.preventDefault()} style={{marginTop:16,padding:"12px 24px",border:`1px dashed ${T.dim}`,borderRadius:12,color:T.muted,fontSize:12,textAlign:"center"}}>Glissez vos photos, plans ou documents ici</div>}
      </div>

      {/* QUESTIONS */}
      {state==="questions"&&(
        <div style={{flex:1,display:"flex",alignItems:"center",justifyContent:"center",padding:40}}>
          <div style={{maxWidth:560,width:"100%",background:T.card,border:`1px solid ${T.border}`,borderRadius:20,padding:32}}>
            <div style={{fontSize:16,fontWeight:700,marginBottom:6}}>Quelques précisions</div>
            <div style={{color:T.muted,fontSize:13,marginBottom:24}}>Pour générer un devis précis, DEVIA a besoin de ces informations :</div>
            {missingQ.map(q=>(
              <div key={q.id} style={{marginBottom:20}}>
                <div style={{fontSize:12,color:T.accent,textTransform:"uppercase",letterSpacing:"0.08em",marginBottom:10}}>{q.label}</div>
                <div style={{display:"flex",flexWrap:"wrap",gap:8}}>
                  {q.options.map(opt=>(
                    <button key={opt} onClick={()=>setAnswers(a=>({...a,[q.label]:opt}))}
                      style={{padding:"8px 16px",background:answers[q.label]===opt?T.accent:T.surface,border:`1px solid ${answers[q.label]===opt?T.accent:T.border}`,borderRadius:20,color:answers[q.label]===opt?"#0a0800":T.text,fontSize:12,cursor:"pointer",transition:"all 0.15s"}}>
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            ))}
            <div style={{display:"flex",gap:10,marginTop:8}}>
              <button onClick={()=>setState("idle")} style={{flex:1,padding:"11px 0",background:"none",border:`1px solid ${T.border}`,borderRadius:10,color:T.muted,fontSize:13,cursor:"pointer"}}>Retour</button>
              <button onClick={()=>doGenerate(answers)} style={{flex:2,padding:"11px 0",background:T.accent,border:"none",borderRadius:10,color:"#0a0800",fontWeight:700,fontSize:13,cursor:"pointer"}}>Générer le devis</button>
            </div>
          </div>
        </div>
      )}

      {/* RÉSULTATS */}
      {state==="done"&&result&&(
        <div style={{flex:1,display:"flex",flexDirection:"column",overflow:"hidden"}}>
          <div style={{display:"flex",alignItems:"center",borderBottom:`1px solid ${T.border}`,background:T.surface,padding:"0 32px"}}>
            {[["devis","Devis estimatif"],["3d","Modélisation 3D"],["calcul","Feuille de calcul"]].map(([id,label])=>(
              <button key={id} onClick={()=>setTab(id)} style={{padding:"14px 22px",background:"none",border:"none",borderBottom:tab===id?`2px solid ${T.accent}`:"2px solid transparent",color:tab===id?T.accent:T.muted,fontSize:13,fontWeight:600,cursor:"pointer",transition:"color 0.2s"}}>{label}</button>
            ))}
            <div style={{marginLeft:"auto",fontSize:12,color:T.muted}}>{result.description}</div>
            <button onClick={reset} style={{marginLeft:16,padding:"6px 16px",background:"none",border:`1px solid ${T.border}`,borderRadius:20,color:T.muted,fontSize:12,cursor:"pointer"}}>Nouveau projet</button>
          </div>
          <div style={{flex:1,overflow:"hidden",display:"flex"}}>
            {tab==="devis"&&(
              <div style={{flex:1,overflowY:"auto",padding:"40px 0"}}>
                <div style={{maxWidth:700,margin:"0 auto",padding:"0 32px"}}>
                  <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:32}}>
                    <div>
                      <div style={{fontSize:26,fontWeight:800,letterSpacing:"-0.04em"}}>DEVIS</div>
                      <div style={{color:T.muted,fontSize:13,marginTop:2}}>N° {new Date().getFullYear()}-{String(Math.floor(Math.random()*900)+100)} · {result.date}</div>
                    </div>
                    <div style={{padding:"8px 16px",background:T.accentLo,borderRadius:20,border:`1px solid ${T.accent}33`}}>
                      <span style={{color:T.accent,fontSize:12,fontWeight:600}}>Devis généré par DEVIA</span>
                    </div>
                  </div>
                  {settings.nomEntreprise&&(
                    <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,padding:20,marginBottom:20}}>
                      <div style={{fontSize:11,color:T.accent,textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:8}}>Votre entreprise</div>
                      <div style={{fontWeight:600}}>{settings.nomEntreprise}</div>
                      {settings.adresse&&<div style={{color:T.muted,fontSize:13}}>{settings.adresse}</div>}
                      {settings.telephone&&<div style={{color:T.muted,fontSize:13}}>{settings.telephone} · {settings.email}</div>}
                    </div>
                  )}
                  <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,padding:24,marginBottom:20}}>
                    <div style={{fontSize:11,color:T.accent,textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:6}}>Description du projet</div>
                    <div style={{color:T.text,fontSize:14,lineHeight:1.6}}>{result.description}</div>
                    {result.params&&(
                      <div style={{display:"flex",gap:10,marginTop:12,flexWrap:"wrap"}}>
                        {[["Largeur",`${result.params.w}m`],["Longueur",`${result.params.l}m`],["Hauteur mur",`${result.params.h}m`],["Pente",`${result.params.pente}°`]].map(([k,v])=>(
                          <div key={k} style={{padding:"6px 14px",background:T.surface,border:`1px solid ${T.border}`,borderRadius:8,fontSize:12}}>
                            <span style={{color:T.muted}}>{k} : </span><span style={{color:T.text,fontWeight:600}}>{v}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  {result.zones&&(
                    <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,padding:20,marginBottom:20}}>
                      <div style={{fontSize:11,color:T.accent,textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:12}}>Données géographiques — Eurocodes</div>
                      <div style={{display:"flex",gap:10,flexWrap:"wrap"}}>
                        {[["Neige EN 1991-1-3",`Zone ${result.zones.neige}`,`sk = ${result.zones.sk} kN/m²`,"#60a5fa"],["Vent EN 1991-1-4",`Zone ${result.zones.vent}`,`qb = ${result.zones.qb} Pa`,"#a78bfa"],["Sismique EN 1998-1",`Zone ${result.zones.sismique}`,`ag = ${result.zones.ag}%g`,"#f97316"],["Altitude",`${result.zones.altitude} m`,"Neige ajustée","#3ecf8e"]].map(([label,z,val,color])=>(
                          <div key={label} style={{flex:"1 1 140px",padding:"12px 16px",background:`${color}0d`,border:`1px solid ${color}22`,borderRadius:12}}>
                            <div style={{fontSize:10,color:T.muted,marginBottom:4,textTransform:"uppercase",letterSpacing:"0.06em"}}>{label}</div>
                            <div style={{color,fontWeight:700,fontSize:15,marginBottom:2}}>{z}</div>
                            <div style={{color:T.muted,fontSize:11}}>{val}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,padding:24}}>
                    <DevisTable devis={result.devis}/>
                  </div>
                  {settings.mentionsLegales&&<div style={{marginTop:16,padding:"12px 16px",background:T.surface,border:`1px solid ${T.border}`,borderRadius:10,fontSize:11,color:T.muted,lineHeight:1.7}}>{settings.mentionsLegales}</div>}
                  <div style={{marginTop:20,display:"flex",gap:10,justifyContent:"flex-end"}}>
                    <button onClick={()=>window.print()} style={{padding:"10px 20px",background:"none",border:`1px solid ${T.border}`,borderRadius:10,color:T.muted,fontSize:12,cursor:"pointer"}}>Imprimer / Exporter PDF</button>
                    <button style={{padding:"10px 20px",background:T.accent,border:"none",borderRadius:10,color:"#0a0800",fontSize:12,fontWeight:700,cursor:"pointer"}}>Transmettre au client</button>
                  </div>
                </div>
              </div>
            )}
            {tab==="3d"&&<div style={{flex:1,position:"relative"}}><Viewer3D params={result.params||{}} active={tab==="3d"}/></div>}
            {tab==="calcul"&&(
              <div style={{flex:1,overflowY:"auto",padding:"40px 0"}}>
                <div style={{maxWidth:700,margin:"0 auto",padding:"0 32px"}}>
                  <div style={{fontSize:22,fontWeight:700,letterSpacing:"-0.03em",marginBottom:6}}>Feuille de calcul technique</div>
                  <div style={{color:T.muted,fontSize:13,marginBottom:24}}>Justification des sections — Conforme Eurocode 5 (NF EN 1995-1-1)</div>
                  <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:14,padding:24}}>
                    <FeuilleCalcTable calc={result.calcul}/>
                  </div>
                  <div style={{marginTop:16,display:"flex",justifyContent:"flex-end"}}>
                    <button onClick={()=>window.print()} style={{padding:"10px 20px",background:"none",border:`1px solid ${T.border}`,borderRadius:10,color:T.muted,fontSize:12,cursor:"pointer"}}>Exporter en PDF</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {state==="loading"&&(
        <div style={{flex:1,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",gap:20,padding:40}}>
          <div style={{width:56,height:56,border:`3px solid ${T.border}`,borderTop:`3px solid ${T.accent}`,borderRadius:"50%",animation:"spin 0.8s linear infinite"}}/>
          <div style={{color:T.muted,fontSize:14}}>Analyse du projet en cours, veuillez patienter…</div>
        </div>
      )}
    </>
  )}

  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    *{box-sizing:border-box;margin:0;padding:0;}
    body{background:${T.bg};}
    @keyframes spin{to{transform:rotate(360deg)}}
    ::-webkit-scrollbar{width:5px;}
    ::-webkit-scrollbar-track{background:${T.surface};}
    ::-webkit-scrollbar-thumb{background:${T.dim};border-radius:3px;}
    textarea::placeholder,input::placeholder{color:${T.muted};}
  `}</style>
</div>
```

);
}
