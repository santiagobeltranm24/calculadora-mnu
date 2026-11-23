"""Newton multivariable para sistemas no lineales de dos ecuaciones."""
import math
import numpy as np
import sympy as sp

x, y = sp.symbols("x y")
ALLOWED = {"x":x,"y":y,"sin":sp.sin,"cos":sp.cos,"tan":sp.tan,
           "exp":sp.exp,"log":sp.log,"sqrt":sp.sqrt,"pi":sp.pi,"E":sp.E}

def resolver(cuerpo):
    try:
        textos=[str(cuerpo["f1"]).strip(),str(cuerpo["f2"]).strip()]
        if any(not v or len(v)>300 for v in textos):
            raise ValueError("Introduce dos ecuaciones de hasta 300 caracteres")
        expresiones=[sp.sympify(t,locals=ALLOWED) for t in textos]
        if any(expr.free_symbols - {x,y} for expr in expresiones):
            raise ValueError("Las ecuaciones solo pueden usar las variables x, y")
        if any(expr.has(sp.Integral,sp.Derivative,sp.Sum,sp.Limit) for expr in expresiones):
            raise ValueError("Escribe expresiones evaluables, no operadores simbólicos")
        punto=np.array([float(cuerpo["x0"]),float(cuerpo["y0"])],dtype=float)
        tol=float(cuerpo.get("tol",1e-7))
        max_iter=int(cuerpo.get("iter_max",30))
        if not np.isfinite(punto).all() or not math.isfinite(tol) or not 0<tol<1 or not 1<=max_iter<=100:
            raise ValueError("Revisa valores iniciales, tolerancia (0 < tol < 1) e iteraciones (1–100)")
        vector=sp.Matrix(expresiones)
        matriz=vector.jacobian([x,y])
        ef=sp.lambdify((x,y),vector,modules="numpy")
        ej=sp.lambdify((x,y),matriz,modules="numpy")
        def evals(p):
            v=np.asarray(ef(*p),dtype=float).reshape(2)
            j=np.asarray(ej(*p),dtype=float).reshape(2,2)
            if not np.isfinite(v).all() or not np.isfinite(j).all():
                raise ValueError("La función o la Jacobiana generan valores no finitos")
            return v,j
        filas=[];pasos=[];convergio=False;aviso=None
        for k in range(1,max_iter+1):
            f,j=evals(punto)
            norma=float(np.linalg.norm(f,ord=np.inf))
            if norma<=tol:
                convergio=True
                break
            if np.linalg.cond(j)>1e12:
                aviso="La Jacobiana es singular o está mal condicionada cerca de la aproximación."
                break
            try: delta=np.linalg.solve(j,-f)
            except np.linalg.LinAlgError:
                aviso="No se puede resolver J·Δ = −F: Jacobiana singular."
                break
            escala=1.0
            nuevo=punto+delta
            # Amortiguación: evita pasos que empeoran mucho el residuo.
            for _ in range(18):
                try: fn,_=evals(nuevo);nuevo_norma=float(np.linalg.norm(fn,ord=np.inf))
                except (ValueError,OverflowError,ZeroDivisionError): nuevo_norma=float("inf")
                if nuevo_norma < norma or nuevo_norma <= tol:break
                escala*=0.5
                nuevo=punto+escala*delta
            if not math.isfinite(nuevo_norma) or nuevo_norma>=norma:
                aviso="No se encontró un paso que disminuya el residuo. Prueba otro punto inicial."
                break
            error=float(np.linalg.norm(nuevo-punto,ord=np.inf))
            filas.append({"n":k,"x":float(nuevo[0]),"y":float(nuevo[1]),"error":error,"residuo":nuevo_norma})
            pasos.append({"titulo":f"Iteración {k}: evaluar F y J",
                "detalle":f"X{k-1}=({punto[0]:.8g}, {punto[1]:.8g}); F=({f[0]:.8g}, {f[1]:.8g}); J=[[{j[0,0]:.8g}, {j[0,1]:.8g}], [{j[1,0]:.8g}, {j[1,1]:.8g}]]."})
            pasos.append({"titulo":f"Iteración {k}: resolver J·Δ = −F",
                "detalle":f"Δ=({delta[0]:.8g}, {delta[1]:.8g}); factor λ={escala:.6g}; X{k}=X{k-1}+λΔ=({nuevo[0]:.8g}, {nuevo[1]:.8g}); error={error:.4g}; ||F(X{k})||∞={nuevo_norma:.4g}."})
            punto=nuevo
            if nuevo_norma<=tol:
                convergio=True;break
        f_final,_=evals(punto)
        residual=float(np.linalg.norm(f_final,ord=np.inf))
        if not convergio and aviso is None:aviso="No alcanzó la tolerancia antes del máximo de iteraciones; intenta otro punto inicial o más iteraciones."
        return {"solucion":[float(v) for v in punto],"residuo":residual,
           "convergio":convergio,"iteraciones":len(filas),"tabla":filas,"pasos":pasos,
           "jacobiana":[[str(matriz[i,j]) for j in range(2)] for i in range(2)],
           "funciones":[str(t) for t in expresiones],
           "aviso":aviso,
           "formula":"J(Xk)·Δk = −F(Xk); X(k+1) = Xk + λ·Δk",
           "info":"Comprueba ambas ecuaciones con el residuo final. Newton local puede converger a distintas raíces según X0."}
    except (TypeError,KeyError,OverflowError,sp.SympifyError) as exc:
        raise ValueError("Revisa las ecuaciones y parámetros: "+str(exc))
