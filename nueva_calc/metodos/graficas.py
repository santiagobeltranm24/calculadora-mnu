"""Datos para gráficas del Hito 4; sin alterar los algoritmos."""
import math
import sympy as sp
from .nucleo import VAR, parsear, numerica

def _serie(nombre, puntos, tipo="linea"):
    return {"nombre":nombre,"tipo":tipo,"puntos":[[float(x),float(y)] for x,y in puntos if math.isfinite(float(x)) and math.isfinite(float(y))]}

def _grafica(titulo, series, eje_x="x", eje_y="y"):
    return {"titulo":titulo,"eje_x":eje_x,"eje_y":eje_y,"series":series}

def _muestreo(funcion, inicio, fin, n=120):
    if inicio == fin:
        inicio-=1
        fin+=1
    puntos=[]
    for i in range(n+1):
        x=inicio+(fin-inicio)*i/n
        try:
            y=float(funcion(x))
            if math.isfinite(y): puntos.append((x,y))
        except (ValueError,ZeroDivisionError,OverflowError,TypeError):
            pass
    return puntos

def _rango(xs, objetivo=None):
    mn,mx=min(xs),max(xs)
    if objetivo is not None:
        mn,mx=min(mn,objetivo),max(mx,objetivo)
    margen=(mx-mn)*.12 if mx!=mn else 1
    return mn-margen,mx+margen

def _filas(cuerpo):
    return [(float(f[0]),float(f[1])) for f in cuerpo["puntos"]]

def _barycentrica(xs, ys):
    pesos=[]
    for i,xi in enumerate(xs):
        producto=1.
        for j,xj in enumerate(xs):
            if i!=j: producto*=xi-xj
        pesos.append(1./producto)
    def evaluar(x):
        for xi,yi in zip(xs,ys):
            if abs(x-xi)<1e-12*max(1,abs(xi)): return yi
        a=[w/(x-xi) for w,xi in zip(pesos,xs)]
        return sum(v*y for v,y in zip(a,ys))/sum(a)
    return evaluar

def construir(slug, cuerpo, resultado):
    if slug=="redondeo-truncamiento":
        valor=float(cuerpo["numero"])
        redondeado=float(resultado["resultados"][1][1])
        truncado=float(resultado["resultados"][2][1])
        return [_grafica("Comparación de valores",[
            _serie("Valor real",[(0,valor)],"puntos"),
            _serie("Redondeado",[(1,redondeado)],"puntos"),
            _serie("Truncado",[(2,truncado)],"puntos")],"0 = real · 1 = redondeado · 2 = truncado","Valor")]
    if slug=="taylor":
        expr=parsear(cuerpo["f"])
        a=float(cuerpo["a"]);x=float(cuerpo["x"]);n=int(cuerpo["n"])
        polinomio=sp.series(expr,VAR,a,n+1).removeO()
        real=numerica(expr);aprox=numerica(polinomio)
        inicio,fin=_rango([a,x])
        datos=[(k,float(fila[5])) for k,fila in enumerate(resultado["tablas"][0]["filas"])]
        return [
            _grafica("Función original y polinomio de Taylor",[
                _serie("Función original f(x)",_muestreo(real,inicio,fin)),
                _serie("Polinomio de grado "+str(n),_muestreo(aprox,inicio,fin)),
                _serie("Punto evaluado",[(x,float(resultado["resultados"][1][1]))],"puntos")]),
            _grafica("Error absoluto al aumentar el orden",[_serie("Error absoluto",datos)],"Orden k","|f(x) − Pₖ(x)|")]
    if slug.startswith("interpolacion-") or slug in ("newton-adelante","lagrange","diferencias-divididas"):
        puntos=sorted(_filas(cuerpo));xs=[p[0] for p in puntos];ys=[p[1] for p in puntos]
        x=float(cuerpo["x"])
        y=float(next(v for etiqueta,v in resultado["resultados"] if "interpolado" in etiqueta))
        inicio,fin=_rango(xs,x)
        if slug=="interpolacion-lineal":
            def evaluar(z):
                i=next((i for i in range(len(xs)-1) if xs[i]<=z<=xs[i+1]),0 if z<xs[0] else len(xs)-2)
                return ys[i]+(ys[i+1]-ys[i])*(z-xs[i])/(xs[i+1]-xs[i])
            nombre="Interpolación lineal por tramos"
        else:
            evaluar=_barycentrica(xs,ys);nombre="Polinomio interpolador"
        return [_grafica("Interpolación y puntos conocidos",[
            _serie(nombre,_muestreo(evaluar,inicio,fin)),
            _serie("Datos originales",puntos,"puntos"),
            _serie("Valor interpolado",[(x,y)],"puntos")])]
    if slug.startswith("regresion-"):
        puntos=_filas(cuerpo)
        parametros={k.split(" ")[0]:float(v) for k,v in resultado["resultados"] if k.split(" ")[0] in ("a","b","c")}
        a,b,c=parametros["a"],parametros["b"],parametros.get("c",0)
        xp=cuerpo.get("x_proyectar");xp=float(xp) if xp is not None and str(xp).strip() else None
        if slug=="regresion-lineal": fn=lambda x:a+b*x
        elif slug=="regresion-exponencial": fn=lambda x:a*math.exp(b*x)
        elif slug=="regresion-potencial": fn=lambda x:a*x**b if x>0 else float("nan")
        else: fn=lambda x:a+b*x+c*x*x
        inicio,fin=_rango([p[0] for p in puntos],xp)
        if slug=="regresion-potencial": inicio=max(inicio,min(p[0] for p in puntos)*.1)
        series=[_serie("Modelo ajustado",_muestreo(fn,inicio,fin)),_serie("Datos observados",puntos,"puntos")]
        if xp is not None:
            try: series.append(_serie("Proyección",[(xp,fn(xp))],"puntos"))
            except (OverflowError,ValueError): pass
        return [_grafica("Ajuste de regresión y proyección",series)]
    if slug=="series-de-tiempo":
        filas=resultado["tablas"][0]["filas"];reales=[];previstos=[]
        for fila in filas:
            t=float(fila[0])
            if fila[1] not in (None,"—"): reales.append((t,float(fila[1])))
            if fila[2] not in (None,"—"): previstos.append((t,float(fila[2])))
        return [_grafica("Datos reales y pronósticos",[
            _serie("Valores reales",reales),_serie("Pronósticos",previstos)],"Periodo t","Valor")]
    return []
