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
    mu = su / n
    mv = sv / n
    cov = math.fsum((u - mu) * (v - mv) for u, v in zip(us, vs))
    var = math.fsum((u - mu) ** 2 for u in us)
    if var <= 1e-24:
        raise ValueError("Los valores de x no pueden ser todos iguales")
    pendiente = cov / var
    intercepto = mv - pendiente * mu
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
    mx = sum(xs) / n
    my = sum(ys) / n
    numerador_r = math.fsum((x - mx) * (y - my) for x, y in filas)
    var_x = math.fsum((x - mx) ** 2 for x in xs)
    var_y = math.fsum((y - my) ** 2 for y in ys)
    r = max(-1.0, min(1.0, numerador_r / math.sqrt(var_x * var_y))) if var_x > 0 and var_y > 0 else None

    tabla = [
        [str(i + 1), f6(x), f6(y), f6(x * y), f6(x * x), f6(yh), f6(y - yh)]
        for i, (x, y, yh) in enumerate(zip(xs, ys, ajustados))
    ]
    tabla.append(["Σ", f6(sx), f6(sy), f6(sxy), f6(sxx), None, None])

    proyeccion = (f"proyección en x = {xp:g}", a + b * xp) if xp is not None else None
    pasos = [
        {"titulo": "Sumas", "detalle": f"n = {n},  Σx = {f6(sx)},  Σy = {f6(sy)},  Σxy = {f6(sxy)},  Σx² = {f6(sxx)}"},
        {"titulo": "Pendiente (sustitución numérica)", "detalle": f"b = (nΣxy − ΣxΣy) / (nΣx² − (Σx)²) = ({n}·{f6(sxy)} − {f6(sx)}·{f6(sy)}) / ({n}·{f6(sxx)} − ({f6(sx)})²) = {f6(b)}. Se calcula internamente con X centrada para mejorar precisión."},
        {"titulo": "Intercepto (sustitución numérica)", "detalle": f"a = ȳ − b·x̄ = ({f6(sy)}/{n}) − ({f6(b)})·({f6(sx)}/{n}) = {f6(a)}"},
        {"titulo": "Paso 4. Correlación de Pearson", "detalle": f"r = Σ[(x−x̄)(y−ȳ)] / √{{Σ(x−x̄)²·Σ(y−ȳ)²}} = {f6(r) if r is not None else 'no definida (Y constante)'}"},
        {"titulo": "Paso 5. Evaluación del ajuste", "detalle": f"Se calcula ŷ_i = a + b·x_i, cada residuo e_i = y_i − ŷ_i y la suma de errores al cuadrado SSE = {f6(sse)}. R² = {f6(r2)}."},
    ]
    return _armar(
        f"y = {a:.6g} + {b:.6g}·x",
        [["a (intercepto)", f6(a)], ["b (pendiente)", f6(b)], ["coeficiente de correlación r", f6(r) if r is not None else "no definido"]],
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

    # Ajuste por mínimos cuadrados con X centradas y escaladas.
    import numpy as np
    centro = sum(xs) / n
    escala = max(abs(x - centro) for x in xs)
    if escala <= 1e-12:
        raise ValueError("Se necesitan al menos 3 valores distintos de x")
    z = np.array([(x - centro) / escala for x in xs], dtype=float)
    matriz_ajuste = np.column_stack((np.ones(n), z, z * z))
    coef, _, rango, _ = np.linalg.lstsq(matriz_ajuste, np.asarray(ys, dtype=float), rcond=None)
    if rango < 3:
        raise ValueError("No se puede ajustar una parábola: se necesitan al menos 3 valores distintos de x")
    A, B, C = map(float, coef)
    c = C / (escala ** 2)
    b = B / escala - 2 * c * centro
    a = A - (B / escala) * centro + c * centro ** 2

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
        {"titulo": "Solución por mínimos cuadrados estables", "detalle": f"Se centra y escala x antes de resolver: a = {f6(a)}, b = {f6(b)}, c = {f6(c)}"},
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
    n = len(ys)
    if not all(math.isfinite(y) for y in ys):
        raise ValueError("Los valores deben ser finitos")
    metodo = cuerpo.get("metodo","promedio-movil")
    auto = str(cuerpo.get("optimizar","false")).lower() in ("true","on","1")
    criterio = cuerpo.get("criterio","MAD")
    if auto:
        (parametro, seleccion), comparaciones, inicio = _optimizar_serie(ys, metodo, criterio)
    else:
        try: parametro = float(cuerpo["parametro"])
        except (KeyError,TypeError,ValueError): raise ValueError("Introduce un parámetro numérico")
        comparaciones = []
        inicio = None
        seleccion = None
    pronos, siguiente, nombre, formula = _pronosticar_serie(ys,metodo,parametro)
    indicadores = _metricas(ys,pronos)
    tabla = []
    detalle = []
    for t in range(n):
        pronostico = pronos[t]
        if pronostico is None:
            tabla.append([str(t+1),f6(ys[t]),None,None,None,None,None])
            continue
        err = ys[t]-pronostico
        porc = abs(err)/abs(ys[t])*100 if ys[t]!=0 else None
        tabla.append([str(t+1),f6(ys[t]),f6(pronostico),f6(err),f6(abs(err)),f6(err*err),f6(porc)])
        if metodo == "promedio-movil":
            k = int(parametro)
            base = " + ".join(f6(v) for v in ys[t-k:t])
            expresion = f"({base}) / {k}"
        else:
            if t==1: expresion=f"F₂=Y₁={f6(ys[0])}"
            else: expresion=f"{f6(parametro)}·{f6(ys[t-1])} + (1−{f6(parametro)})·{f6(pronos[t-1])}"
        detalle.append([str(t+1),expresion,f6(pronostico)])
    tabla.append([str(n+1),"—",f6(siguiente),None,None,None,None])
    resultados = [[f"Pronóstico para el periodo {n+1}",f6(siguiente)],
                  ["Parámetro utilizado ("+("k" if metodo=="promedio-movil" else "α")+")",f6(parametro)],
                  ["MAD",f6(indicadores["MAD"])],["MSE",f6(indicadores["MSE"])],
                  ["MAPE (%)",f6(indicadores["MAPE"]) if indicadores["MAPE"] is not None else "no definido"],
                  ["r de Pearson (real/pronóstico)",f6(indicadores["r"]) if indicadores["r"] is not None else "no definido"]]
    tablas = [{"titulo":nombre,"columnas":["Periodo","Real","Pronóstico","Error","|Error|","Error²","Error %"],"filas":tabla},
              {"titulo":"Sustitución numérica de cada pronóstico","columnas":["Periodo","Cálculo","Resultado"],"filas":detalle}]
    pasos = [{"titulo":"Paso 1. Configuración","detalle":f"Método: {nombre}. {formula}"},
             {"titulo":"Paso 2. Sustituciones","detalle":"La segunda tabla muestra los valores numéricos introducidos en cada fórmula, sin usar datos futuros."},
             {"titulo":"Paso 3. Errores","detalle":"Error = Real − Pronóstico. MAD = promedio |Error|; MSE = promedio Error²; MAPE = promedio 100·|Error|/|Real| (sin periodos con Real=0)."},
             {"titulo":"Paso 4. Correlación","detalle":"r de Pearson relaciona valores reales y pronosticados; no equivale a un error de predicción."},
             {"titulo":"Paso 5. Siguiente periodo","detalle":f"Con los últimos datos disponibles: F_{n+1} = {f6(siguiente)}"}]
    if auto:
        tablas.append({"titulo":f"Comparación en los mismos periodos ({inicio+1}–{n})",
                      "columnas":["k / α","MAD","MSE","MAPE (%)","r","periodos"],
                      "filas":[[f6(c),f6(m["MAD"]),f6(m["MSE"]),f6(m["MAPE"]) if m["MAPE"] is not None else "—",f6(m["r"]) if m["r"] is not None else "—",str(m["periodos"])] for c,m in comparaciones]})
        resultados.append(["Mejor parámetro por "+criterio,f6(parametro)])
        resultados.append([criterio+" en la ventana comparada",f6(seleccion[criterio])])
        pasos.append({"titulo":"Paso 6. Selección automática","detalle":f"Se probaron {len(comparaciones)} parámetros sobre los mismos periodos {inicio+1}–{n}. Se eligió el menor {criterio}; no garantiza el mejor resultado futuro."})
    return {"resultados":resultados,"tablas":tablas,"pasos":pasos,
            "aviso":None,"info":"La última fila contiene el pronóstico del siguiente periodo. La optimización histórica no implica validación independiente."}
