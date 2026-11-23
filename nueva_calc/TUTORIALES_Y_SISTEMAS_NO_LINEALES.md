# Nueva funcionalidad: tutoriales y sistemas no lineales

## Tutorial paso a paso
Todos los métodos que usan las vistas de raíces, sistemas lineales y calculadoras genéricas muestran ahora un panel para navegar por los pasos; conserva las tablas y las gráficas anteriores. Las ayudas existentes muestran fórmulas generales. En métodos iterativos, la vista muestra los valores por iteración; Jacobi incorpora sustituciones numéricas.

## Newton para sistemas no lineales
Hito 4 → Sistemas no lineales → Newton para sistemas no lineales.

Ejemplo:
- f1(x,y) = x**2 + y**2 - 4
- f2(x,y) = x - y - 1
- X0 = (1.8, 0.8)

Se resuelve J(X)Δ = -F(X) con numpy.linalg.solve (sin invertir la matriz explícitamente). Se usa búsqueda de paso amortiguado si el residuo no mejora. Se muestran Jacobiana, evaluación en cada punto, incremento, factor de paso y residuo de comprobación.

El método es local, no garantiza convergencia desde cualquier punto y puede encontrar diferentes soluciones según X0.
