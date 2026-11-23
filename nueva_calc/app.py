from flask import Flask, jsonify, render_template, request, abort

from metodos import (
    redondeo, punto_fijo, newton, newton2,
    biseccion, falsa_posicion, secante, lineales,
    aproximacion, interpolacion, proyecciones, graficas,
)
from metodos.ayuda import AYUDA

app = Flask(__name__)

CAMPO_TOL = {"nombre": "tol", "etiqueta": "tolerancia", "valor": "0.0001"}
CAMPO_ITER = {"nombre": "iter_max", "etiqueta": "iteraciones máximas", "valor": "50"}

RAICES = {
    "biseccion": {
        "hito": 3,
        "grafica": False,
        "titulo": "Bisección",
        "resumen": "Divide el intervalo [a, b] a la mitad conservando el cambio de signo.",
        "descripcion": "Requiere f(a)·f(b) < 0. En cada paso toma el punto medio c y se queda con la mitad donde f cambia de signo; el error baja a la mitad en cada iteración.",
        "funcion": biseccion.ejecutar,
        "campos": [
            {"nombre": "f", "etiqueta": "f(x)", "valor": "x**3 + 4*x**2 - 10", "texto": True},
            {"nombre": "a", "etiqueta": "a", "valor": "1"},
            {"nombre": "b", "etiqueta": "b", "valor": "2"},
            CAMPO_TOL, CAMPO_ITER,
        ],
        "columnas": [["n", "n"], ["a", "a"], ["b", "b"], ["c", "c"], ["fc", "f(c)"], ["error", "error"]],
        "ggb": "f",
    },
    "falsa-posicion": {
        "hito": 3,
        "grafica": False,
        "titulo": "Falsa posición",
        "resumen": "Usa la recta entre (a, f(a)) y (b, f(b)) para estimar la raíz.",
        "descripcion": "Variante de bisección que, en lugar del punto medio, toma el corte con el eje x de la recta que une los extremos. Requiere f(a)·f(b) < 0.",
        "funcion": falsa_posicion.ejecutar,
        "campos": [
            {"nombre": "f", "etiqueta": "f(x)", "valor": "x**3 + 4*x**2 - 10", "texto": True},
            {"nombre": "a", "etiqueta": "a", "valor": "1"},
            {"nombre": "b", "etiqueta": "b", "valor": "2"},
            CAMPO_TOL, CAMPO_ITER,
        ],
        "columnas": [["n", "n"], ["a", "a"], ["b", "b"], ["c", "c"], ["fc", "f(c)"], ["error", "error"]],
        "ggb": "f",
    },
    "secante": {
        "hito": 3,
        "grafica": False,
        "titulo": "Secante",
        "resumen": "Aproxima la derivada de Newton con dos puntos previos, sin derivar.",
        "descripcion": "Necesita dos valores iniciales x0 y x1 y no exige que haya cambio de signo ni calcula f'(x): usa la recta secante entre los dos últimos puntos.",
        "funcion": secante.ejecutar,
        "campos": [
            {"nombre": "f", "etiqueta": "f(x)", "valor": "x**3 + 4*x**2 - 10", "texto": True},
            {"nombre": "x0", "etiqueta": "x0", "valor": "1"},
            {"nombre": "x1", "etiqueta": "x1", "valor": "2"},
            CAMPO_TOL, CAMPO_ITER,
        ],
        "columnas": [["n", "n"], ["xa", "x_(n−1)"], ["xb", "x_n"], ["fa", "f(x_(n−1))"], ["fb", "f(x_n)"], ["xn", "x_(n+1)"], ["error", "error"]],
        "ggb": "f",
    },
    "punto-fijo": {
        "hito": 2,
        "grafica": True,
        "titulo": "Punto fijo",
        "resumen": "Itera x_(n+1) = g(x_n) hasta cumplir la tolerancia.",
        "descripcion": "Reescribe f(x) = 0 como x = g(x) e itera. Converge si |g'(x)| < 1 cerca de la raíz. La gráfica incluye la recta y = x para ver el cruce.",
        "funcion": punto_fijo.ejecutar,
        "campos": [
            {"nombre": "g", "etiqueta": "g(x)", "valor": "sqrt(10/(x+4))", "texto": True},
            {"nombre": "x0", "etiqueta": "x0", "valor": "1.5"},
            CAMPO_TOL, CAMPO_ITER,
        ],
        "columnas": [["n", "n"], ["xi", "x_n"], ["gxi", "g(x_n)"], ["error", "error"]],
        "ggb": "g",
    },
    "newton": {
        "hito": 2,
        "grafica": True,
        "titulo": "Newton-Raphson",
        "resumen": "Usa la derivada simbólica: x_(n+1) = x_n − f/f'.",
        "descripcion": "Deriva f(x) automáticamente y avanza por la tangente en cada punto. Converge rápido cuando la derivada no se anula cerca de la raíz.",
        "funcion": newton.ejecutar,
        "campos": [
            {"nombre": "f", "etiqueta": "f(x)", "valor": "x**3 + 4*x**2 - 10", "texto": True},
            {"nombre": "x0", "etiqueta": "x0", "valor": "1.5"},
            CAMPO_TOL, CAMPO_ITER,
        ],
        "columnas": [["n", "n"], ["xi", "x_n"], ["fxi", "f(x_n)"], ["dfxi", "f'(x_n)"], ["xn", "x_(n+1)"], ["error", "error"]],
        "ggb": "f",
    },
    "newton-segundo-orden": {
        "hito": 2,
        "grafica": True,
        "titulo": "Newton de segundo orden",
        "resumen": "Variante para raíces múltiples con f, f' y f''.",
        "descripcion": "Aplica x_(n+1) = x_n − f·f' / (f'² − f·f''). Es útil cuando la raíz es múltiple y el método clásico converge lento.",
        "funcion": newton2.ejecutar,
        "campos": [
            {"nombre": "f", "etiqueta": "f(x)", "valor": "(x-1)**2 * (x+3)", "texto": True},
            {"nombre": "x0", "etiqueta": "x0", "valor": "0.5"},
            CAMPO_TOL, CAMPO_ITER,
        ],
        "columnas": [["n", "n"], ["xi", "x_n"], ["fxi", "f(x_n)"], ["dfxi", "f'(x_n)"], ["d2fxi", "f''(x_n)"], ["xn", "x_(n+1)"], ["error", "error"]],
        "ggb": "f",
    },
}

SISTEMAS = {
    "gauss": {
        "hito": 3,
        "titulo": "Gauss con pivoteo",
        "resumen": "Eliminación hacia adelante con pivoteo parcial y sustitución regresiva.",
        "descripcion": "Triangulariza la matriz aumentada eligiendo en cada columna el pivote de mayor valor absoluto, y luego resuelve por sustitución hacia atrás. Muestra cada paso.",
        "funcion": lineales.gauss_pivoteo,
        "iterativo": False,
        "ejemplo": {"A": [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], "b": [8, -11, -3]},
    },
    "gauss-jordan": {
        "hito": 3,
        "titulo": "Gauss-Jordan con pivoteo",
        "resumen": "Reduce la matriz aumentada hasta la identidad con pivoteo parcial.",
        "descripcion": "Normaliza cada pivote a 1 y elimina arriba y abajo, de modo que la última columna es directamente la solución.",
        "funcion": lineales.gauss_jordan_pivoteo,
        "iterativo": False,
        "ejemplo": {"A": [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], "b": [8, -11, -3]},
    },
    "jacobi": {
        "hito": 3,
        "titulo": "Jacobi",
        "resumen": "Método iterativo que despeja cada incógnita con los valores anteriores.",
        "descripcion": "Parte de un vector inicial y actualiza todas las componentes a la vez. Converge si la matriz es estrictamente diagonal dominante.",
        "funcion": lineales.jacobi,
        "iterativo": True,
        "ejemplo": {"A": [[10, -1, 2], [-1, 11, -1], [2, -1, 10]], "b": [6, 25, -11]},
    },
    "gauss-seidel": {
        "hito": 4,
        "titulo": "Gauss-Seidel",
        "resumen": "Iterativo como Jacobi, pero usa de inmediato los valores recién calculados.",
        "descripcion": "Parte de un vector inicial y actualiza las componentes una por una, reutilizando en la misma iteración los valores ya actualizados. Suele converger más rápido que Jacobi.",
        "funcion": lineales.gauss_seidel,
        "iterativo": True,
        "ejemplo": {"A": [[10, -1, 2], [-1, 11, -1], [2, -1, 10]], "b": [6, 25, -11]},
    },
}

DATOS_XY = {"titulo": "Puntos (x, y)", "columnas": ["x", "y"], "minimo": 2, "indice": False}
CAMPO_X_INTERP = {"nombre": "x", "etiqueta": "x a interpolar", "valor": "2.5"}
CAMPO_X_PROY = {"nombre": "x_proyectar", "etiqueta": "x a proyectar (opcional)", "valor": "6"}

GENERICOS = {
    "redondeo-truncamiento": {
        "hito": 4,
        "seccion": "Aproximación",
        "titulo": "Redondeo y truncamiento",
        "resumen": "Compara el error al redondear y al truncar un número a k dígitos.",
        "descripcion": "Limita un número a una cantidad de decimales o de cifras significativas de dos maneras, redondeando y truncando, y compara el error absoluto, relativo y porcentual de cada una.",
        "funcion": aproximacion.redondeo_truncamiento,
        "datos": None,
        "campos": [
            {"nombre": "numero", "etiqueta": "número", "valor": "3.14159265", "texto": True},
            {"nombre": "cantidad", "etiqueta": "cantidad k", "valor": "3"},
            {"nombre": "tipo", "etiqueta": "tipo", "opciones": [["decimales", "Decimales"], ["cifras", "Cifras significativas"]]},
        ],
    },
    "taylor": {
        "hito": 4,
        "seccion": "Aproximación",
        "titulo": "Desarrollo de Taylor",
        "resumen": "Aproxima f(x) con un polinomio de derivadas y mide el error de truncamiento.",
        "descripcion": "Construye el polinomio de Taylor de f centrado en a, lo evalúa en x y muestra cada término, la suma parcial y cómo baja el error al agregar términos.",
        "funcion": aproximacion.taylor,
        "datos": None,
        "campos": [
            {"nombre": "f", "etiqueta": "f(x)", "valor": "exp(x)", "texto": True},
            {"nombre": "a", "etiqueta": "centro a", "valor": "0"},
            {"nombre": "n", "etiqueta": "orden n", "valor": "4"},
            {"nombre": "x", "etiqueta": "x a evaluar", "valor": "0.5"},
        ],
    },
    "interpolacion-lineal": {
        "hito": 4,
        "seccion": "Interpolación",
        "titulo": "Interpolación lineal",
        "resumen": "Estima un valor sobre la recta que une dos puntos consecutivos.",
        "descripcion": "Busca los dos puntos que encierran a x y calcula el valor interpolado sobre la recta que los une.",
        "funcion": interpolacion.lineal,
        "datos": {**DATOS_XY, "filas": [[1, 0], [2, 0.6931], [3, 1.0986], [4, 1.3863], [5, 1.6094]]},
        "campos": [CAMPO_X_INTERP],
    },
    "newton-adelante": {
        "hito": 4,
        "seccion": "Interpolación",
        "titulo": "Newton hacia adelante",
        "resumen": "Interpola con diferencias finitas hacia adelante en datos igualmente espaciados.",
        "descripcion": "Construye la tabla de diferencias finitas y evalúa el polinomio de Newton hacia adelante. Los valores de x deben estar igualmente espaciados.",
        "funcion": interpolacion.newton_adelante,
        "datos": {**DATOS_XY, "filas": [[1, 0], [2, 0.6931], [3, 1.0986], [4, 1.3863], [5, 1.6094]]},
        "campos": [CAMPO_X_INTERP],
    },
    "lagrange": {
        "hito": 4,
        "seccion": "Interpolación",
        "titulo": "Polinomio de Lagrange",
        "resumen": "Suma de polinomios base que pasan por todos los puntos.",
        "descripcion": "Calcula cada polinomio base L_i(x), los combina con los valores y_i y entrega el valor interpolado junto con el polinomio resultante.",
        "funcion": interpolacion.lagrange,
        "datos": {**DATOS_XY, "filas": [[1, 0], [2, 0.6931], [3, 1.0986], [4, 1.3863], [5, 1.6094]]},
        "campos": [CAMPO_X_INTERP],
    },
    "diferencias-divididas": {
        "hito": 4,
        "seccion": "Interpolación",
        "titulo": "Diferencias divididas",
        "resumen": "Polinomio de Newton con tabla de diferencias divididas, admite espaciado irregular.",
        "descripcion": "Arma la tabla de diferencias divididas, toma la primera fila como coeficientes y evalúa el polinomio de Newton en x.",
        "funcion": interpolacion.diferencias_divididas,
        "datos": {**DATOS_XY, "filas": [[1, 0], [2, 0.6931], [3, 1.0986], [4, 1.3863], [5, 1.6094]]},
        "campos": [CAMPO_X_INTERP],
    },
    "regresion-lineal": {
        "hito": 4,
        "seccion": "Proyecciones",
        "titulo": "Proyección lineal",
        "resumen": "Recta de mínimos cuadrados y = a + b·x.",
        "descripcion": "Ajusta una recta a los datos por mínimos cuadrados, muestra las sumas, el coeficiente de correlación y proyecta el valor que pidas.",
        "funcion": proyecciones.lineal,
        "datos": {**DATOS_XY, "filas": [[1, 2.1], [2, 3.9], [3, 6.2], [4, 7.8], [5, 10.1]]},
        "campos": [CAMPO_X_PROY],
    },
    "regresion-exponencial": {
        "hito": 4,
        "seccion": "Proyecciones",
        "titulo": "Proyección exponencial",
        "resumen": "Ajuste y = a·e^(b·x) linealizando con logaritmo natural.",
        "descripcion": "Linealiza el modelo con ln y, hace regresión lineal y recupera los parámetros a y b. Requiere valores de y positivos.",
        "funcion": proyecciones.exponencial,
        "datos": {**DATOS_XY, "filas": [[0, 2], [1, 3.1], [2, 4.9], [3, 7.6], [4, 12]]},
        "campos": [{**CAMPO_X_PROY, "valor": "5"}],
    },
    "regresion-potencial": {
        "hito": 4,
        "seccion": "Proyecciones",
        "titulo": "Proyección potencial",
        "resumen": "Ajuste y = a·x^b linealizando con logaritmos.",
        "descripcion": "Aplica logaritmo natural a x y a y, hace regresión lineal y recupera a y b. Requiere valores positivos.",
        "funcion": proyecciones.potencial,
        "datos": {**DATOS_XY, "filas": [[1, 2], [2, 5.7], [3, 10.4], [4, 16.1], [5, 22.4]]},
        "campos": [CAMPO_X_PROY],
    },
    "regresion-cuadratica": {
        "hito": 4,
        "seccion": "Proyecciones",
        "titulo": "Proyección cuadrática",
        "resumen": "Parábola de mínimos cuadrados y = a + b·x + c·x².",
        "descripcion": "Plantea las ecuaciones normales con las sumas de potencias de x, las resuelve y proyecta con la parábola ajustada.",
        "funcion": proyecciones.cuadratica,
        "datos": {**DATOS_XY, "filas": [[0, 1.1], [1, 2.3], [2, 5.4], [3, 8.2], [4, 14.1], [5, 18.9]]},
        "campos": [CAMPO_X_PROY],
    },
    "series-de-tiempo": {
        "hito": 4,
        "seccion": "Proyecciones",
        "titulo": "Series de tiempo",
        "resumen": "Pronostica el siguiente periodo con promedio móvil o suavizamiento exponencial.",
        "descripcion": "Calcula pronósticos y muestra cada sustitución numérica. Permite comparar automáticamente k o α según MAD, MSE o MAPE; informa r de Pearson por separado.",
        "funcion": proyecciones.series_tiempo,
        "datos": {
            "titulo": "Valores de la serie (en orden)",
            "columnas": ["valor"],
            "minimo": 3,
            "indice": True,
            "filas": [[120], [132], [128], [141], [150], [147], [158], [165]],
        },
        "campos": [
            {"nombre": "metodo", "etiqueta": "método", "opciones": [["promedio-movil", "Promedio móvil"], ["suavizamiento", "Suavizamiento exponencial"]]},
            {"nombre": "parametro", "etiqueta": "periodo k / factor α", "valor": "3"},
            {"nombre": "optimizar", "etiqueta": "selección automática", "opciones": [["false", "Usar parámetro manual"], ["true", "Buscar mejor parámetro automáticamente"]]},
            {"nombre": "criterio", "etiqueta": "elegir mejor según", "opciones": [["MAD", "Menor MAD"], ["MSE", "Menor MSE"], ["MAPE", "Menor MAPE"]]},
        ],
    },
}

ERRORES = {
    "slug": "errores",
    "titulo": "Errores de redondeo",
    "resumen": "Conversión de base, error absoluto, relativo y propagado.",
    "hito": 2,
}


def _items(diccionario, hito, seccion=None):
    return [
        {"slug": slug, "titulo": c["titulo"], "ruta": f"/hito{hito}/{slug}", "resumen": c["resumen"]}
        for slug, c in diccionario.items()
        if c["hito"] == hito and (seccion is None or c.get("seccion") == seccion)
    ]


def _construir_hitos():
    errores = {
        "slug": ERRORES["slug"],
        "titulo": ERRORES["titulo"],
        "ruta": "/hito2/errores",
        "resumen": ERRORES["resumen"],
    }
    return [
        {
            "numero": 2,
            "nombre": "Hito 2",
            "ruta": "/hito2",
            "resumen": "Errores de redondeo, punto fijo y las dos versiones de Newton-Raphson, con gráfica en GeoGebra.",
            "secciones": [
                {"nombre": "Aproximación", "items": [errores]},
                {"nombre": "Raíces de ecuaciones", "items": _items(RAICES, 2)},
            ],
        },
        {
            "numero": 3,
            "nombre": "Hito 3",
            "ruta": "/hito3",
            "resumen": "Bisección, falsa posición y secante, más Gauss, Gauss-Jordan y Jacobi para sistemas lineales, con tablas e iteraciones.",
            "secciones": [
                {"nombre": "Raíces de ecuaciones", "items": _items(RAICES, 3)},
                {"nombre": "Sistemas lineales", "items": _items(SISTEMAS, 3)},
            ],
        },
        {
            "numero": 4,
            "nombre": "Hito 4",
            "ruta": "/hito4",
            "resumen": "Redondeo y truncamiento, Taylor, Gauss-Seidel, interpolación y proyecciones, con tablas, pasos y proyecciones.",
            "secciones": [
                {"nombre": "Aproximación", "items": _items(GENERICOS, 4, "Aproximación")},
                {"nombre": "Sistemas lineales", "items": _items(SISTEMAS, 4)},
                {"nombre": "Interpolación", "items": _items(GENERICOS, 4, "Interpolación")},
                {"nombre": "Proyecciones", "items": _items(GENERICOS, 4, "Proyecciones")},
            ],
        },
    ]


HITOS = _construir_hitos()


@app.context_processor
def inyectar_navegacion():
    return {"hitos": HITOS}


def respuesta_api(funcion):
    try:
        return jsonify({"ok": True, **funcion()})
    except Exception as err:
        return jsonify({"ok": False, "mensaje": str(err)}), 400


def convertir_parametros(cuerpo):
    datos = {}
    for clave, valor in cuerpo.items():
        if clave in ("f", "g"):
            datos[clave] = valor
        elif clave == "iter_max":
            if valor not in (None, ""):
                datos[clave] = int(valor)
        elif valor not in (None, ""):
            datos[clave] = float(valor)
    return datos


@app.route("/")
def vista_inicio():
    return render_template("inicio.html", seccion="inicio")


@app.route("/hito<int:numero>")
def vista_hito(numero):
    hito = next((h for h in HITOS if h["numero"] == numero), None)
    if hito is None:
        abort(404)
    return render_template("hito.html", seccion=f"hito{numero}", hito=hito)


@app.route("/hito2/errores")
def vista_errores():
    return render_template("redondeo.html", seccion="errores", hito=2, ayuda=AYUDA.get("errores"))


@app.route("/hito<int:numero>/<slug>")
def vista_metodo(numero, slug):
    ayuda = AYUDA.get(slug)
    config = RAICES.get(slug)
    if config is not None and config["hito"] == numero:
        return render_template("raiz.html", seccion=slug, slug=slug, m=config, ayuda=ayuda)
    config = SISTEMAS.get(slug)
    if config is not None and config["hito"] == numero:
        return render_template("sistema.html", seccion=slug, slug=slug, m=config, ayuda=ayuda)
    config = GENERICOS.get(slug)
    if config is not None and config["hito"] == numero:
        return render_template("generico.html", seccion=slug, slug=slug, m=config, ayuda=ayuda)
    abort(404)


@app.route("/api/raices/<slug>", methods=["POST"])
def api_raiz(slug):
    config = RAICES.get(slug)
    if config is None:
        abort(404)
    cuerpo = request.get_json(force=True)
    return respuesta_api(lambda: config["funcion"](**convertir_parametros(cuerpo)))


@app.route("/api/sistemas/<slug>", methods=["POST"])
def api_sistema(slug):
    config = SISTEMAS.get(slug)
    if config is None:
        abort(404)
    cuerpo = request.get_json(force=True)

    def ejecutar():
        A = cuerpo["A"]
        b = cuerpo["b"]
        if config["iterativo"]:
            return config["funcion"](
                A, b,
                cuerpo.get("x0"),
                float(cuerpo.get("tol") or 1e-6),
                int(cuerpo.get("iter_max") or 50),
            )
        return config["funcion"](A, b)

    return respuesta_api(ejecutar)


@app.route("/api/generico/<slug>", methods=["POST"])
def api_generico(slug):
    config = GENERICOS.get(slug)
    if config is None:
        abort(404)
    cuerpo = request.get_json(force=True)
    def ejecutar():
        resultado = config["funcion"](cuerpo)
        if config["hito"] == 4:
            try:
                resultado["graficas"] = graficas.construir(slug, cuerpo, resultado)
            except (ValueError, OverflowError, ZeroDivisionError, TypeError):
                resultado["graficas"] = []
        return resultado
    return respuesta_api(ejecutar)


@app.route("/api/base", methods=["POST"])
def api_base():
    cuerpo = request.get_json(force=True)
    return respuesta_api(lambda: redondeo.convertir_base(int(cuerpo["numero"]), int(cuerpo["base"])))


@app.route("/api/comparar", methods=["POST"])
def api_comparar():
    cuerpo = request.get_json(force=True)
    return respuesta_api(lambda: redondeo.comparar_valores(float(cuerpo["real"]), float(cuerpo["aprox"])))


@app.route("/api/error-funcion", methods=["POST"])
def api_error_funcion():
    cuerpo = request.get_json(force=True)
    return respuesta_api(lambda: redondeo.error_en_funcion(
        cuerpo["f"], float(cuerpo["real"]), float(cuerpo["aprox"])
    ))


if __name__ == "__main__":
    app.run(debug=True)
