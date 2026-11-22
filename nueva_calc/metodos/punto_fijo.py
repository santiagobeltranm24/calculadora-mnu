from .nucleo import parsear, numerica, evaluar, resultado, VAR
import sympy as sp


def ejecutar(g, x0, tol=1e-6, iter_max=50):
    expr = parsear(g)
    fn = numerica(expr)
    derivada = sp.diff(expr, VAR)
    dfn = numerica(derivada)

    xi = float(x0)
    tabla = []
    puntos = [[xi, evaluar(fn, xi)]]
    convergio = False

    aviso = None
    try:
        pendiente = abs(evaluar(dfn, xi))
        if pendiente >= 1:
            aviso = f"|g'(x0)| = {pendiente:.4f} ≥ 1: la convergencia no está garantizada"
    except ValueError:
        pass

    for paso in range(1, int(iter_max) + 1):
        xn = evaluar(fn, xi)
        error = abs(xn - xi)
        tabla.append({"n": paso, "xi": xi, "gxi": xn, "error": error})
        puntos.append([xi, xn])
        xi = xn
        if error <= tol:
            convergio = True
            break

    return resultado(
        convergio,
        xi,
        tabla,
        expr,
        puntos,
        aviso=aviso,
        info=f"g'(x) = {sp.sstr(derivada)}",
        extras=["y=x"],
    )
