// Desarrollo numérico de las iteraciones de búsqueda de raíces.
(function(){
"use strict";
const n=v=>typeof v==="number"&&Number.isFinite(v)?Number(v.toPrecision(10)).toString():String(v??"—");
window.desarrolloRaices=function(slug,filas,formula){
 const pasos=[{titulo:"1. Fórmula general",detalle:formula}];
 (filas||[]).forEach((f,i)=>{
   let detalle="";
   if(slug==="biseccion"){
     detalle="c = (a+b)/2 = ("+n(f.a)+" + "+n(f.b)+")/2 = "+n(f.c)+
       "; f(c) = "+n(f.fc)+"; límite de error = ("+n(f.b)+" − "+n(f.a)+")/2 = "+n(f.error);
     if(f.fa!==undefined&&f.fb!==undefined)detalle+="; f(a)="+n(f.fa)+", f(b)="+n(f.fb);
   }else if(slug==="falsa-posicion"){
     detalle="c = (a·f(b)−b·f(a))/(f(b)−f(a)) = ("+n(f.a)+"·"+n(f.fb)+
        " − "+n(f.b)+"·"+n(f.fa)+")/("+n(f.fb)+" − "+n(f.fa)+") = "+n(f.c)+
        "; f(c) = "+n(f.fc)+"; error = "+n(f.error);
   }else if(slug==="secante"){
     detalle="x_nuevo = x_n − f(x_n)·(x_n−x_anterior)/(f(x_n)−f(x_anterior)) = "+
       n(f.xb)+" − ("+n(f.fb)+"·("+n(f.xb)+" − "+n(f.xa)+"))/("+n(f.fb)+" − "+n(f.fa)+
       ") = "+n(f.xn)+"; error = "+n(f.error);
   }else if(slug==="newton"){
     detalle="x_nuevo = x − f(x)/f'(x) = "+n(f.xi)+" − ("+n(f.fxi)+")/("+n(f.dfxi)+
       ") = "+n(f.xn)+"; error = "+n(f.error);
   }else if(slug==="newton-segundo-orden"){
     detalle="x_nuevo = x − f·f'/(f'^2−f·f'') = "+n(f.xi)+" − ("+n(f.fxi)+
       "·"+n(f.dfxi)+")/("+n(f.dfxi)+"²−"+n(f.fxi)+"·"+n(f.d2fxi)+
       ") = "+n(f.xn)+"; error = "+n(f.error);
   }else if(slug==="punto-fijo"){
     detalle="x_nuevo = g(x) = g("+n(f.xi)+") = "+n(f.gxi)+"; error = |"+
       n(f.gxi)+" − "+n(f.xi)+"| = "+n(f.error);
   }else{
     detalle=Object.entries(f).map(([k,v])=>k+" = "+n(v)).join("; ");
   }
   pasos.push({titulo:"Iteración "+(i+1)+" — sustitución",detalle});
 });
 return pasos;
};
})();
