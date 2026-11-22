import math
import re

import numpy as np
import sympy as sp

VAR = sp.Symbol("x")

CONTEXTO = {
    "x": VAR,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "exp": sp.exp,
    "log": sp.log,
    "ln": sp.log,
    "sqrt": sp.sqrt,
    "pi": sp.pi,
    "E": sp.E,
    "Abs": sp.Abs,
    "abs": sp.Abs,
}

ALFABETO = "0123456789ABCDEF"


def parsear(expresion):
    return sp.sympify(expresion, locals=CONTEXTO)


def numerica(expr):
    return sp.lambdify(VAR, expr, "numpy")


def evaluar(funcion, valor):
    try:
        with np.errstate(all="ignore"):
            resultado = float(funcion(valor))
    except ZeroDivisionError:
        raise ValueError(f"División entre cero al evaluar en x = {valor}")
    except Exception as err:
        raise ValueError(f"No se pudo evaluar en x = {valor}: {err}")
    if not math.isfinite(resultado):
        raise ValueError(f"La función no está definida o diverge en x = {valor}")
    return resultado


def a_geogebra(expr):
    texto = sp.sstr(expr).replace("**", "^")
    texto = texto.replace("Abs(", "abs(")
    return re.sub(r"\bE\b", "e", texto)


def resultado(convergio, raiz, tabla, expr, puntos, aviso=None, info=None, extras=None):
    return {
        "convergio": bool(convergio),
        "raiz": raiz,
        "iteraciones": len(tabla),
        "tabla": tabla,
        "expresion_ggb": a_geogebra(expr),
        "puntos": puntos,
        "aviso": aviso,
        "info": info,
        "extras": extras or [],
    }


def entero_a_base(numero, base):
    if base < 2 or base > 16:
        raise ValueError("La base debe estar entre 2 y 16")
    if numero == 0:
        return "0"
    negativo = numero < 0
    n = abs(numero)
    digitos = []
    while n > 0:
        n, resto = divmod(n, base)
        digitos.append(ALFABETO[resto])
    digitos.reverse()
    texto = "".join(digitos)
    return "-" + texto if negativo else texto


def f6(valor):
    if valor is None:
        return None
    if valor == 0:
        return "0.000000"
    if abs(valor) < 1e-6:
        return f"{valor:.2e}"
    return f"{valor:.6f}"


def polinomio_texto(coeficientes):
    grado_max = len(coeficientes) - 1
    partes = []
    for i, c in enumerate(coeficientes):
        grado = grado_max - i
        if abs(c) < 1e-12:
            continue
        magnitud = f"{abs(c):.6g}"
        if grado == 0:
            cuerpo = magnitud
        elif grado == 1:
            cuerpo = f"{magnitud}·x"
        else:
            cuerpo = f"{magnitud}·x^{grado}"
        partes.append(("-" if c < 0 else "+", cuerpo))
    if not partes:
        return "0"
    texto = ("-" if partes[0][0] == "-" else "") + partes[0][1]
    for signo, cuerpo in partes[1:]:
        texto += f" {signo} {cuerpo}"
    return texto


def leer_filas(cuerpo, columnas, minimo):
    filas = []
    for fila in cuerpo.get("puntos", []):
        celdas = [str(v).strip() for v in fila]
        if all(c == "" for c in celdas):
            continue
        if any(c == "" for c in celdas) or len(celdas) != columnas:
            raise ValueError("Hay filas incompletas en la tabla de datos")
        try:
            filas.append([float(c) for c in celdas])
        except ValueError:
            raise ValueError("La tabla solo admite valores numéricos")
    if len(filas) < minimo:
        raise ValueError(f"Se necesitan al menos {minimo} filas con datos")
    return filas
