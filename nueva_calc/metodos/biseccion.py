from .nucleo import parsear, numerica, evaluar, resultado


def ejecutar(f, a, b, tol=1e-6, iter_max=50):
    expr = parsear(f)
    fn = numerica(expr)
    a = float(a)
    b = float(b)
    if a >= b:
        raise ValueError("Debe cumplirse a < b")

    fa = evaluar(fn, a)
    fb = evaluar(fn, b)
    puntos = [[a, fa], [b, fb]]

    if fa == 0 or fb == 0:
        raiz = a if fa == 0 else b
        return resultado(True, raiz, [], expr, puntos, aviso="Un extremo del intervalo ya es raíz")
    if fa * fb > 0:
        raise ValueError("f(a) y f(b) deben tener signos opuestos")

    tabla = []
    convergio = False
    c = a

    for paso in range(1, int(iter_max) + 1):
        c = (a + b) / 2
        fc = evaluar(fn, c)
        error = (b - a) / 2
        tabla.append({"n": paso, "a": a, "b": b, "c": c, "fc": fc, "error": error})
        puntos.append([c, fc])
        if fc == 0 or error <= tol:
            convergio = True
            break
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc

    return resultado(convergio, c, tabla, expr, puntos, info="error = (b − a) / 2 en cada iteración")
