/* Renderizador SVG local, sin dependencias de CDN. */
(function(){
"use strict";
const NS="http://www.w3.org/2000/svg";
const colores=["#a78bfa","#22d3ee","#fbbf24","#fb7185","#4ade80","#f472b6"];
function svg(nombre,attr={},padre){
  const e=document.createElementNS(NS,nombre);
  Object.entries(attr).forEach(([k,v])=>e.setAttribute(k,v));
  if(padre)padre.appendChild(e);
  return e;
}
function texto(p,x,y,contenido,attr={}){
  const e=svg("text",{x,y,fill:"#abb3ca","font-size":"12","font-family":"sans-serif",...attr},p);
  e.textContent=contenido;return e;
}
function fmt(x){
  if(!Number.isFinite(x))return "—";
  return Math.abs(x)>=10000||(Math.abs(x)<.001&&x!==0)?x.toExponential(2):Number(x.toPrecision(5)).toString();
}
function render(g,destino){
  const series=(g.series||[]).map(s=>({...s,puntos:(s.puntos||[]).map(p=>[Number(p[0]),Number(p[1])]).filter(p=>p.every(Number.isFinite))})).filter(s=>s.puntos.length);
  if(!series.length)return;
  const tarjeta=document.createElement("section");tarjeta.className="grafica-tarjeta";
  const h=document.createElement("h3");h.textContent=g.titulo||"Gráfica";tarjeta.appendChild(h);
  const leyenda=document.createElement("div");leyenda.className="grafica-leyenda";
  series.forEach((s,i)=>{
    const item=document.createElement("span"),m=document.createElement("i");
    m.style.background=colores[i%colores.length];
    item.appendChild(m);item.appendChild(document.createTextNode(s.nombre));leyenda.appendChild(item);
  });
  tarjeta.appendChild(leyenda);
  const marco=document.createElement("div");marco.className="grafica-marco";
  const W=760,H=355,L=78,R=26,T=20,B=62;
  const pts=series.flatMap(s=>s.puntos);
  let xmin=Math.min(...pts.map(p=>p[0])),xmax=Math.max(...pts.map(p=>p[0]));
  let ymin=Math.min(...pts.map(p=>p[1])),ymax=Math.max(...pts.map(p=>p[1]));
  const dx=xmax-xmin||Math.max(1,Math.abs(xmax)*.1),dy=ymax-ymin||Math.max(1,Math.abs(ymax)*.1);
  xmin-=dx*.04;xmax+=dx*.04;ymin-=dy*.12;ymax+=dy*.12;
  const X=x=>L+(x-xmin)/(xmax-xmin)*(W-L-R);
  const Y=y=>H-B-(y-ymin)/(ymax-ymin)*(H-T-B);
  const gra=svg("svg",{viewBox:`0 0 ${W} ${H}`,role:"img","aria-label":g.titulo||"Gráfica",preserveAspectRatio:"xMidYMid meet"},marco);
  for(let i=0;i<=5;i++){
    const y=T+i*(H-T-B)/5;
    svg("line",{x1:L,y1:y,x2:W-R,y2:y,stroke:"#fff","stroke-opacity":".1"},gra);
    texto(gra,L-10,y+4,fmt(ymax-(y-T)/(H-T-B)*(ymax-ymin)),{"text-anchor":"end"});
    const x=L+i*(W-L-R)/5;
    svg("line",{x1:x,y1:T,x2:x,y2:H-B,stroke:"#fff","stroke-opacity":".08"},gra);
    texto(gra,x,H-B+21,fmt(xmin+(x-L)/(W-L-R)*(xmax-xmin)),{"text-anchor":"middle"});
  }
  svg("rect",{x:L,y:T,width:W-L-R,height:H-T-B,fill:"none",stroke:"#fff","stroke-opacity":".22"},gra);
  series.forEach((s,i)=>{
    const color=colores[i%colores.length];
    if(s.tipo!=="puntos"&&s.puntos.length>1)
      svg("polyline",{points:s.puntos.map(p=>`${X(p[0]).toFixed(2)},${Y(p[1]).toFixed(2)}`).join(" "),fill:"none",stroke:color,"stroke-width":"2.6","stroke-linecap":"round","stroke-linejoin":"round"},gra);
    if(s.tipo==="puntos"||s.puntos.length<=25)
      s.puntos.forEach(p=>{
        const c=svg("circle",{cx:X(p[0]),cy:Y(p[1]),r:s.tipo==="puntos"?5:3,fill:color,stroke:"#151226","stroke-width":"1.5"},gra);
        svg("title",{},c).textContent=`${s.nombre}: (${fmt(p[0])}, ${fmt(p[1])})`;
      });
  });
  texto(gra,(L+W-R)/2,H-12,g.eje_x||"x",{"text-anchor":"middle","font-size":"13"});
  texto(gra,16,(T+H-B)/2,g.eje_y||"y",{"text-anchor":"middle","font-size":"13",transform:`rotate(-90 16 ${(T+H-B)/2})`});
  tarjeta.appendChild(marco);destino.appendChild(tarjeta);
}
window.mostrarGraficas=function(graficas,contenedor){
  if(!contenedor)return;
  contenedor.replaceChildren();
  (graficas||[]).forEach(g=>render(g,contenedor));
};
})();
