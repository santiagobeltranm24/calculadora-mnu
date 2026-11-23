# Calculadora de Métodos Numéricos

Aplicación web académica para explorar y ejecutar métodos numéricos. El proyecto reúne explicaciones, formularios interactivos, tablas de iteraciones y resultados para el estudio de análisis numérico.

## Descargar la calculadora

Puedes descargar el proyecto completo en formato ZIP desde este enlace:

[**Descargar calculadora-mnu (.zip)**](https://github.com/santiagobeltranm24/calculadora-mnu/archive/refs/heads/main.zip)

Después de descomprimirlo, sigue los pasos de [Ejecución local](#ejecución-local) para instalar las dependencias e iniciar la aplicación en tu computadora.

## Funcionalidades

### Hito 2 — Aproximación y raíces
- Análisis de errores de redondeo.
- Método de punto fijo.
- Newton-Raphson y Newton de segundo orden.
- Visualización de funciones y apoyo gráfico con GeoGebra.

### Hito 3 — Raíces y sistemas lineales
- Bisección, falsa posición y secante.
- Eliminación de Gauss con pivoteo parcial.
- Gauss-Jordan con pivoteo parcial.
- Método iterativo de Jacobi.

### Hito 4 — Interpolación y proyecciones
- Redondeo y truncamiento.
- Desarrollo de Taylor.
- Gauss-Seidel.
- Interpolación lineal, Newton hacia adelante, Lagrange y diferencias divididas.
- Regresión lineal, exponencial, potencial y cuadrática.
- Series de tiempo.

## Tecnologías

- **Python** como lenguaje principal.
- **Flask** para las rutas, vistas y API.
- **SymPy** para operaciones simbólicas y derivadas.
- **NumPy** para cálculos numéricos.
- HTML, CSS y JavaScript para la interfaz.

## Estructura del proyecto

```text
calculadora-mnu/
├── README.md
├── render.yaml
└── nueva_calc/
    ├── app.py
    ├── requirements.txt
    ├── metodos/
    │   ├── aproximacion.py
    │   ├── interpolacion.py
    │   ├── lineales.py
    │   ├── proyecciones.py
    │   └── ...
    ├── templates/
    └── static/
        ├── css/
        └── js/
```

## Ejecución local

Se recomienda Python 3.10 o superior.

1. Clona el repositorio:

   ```bash
   git clone https://github.com/santiagobeltranm24/calculadora-mnu.git
   cd calculadora-mnu/nueva_calc
   ```

2. (Opcional, recomendado) Crea y activa un entorno virtual:

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **Linux / macOS**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Inicia la aplicación:

   ```bash
   python app.py
   ```

5. Abre [http://127.0.0.1:5000](http://127.0.0.1:5000) en tu navegador.

## Despliegue

La aplicación utiliza Flask y tiene endpoints de API en el servidor, por lo que **GitHub Pages no puede ejecutarla directamente** (Pages solo aloja sitios estáticos).

El repositorio incluye una configuración `render.yaml` para desplegarla como servicio web en [Render](https://render.com/):

1. Inicia sesión en Render y conecta tu cuenta de GitHub.
2. Selecciona **New → Blueprint** y elige este repositorio.
3. Render detectará `render.yaml`; revisa la configuración y crea el servicio.
4. Cuando termine el despliegue, Render proporcionará una URL pública `onrender.com).

El plan gratuito de Render puede suspender el servicio tras un periodo sin actividad; la primera visita posterior puede tardar unos segundos.

## Notas

- Los métodos se ejecutan en el backend de Python; no basta con publicar los archivos HTML en un hosting estático.
- Los ejemplos y valores iniciales sirven como punto de partida para probar cada método.
- Este proyecto tiene fines educativos y de apoyo al aprendizaje de métodos numéricos.

## Autor

Proyecto académico desarrollado por **Santiago Beltrán**.
