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
    c_ant = None

    for paso in range(1, int(iter_max) + 1):
        denominador = fb - fa
        if denominador == 0:
            raise ValueError("f(a) y f(b) son iguales, no se puede trazar la secante")
        c = (a * fb - b * fa) / denominador
        fc = evaluar(fn, c)
        error = None if c_ant is None else abs(c - c_ant)
        tabla.append({"n": paso, "a": a, "b": b, "c": c, "fc": fc, "error": error})
        puntos.append([c, fc])
        if fc == 0 or (error is not None and error <= tol):
            convergio = True
            break
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
        c_ant = c

    return resultado(
        convergio, c, tabla, expr, puntos,
        info="c = (a·f(b) − b·f(a)) / (f(b) − f(a)); error = |c_n − c_(n−1)|",
    )
