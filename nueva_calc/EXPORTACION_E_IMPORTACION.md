# Importación y exportación de ejercicios

## Importación CSV y Excel
Disponible en los métodos que utilizan tablas de puntos, series de tiempo y matrices de sistemas.
- Acepta CSV, XLSX, XLS, XLSB y ODS, leyendo **la primera hoja** en hojas de cálculo.
- Se leen las primeras columnas numéricas necesarias: 1 para series, 2 para puntos X/Y y n+1 para sistemas lineales de dimensión n.
- Se permite una fila inicial de encabezados; los valores deben ser numéricos. El archivo se procesa en memoria, sin guardarse.
- Tamaño máximo 2 MB, hasta 500 filas.
- Las columnas sobrantes se ignoran. Ajusta primero el tamaño n de los sistemas.

## PDF
Después de calcular se activa "Descargar procedimiento PDF". Incluye los parámetros, fórmula general, pasos numéricos disponibles, tablas, advertencias y las gráficas correspondientes al cálculo. No necesita iniciar sesión.

## Gráficas
- Rueda del ratón: zoom.
- Arrastrar con el puntero: mover.
- Hover: coordenadas del punto más cercano.
- Botones +, −, Restablecer, SVG.

## Pruebas
Ejecuta desde `nueva_calc`:
```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
```
Las pruebas cubren rutas existentes, bisección, Newton, regresión, sistemas no lineales, CSV, Excel y PDF.
