// Tutorial paso a paso reutilizable para todos los métodos.
function crearTutorPasos(contenedor, pasos) {
  if (!contenedor) return;
  contenedor.replaceChildren();
  if (!Array.isArray(pasos) || pasos.length===0) return;
  const guia=document.createElement("section");guia.className="tutorial-activo";
  const encabezado=document.createElement("div");encabezado.className="tutorial-cabecera";
  const rotulo=document.createElement("strong");rotulo.textContent="Tutorial interactivo";
  const progreso=document.createElement("span");progreso.className="tutorial-progreso";encabezado.append(rotulo,progreso);guia.appendChild(encabezado);
  const barra=document.createElement("div");barra.className="tutorial-barra";
  const relleno=document.createElement("div");relleno.className="tutorial-relleno";barra.appendChild(relleno);guia.appendChild(barra);
  const tarjeta=document.createElement("article");tarjeta.className="tutorial-tarjeta";guia.appendChild(tarjeta);
  const controles=document.createElement("div");controles.className="tutorial-controles";
  const anterior=document.createElement("button");anterior.type="button";anterior.className="boton-suave";anterior.textContent="← Anterior";
  const siguiente=document.createElement("button");siguiente.type="button";siguiente.className="boton";siguiente.textContent="Siguiente →";
  const todo=document.createElement("button");todo.type="button";todo.className="boton-suave";todo.textContent="Ver todos";
  controles.append(anterior,siguiente,todo);guia.appendChild(controles);
  let indice=0;let todos=false;
  const pintar=()=>{
    tarjeta.replaceChildren();
    const visible=todos?pasos:[pasos[indice]];
    visible.forEach((paso,j)=>{
      const d=document.createElement("div");d.className="tutorial-paso";
      const h=document.createElement("h3");h.textContent=(todos?"Paso "+(j+1)+": ":"")+paso.titulo;
      const p=document.createElement("p");p.textContent=paso.detalle||"";
      d.append(h,p);tarjeta.appendChild(d);
    });
    progreso.textContent=todos?"Todos los pasos":(indice+1)+" / "+pasos.length;
    relleno.style.width=(todos?100:(indice+1)/pasos.length*100)+"%";
    anterior.disabled=todos||indice===0;
    siguiente.disabled=todos||indice===pasos.length-1;
    todo.textContent=todos?"Ver uno a uno":"Ver todos";
  };
  anterior.addEventListener("click",()=>{indice=Math.max(0,indice-1);pintar();});
  siguiente.addEventListener("click",()=>{indice=Math.min(pasos.length-1,indice+1);pintar();});
  todo.addEventListener("click",()=>{todos=!todos;pintar();});
  contenedor.appendChild(guia);
  pintar();
}
