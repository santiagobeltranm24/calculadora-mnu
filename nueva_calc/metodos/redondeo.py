from .nucleo import parsear, numerica, entero_a_base, VAR
import sympy as sp


def convertir_base(numero, base):
    return {"convertido": entero_a_base(numero, base)}


def comparar_valores(real, aprox):
    if real == 0:
        raise ValueError("El valor real no puede ser cero")
    ea = abs(real - aprox)
    er = ea / abs(real)
    ep = er * 100
    cifras = 0
    limite = er
    while limite < 5 * (10 ** (-(cifras + 1))):
        cifras += 1
    return {
        "ea": ea,
        "er": er,
        "ep": ep,
        "cifras": cifras,
    }


def error_en_funcion(f_texto, real, aprox):
    expr = parsear(f_texto)
    derivada = sp.diff(expr, VAR)
    f = numerica(expr)
    df = numerica(derivada)

    f_real = float(f(real))
    f_aprox = float(f(aprox))
    base = comparar_valores(f_real, f_aprox)

    pendiente = float(df(real))
    ea_lineal = abs(pendiente) * abs(real - aprox)

    return {
        "f_real": f_real,
        "f_aprox": f_aprox,
        "derivada_txt": sp.sstr(derivada),
        "pendiente": pendiente,
        "ea_estimado": ea_lineal,
        **base,
    }
