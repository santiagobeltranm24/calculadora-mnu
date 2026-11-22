from .nucleo import parsear, numerica, evaluar, resultado


def ejecutar(f, x0, x1, tol=1e-6, iter_max=50):
    expr = parsear(f)
    fn = numerica(expr)
    xa = float(x0)
    xb = float(x1)
    if xa == xb:
        raise ValueError("x0 y x1 deben ser distintos")

    fa = evaluar(fn, xa)
    fb = evaluar(fn, xb)
    puntos = [[xa, fa], [xb, fb]]
    tabla = []
    convergio = False

    for paso in range(1, int(iter_max) + 1):
        denominador = fb - fa
        if denominador == 0:
            raise ValueError("f(x_n) = f(x_(n−1)): la secante es horizontal")
        xn = xb - fb * (xb - xa) / denominador
        fxn = evaluar(fn, xn)
        error = abs(xn - xb)
        tabla.append({"n": paso, "xa": xa, "xb": xb, "fa": fa, "fb": fb, "xn": xn, "error": error})
        puntos.append([xn, fxn])
        xa, fa = xb, fb
        xb, fb = xn, fxn
        if error <= tol:
            convergio = True
            break

    return resultado(
        convergio, xb, tabla, expr, puntos,
        info="x_(n+1) = x_n − f(x_n)·(x_n − x_(n−1)) / (f(x_n) − f(x_(n−1)))",
    )
