import math

from . import lineales
from .nucleo import f6, leer_filas


def _opcional(cuerpo, clave):
    valor = cuerpo.get(clave)
    if valor is None or str(valor).strip() == "":
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValueError("El valor a proyectar debe ser numérico")


def _recta(us, vs):
    n = len(us)
    su = sum(us)
    sv = sum(vs)
    suv = sum(u * v for u, v in zip(us, vs))
    suu = sum(u * u for u in us)
    denominador = n * suu - su ** 2
    if abs(denominador) < 1e-12:
        raise ValueError("Los valores de x no pueden ser todos iguales")
    pendiente = (n * suv - su * sv) / denominador
    intercepto = sv / n - pendiente * su / n
    return intercepto, pendiente, (n, su, sv, suv, suu)


def _determinacion(reales, ajustados):
    media = sum(reales) / len(reales)
    sst = sum((y - media) ** 2 for y in reales)
    sse = sum((y - yh) ** 2 for y, yh in zip(reales, ajustados))
    return 1 - sse / sst if sst > 0 else 1.0, sse


def _armar(titulo_ecuacion, parametros, filas_tabla, columnas_tabla, r2, sse, proyeccion, pasos, info, aviso=None):
    resultados = [["ecuación", titulo_ecuacion]]
    resultados += parametros
    resultados.append(["coeficiente de determinación R²", f6(r2)])
    resultados.append(["suma de errores al cuadrado", f6(sse)])
    if proyeccion is not None:
        resultados.append([proyeccion[0], f6(proyeccion[1])])
    return {
        "resultados": resultados,
        "tablas": [{"titulo": "Tabla de cálculo", "columnas": columnas_tabla, "filas": filas_tabla}],
        "pasos": pasos,
        "aviso": aviso,
        "info": info,
    }


def lineal(cuerpo):
    filas = leer_filas(cuerpo, 2, 2)
    xs = [p[0] for p in filas]
    ys = [p[1] for p in filas]
    xp = _opcional(cuerpo, "x_proyectar")

    a, b, (n, sx, sy, sxy, sxx) = _recta(xs, ys)
    ajustados = [a + b * x for x in xs]
    r2, sse = _determinacion(ys, ajustados)
    syy = sum(y * y for y in ys)
    raiz = math.sqrt((n * sxx - sx ** 2) * (n * syy - sy ** 2))
    r = (n * sxy - sx * sy) / raiz if raiz > 0 else 1.0

    tabla = [
        [str(i + 1), f6(x), f6(y), f6(x * y), f6(x * x), f6(yh), f6(y - yh)]
        for i, (x, y, yh) in enumerate(zip(xs, ys, ajustados))
    ]
    tabla.append(["Σ", f6(sx), f6(sy), f6(sxy), f6(sxx), None, None])

    proyeccion = (f"proyección en x = {xp:g}", a + b * xp) if xp is not None else None
    pasos = [
        {"titulo": "Sumas", "detalle": f"n = {n},  Σx = {f6(sx)},  Σy = {f6(sy)},  Σxy = {f6(sxy)},  Σx² = {f6(sxx)}"},
        {"titulo": "Pendiente", "detalle": f"b = (nΣxy − ΣxΣy) / (nΣx² − (Σx)²) = {f6(b)}"},
        {"titulo": "Intercepto", "detalle": f"a = ȳ − b·x̄ = {f6(a)}"},
        {"titulo": "Correlación", "detalle": f"r = {f6(r)}"},
    ]
    return _armar(
        f"y = {a:.6g} + {b:.6g}·x",
        [["a (intercepto)", f6(a)], ["b (pendiente)", f6(b)], ["coeficiente de correlación r", f6(r)]],
        tabla, ["i", "x", "y", "x·y", "x²", "ŷ", "y − ŷ"], r2, sse, proyeccion, pasos,
        "Modelo y = a + b·x ajustado por mínimos cuadrados.",
    )


def exponencial(cuerpo):
    filas = leer_filas(cuerpo, 2, 2)
    xs = [p[0] for p in filas]
    ys = [p[1] for p in filas]
    if any(y <= 0 for y in ys):
        raise ValueError("El modelo exponencial requiere que todos los valores de y sean positivos")
    xp = _opcional(cuerpo, "x_proyectar")

    lys = [math.log(y) for y in ys]
    A, B, (n, sx, sly, sxly, sxx) = _recta(xs, lys)
    a = math.exp(A)
    b = B
    ajustados = [a * math.exp(b * x) for x in xs]
    r2, sse = _determinacion(ys, ajustados)

    tabla = [
        [str(i + 1), f6(x), f6(y), f6(ly), f6(x * ly), f6(x * x), f6(yh)]
        for i, (x, y, ly, yh) in enumerate(zip(xs, ys, lys, ajustados))
    ]
    tabla.append(["Σ", f6(sx), f6(sum(ys)), f6(sly), f6(sxly), f6(sxx), None])

    proyeccion = (f"proyección en x = {xp:g}", a * math.exp(b * xp)) if xp is not None else None
    pasos = [
        {"titulo": "Linealización", "detalle": "y = a·e^(b·x)  →  ln y = ln a + b·x"},
        {"titulo": "Regresión de ln y contra x", "detalle": f"ln a = {f6(A)},  b = {f6(B)}"},
        {"titulo": "Parámetros originales", "detalle": f"a = e^(ln a) = {f6(a)},  b = {f6(b)}"},
    ]
    return _armar(
        f"y = {a:.6g}·e^({b:.6g}·x)",
        [["a", f6(a)], ["b", f6(b)]],
        tabla, ["i", "x", "y", "ln y", "x·ln y", "x²", "ŷ"], r2, sse, proyeccion, pasos,
        "El R² se calcula sobre los valores originales de y.",
    )


def potencial(cuerpo):
    filas = leer_filas(cuerpo, 2, 2)
    xs = [p[0] for p in filas]
    ys = [p[1] for p in filas]
    if any(x <= 0 for x in xs) or any(y <= 0 for y in ys):
        raise ValueError("El modelo potencial requiere que x y y sean positivos")
    xp = _opcional(cuerpo, "x_proyectar")
    if xp is not None and xp <= 0:
        raise ValueError("El valor a proyectar debe ser positivo")

    lxs = [math.log(x) for x in xs]
    lys = [math.log(y) for y in ys]
    A, B, (n, slx, sly, slxly, slxlx) = _recta(lxs, lys)
    a = math.exp(A)
    b = B
    ajustados = [a * x ** b for x in xs]
    r2, sse = _determinacion(ys, ajustados)

    tabla = [
        [str(i + 1), f6(x), f6(y), f6(lx), f6(ly), f6(lx * ly), f6(lx * lx), f6(yh)]
        for i, (x, y, lx, ly, yh) in enumerate(zip(xs, ys, lxs, lys, ajustados))
    ]
    tabla.append(["Σ", f6(sum(xs)), f6(sum(ys)), f6(slx), f6(sly), f6(slxly), f6(slxlx), None])

    proyeccion = (f"proyección en x = {xp:g}", a * xp ** b) if xp is not None else None
    pasos = [
        {"titulo": "Linealización", "detalle": "y = a·x^b  →  ln y = ln a + b·ln x"},
        {"titulo": "Regresión de ln y contra ln x", "detalle": f"ln a = {f6(A)},  b = {f6(B)}"},
        {"titulo": "Parámetros originales", "detalle": f"a = e^(ln a) = {f6(a)},  b = {f6(b)}"},
    ]
    return _armar(
        f"y = {a:.6g}·x^{b:.6g}",
        [["a", f6(a)], ["b", f6(b)]],
        tabla, ["i", "x", "y", "ln x", "ln y", "ln x·ln y", "(ln x)²", "ŷ"], r2, sse, proyeccion, pasos,
        "El R² se calcula sobre los valores originales de y.",
    )


def cuadratica(cuerpo):
    filas = leer_filas(cuerpo, 2, 3)
    xs = [p[0] for p in filas]
    ys = [p[1] for p in filas]
    xp = _opcional(cuerpo, "x_proyectar")
    n = len(xs)

    s1 = sum(xs)
    s2 = sum(x ** 2 for x in xs)
    s3 = sum(x ** 3 for x in xs)
    s4 = sum(x ** 4 for x in xs)
    sy = sum(ys)
    sxy = sum(x * y for x, y in zip(xs, ys))
    sx2y = sum(x * x * y for x, y in zip(xs, ys))

    matriz = [[n, s1, s2], [s1, s2, s3], [s2, s3, s4]]
    independientes = [sy, sxy, sx2y]
    try:
        a, b, c = lineales.gauss_pivoteo(matriz, independientes)["solucion"]
    except ValueError:
        raise ValueError("No se puede ajustar una parábola: se necesitan al menos 3 valores de x distintos")

    ajustados = [a + b * x + c * x * x for x in xs]
    r2, sse = _determinacion(ys, ajustados)

    tabla = [
        [str(i + 1), f6(x), f6(y), f6(x ** 2), f6(x ** 3), f6(x ** 4), f6(x * y), f6(x * x * y), f6(yh)]
        for i, (x, y, yh) in enumerate(zip(xs, ys, ajustados))
    ]
    tabla.append(["Σ", f6(s1), f6(sy), f6(s2), f6(s3), f6(s4), f6(sxy), f6(sx2y), None])

    proyeccion = (f"proyección en x = {xp:g}", a + b * xp + c * xp * xp) if xp is not None else None
    pasos = [
        {"titulo": "Ecuaciones normales", "detalle": (
            f"{n}·a + {f6(s1)}·b + {f6(s2)}·c = {f6(sy)}\n"
            f"{f6(s1)}·a + {f6(s2)}·b + {f6(s3)}·c = {f6(sxy)}\n"
            f"{f6(s2)}·a + {f6(s3)}·b + {f6(s4)}·c = {f6(sx2y)}"
        )},
        {"titulo": "Solución del sistema (Gauss con pivoteo)", "detalle": f"a = {f6(a)},  b = {f6(b)},  c = {f6(c)}"},
    ]
    return _armar(
        f"y = {a:.6g} + {b:.6g}·x + {c:.6g}·x²",
        [["a", f6(a)], ["b", f6(b)], ["c", f6(c)]],
        tabla, ["i", "x", "y", "x²", "x³", "x⁴", "x·y", "x²·y", "ŷ"], r2, sse, proyeccion, pasos,
        "Modelo y = a + b·x + c·x² ajustado por mínimos cuadrados.",
    )



def _pronosticar_serie(ys, metodo, parametro):
    """Pronósticos de un paso adelante, usando exclusivamente información pasada."""
    n = len(ys)
    pronosticos = [None] * n
    if metodo == "promedio-movil":
        k = int(parametro)
        if k < 2 or k >= n or k != parametro:
            raise ValueError("El periodo k debe ser un entero entre 2 y n-1")
        for t in range(k, n):
            pronosticos[t] = sum(ys[t-k:t]) / k
        siguiente = sum(ys[n-k:]) / k
        descripcion = f"Promedio móvil de {k} periodos"
        formula = f"F(t+1) = (Y_t + … + Y_(t−{k-1})) / {k}"
    elif metodo == "suavizamiento":
        alfa = float(parametro)
        if not math.isfinite(alfa) or not 0 < alfa <= 1:
            raise ValueError("El factor α debe ser mayor que 0 y menor o igual que 1")
        pronosticos[1] = ys[0]
        for t in range(2, n):
            pronosticos[t] = alfa * ys[t-1] + (1-alfa) * pronosticos[t-1]
        siguiente = alfa * ys[n-1] + (1-alfa) * pronosticos[n-1]
        descripcion = f"Suavizamiento exponencial (α = {alfa:g})"
        formula = "F(1) = Y_1 (inicio);  F(t+1) = α·Y_t + (1 − α)·F(t)"
    else:
        raise ValueError("Método de serie de tiempo no reconocido")
    return pronosticos, siguiente, descripcion, formula


def _pearson(reales, pronosticos):
    """r de Pearson sobre los pares con pronóstico; indefinido si hay varianza cero."""
    if len(reales) < 2:
        return None
    media_y = sum(reales)/len(reales)
    media_p = sum(pronosticos)/len(pronosticos)
    a = sum((y-media_y)*(p-media_p) for y,p in zip(reales,pronosticos))
    b = sum((y-media_y)**2 for y in reales)
    c = sum((p-media_p)**2 for p in pronosticos)
    return max(-1.0,min(1.0,a/math.sqrt(b*c))) if b>1e-20 and c>1e-20 else None


def _metricas(ys, pronosticos, desde=0):
    pares = [(ys[t], pronosticos[t]) for t in range(desde,len(ys)) if pronosticos[t] is not None]
    if not pares:
        raise ValueError("No hay pronósticos para comparar")
    errores = [y-p for y,p in pares]
    validos_mape = [(y,p) for y,p in pares if y != 0]
    mad = sum(abs(e) for e in errores)/len(errores)
    mse = sum(e*e for e in errores)/len(errores)
    mape = sum(abs((y-p)/y)*100 for y,p in validos_mape)/len(validos_mape) if validos_mape else None
    return {"MAD":mad, "MSE":mse, "MAPE":mape,
            "r":_pearson([y for y,_ in pares],[p for _,p in pares]),
            "periodos":len(pares)}


def _optimizar_serie(ys, metodo, metrica):
    """Comparación justa con misma ventana temporal para todos los candidatos.

    No usa observaciones futuras para pronosticar cada periodo de evaluación.
    El parámetro se selecciona con datos históricos; no se estima error futuro.
    """
    n = len(ys)
    if n < 5:
        raise ValueError("Para optimizar se necesitan al menos 5 periodos")
    if metrica not in ("MAD","MSE","MAPE"):
        raise ValueError("La métrica de selección debe ser MAD, MSE o MAPE")
    # Últimos ~40% de los periodos, al menos 2; misma ventana para cada candidato.
    longitud = max(2, math.ceil(n*.4))
    inicio = n-longitud
    if metodo == "promedio-movil":
        candidatos = list(range(2,inicio+1))
    elif metodo == "suavizamiento":
        candidatos = [i/20 for i in range(1,21)]
    else:
        raise ValueError("Método de serie de tiempo no reconocido")
    if not candidatos:
        raise ValueError("No hay suficientes periodos para comparar parámetros")
    comparaciones=[]
    for p in candidatos:
        pronosticos,_,_,_ = _pronosticar_serie(ys,metodo,p)
        valores = _metricas(ys,pronosticos,inicio)
        comparaciones.append((p,valores))
    elegibles = [(p,v) for p,v in comparaciones if v[metrica] is not None]
    if not elegibles:
        raise ValueError("No se puede optimizar MAPE: todos los valores reales de evaluación son cero")
    mejor=min(elegibles,key=lambda pv:(pv[1][metrica],pv[0]))
    return mejor, comparaciones, inicio


def series_tiempo(cuerpo):
    filas = leer_filas(cuerpo, 1, 3)
    ys = [p[0] for p in filas]
    if not all(math.isfinite(y) for y in ys):
        raise ValueError("Todos los valores de la serie deben ser finitos")
    n = len(ys)
    metodo = cuerpo.get("metodo","promedio-movil")
    optimizar = cuerpo.get("optimizar") in (True,"true","on","1",1)
    criterio = cuerpo.get("criterio","MAD")
    comparaciones=[]
    inicio_eval=None
    if optimizar:
        (parametro,metricas_mejor),comparaciones,inicio_eval=_optimizar_serie(ys,metodo,criterio)
    else:
        try:
            parametro = float(cuerpo["parametro"])
        except (KeyError,TypeError,ValueError):
            raise ValueError("Escribe un valor válido para el parámetro")

    pronosticos,siguiente,descripcion,formula=_pronosticar_serie(ys,metodo,parametro)
    medicion=_metricas(ys,pronosticos)
    tabla=[]
    for t in range(n):
        f=pronosticos[t]
        if f is None:
            tabla.append([str(t+1),f6(ys[t]),None,None,None,None,None])
            continue
        e=ys[t]-f
        porcentaje=abs(e)/abs(ys[t])*100 if ys[t]!=0 else None
        tabla.append([str(t+1),f6(ys[t]),f6(f),f6(e),f6(abs(e)),f6(e*e),f6(porcentaje) if porcentaje is not None else None])
    tabla.append([str(n+1),"—",f6(siguiente),None,None,None,None])

    resultados=[
        [f"pronóstico para el periodo {n+1}",f6(siguiente)],
        ["parámetro utilizado ("+("k" if metodo=="promedio-movil" else "α")+")",f6(parametro)],
        ["MAD (error absoluto medio)",f6(medicion["MAD"])],
        ["MSE (error cuadrático medio)",f6(medicion["MSE"])],
        ["MAPE (%)",f6(medicion["MAPE"]) if medicion["MAPE"] is not None else "—"],
        ["r de Pearson (real frente a pronóstico)",f6(medicion["r"]) if medicion["r"] is not None else "no definido"],
    ]
    tablas=[{"titulo":descripcion,
        "columnas":["t","valor real","pronóstico","error","|error|","error²","|error| / valor (%)"],
        "filas":tabla}]
    pasos=[
        {"titulo":"Fórmula","detalle":formula},
        {"titulo":"Medidas de error","detalle":"MAD = promedio |error|, MSE = promedio error², MAPE = promedio |error|/|valor real|·100. r = correlación lineal de valores reales y pronosticados; no mide directamente la precisión."}
    ]
    if optimizar:
        tablas.append({
            "titulo":"Comparación de parámetros (misma ventana de evaluación)",
            "columnas":["k" if metodo=="promedio-movil" else "α","MAD","MSE","MAPE (%)","r Pearson","periodos"],
            "filas":[[f6(p),f6(v["MAD"]),f6(v["MSE"]),
                      f6(v["MAPE"]) if v["MAPE"] is not None else "—",
                      f6(v["r"]) if v["r"] is not None else "no definido",
                      str(v["periodos"])] for p,v in comparaciones],
        })
        resultados += [
            ["mejor parámetro según "+criterio,f6(parametro)],
            [criterio+" en ventana de evaluación",f6(metricas_mejor[criterio])],
            ["periodos comparados",f"del {inicio_eval+1} al {n}"],
        ]
        pasos.append({"titulo":"Cómo se eligió el mejor parámetro",
                      "detalle":f"Se probaron {len(comparaciones)} parámetros. Todos se evaluaron en los periodos {inicio_eval+1} a {n}, usando únicamente observaciones pasadas para cada pronóstico. Se eligió el mínimo {criterio}. No equivale a validar la precisión futura con datos independientes."})
    return {
        "resultados":resultados,
        "tablas":tablas,
        "pasos":pasos,
        "aviso":None,
        "info":"La última fila es el pronóstico del siguiente periodo. r cercano a ±1 indica asociación lineal fuerte, no necesariamente error bajo.",
    }
