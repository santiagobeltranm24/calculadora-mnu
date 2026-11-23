"""Importación segura de columnas numéricas desde CSV y Excel (primera hoja)."""
import csv
import io
import math
from python_calamine import CalamineWorkbook

MAX_FILAS = 500
MAX_BYTES = 2 * 1024 * 1024

def _numero(celda):
    if isinstance(celda, bool) or celda is None:
        raise ValueError("celda vacía o no numérica")
    if isinstance(celda, (float, int)):
        v = float(celda)
    else:
        txt = str(celda).strip().replace("\u00a0","").replace(" ","")
        if not txt: raise ValueError("celda vacía")
        if "," in txt and "." not in txt:
            txt = txt.replace(",", ".")
        v = float(txt)
    if not math.isfinite(v):
        raise ValueError("se esperan números finitos")
    return v

def extraer(archivo, columnas):
    if not isinstance(columnas,int) or not 1<=columnas<=7:
        raise ValueError("Elige entre 1 y 7 columnas")
    nombre = (archivo.filename or "").lower()
    contenido = archivo.read(MAX_BYTES + 1)
    if not contenido or len(contenido)>MAX_BYTES:
        raise ValueError("El archivo está vacío o supera 2 MB")
    if nombre.endswith(".csv"):
        try: texto=contenido.decode("utf-8-sig")
        except UnicodeDecodeError: texto=contenido.decode("latin-1")
        muestra=texto[:4096]
        try: separador=csv.Sniffer().sniff(muestra,delimiters=",;\t").delimiter
        except csv.Error: separador=";" if muestra.count(";")>muestra.count(",") else ","
        crudas=list(csv.reader(io.StringIO(texto),delimiter=separador))
    elif nombre.endswith((".xlsx",".xls",".xlsb",".ods")):
        try:
            wb=CalamineWorkbook.from_filelike(io.BytesIO(contenido))
            if not wb.sheet_names:raise ValueError("No hay hojas en el libro")
            crudas=wb.get_sheet_by_index(0).to_python()
            wb.close()
        except ValueError:raise
        except Exception as exc:raise ValueError("No se pudo leer el Excel: "+str(exc))
    else:
        raise ValueError("Formato no permitido: carga CSV, XLSX, XLS, XLSB u ODS")

    resultados=[]
    omitio_encabezado=False
    for numero_fila,fila in enumerate(crudas):
        if len(resultados)>=MAX_FILAS:
            raise ValueError("Se admiten hasta 500 filas numéricas")
        if not fila or all(str(v).strip()=="" for v in fila):
            continue
        if len(fila)<columnas:
            raise ValueError(f"Fila {numero_fila+1}: se necesitan {columnas} columnas")
        try:
            valores=[_numero(v) for v in fila[:columnas]]
        except (ValueError,TypeError):
            if numero_fila==0 and not omitio_encabezado:
                omitio_encabezado=True
                continue
            raise ValueError(f"Fila {numero_fila+1}: se encontraron celdas vacías o no numéricas")
        resultados.append(valores)
    if not resultados:
        raise ValueError("El archivo no contiene filas numéricas; revisa columnas y encabezados")
    return resultados
