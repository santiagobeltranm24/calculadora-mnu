from .nucleo import parsear, numerica, evaluar, resultado, VAR
import sympy as sp


def ejecutar(f, x0, tol=1e-6, iter_max=50):
    expr = parsear(f)
    derivada = sp.diff(expr, VAR)
    segunda = sp.diff(derivada, VAR)
    fn = numerica(expr)
    dfn = numerica(derivada)
    d2fn = numerica(segunda)

    xi = float(x0)
    tabla = []
    puntos = [[xi, evaluar(fn, xi)]]
    convergio = False

    for paso in range(1, int(iter_max) + 1):
        fxi = evaluar(fn, xi)
        dfxi = evaluar(dfn, xi)
        d2fxi = evaluar(d2fn, xi)
        denominador = dfxi ** 2 - fxi * d2fxi
        if denominador == 0:
            raise ValueError(f"El denominador se anula en x = {xi}")
        xn = xi - (fxi * dfxi) / denominador
        error = abs(xn - xi)
        tabla.append({
            "n": paso, "xi": xi, "fxi": fxi, "dfxi": dfxi,
            "d2fxi": d2fxi, "xn": xn, "error": error,
        })
        puntos.append([xn, evaluar(fn, xn)])
        xi = xn
        if error <= tol:
            convergio = True
            break

    return resultado(
        convergio, xi, tabla, expr, puntos,
        info=f"f'(x) = {sp.sstr(derivada)}   ·   f''(x) = {sp.sstr(segunda)}",
    )
