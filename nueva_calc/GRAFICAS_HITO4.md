# Gráficas del Hito 4

Se incorporaron gráficos SVG sin dependencias externas. Se generan automáticamente al pulsar **Calcular**, conservando las tablas y resultados.

- Redondeo y truncamiento: comparación de los valores.
- Taylor: función, polinomio y error por orden.
- Gauss-Seidel: error e incógnitas por iteración.
- Interpolación lineal, Newton hacia adelante, Lagrange y diferencias divididas: puntos originales, función interpolada y valor calculado.
- Regresiones lineal, exponencial, potencial y cuadrática: puntos, modelo y proyección.
- Series de tiempo: valores reales y pronósticos.

Archivos nuevos: `metodos/graficas.py` y `static/js/graficas.js`. También se modificaron las plantillas, estilos y `app.py`.

Para iniciar en local, instala `requirements.txt` y ejecuta `python app.py`. Para Render, usa el comando de arranque del servicio existente.
