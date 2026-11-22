import math

EPS = 1e-12


def _preparar(A, b):
    n = len(A)
    if n < 2 or len(b) != n or any(len(fila) != n for fila in A):
        raise ValueError("La matriz debe ser cuadrada y b debe tener su misma dimensión")
    return [[float(v) for v in A[i]] + [float(b[i])] for i in range(n)]


def _copia(aum):
    return [fila[:] for fila in aum]


def _residuo(A, b, x):
    n = len(A)
    return max(abs(sum(float(A[i][j]) * x[j] for j in range(n)) - float(b[i])) for i in range(n))


def _pivotear(aum, k, n, pasos):
    p = max(range(k, n), key=lambda i: abs(aum[i][k]))
    if abs(aum[p][k]) < EPS:
        raise ValueError("El sistema es singular: no tiene solución única")
    if p != k:
        aum[k], aum[p] = aum[p], aum[k]
        pasos.append({"titulo": f"Pivoteo parcial: intercambio F{k + 1} ↔ F{p + 1}", "matriz": _copia(aum), "pivote": [k, k]})


def gauss_pivoteo(A, b):
    aum = _preparar(A, b)
    n = len(aum)
    pasos = [{"titulo": "Matriz aumentada inicial", "matriz": _copia(aum), "pivote": None}]

    for k in range(n):
        _pivotear(aum, k, n, pasos)
        multiplicadores = []
        for i in range(k + 1, n):
            m = aum[i][k] / aum[k][k]
            multiplicadores.append(f"m{i + 1}{k + 1} = {m:.4f}")
            for j in range(k, n + 1):
                aum[i][j] -= m * aum[k][j]
            aum[i][k] = 0.0
        if multiplicadores:
            titulo = f"Eliminación en la columna {k + 1} ({', '.join(multiplicadores)})"
        else:
            titulo = f"Columna {k + 1}: sin filas por debajo del pivote"
        pasos.append({"titulo": titulo, "matriz": _copia(aum), "pivote": [k, k]})

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        suma = sum(aum[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (aum[i][n] - suma) / aum[i][i]

    return {"solucion": x, "pasos": pasos, "residuo": _residuo(A, b, x)}


def gauss_jordan_pivoteo(A, b):
    aum = _preparar(A, b)
    n = len(aum)
    pasos = [{"titulo": "Matriz aumentada inicial", "matriz": _copia(aum), "pivote": None}]

    for k in range(n):
        _pivotear(aum, k, n, pasos)
        pivote = aum[k][k]
        aum[k] = [v / pivote for v in aum[k]]
        aum[k][k] = 1.0
        pasos.append({"titulo": f"Normalización: F{k + 1} ← F{k + 1} / {pivote:.4f}", "matriz": _copia(aum), "pivote": [k, k]})

        for i in range(n):
            if i == k:
                continue
            m = aum[i][k]
            if m == 0:
                continue
            for j in range(k, n + 1):
                aum[i][j] -= m * aum[k][j]
            aum[i][k] = 0.0
        pasos.append({"titulo": f"Eliminación en la columna {k + 1} (arriba y abajo del pivote)", "matriz": _copia(aum), "pivote": [k, k]})

    x = [aum[i][n] for i in range(n)]
    return {"solucion": x, "pasos": pasos, "residuo": _residuo(A, b, x)}


def jacobi(A, b, x0=None, tol=1e-6, iter_max=50):
    aum = _preparar(A, b)
    n = len(aum)
    M = [fila[:n] for fila in aum]
    c = [fila[n] for fila in aum]

    for i in range(n):
        if abs(M[i][i]) < EPS:
            raise ValueError(f"El elemento diagonal a{i + 1}{i + 1} es cero: reordena las ecuaciones")

    dominante = all(
        abs(M[i][i]) > sum(abs(M[i][j]) for j in range(n) if j != i) for i in range(n)
    )
    aviso = None if dominante else "La matriz no es estrictamente diagonal dominante: la convergencia no está garantizada"

    x = [float(v) for v in x0] if x0 else [0.0] * n
    if len(x) != n:
        raise ValueError("El vector inicial debe tener n componentes")

    tabla = []
    convergio = False

    for paso in range(1, int(iter_max) + 1):
        nuevo = [
            (c[i] - sum(M[i][j] * x[j] for j in range(n) if j != i)) / M[i][i]
            for i in range(n)
        ]
        if not all(math.isfinite(v) for v in nuevo):
            raise ValueError("El método diverge: aparecen valores no finitos")
        error = max(abs(nuevo[i] - x[i]) for i in range(n))
        tabla.append({"n": paso, "valores": nuevo, "error": error})
        x = nuevo
        if error <= tol:
            convergio = True
            break

    return {
        "convergio": convergio,
        "solucion": x,
        "iteraciones": len(tabla),
        "tabla": tabla,
        "residuo": _residuo(A, b, x),
        "aviso": aviso,
        "info": "x_i^(k+1) = (b_i − Σ_(j≠i) a_ij·x_j^(k)) / a_ii; error = máx|x^(k+1) − x^(k)|",
    }


def gauss_seidel(A, b, x0=None, tol=1e-6, iter_max=50):
    aum = _preparar(A, b)
    n = len(aum)
    M = [fila[:n] for fila in aum]
    c = [fila[n] for fila in aum]

    for i in range(n):
        if abs(M[i][i]) < EPS:
            raise ValueError(f"El elemento diagonal a{i + 1}{i + 1} es cero: reordena las ecuaciones")

    dominante = all(
        abs(M[i][i]) > sum(abs(M[i][j]) for j in range(n) if j != i) for i in range(n)
    )
    aviso = None if dominante else "La matriz no es estrictamente diagonal dominante: la convergencia no está garantizada"

    x = [float(v) for v in x0] if x0 else [0.0] * n
    if len(x) != n:
        raise ValueError("El vector inicial debe tener n componentes")

    tabla = []
    convergio = False

    for paso in range(1, int(iter_max) + 1):
        previo = x[:]
        for i in range(n):
            x[i] = (c[i] - sum(M[i][j] * x[j] for j in range(n) if j != i)) / M[i][i]
        if not all(math.isfinite(v) for v in x):
            raise ValueError("El método diverge: aparecen valores no finitos")
        error = max(abs(x[i] - previo[i]) for i in range(n))
        tabla.append({"n": paso, "valores": x[:], "error": error})
        if error <= tol:
            convergio = True
            break

    return {
        "convergio": convergio,
        "solucion": x,
        "iteraciones": len(tabla),
        "tabla": tabla,
        "residuo": _residuo(A, b, x),
        "aviso": aviso,
        "info": "x_i^(k+1) = (b_i − Σ_(j<i) a_ij·x_j^(k+1) − Σ_(j>i) a_ij·x_j^(k)) / a_ii; error = máx|x^(k+1) − x^(k)|",
    }
