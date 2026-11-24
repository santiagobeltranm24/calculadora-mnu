/* Gráficas SVG interactivas: zoom, desplazamiento, tooltip y exportación SVG. */
(function(){
"use strict";
const NS="http://www.w3.org/2000/svg";
const COLORES=["#2563eb","#0891b2","#d97706","#a855f7","#16a34a","#e11d48"];
function elemento(tag,props={},parent){
 const el=document.createElementNS(NS,tag);
 Object.entries(props).forEach(([k,v])=>el.setAttribute(k,String(v)));
 if(parent)parent.appendChild(el);
 return el;
}
function texto(parent,x,y,value,props={}){
 const el=elemento("text",{x,y,fill:"#64748b","font-size":12,"font-family":"Inter, sans-serif",...props},parent);
 el.textContent=value;return el;
}
function num(n){
 if(!Number.isFinite(n))return "—";
 return Math.abs(n)>=1e5||(Math.abs(n)<.0001&&n!==0)?n.toExponential(2):Number(n.toPrecision(6)).toString();
}
function grafica(g,host){
 const data=(g.series||[]).slice(0,9).map(s=>({
    nombre:String(s.nombre||"Serie"),tipo:s.tipo||"linea",
    puntos:(s.puntos||[]).slice(0,4000).map(v=>[Number(v[0]),Number(v[1])]).filter(p=>p.every(Number.isFinite))
 })).filter(s=>s.puntos.length);
 if(!data.length)return;
 const card=document.createElement("section");card.className="grafica-tarjeta";
 const cab=document.createElement("div");cab.className="grafica-cabecera";
 const h=document.createElement("h3");h.textContent=g.titulo||"Gráfica";cab.appendChild(h);
 const controls=document.createElement("div");controls.className="grafica-controles";
 function boton(label,title,fn){
   const b=document.createElement("button");b.type="button";b.className="boton-suave";b.textContent=label;
   b.setAttribute("aria-label",title);b.title=title;b.addEventListener("click",fn);controls.appendChild(b);return b;
 }
 cab.appendChild(controls);card.appendChild(cab);
 const legend=document.createElement("div");legend.className="grafica-leyenda";
 data.forEach((s,i)=>{const x=document.createElement("span"),dot=document.createElement("i");dot.style.background=COLORES[i%COLORES.length];x.append(dot,document.createTextNode(s.nombre));legend.appendChild(x);});
 card.appendChild(legend);
 const frame=document.createElement("div");frame.className="grafica-marco grafica-interactiva";
 const W=760,H=355,L=82,R=28,T=22,B=62;
 const points=data.flatMap(s=>s.puntos);
 let x1=Math.min(...points.map(p=>p[0])),x2=Math.max(...points.map(p=>p[0]));
 let y1=Math.min(...points.map(p=>p[1])),y2=Math.max(...points.map(p=>p[1]));
 let dx=x2-x1||Math.max(1,Math.abs(x1)*.12),dy=y2-y1||Math.max(1,Math.abs(y1)*.12);
 const home={xmin:x1-dx*.04,xmax:x2+dx*.04,ymin:y1-dy*.12,ymax:y2+dy*.12};
 let vista={...home};
 const svg=elemento("svg",{viewBox:`0 0 ${W} ${H}`,role:"img","aria-label":g.titulo||"Gráfica",preserveAspectRatio:"xMidYMid meet"},frame);
 svg.style.touchAction="none";
 const group=elemento("g",{},svg);
 const label=document.createElement("div");label.className="grafica-tooltip";label.hidden=true;frame.appendChild(label);
 function escX(x){return L+(x-vista.xmin)/(vista.xmax-vista.xmin)*(W-L-R);}
 function escY(y){return H-B-(y-vista.ymin)/(vista.ymax-vista.ymin)*(H-T-B);}
 function datosX(x){return vista.xmin+(x-L)/(W-L-R)*(vista.xmax-vista.xmin);}
 function datosY(y){return vista.ymin+(H-B-y)/(H-T-B)*(vista.ymax-vista.ymin);}
 const box=()=>({w:svg.getBoundingClientRect().width,h:svg.getBoundingClientRect().height});
 function pixel(ev){
   const rect=svg.getBoundingClientRect();
   return [(ev.clientX-rect.left)*W/rect.width,(ev.clientY-rect.top)*H/rect.height];
 }
 function pintar(){
   group.replaceChildren();
   for(let i=0;i<=5;i++){
     const yy=T+i*(H-T-B)/5,xx=L+i*(W-L-R)/5;
     elemento("line",{x1:L,y1:yy,x2:W-R,y2:yy,stroke:"#cbd5e1","stroke-opacity":".65"},group);
     texto(group,L-10,yy+4,num(vista.ymax-i/5*(vista.ymax-vista.ymin)),{"text-anchor":"end"});
     elemento("line",{x1:xx,y1:T,x2:xx,y2:H-B,stroke:"#cbd5e1","stroke-opacity":".55"},group);
     texto(group,xx,H-B+23,num(vista.xmin+i/5*(vista.xmax-vista.xmin)),{"text-anchor":"middle"});
   }
   elemento("rect",{x:L,y:T,width:W-L-R,height:H-T-B,fill:"none",stroke:"#94a3b8","stroke-opacity":".55"},group);
   const defs=elemento("defs",{},group);
   const clip=elemento("clipPath",{id:"grafclip-"+identificador},defs);
   elemento("rect",{x:L,y:T,width:W-L-R,height:H-T-B},clip);
   const curvas=elemento("g",{"clip-path":"url(#grafclip-"+identificador+")"},group);
   data.forEach((s,i)=>{
     const color=COLORES[i%COLORES.length];
     if(s.tipo!=="puntos"&&s.puntos.length>1)
       elemento("polyline",{points:s.puntos.map(p=>escX(p[0]).toFixed(2)+","+escY(p[1]).toFixed(2)).join(" "),fill:"none",stroke:color,"stroke-width":2.5,"stroke-linecap":"round","stroke-linejoin":"round"},curvas);
     if(s.tipo==="puntos"||s.puntos.length<30)
       s.puntos.forEach(p=>{
         const c=elemento("circle",{cx:escX(p[0]),cy:escY(p[1]),r:s.tipo==="puntos"?5:3,fill:color,stroke:"#fff","stroke-width":1},curvas);
         elemento("title",{},c).textContent=s.nombre+": ("+num(p[0])+", "+num(p[1])+")";
       });
   });
   texto(group,(L+W-R)/2,H-12,g.eje_x||"x",{"text-anchor":"middle","font-size":13});
   texto(group,16,(T+H-B)/2,g.eje_y||"y",{"text-anchor":"middle","font-size":13,transform:`rotate(-90 16 ${(T+H-B)/2})`});
 }
 let identificador=Math.random().toString(36).slice(2);
 function zoom(factor,centro){
   const px=centro?centro[0]:(L+W-R)/2,py=centro?centro[1]:(T+H-B)/2;
   const origenX=datosX(px),origenY=datosY(py);
   const rangoX=Math.max(1e-12,(vista.xmax-vista.xmin)*factor);
   const rangoY=Math.max(1e-12,(vista.ymax-vista.ymin)*factor);
   const ux=(px-L)/(W-L-R),uy=(H-B-py)/(H-T-B);
   vista={xmin:origenX-ux*rangoX,xmax:origenX+(1-ux)*rangoX,
          ymin:origenY-uy*rangoY,ymax:origenY+(1-uy)*rangoY};
   label.hidden=true;pintar();
 }
 boton("+","Acercar",()=>zoom(.75));
 boton("−","Alejar",()=>zoom(1.33));
 boton("Restablecer","Restablecer encuadre",()=>{vista={...home};pintar();});
 boton("SVG","Descargar gráfica SVG",()=>{
    const copia=svg.cloneNode(true);
    copia.setAttribute("xmlns",NS);
    const contenido=new XMLSerializer().serializeToString(copia);
    const url=URL.createObjectURL(new Blob([contenido],{type:"image/svg+xml;charset=utf-8"}));
    const a=document.createElement("a");a.href=url;a.download="grafica-metodos.svg";a.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
 });
 let arrastre=null;
 svg.addEventListener("pointerdown",ev=>{
   if(ev.button!==0)return;
   arrastre={at:pixel(ev),vista:{...vista}};
   try{svg.setPointerCapture(ev.pointerId);}catch(_){};label.hidden=true;
 });
 svg.addEventListener("pointermove",ev=>{
   const pos=pixel(ev);
   if(arrastre){
     const difX=(pos[0]-arrastre.at[0])/(W-L-R)*(arrastre.vista.xmax-arrastre.vista.xmin);
     const difY=(pos[1]-arrastre.at[1])/(H-T-B)*(arrastre.vista.ymax-arrastre.vista.ymin);
     vista={xmin:arrastre.vista.xmin-difX,xmax:arrastre.vista.xmax-difX,
       ymin:arrastre.vista.ymin+difY,ymax:arrastre.vista.ymax+difY};pintar();
     return;
   }
   let mejor=null,dist=16*16;
   if(pos[0]<L||pos[0]>W-R||pos[1]<T||pos[1]>H-B){label.hidden=true;return;}
   data.forEach(s=>s.puntos.forEach(p=>{
     const sx=escX(p[0]),sy=escY(p[1]),d=(sx-pos[0])**2+(sy-pos[1])**2;
     if(d<dist){dist=d;mejor={serie:s.nombre,p};}
   }));
   if(mejor){
     label.textContent=mejor.serie+": ("+num(mejor.p[0])+", "+num(mejor.p[1])+")";
     label.style.left=Math.min(82,pos[0]/W*100)+"%";
     label.style.top=Math.max(4,pos[1]/H*100-12)+"%";
     label.hidden=false;
   }else label.hidden=true;
 });
 const soltar=()=>{arrastre=null;};
 svg.addEventListener("pointerup",soltar);svg.addEventListener("pointercancel",soltar);svg.addEventListener("pointerleave",()=>{if(!arrastre)label.hidden=true;});
 svg.addEventListener("wheel",ev=>{
   ev.preventDefault();zoom(ev.deltaY<0?.85:1.18,pixel(ev));
 },{passive:false});
 pintar();card.appendChild(frame);
 const instruccion=document.createElement("p");instruccion.className="grafica-ayuda";instruccion.textContent="Rueda: zoom · Arrastra: mover · Acerca el puntero a un punto para ver sus coordenadas.";card.appendChild(instruccion);
 host.appendChild(card);
}
window.mostrarGraficas=function(graficas,contenedor){
 if(!contenedor)return;
 contenedor.replaceChildren();
 (graficas||[]).forEach(g=>grafica(g,contenedor));
};
})();