const COLOR_CURVA = [124, 58, 237];
const COLOR_PUNTO = [236, 72, 153];
const COLOR_RECTA = [251, 146, 60];

let appletGGB = null;
let appletListo = false;
let appletFallido = false;
let accionPendiente = null;

function montarGraficadora(idContenedor) {
  const host = document.getElementById(idContenedor);
  if (typeof GGBApplet === "undefined") {
    appletFallido = true;
    host.classList.add("sin-ggb");
    host.textContent = "No se pudo cargar GeoGebra. Revisa tu conexión a internet y recarga la página.";
    return;
  }
  const config = {
    appName: "graphing",
    width: host.clientWidth || 480,
    height: 440,
    showToolBar: false,
    showAlgebraInput: false,
    showMenuBar: false,
    enableRightClick: false,
    showResetIcon: false,
    borderColor: "#2b2547",
    appletOnLoad: (api) => {
      appletGGB = api;
      appletListo = true;
      if (accionPendiente) {
        const accion = accionPendiente;
        accionPendiente = null;
        accion();
      }
    },
  };
  new GGBApplet(config, true).inject(idContenedor);
}

function conGraficadora(accion) {
  if (appletFallido) return;
  if (appletListo) accion();
  else accionPendiente = accion;
}

function dibujarPuntos(puntos) {
  puntos.forEach((p, i) => {
    const id = `P_{${i}}`;
    appletGGB.evalCommand(`${id}=(${p[0]},${p[1]})`);
    appletGGB.setColor(id, ...COLOR_PUNTO);
    appletGGB.setPointSize(id, 4);
    appletGGB.setLabelVisible(id, false);
  });
}

function ajustarZoom(puntos) {
  if (puntos.length === 0) return;
  const xs = puntos.map((p) => p[0]);
  const ys = puntos.map((p) => p[1]);
  const mx = Math.max((Math.max(...xs) - Math.min(...xs)) * 0.35, 1);
  const my = Math.max((Math.max(...ys) - Math.min(...ys)) * 0.35, 1);
  appletGGB.setCoordSystem(
    Math.min(...xs) - mx,
    Math.max(...xs) + mx,
    Math.min(...ys) - my,
    Math.max(...ys) + my
  );
}

function graficarFuncion(expresion, puntos, nombre, extras) {
  conGraficadora(() => {
    appletGGB.reset();
    appletGGB.evalCommand(`${nombre}(x)=${expresion}`);
    appletGGB.setColor(nombre, ...COLOR_CURVA);
    appletGGB.setLineThickness(nombre, 5);
    (extras || []).forEach((cmd, i) => {
      const id = `aux_{${i}}`;
      appletGGB.evalCommand(`${id}:${cmd}`);
      appletGGB.setColor(id, ...COLOR_RECTA);
      appletGGB.setLineStyle(id, 1);
    });
    dibujarPuntos(puntos);
    ajustarZoom(puntos);
  });
}

function formatear(valor, clave) {
  if (valor === null || valor === undefined) return "—";
  if (typeof valor !== "number") return String(valor);
  if (clave === "n") return String(valor);
  if (valor !== 0 && Math.abs(valor) < 1e-6) return valor.toExponential(2);
  return valor.toFixed(6);
}

function formatearCorto(valor) {
  const texto = Number(valor.toFixed(4)).toString();
  return texto === "-0" ? "0" : texto;
}

async function llamarApi(ruta, cuerpo) {
  const resp = await fetch(ruta, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo),
  });
  return resp.json();
}

function mostrarEstado(elemento, clase, texto) {
  elemento.className = `estado estado--${clase}`;
  elemento.textContent = texto;
}

// Exporta fórmulas, pasos, tablas y gráficas al PDF generado por Flask.
async function descargarPDFReporte(reporte, nombre="procedimiento-metodos-numericos.pdf") {
  if (!reporte) throw new Error("Primero realiza el cálculo");
  const respuesta=await fetch("/api/exportar-pdf",{
    method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify(reporte)
  });
  if(!respuesta.ok){
    let mensaje="No se pudo generar el PDF";
    try{const d=await respuesta.json();mensaje=d.mensaje||mensaje;}catch(_){}
    throw new Error(mensaje);
  }
  const blob=await respuesta.blob();
  if(blob.type!=="application/pdf")throw new Error("El servidor no devolvió un PDF válido");
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a");a.href=url;a.download=nombre;a.style.display="none";
  document.body.appendChild(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),2000);
}
async function importarArchivoNumerico(file,columnas) {
  if(!file)throw new Error("Selecciona un archivo CSV o Excel");
  const form=new FormData();form.append("archivo",file);form.append("columnas",String(columnas));
  const respuesta=await fetch("/api/importar-tabla",{method:"POST",body:form});
  const data=await respuesta.json();
  if(!respuesta.ok||!data.ok)throw new Error(data.mensaje||"No se pudo importar el archivo");
  return data.filas;
}
