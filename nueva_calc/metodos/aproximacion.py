import math
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, InvalidOperation, localcontext

import sympy as sp

from .nucleo import VAR, evaluar, f6, numerica, parsear, polinomio_texto


def _cuantizar(valor, cantidad, tipo, modo):
    with localcontext() as ctx:
        ctx.prec = 80
        if tipo == "decimales":
            paso = Decimal(1).scaleb(-cantidad)
            return valor.quantize(paso, rounding=modo)
        if valor == 0:
            return valor
        exponente = valor.adjusted() - cantidad + 1
        return valor.quantize(Decimal(1).scaleb(exponente), rounding=modo)


def _errores(original, aproximado):
    ea = abs(original - aproximado)
    er = ea / abs(original) if original != 0 else Decimal(0)
    return float(ea), float(er), float(er * 100)


def redondeo_truncamiento(cuerpo):
    try:
        original = Decimal(str(cuerpo["numero"]).strip())
    except (InvalidOperation, KeyError):
        raise ValueError("Escribe un número válido")
    cantidad = int(cuerpo["cantidad"])
    tipo = cuerpo.get("tipo", "decimales")
    if cantidad < 0 or cantidad > 30:
        raise ValueError("La cantidad debe estar entre 0 y 30")
    if tipo == "cifras" and cantidad < 1:
        raise ValueError("Las cifras significativas deben ser al menos 1")

    redondeado = _cuantizar(original, cantidad, tipo, ROUND_HALF_UP)
    truncado = _cuantizar(original, cantidad, tipo, ROUND_DOWN)
    er_red = _errores(original, redondeado)
    er_tru = _errores(original, truncado)

    unidad = "decimales" if tipo == "decimales" else "cifras significativas"
    mejor = "el redondeo" if er_red[0] <= er_tru[0] else "el truncamiento"

    return {
        "resultados": [
            ["Número original", str(original)],
            [f"Redondeado a {cantidad} {unidad}", str(redondeado)],
            [f"Truncado a {cantidad} {unidad}", str(truncado)],
        ],
        "tablas": [{
            "titulo": "Comparación de errores",
            "columnas": ["método", "valor aproximado", "error absoluto", "error relativo", "error porcentual (%)"],
            "filas": [
                ["Redondeo", str(redondeado), f6(er_red[0]), f6(er_red[1]), f6(er_red[2])],
                ["Truncamiento", str(truncado), f6(er_tru[0]), f6(er_tru[1]), f6(er_tru[2])],
            ],
        }],
        "pasos": [
            {"titulo": "Truncamiento", "detalle": f"Se conservan {cantidad} {unidad} y se descartan los demás dígitos sin modificar los que quedan: {original} → {truncado}"},
            {"titulo": "Redondeo", "detalle": f"Si el primer dígito descartado es 5 o más, se suma 1 al último dígito conservado: {original} → {redondeado}"},
            {"titulo": "Errores", "detalle": "EA = |x − x*|,  ER = EA / |x|,  EP = ER · 100"},
        ],
        "aviso": None,
        "info": f"En este caso el menor error absoluto lo da {mejor}.",
    }


def taylor(cuerpo):
    expr = parsear(cuerpo["f"])
    a = float(cuerpo["a"])
    n = int(cuerpo["n"])
    x = float(cuerpo["x"])
    if n < 0 or n > 12:
        raise ValueError("El orden n debe estar entre 0 y 12")

    real = evaluar(numerica(expr), x)
    derivada = expr
    suma = 0.0
    filas = []
    coeficientes = []

    for k in range(n + 1):
        if k > 0:
            derivada = sp.diff(derivada, VAR)
        dk = evaluar(numerica(derivada), a)
        coef = dk / math.factorial(k)
        termino = coef * (x - a) ** k
        suma += termino
        ea = abs(real - suma)
        er = ea / abs(real) * 100 if real != 0 else None
        filas.append([str(k), f6(dk), f6(coef), f6(termino), f6(suma), f6(ea), f6(er)])
        coeficientes.append(coef)

    ea_final = abs(real - suma)
    er_final = ea_final / abs(real) * 100 if real != 0 else None

    base = "x" if a == 0 else f"(x − {a:g})"
    terminos = []
    for k, c in enumerate(coeficientes):
        if abs(c) < 1e-12:
            continue
        magnitud = f"{c:.6g}"
        if k == 0:
            terminos.append(magnitud)
        elif k == 1:
            terminos.append(f"{magnitud}·{base}")
        else:
            terminos.append(f"{magnitud}·{base}^{k}")
    polinomio = " + ".join(terminos).replace("+ -", "− ") if terminos else "0"

    return {
        "resultados": [
            ["f(x) real", f6(real)],
            [f"P_{n}(x) aproximado", f6(suma)],
            ["error absoluto", f6(ea_final)],
            ["error relativo (%)", f6(er_final) if er_final is not None else "—"],
        ],
        "tablas": [{
            "titulo": "Términos de la serie",
            "columnas": ["k", "f^(k)(a)", "f^(k)(a) / k!", "término", "P_k(x)", "error absoluto", "error relativo (%)"],
            "filas": filas,
        }],
        "pasos": [{"titulo": "Polinomio de Taylor", "detalle": f"P_{n}(x) = {polinomio}"}],
        "aviso": None,
        "info": "término_k = f^(k)(a) / k! · (x − a)^k; el error es |f(x) − P_k(x)|",
    }
