"""Exportación PDF de cálculos. Los datos recibidos se limitan y escapan."""
from io import BytesIO
import math
import unicodedata
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, Line, PolyLine, Circle, String

def _texto(v,limite=2500):
    if v is None:return "-"
    t=str(v)[:limite]
    cambio={"Σ":"Sum","Δ":"Delta","α":"alpha","β":"beta","λ":"lambda","∞":"inf",
            "≤":"<=","≥":">=","−":"-","≈":"~","²":"^2","³":"^3","√":"sqrt",
            "ŷ":"y_estimado","x̄":"x_media","ȳ":"y_media","∈":"en","·":"*",
            "π":"pi","θ":"theta","μ":"mu","∑":"sum"}
    for k,n in cambio.items():t=t.replace(k,n)
    return unicodedata.normalize("NFKD",t).encode("latin-1","replace").decode("latin-1")

def _p(v,style):
    return Paragraph(escape(_texto(v)).replace("\n","<br/>"),style)

def _tabla(tabla,estilos):
    cols=tabla.get("columnas",[])
    filas=tabla.get("filas",[])
    if not isinstance(cols,list) or not isinstance(filas,list) or not cols:return []
    cols=cols[:10];filas=filas[:220]
    data=[[ _p(c,estilos["CellHead"]) for c in cols]]
    for fila in filas:
        if not isinstance(fila,list):continue
        data.append([_p(fila[i] if i<len(fila) else "",estilos["Cell"]) for i in range(len(cols))])
    anchura=(A4[0]-80)/len(cols)
    t=LongTable(data,colWidths=[anchura]*len(cols),repeatRows=1,hAlign="LEFT")
    t.setStyle(TableStyle([
       ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#312459")),
       ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.whitesmoke,colors.white]),
       ("GRID",(0,0),(-1,-1),.25,colors.HexColor("#dddddd")),
       ("VALIGN",(0,0),(-1,-1),"TOP"),
       ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
       ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    return [t,Spacer(1,12)]

def _grafica(g):
    series=g.get("series",[]) if isinstance(g,dict) else []
    validas=[]
    for s in series[:6]:
        puntos=[]
        for p in s.get("puntos",[])[:500]:
            try:
                a,b=float(p[0]),float(p[1])
                if math.isfinite(a) and math.isfinite(b):puntos.append((a,b))
            except (TypeError,ValueError,IndexError):pass
        if puntos:validas.append((s,puntos))
    if not validas:return None
    allp=[p for _,ps in validas for p in ps]
    xmin,xmax=min(p[0] for p in allp),max(p[0] for p in allp)
    ymin,ymax=min(p[1] for p in allp),max(p[1] for p in allp)
    dx=xmax-xmin or 1.;dy=ymax-ymin or 1.
    xmin-=dx*.05;xmax+=dx*.05;ymin-=dy*.12;ymax+=dy*.12
    W,H=510,235;L,R,B,T=50,18,35,22
    X=lambda x:L+(x-xmin)/(xmax-xmin)*(W-L-R)
    Y=lambda y:B+(y-ymin)/(ymax-ymin)*(H-B-T)
    d=Drawing(W,H)
    d.add(Rect(L,B,W-L-R,H-B-T,strokeColor=colors.HexColor("#d9d1ec"),fillColor=None))
    paleta=["#7453c6","#0891b2","#c28722","#ba456d","#288569","#a35fbf"]
    for i in range(6):
        fy=B+i*(H-B-T)/5
        d.add(Line(L,fy,W-R,fy,strokeColor=colors.HexColor("#e8e5ee")))
        d.add(String(2,fy,_texto(f"{ymin+(ymax-ymin)*i/5:.4g}"),fontSize=7,fillColor=colors.HexColor("#54505b")))
        fx=L+i*(W-L-R)/5
        d.add(String(fx-12,15,_texto(f"{xmin+(xmax-xmin)*i/5:.4g}"),fontSize=7,fillColor=colors.HexColor("#54505b")))
    for i,(s,ps) in enumerate(validas):
        c=colors.HexColor(paleta[i%len(paleta)])
        if s.get("tipo")!="puntos" and len(ps)>1:
            d.add(PolyLine([z for p in ps for z in (X(p[0]),Y(p[1]))],strokeColor=c,strokeWidth=1.6,fillColor=None))
        if s.get("tipo")=="puntos" or len(ps)<=24:
            for px,py in ps:d.add(Circle(X(px),Y(py),2.4,fillColor=c,strokeColor=None))
        d.add(String(L+i*77,H-11,_texto(s.get("nombre","Serie"))[:13],fontSize=7,fillColor=c))
    return d

def generar(cuerpo):
    if not isinstance(cuerpo,dict):raise ValueError("Datos de reporte incorrectos")
    memoria=BytesIO()
    doc=SimpleDocTemplate(memoria,pagesize=A4,leftMargin=40,rightMargin=40,topMargin=45,bottomMargin=45,
                          title="Reporte de métodos numéricos",author="Calculadora educativa")
    estilos=getSampleStyleSheet()
    estilos.add(ParagraphStyle(name="Cell",parent=estilos["Normal"],fontSize=7,leading=9,spaceAfter=0))
    estilos.add(ParagraphStyle(name="CellHead",parent=estilos["Cell"],textColor=colors.white))
    estilos.add(ParagraphStyle(name="FormulaMN",parent=estilos["BodyText"],fontName="Courier",fontSize=9,leading=14,
                               backColor=colors.HexColor("#f5f2fc"),spaceBefore=8,spaceAfter=10))
    titulo=_texto(cuerpo.get("titulo","Reporte de cálculo"),140)
    story=[_p(titulo,estilos["Title"]),Spacer(1,12),_p("REPORTE EDUCATIVO - MÉTODOS NUMÉRICOS",estilos["Heading3"])]
    if cuerpo.get("formula"):
        story.extend([_p("Fórmula del método",estilos["Heading2"]),_p(cuerpo["formula"],estilos["FormulaMN"])])
    params=cuerpo.get("parametros",{})
    if isinstance(params,dict):
        story.append(_p("Datos de entrada",estilos["Heading2"]))
        for clave,val in list(params.items())[:30]:
            story.append(_p(f"{clave}: {val}",estilos["BodyText"]))
    resultados=cuerpo.get("resultados",[])
    if isinstance(resultados,list) and resultados:
        story.append(_p("Resultados",estilos["Heading2"]))
        for par in resultados[:35]:
            if isinstance(par,list) and len(par)>=2:
                story.append(_p(f"{par[0]}: {par[1]}",estilos["BodyText"]))
    pasos=cuerpo.get("pasos",[])
    if isinstance(pasos,list) and pasos:
        story.append(_p("Procedimiento paso a paso",estilos["Heading2"]))
        for i,p in enumerate(pasos[:160],1):
            if not isinstance(p,dict):continue
            story.append(_p(f"{i}. {p.get('titulo','Paso')}",estilos["Heading3"]))
            if p.get("detalle") is not None:story.append(_p(p["detalle"],estilos["BodyText"]))
            if isinstance(p.get("matriz"),list):
                m=p["matriz"]
                if m and isinstance(m[0],list):
                    story.extend(_tabla({"columnas":[f"c{j+1}" for j in range(min(10,len(m[0])))],"filas":m},estilos))
    tablas=cuerpo.get("tablas",[])
    if isinstance(tablas,list):
        for tab in tablas[:12]:
            if not isinstance(tab,dict):continue
            story.append(_p(tab.get("titulo","Tabla de cálculo"),estilos["Heading2"]))
            story.extend(_tabla(tab,estilos))
    graficas=cuerpo.get("graficas",[])
    if isinstance(graficas,list):
        for g in graficas[:6]:
            if not isinstance(g,dict):continue
            graf=_grafica(g)
            if graf:
                story.append(_p(g.get("titulo","Gráfica"),estilos["Heading2"]))
                story.append(graf);story.append(Spacer(1,12))
    if cuerpo.get("aviso"):
        story.extend([_p("Advertencias",estilos["Heading2"]),_p(cuerpo["aviso"],estilos["BodyText"])])
    if cuerpo.get("info"):
        story.append(_p(cuerpo["info"],estilos["BodyText"]))
    doc.build(story)
    memoria.seek(0)
    return memoria
