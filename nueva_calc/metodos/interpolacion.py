import math

import numpy as np

from .nucleo import f6, leer_filas, polinomio_texto


def _puntos(cuerpo, minimo=2):
    filas = leer_filas(cuerpo, 2, minimo)
    filas.sort(key=lambda p: p[0])
    xs = [p[0] for p in filas]
    ys = [p[1] for p in filas]
    if len(set(xs)) != len(xs):
        raise ValueError("Los valores de x deben ser distintos")
    return xs, ys


def _objetivo(cuerpo):
    try:
        return float(cuerpo["x"])
    except (KeyError, ValueError):
        raise ValueError("Escribe el valor de x a interpolar")


def _fuera_de_rango(xs, x):
    if x < xs[0] or x > xs[-1]:
        return "El valor x está fuera del rango de los datos: es extrapolación y la estimación es menos confiable"
    return None


def lineal(cuerpo):
    xs, ys = _puntos(cuerpo)
    x = _objetivo(cuerpo)

    i = 0
    for k in range(len(xs) - 1):
        if xs[k] <= x <= xs[k + 1]:
            i = k
            break
    else:
        i = 0 if x < xs[0] else len(xs) - 2

    x0, x1, y0, y1 = xs[i], xs[i + 1], ys[i], ys[i + 1]
    m = (y1 - y0) / (x1 - x0)
    y = y0 + m * (x - x0)

    return {
        "resultados": [
            ["x a interpolar", f6(x)],
            ["pendiente m", f6(m)],
            ["y interpolado", f6(y)],
        ],
        "tablas": [{
            "titulo": "Puntos utilizados",
            "columnas": ["punto", "x", "y"],
            "filas": [["(x0, y0)", f6(x0), f6(y0)], ["(x1, y1)", f6(x1), f6(y1)]],
        }],
        "pasos": [
            {"titulo": "Pendiente", "detalle": f"m = (y1 − y0) / (x1 − x0) = ({f6(y1)} − {f6(y0)}) / ({f6(x1)} − {f6(x0)}) = {f6(m)}"},
            {"titulo": "Valor interpolado", "detalle": f"y = y0 + m·(x − x0) = {f6(y0)} + {f6(m)}·({f6(x)} − {f6(x0)}) = {f6(y)}"},
        ],
        "aviso": _fuera_de_rango(xs, x),
        "info": "Se usan los dos puntos consecutivos que encierran a x.",
    }


def newton_adelante(cuerpo):
    xs, ys = _puntos(cuerpo)
    x = _objetivo(cuerpo)
    n = len(xs)

    h = xs[1] - xs[0]
    for i in range(1, n):
        if abs((xs[i] - xs[i - 1]) - h) > 1e-8 * max(1.0, abs(h)):
            raise ValueError("Los valores de x deben estar igualmente espaciados")

    columnas = [ys[:]]
    for k in range(1, n):
        previa = columnas[-1]
        columnas.append([previa[i + 1] - previa[i] for i in range(len(previa) - 1)])

    s = (x - xs[0]) / h
    suma = 0.0
    coef_s = 1.0
    filas_terminos = []
    for k in range(n):
        if k > 0:
            coef_s *= (s - (k - 1)) / k
        delta = columnas[k][0]
        termino = coef_s * delta
        suma += termino
        filas_terminos.append([str(k), f6(delta), f6(coef_s), f6(termino), f6(suma)])

    cabecera = ["x", "y"] + [f"Δ^{k}y" if k > 1 else "Δy" for k in range(1, n)]
    filas_dif = []
    for i in range(n):
        fila = [f6(xs[i])]
        for k in range(n):
            fila.append(f6(columnas[k][i]) if i < len(columnas[k]) else None)
        filas_dif.append(fila)

    return {
        "resultados": [
            ["paso h", f6(h)],
            ["s = (x − x0) / h", f6(s)],
            ["P(x) interpolado", f6(suma)],
        ],
        "tablas": [
            {"titulo": "Tabla de diferencias finitas", "columnas": cabecera, "filas": filas_dif},
            {"titulo": "Términos de la fórmula", "columnas": ["k", "Δ^k y0", "s(s−1)…(s−k+1) / k!", "término", "suma parcial"], "filas": filas_terminos},
        ],
        "pasos": [{"titulo": "Fórmula", "detalle": "P(x) = y0 + s·Δy0 + s(s−1)/2!·Δ²y0 + s(s−1)(s−2)/3!·Δ³y0 + …"}],
        "aviso": _fuera_de_rango(xs, x),
        "info": "Requiere x igualmente espaciados; es más preciso cuando x está cerca del inicio de la tabla.",
    }


def lagrange(cuerpo):
    xs, ys = _puntos(cuerpo)
    x = _objetivo(cuerpo)
    n = len(xs)

    filas = []
    suma = 0.0
    polinomio = np.zeros(n)
    detalles = []
    for i in range(n):
        numerador = 1.0
        denominador = 1.0
        raices = []
        for j in range(n):
            if j != i:
                numerador *= (x - xs[j])
                denominador *= (xs[i] - xs[j])
                raices.append(xs[j])
        li = numerador / denominador
        suma += ys[i] * li
        filas.append([str(i), f6(xs[i]), f6(ys[i]), f6(li), f6(ys[i] * li)])
        base = np.poly(raices) if raices else np.array([1.0])
        polinomio = np.polyadd(polinomio, ys[i] / denominador * base)
        detalles.append(f"L_{i}(x) = Π (x − x_j)/(x_{i} − x_j), j ≠ {i}  →  {f6(li)}")

    coeficientes = np.atleast_1d(polinomio).tolist()

    return {
        "resultados": [
            ["x a interpolar", f6(x)],
            ["P(x) interpolado", f6(suma)],
            ["grado del polinomio", str(n - 1)],
        ],
        "tablas": [{
            "titulo": "Polinomios base y términos",
            "columnas": ["i", "x_i", "y_i", "L_i(x)", "y_i · L_i(x)"],
            "filas": filas,
        }],
        "pasos": [
            {"titulo": "Polinomio resultante", "detalle": f"P(x) = {polinomio_texto(coeficientes)}"},
            {"titulo": "Bases evaluadas", "detalle": "\n".join(detalles)},
        ],
        "aviso": _fuera_de_rango(xs, x),
        "info": "P(x) = Σ y_i · L_i(x); no requiere espaciado uniforme.",
    }


def diferencias_divididas(cuerpo):
    xs, ys = _puntos(cuerpo)
    x = _objetivo(cuerpo)
    n = len(xs)

    columnas = [ys[:]]
    for k in range(1, n):
        previa = columnas[-1]
        columnas.append([(previa[i + 1] - previa[i]) / (xs[i + k] - xs[i]) for i in range(len(previa) - 1)])

    coeficientes = [columnas[k][0] for k in range(n)]

    suma = 0.0
    producto = 1.0
    filas_terminos = []
    polinomio = np.array([0.0])
    for k in range(n):
        if k > 0:
            producto *= (x - xs[k - 1])
        termino = coeficientes[k] * producto
        suma += termino
        filas_terminos.append([str(k), f6(coeficientes[k]), f6(producto), f6(termino), f6(suma)])
        base = np.poly(xs[:k]) if k > 0 else np.array([1.0])
        polinomio = np.polyadd(polinomio, coeficientes[k] * base)

    cabecera = ["x", "f[x_i]"] + [f"orden {k}" for k in range(1, n)]
    filas_dif = []
    for i in range(n):
        fila = [f6(xs[i])]
        for k in range(n):
            fila.append(f6(columnas[k][i]) if i < len(columnas[k]) else None)
        filas_dif.append(fila)

    return {
        "resultados": [
            ["x a interpolar", f6(x)],
            ["P(x) interpolado", f6(suma)],
            ["grado del polinomio", str(n - 1)],
        ],
        "tablas": [
            {"titulo": "Tabla de diferencias divididas", "columnas": cabecera, "filas": filas_dif},
            {"titulo": "Evaluación del polinomio de Newton", "columnas": ["k", "coeficiente", "(x−x0)…(x−x_(k−1))", "término", "suma parcial"], "filas": filas_terminos},
        ],
        "pasos": [{"titulo": "Polinomio resultante", "detalle": f"P(x) = {polinomio_texto(np.atleast_1d(polinomio).tolist())}"}],
        "aviso": _fuera_de_rango(xs, x),
        "info": "Los coeficientes son la primera fila de la tabla: f[x0], f[x0,x1], f[x0,x1,x2], …",
    }
