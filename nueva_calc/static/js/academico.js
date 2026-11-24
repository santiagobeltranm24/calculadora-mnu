/* Navegación y búsqueda; la matemática permanece en los módulos existentes. */
(function () {
  "use strict";
  const menu = document.getElementById("menu-lateral");
  const boton = document.getElementById("boton-menu");
  const fondo = document.getElementById("fondo-menu");
  function mostrarMenu(abierto) {
    document.body.classList.toggle("menu-abierto", abierto);
    if (boton) {
      boton.setAttribute("aria-expanded", String(abierto));
      boton.setAttribute("aria-label", abierto ? "Cerrar menú de temas" : "Abrir menú de temas");
    }
  }
  if (boton) boton.addEventListener("click", () => mostrarMenu(!document.body.classList.contains("menu-abierto")));
  if (fondo) fondo.addEventListener("click", () => mostrarMenu(false));
  if (menu) menu.querySelectorAll("a").forEach(a => a.addEventListener("click", () => mostrarMenu(false)));
  document.addEventListener("keydown", ev => { if (ev.key === "Escape") mostrarMenu(false); });
  const campo = document.getElementById("buscar-metodos");
  if (!campo) return;
  const botones = Array.from(document.querySelectorAll(".filtro-tema"));
  const tarjetas = Array.from(document.querySelectorAll(".metodo-tarjeta"));
  const secciones = Array.from(document.querySelectorAll(".tema-seccion"));
  const contador = document.getElementById("contador-metodos");
  const vacio = document.getElementById("sin-resultados");
  let filtro = "todos";
  const limpiar = s => String(s).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
  function actualizar() {
    const buscar = limpiar(campo.value);
    let visibles = 0;
    tarjetas.forEach(tarjeta => {
      const mostrar = (filtro === "todos" || tarjeta.dataset.tema === filtro)
          && limpiar(tarjeta.dataset.busqueda || tarjeta.textContent).includes(buscar);
      tarjeta.hidden = !mostrar;
      if (mostrar) visibles++;
    });
    secciones.forEach(s => s.hidden = !Array.from(s.querySelectorAll(".metodo-tarjeta")).some(t => !t.hidden));
    if (vacio) vacio.hidden = visibles !== 0;
    if (contador) contador.textContent = visibles + (visibles === 1 ? " método disponible" : " métodos disponibles");
  }
  botones.forEach(b => b.addEventListener("click", () => {
    filtro = b.dataset.filtro || "todos";
    botones.forEach(opcion => {
      const activo = opcion === b;
      opcion.classList.toggle("seleccionado", activo);
      opcion.setAttribute("aria-pressed", String(activo));
    });
    actualizar();
  }));
  campo.addEventListener("input", actualizar);
  actualizar();
})();
