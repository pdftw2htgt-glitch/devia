import { useState, useRef, useEffect, useCallback } from “react”;
import * as THREE from “three”;

// ─── THEME ──────────────────────────────────────────────────────────────────
const T = {
bg:       “#08090c”,
surface:  “#0f1117”,
card:     “#13161f”,
border:   “#1e2231”,
accent:   “#f0c040”,
accentLo: “#f0c04018”,
text:     “#e8eaf2”,
muted:    “#545870”,
dim:      “#2a2e40”,
wood:     “#c4894a”,
woodDk:   “#8b5e2e”,
ok:       “#3ecf8e”,
};

// ─── 3D VIEWER ──────────────────────────────────────────────────────────────
function Viewer3D({ params, active }) {
const mountRef = useRef(null);
const rendRef  = useRef(null);
const frameRef = useRef(null);
const rotRef   = useRef({ theta: 0.7, phi: 0.45, r: 16 });
const dragRef  = useRef({ down: false, lx: 0, ly: 0 });

const build = useCallback(() => {
const scene = new THREE.Scene();
scene.background = new THREE.Color(T.bg);
scene.fog = new THREE.FogExp2(T.bg, 0.04);
scene.add(new THREE.GridHelper(40, 40, “#141824”, “#111420”));

```
const { w = 8, l = 12, h = 3, pente = 35, type = "2pans" } = params;
const rise = (w / 2) * Math.tan((pente * Math.PI) / 180);

const mat  = (c) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.82, metalness: 0.04 });
const box  = (W, H, D, m) => new THREE.Mesh(new THREE.BoxGeometry(W, H, D), mat(m));
const add  = (m) => scene.add(m);

// Walls ghost
const wm = new THREE.MeshStandardMaterial({ color:"#1a2040", transparent:true, opacity:0.28, roughness:1 });
[[w,h,0.08,0,h/2,-l/2],[w,h,0.08,0,h/2,l/2],[0.08,h,l,-w/2,h/2,0],[0.08,h,l,w/2,h/2,0]]
  .forEach(([W,H,D,x,y,z]) => { const m=new THREE.Mesh(new THREE.BoxGeometry(W,H,D),wm); m.position.set(x,y,z); add(m); });

// Sablières
[-w/2+0.08, w/2-0.08].forEach(x => { const m=box(0.14,0.14,l,T.wood); m.position.set(x,h,0); add(m); });

// Faîtage
const fg = box(0.14,0.14,l,T.woodDk); fg.position.set(0,h+rise,0); add(fg);

// Chevrons
const rLen = Math.sqrt((w/2)**2 + rise**2) + 0.4;
const rAng = Math.atan2(rise, w/2);
const nR   = Math.ceil(l/0.55)+1;
for(let i=0;i<=nR;i++){
  const z=-l/2+(i/nR)*l;
  [-1,1].forEach(s=>{
    const r=box(0.07,0.11,rLen,T.wood);
    r.rotation.z=s*rAng; r.position.set(s*(w/4-0.1),h+rise/2,z); add(r);
  });
}

// Pannes
[0.25,0.5,0.75].forEach(t=>{
  const px=(w/2)*(1-t), py=h+rise*t;
  [-1,1].forEach(s=>{ const p=box(0.12,0.12,l,T.woodDk); p.position.set(s*px,py,0); add(p); });
});

// Entraits
for(let i=0;i<=nR;i+=3){
  const z=-l/2+(i/nR)*l;
  const e=box(w-0.2,0.14,0.1,T.woodDk); e.position.set(0,h+0.08,z); add(e);
}

// Couverture transparente
const rm=new THREE.MeshStandardMaterial({color:"#1c2850",transparent:true,opacity:0.22,side:THREE.DoubleSide});
[-1,1].forEach(s=>{
  const rf=new THREE.Mesh(new THREE.PlaneGeometry(rLen+0.2,l),rm);
  rf.rotation.z=-s*rAng; rf.position.set(s*(w/4-0.1),h+rise/2,0); add(rf);
});

// Lights
scene.add(new THREE.AmbientLight("#b0c8e0",0.65));
const sun=new THREE.DirectionalLight("#fff4d0",1.5); sun.position.set(12,20,8); add(sun);
const fill=new THREE.DirectionalLight("#8090ff",0.35); fill.position.set(-8,3,-6); add(fill);

return scene;
```

}, [params]);

useEffect(() => {
if (!mountRef.current || !active) return;
const W=mountRef.current.clientWidth, H=mountRef.current.clientHeight;
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(W,H); renderer.setPixelRatio(window.devicePixelRatio);
mountRef.current.appendChild(renderer.domElement);
rendRef.current=renderer;
const camera=new THREE.PerspectiveCamera(44,W/H,0.1,200);
const scene=build();

```
const tick=()=>{
  frameRef.current=requestAnimationFrame(tick);
  const {theta,phi,r}=rotRef.current;
  camera.position.set(r*Math.sin(theta)*Math.cos(phi),r*Math.sin(phi),r*Math.cos(theta)*Math.cos(phi));
  camera.lookAt(0,2,0);
  renderer.render(scene,camera);
};
tick();

const onDown=e=>{dragRef.current={down:true,lx:e.clientX,ly:e.clientY};};
const onUp=()=>{dragRef.current.down=false;};
const onMove=e=>{
  if(!dragRef.current.down)return;
  rotRef.current.theta-=(e.clientX-dragRef.current.lx)*0.01;
  rotRef.current.phi=Math.max(0.1,Math.min(1.4,rotRef.current.phi+(e.clientY-dragRef.current.ly)*0.01));
  dragRef.current={down:true,lx:e.clientX,ly:e.clientY};
};
const onWheel=e=>{rotRef.current.r=Math.max(5,Math.min(35,rotRef.current.r+e.deltaY*0.02));};
const onResize=()=>{
  if(!mountRef.current)return;
  const W=mountRef.current.clientWidth,H=mountRef.current.clientHeight;
  camera.aspect=W/H; camera.updateProjectionMatrix(); renderer.setSize(W,H);
};
renderer.domElement.addEventListener("mousedown",onDown);
window.addEventListener("mouseup",onUp);
window.addEventListener("mousemove",onMove);
renderer.domElement.addEventListener("wheel",onWheel,{passive:true});
window.addEventListener("resize",onResize);

return()=>{
  cancelAnimationFrame(frameRef.current);
  renderer.domElement.removeEventListener("mousedown",onDown);
  window.removeEventListener("mouseup",onUp);
  window.removeEventListener("mousemove",onMove);
  renderer.domElement.removeEventListener("wheel",onWheel);
  window.removeEventListener("resize",onResize);
  renderer.dispose();
  if(mountRef.current&&renderer.domElement.parentNode===mountRef.current)
    mountRef.current.removeChild(renderer.domElement);
};
```

}, [build, active]);

return (
<div style={{position:“relative”,width:“100%”,height:“100%”}}>
<div ref={mountRef} style={{width:“100%”,height:“100%”}}/>
<div style={{position:“absolute”,bottom:14,left:14,fontSize:11,color:T.muted,fontFamily:“monospace”,background:`${T.bg}cc`,padding:“4px 10px”,borderRadius:20}}>
↔ glisser · ↕ zoom
</div>
</div>
);
}

// ─── DEVIS TABLE ─────────────────────────────────────────────────────────────
function DevisTable({ devis }) {
if (!devis?.lignes) return null;
return (
<div style={{fontFamily:”‘JetBrains Mono’,monospace”,fontSize:12}}>
<div style={{display:“flex”,color:T.muted,borderBottom:`1px solid ${T.border}`,paddingBottom:8,marginBottom:4,fontSize:11,letterSpacing:“0.06em”}}>
<span style={{flex:3}}>DÉSIGNATION</span>
<span style={{flex:1,textAlign:“right”}}>QTÉ</span>
<span style={{flex:“0 0 40px”,textAlign:“right”}}>U.</span>
<span style={{flex:1,textAlign:“right”}}>P.U.</span>
<span style={{flex:1,textAlign:“right”}}>TOTAL</span>
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
{devis.notes&&(
<div style={{marginTop:14,padding:“10px 14px”,background:T.accentLo,borderLeft:`3px solid ${T.accent}55`,borderRadius:4,color:T.muted,fontSize:11,lineHeight:1.7}}>
💡 {devis.notes}
</div>
)}
</div>
);
}

// ─── FILE PILL ────────────────────────────────────────────────────────────────
function FilePill({ file, onRemove }) {
const isImg = file.type.startsWith(“image/”);
return (
<div style={{display:“flex”,alignItems:“center”,gap:8,padding:“6px 12px”,background:T.card,border:`1px solid ${T.border}`,borderRadius:20,fontSize:12,color:T.text}}>
<span>{isImg?“🖼”:“📄”}</span>
<span style={{maxWidth:120,overflow:“hidden”,textOverflow:“ellipsis”,whiteSpace:“nowrap”}}>{file.name}</span>
<button onClick={onRemove} style={{background:“none”,border:“none”,color:T.muted,cursor:“pointer”,fontSize:14,lineHeight:1,padding:0}}>×</button>
</div>
);
}

// ─── MAIN ────────────────────────────────────────────────────────────────────
export default function Devia() {
const [prompt, setPrompt]     = useState(””);
const [files, setFiles]       = useState([]);
const [state, setState]       = useState(“idle”); // idle | loading | done | error
const [result, setResult]     = useState(null);   // { devis, params, description }
const [tab, setTab]           = useState(“devis”);
const [errMsg, setErrMsg]     = useState(””);
const fileRef = useRef(null);
const textRef = useRef(null);

// auto-grow textarea
useEffect(()=>{
if(textRef.current){ textRef.current.style.height=“auto”; textRef.current.style.height=textRef.current.scrollHeight+“px”; }
},[prompt]);

const addFiles = (list) => {
const arr = Array.from(list).filter(f=>
f.type.startsWith(“image/”)||f.type===“application/pdf”||f.type.includes(“text”)
);
setFiles(prev=>[…prev,…arr].slice(0,5));
};

const onDrop = (e) => { e.preventDefault(); addFiles(e.dataTransfer.files); };

const toBase64 = (file) => new Promise((res,rej)=>{
const r=new FileReader();
r.onload=()=>res(r.result.split(”,”)[1]);
r.onerror=rej;
r.readAsDataURL(file);
});

const generate = async () => {
if (!prompt.trim()) return;
setState(“loading”); setErrMsg(””);

```
try {
  // Build message content
  const content = [];

  // Attach images
  for (const f of files) {
    if (f.type.startsWith("image/")) {
      const data = await toBase64(f);
      content.push({ type:"image", source:{ type:"base64", media_type:f.type, data } });
    }
  }

  content.push({ type:"text", text:`Tu es un expert charpentier et estimateur de travaux bois. 
```

À partir de la description suivante${files.length?” et des images/documents joints”:””}, génère :

1. Un devis professionnel détaillé
1. Les paramètres 3D de la structure

Description du projet : ${prompt}

Réponds UNIQUEMENT en JSON valide (aucun texte avant ou après, aucun markdown) avec cette structure exacte :
{
“description”: “résumé court du projet”,
“params”: { “w”: 8, “l”: 12, “h”: 3, “pente”: 35 },
“devis”: {
“lignes”: [
{ “designation”: “…”, “quantite”: 12.5, “unite”: “ml”, “prixUnitaire”: 8.50, “total”: 106.25 }
],
“sousTotal”: 0,
“tva”: 0,
“totalTTC”: 0,
“notes”: “…”
}
}

Règles :

- params.w = largeur en mètres, params.l = longueur, params.h = hauteur mur, params.pente = angle en degrés
- Inclure : bois de charpente (chevrons, pannes, faîtage, sablières, entraits, contrefiches), connecteurs, main d’œuvre, levage
- Prix marché français 2024 réalistes
- Calculer sousTotal = somme des totaux, tva = sousTotal * 0.20, totalTTC = sousTotal + tva` });
  
  ```
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      model:"claude-sonnet-4-20250514",
      max_tokens:1500,
      messages:[{ role:"user", content }]
    })
  });
  
  const data = await res.json();
  const raw  = data.content?.map(b=>b.text||"").join("").trim();
  const clean = raw.replace(/```json|```/g,"").trim();
  const parsed = JSON.parse(clean);
  
  setResult(parsed);
  setState("done");
  setTab("devis");
  ```
  
  } catch(e) {
  console.error(e);
  setErrMsg(“Erreur de génération. Si le problème persiste, un backend proxy est nécessaire (CORS).”);
  setState(“error”);
  }
  };
  
  const onKey = (e) => { if(e.key===“Enter”&&(e.metaKey||e.ctrlKey)) generate(); };
  
  // ── RENDER ────────────────────────────────────────────────────────────────
  return (
  
    <div style={{minHeight:"100vh",background:T.bg,color:T.text,fontFamily:"'Syne','DM Sans',system-ui,sans-serif",display:"flex",flexDirection:"column"}}>
  
  ```
  {/* ── TOP BAR ── */}
  <header style={{display:"flex",alignItems:"center",justifyContent:"space-between",padding:"18px 32px",borderBottom:`1px solid ${T.border}`,background:T.surface,position:"sticky",top:0,zIndex:100}}>
    <div style={{display:"flex",alignItems:"center",gap:12}}>
      <div style={{width:36,height:36,background:T.accent,borderRadius:10,display:"flex",alignItems:"center",justifyContent:"center",fontSize:18,fontWeight:900,color:"#0a0800",letterSpacing:"-0.05em"}}>D</div>
      <div>
        <div style={{fontWeight:800,fontSize:18,letterSpacing:"-0.04em",color:T.text}}>DEVIA</div>
        <div style={{fontSize:10,color:T.muted,letterSpacing:"0.12em",textTransform:"uppercase",marginTop:-2}}>Devis IA · Charpente</div>
      </div>
    </div>
    <div style={{display:"flex",gap:8}}>
      {["Projets","Tarifs","Compte"].map(l=>(
        <button key={l} style={{padding:"7px 16px",background:"none",border:`1px solid ${T.border}`,borderRadius:20,color:T.muted,fontSize:12,cursor:"pointer",letterSpacing:"0.02em"}}>{l}</button>
      ))}
    </div>
  </header>
  
  {/* ── HERO / INPUT ── */}
  <div style={{flex:state==="done"?0:1,padding:"60px 32px 40px",display:"flex",flexDirection:"column",alignItems:"center",transition:"all 0.4s",background:state==="done"?"none":`radial-gradient(ellipse 80% 60% at 50% 0%, ${T.accentLo}, transparent)`}}>
    {state!=="done"&&(
      <>
        <div style={{fontSize:48,fontWeight:800,letterSpacing:"-0.05em",textAlign:"center",lineHeight:1.1,marginBottom:12,background:`linear-gradient(135deg, ${T.text} 40%, ${T.accent})`,WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent"}}>
          Décrivez votre charpente.<br/>DEVIA fait le reste.
        </div>
        <div style={{color:T.muted,fontSize:15,textAlign:"center",marginBottom:40}}>
          Devis professionnel + rendu 3D générés par IA en quelques secondes
        </div>
      </>
    )}
  
    {/* Input box */}
    <div style={{width:"100%",maxWidth:760,background:T.card,border:`1.5px solid ${state==="error"?"#e05555":T.border}`,borderRadius:20,overflow:"hidden",boxShadow:`0 0 60px ${T.accentLo}`}}>
      <textarea
        ref={textRef}
        value={prompt}
        onChange={e=>setPrompt(e.target.value)}
        onKeyDown={onKey}
        placeholder="Ex : Charpente traditionnelle 2 pans pour une maison de 10×14m, pente 35°, bois douglas, avec isolation entre chevrons…"
        style={{width:"100%",minHeight:80,maxHeight:220,background:"none",border:"none",outline:"none",color:T.text,fontSize:15,padding:"20px 22px 10px",resize:"none",fontFamily:"inherit",lineHeight:1.7,boxSizing:"border-box"}}
      />
  
      {/* Files row */}
      {files.length>0&&(
        <div style={{display:"flex",flexWrap:"wrap",gap:8,padding:"0 16px 12px"}}>
          {files.map((f,i)=><FilePill key={i} file={f} onRemove={()=>setFiles(fs=>fs.filter((_,j)=>j!==i))}/>)}
        </div>
      )}
  
      {/* Bottom bar */}
      <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",padding:"10px 16px",borderTop:`1px solid ${T.border}`}}>
        <div style={{display:"flex",gap:8}}>
          <button onClick={()=>fileRef.current?.click()} style={{display:"flex",alignItems:"center",gap:6,padding:"7px 14px",background:T.surface,border:`1px solid ${T.border}`,borderRadius:20,color:T.muted,fontSize:12,cursor:"pointer"}}>
            🖼 Photo / PDF
          </button>
          <input ref={fileRef} type="file" multiple accept="image/*,application/pdf" style={{display:"none"}} onChange={e=>addFiles(e.target.files)}/>
        </div>
        <div style={{display:"flex",alignItems:"center",gap:12}}>
          <span style={{fontSize:11,color:T.muted}}>⌘↵ pour générer</span>
          <button onClick={generate} disabled={state==="loading"||!prompt.trim()}
            style={{padding:"9px 22px",background:state==="loading"||!prompt.trim()?T.dim:T.accent,border:"none",borderRadius:20,color:state==="loading"||!prompt.trim()?T.muted:"#0a0800",fontWeight:700,fontSize:13,cursor:state==="loading"||!prompt.trim()?"not-allowed":"pointer",letterSpacing:"-0.01em",transition:"all 0.2s"}}>
            {state==="loading"?"⏳ Génération…":"✨ Générer"}
          </button>
        </div>
      </div>
    </div>
  
    {errMsg&&<div style={{marginTop:12,color:"#e05555",fontSize:12,textAlign:"center",maxWidth:600}}>{errMsg}</div>}
  
    {/* Drop zone hint */}
    {state==="idle"&&(
      <div onDrop={onDrop} onDragOver={e=>e.preventDefault()}
        style={{marginTop:16,padding:"12px 24px",border:`1px dashed ${T.dim}`,borderRadius:12,color:T.muted,fontSize:12,textAlign:"center",cursor:"default"}}>
        📂 Glissez vos photos ou plans ici
      </div>
    )}
  </div>
  
  {/* ── RESULTS ── */}
  {state==="done"&&result&&(
    <div style={{flex:1,display:"flex",flexDirection:"column",overflow:"hidden"}}>
      
      {/* Result tabs */}
      <div style={{display:"flex",alignItems:"center",borderBottom:`1px solid ${T.border}`,background:T.surface,padding:"0 32px"}}>
        {[["devis","📋 Devis"],["3d","🏗 Vue 3D"]].map(([id,label])=>(
          <button key={id} onClick={()=>setTab(id)}
            style={{padding:"14px 22px",background:"none",border:"none",borderBottom:tab===id?`2px solid ${T.accent}`:"2px solid transparent",color:tab===id?T.accent:T.muted,fontSize:13,fontWeight:600,cursor:"pointer",transition:"color 0.2s"}}>
            {label}
          </button>
        ))}
        <div style={{marginLeft:"auto",fontSize:12,color:T.muted,padding:"0 0 0 12px"}}>
          {result.description}
        </div>
        <button onClick={()=>{setState("idle");setResult(null);setPrompt("");setFiles([]);}}
          style={{marginLeft:16,padding:"6px 16px",background:"none",border:`1px solid ${T.border}`,borderRadius:20,color:T.muted,fontSize:12,cursor:"pointer"}}>
          ↩ Nouveau
        </button>
      </div>
  
      <div style={{flex:1,overflow:"hidden",display:"flex"}}>
  
        {/* DEVIS PANEL */}
        {tab==="devis"&&(
          <div style={{flex:1,overflowY:"auto",padding:"40px 0"}}>
            <div style={{maxWidth:700,margin:"0 auto",padding:"0 32px"}}>
              {/* Header */}
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:32}}>
                <div>
                  <div style={{fontSize:26,fontWeight:800,letterSpacing:"-0.04em"}}>DEVIS</div>
                  <div style={{color:T.muted,fontSize:13,marginTop:2}}>
                    N° {new Date().getFullYear()}-{String(Math.floor(Math.random()*900)+100)} · {new Date().toLocaleDateString("fr-FR",{day:"numeric",month:"long",year:"numeric"})}
                  </div>
                </div>
                <div style={{display:"flex",alignItems:"center",gap:8,padding:"8px 16px",background:T.accentLo,borderRadius:20,border:`1px solid ${T.accent}33`}}>
                  <span style={{color:T.accent,fontSize:12,fontWeight:600}}>✓ Généré par IA</span>
                </div>
              </div>
  
              <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:16,padding:28,marginBottom:20}}>
                <div style={{fontSize:11,color:T.accent,textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:6}}>Objet du devis</div>
                <div style={{color:T.text,fontSize:14,lineHeight:1.6}}>{result.description}</div>
                {result.params&&(
                  <div style={{display:"flex",gap:16,marginTop:12,flexWrap:"wrap"}}>
                    {[["Largeur",`${result.params.w}m`],["Longueur",`${result.params.l}m`],["Hauteur mur",`${result.params.h}m`],["Pente",`${result.params.pente}°`]].map(([k,v])=>(
                      <div key={k} style={{padding:"6px 14px",background:T.surface,border:`1px solid ${T.border}`,borderRadius:8,fontSize:12}}>
                        <span style={{color:T.muted}}>{k} : </span><span style={{color:T.text,fontWeight:600}}>{v}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
  
              <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:16,padding:28}}>
                <DevisTable devis={result.devis}/>
              </div>
  
              <div style={{marginTop:20,display:"flex",gap:10,justifyContent:"flex-end"}}>
                <button onClick={()=>window.print()} style={{padding:"10px 20px",background:"none",border:`1px solid ${T.border}`,borderRadius:10,color:T.muted,fontSize:12,cursor:"pointer"}}>
                  🖨 Imprimer
                </button>
                <button style={{padding:"10px 20px",background:T.accent,border:"none",borderRadius:10,color:"#0a0800",fontSize:12,fontWeight:700,cursor:"pointer"}}>
                  📤 Envoyer au client
                </button>
              </div>
            </div>
          </div>
        )}
  
        {/* 3D PANEL */}
        {tab==="3d"&&(
          <div style={{flex:1,position:"relative"}}>
            <Viewer3D params={result.params||{}} active={tab==="3d"}/>
          </div>
        )}
      </div>
    </div>
  )}
  
  {/* Loading overlay */}
  {state==="loading"&&(
    <div style={{flex:1,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",gap:20,padding:40}}>
      <div style={{width:56,height:56,border:`3px solid ${T.border}`,borderTop:`3px solid ${T.accent}`,borderRadius:"50%",animation:"spin 0.8s linear infinite"}}/>
      <div style={{color:T.muted,fontSize:14}}>Analyse du projet et génération du devis…</div>
    </div>
  )}
  
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    *{box-sizing:border-box;margin:0;padding:0;}
    body{background:${T.bg};}
    @keyframes spin{to{transform:rotate(360deg)}}
    ::-webkit-scrollbar{width:5px;}
    ::-webkit-scrollbar-track{background:${T.surface};}
    ::-webkit-scrollbar-thumb{background:${T.dim};border-radius:3px;}
    textarea::placeholder{color:${T.muted};}
    textarea{scrollbar-width:thin;}
  `}</style>
  ```
  
    </div>
  );

}
