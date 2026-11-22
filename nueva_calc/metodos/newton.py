from .nucleo import parsear, numerica, evaluar, resultado, VAR
import sympy as sp


def ejecutar(f, x0, tol=1e-6, iter_max=50):
    expr = parsear(f)
    derivada = sp.diff(expr, VAR)
    fn = numerica(expr)
    dfn = numerica(derivada)

    xi = float(x0)
    tabla = []
    puntos = [[xi, evaluar(fn, xi)]]
    convergio = False

    for paso in range(1, int(iter_max) + 1):
        fxi = evaluar(fn, xi)
        dfxi = evaluar(dfn, xi)
        if dfxi == 0:
            raise ValueError(f"La derivada se anula en x = {xi}")
        xn = xi - fxi / dfxi
        error = abs(xn - xi)
        tabla.append({"n": paso, "xi": xi, "fxi": fxi, "dfxi": dfxi, "xn": xn, "error": error})
        puntos.append([xn, evaluar(fn, xn)])
        xi = xn
        if error <= tol:
            convergio = True
            break

    return resultado(convergio, xi, tabla, expr, puntos, info=f"f'(x) = {sp.sstr(derivada)}")
