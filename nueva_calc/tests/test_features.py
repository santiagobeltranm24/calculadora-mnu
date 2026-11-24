"""Pruebas de regresión, importación y reportes en Flask."""
import io
import json
import math
import os
import sys
import unittest
import re
import subprocess
import zipfile

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from app import app

def excel_sencillo():
    memoria=io.BytesIO()
    piezas={
      "[Content_Types].xml":"""<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>""",
      "_rels/.rels":"""<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""",
      "xl/workbook.xml":"""<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="Datos" sheetId="1" r:id="rId1"/></sheets></workbook>""",
      "xl/_rels/workbook.xml.rels":"""<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>""",
      "xl/worksheets/sheet1.xml":"""<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>
<row r="1"><c r="A1" t="inlineStr"><is><t>X</t></is></c><c r="B1" t="inlineStr"><is><t>Y</t></is></c></row>
<row r="2"><c r="A2"><v>1</v></c><c r="B2"><v>2</v></c></row>
<row r="3"><c r="A3"><v>2</v></c><c r="B3"><v>4</v></c></row>
</sheetData></worksheet>""",
    }
    with zipfile.ZipFile(memoria,"w") as salida:
        for ruta,txt in piezas.items():
            salida.writestr(ruta,txt)
    memoria.seek(0)
    return memoria

class TestCalculadora(unittest.TestCase):
    def setUp(self):
        self.client=app.test_client()

    def test_paginas_y_rutas_originales(self):
        for ruta in ("/","/hito2/newton","/hito3/gauss","/hito4/lagrange",
                     "/hito4/newton-sistemas","/hito4/series-de-tiempo"):
            with self.subTest(ruta=ruta):
                res=self.client.get(ruta)
                self.assertEqual(res.status_code,200,res.get_data(as_text=True)[:300])
        inicio=self.client.get("/").get_data(as_text=True)
        self.assertIn("Explora los métodos",inicio)
        self.assertNotIn("Hito 4</",inicio)

    def test_biseccion_procedimiento(self):
        r=self.client.post("/api/raices/biseccion",json={"f":"x**2-2","a":1,"b":2,"tol":1e-8,"iter_max":60})
        data=r.get_json()
        self.assertTrue(data["ok"],data)
        self.assertAlmostEqual(data["raiz"],math.sqrt(2),places=6)
        self.assertIn("fa",data["tabla"][0])
        self.assertIn("fb",data["tabla"][0])

    def test_newton_y_regresion(self):
        r=self.client.post("/api/raices/newton",json={"f":"x**2-2","x0":1.5,"tol":1e-9,"iter_max":30})
        data=r.get_json()
        self.assertTrue(data["ok"],data)
        self.assertAlmostEqual(data["raiz"],math.sqrt(2),places=7)
        r=self.client.post("/api/generico/regresion-lineal",json={"puntos":[[1992,510],[1993,515],[1994,518],[1995,522],[1996,528],[1997,532],[1998,536]],"x_proyectar":2021})
        data=r.get_json()
        self.assertTrue(data["ok"],data)
        self.assertGreaterEqual(len(data["graficas"]),1)
        self.assertIn("coeficiente",str(data["resultados"]).lower())

    def test_sistemas_no_lineales(self):
        r=self.client.post("/api/no-lineales/newton",json={"f1":"x**2+y**2-4","f2":"x-y-1","x0":1.8,"y0":.8,"tol":1e-8,"iter_max":40})
        data=r.get_json()
        self.assertTrue(data["ok"],data)
        self.assertTrue(data["convergio"],data)
        self.assertLess(data["residuo"],1e-7)
        self.assertGreater(len(data["pasos"]),0)

    def test_csv_importa_con_cabecera(self):
        body=b"x;y\n1;2\n3;4\n"
        r=self.client.post("/api/importar-tabla",
            data={"archivo":(io.BytesIO(body),"tabla.csv"),"columnas":"2"},
            content_type="multipart/form-data")
        data=r.get_json()
        self.assertTrue(data["ok"],data)
        self.assertEqual(data["filas"],[[1.,2.],[3.,4.]])

    def test_excel_importa(self):
        r=self.client.post("/api/importar-tabla",
            data={"archivo":(excel_sencillo(),"ejemplo.xlsx"),"columnas":"2"},
            content_type="multipart/form-data")
        data=r.get_json()
        self.assertTrue(data["ok"],data)
        self.assertEqual(data["filas"],[[1.,2.],[2.,4.]])

    def test_javascript_en_paginas_generadas(self):
        rutas=["/","/hito2/newton","/hito2/punto-fijo","/hito3/biseccion",
               "/hito3/gauss","/hito4/gauss-seidel","/hito4/lagrange",
               "/hito4/series-de-tiempo","/hito4/newton-sistemas"]
        for ruta in rutas:
            html=self.client.get(ruta).get_data(as_text=True)
            scripts=re.findall(r"<script(?:\\s[^>]*)?>(.*?)</script>",html,re.S)
            for script in scripts:
                if not script.strip():continue
                with self.subTest(ruta=ruta):
                    p=subprocess.run(["node","--check","-"],input=script,text=True,capture_output=True)
                    self.assertEqual(p.returncode,0,p.stderr)

    def test_redisenio_academico_todos_los_metodos(self):
        from app import TEMAS
        nombres=[tema["nombre"] for tema in TEMAS]
        self.assertEqual(nombres, [
            "Aproximación", "Raíces de ecuaciones", "Sistemas lineales",
            "Sistemas no lineales", "Interpolación", "Proyecciones",
        ])
        vistas=self.client.get("/")
        self.assertEqual(vistas.status_code, 200)
        html=vistas.get_data(as_text=True)
        self.assertIn('id="buscar-metodos"', html)
        self.assertIn('data-filtro="todos"', html)
        self.assertIn("css/academico.css", html)
        self.assertIn("js/academico.js", html)
        self.assertEqual(html.count('class="tema-seccion"'), 6)
        slugs=[]
        for tema in TEMAS:
            for item in tema["items"]:
                slugs.append(item["slug"])
                with self.subTest(metodo=item["titulo"]):
                    respuesta=self.client.get(item["ruta"])
                    self.assertEqual(respuesta.status_code,200)
                    pagina=respuesta.get_data(as_text=True)
                    self.assertIn('id="menu-lateral"', pagina)
                    self.assertIn("metodo-navegacion",pagina if item["slug"]!="errores" else pagina)
                    self.assertIn("css/academico.css",pagina)
        self.assertEqual(len(slugs),len(set(slugs)))
        estilo=self.client.get("/static/css/academico.css")
        self.assertEqual(estilo.status_code,200)
        self.assertIn(b"#2563eb",estilo.data)

    def test_pdf_exporta_procedimientos_y_graficas(self):
        payload={"titulo":"Newton y regresión","formula":"x(n+1)=x(n)-f/f'",
          "parametros":{"f":"x**2-2","x0":1.5},
          "resultados":[["Raíz",1.41421356237]],
          "pasos":[{"titulo":"Sustitución","detalle":"x1 = 1.5 - 0.25/3 = 1.4166667"}],
          "tablas":[{"titulo":"Iteraciones","columnas":["n","x","error"],"filas":[[1,1.4166667,0.083333]]}],
          "graficas":[{"titulo":"Convergencia","series":[{"nombre":"Error","tipo":"linea","puntos":[[1,.08],[2,.004],[3,.00001]]}]}]}
        r=self.client.post("/api/exportar-pdf",json=payload)
        self.assertEqual(r.status_code,200,r.get_data(as_text=True)[:150] if r.status_code!=200 else "")
        self.assertTrue(r.data.startswith(b"%PDF"))
        self.assertGreater(len(r.data),1500)

if __name__=="__main__":
    unittest.main()
