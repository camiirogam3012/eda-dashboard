"""tabs/inicio.py – Portada del dashboard."""

from dash import html, dcc

from components import kpi, fmt
from data.data_loader import resumen_general, cambio_porcentual, objetivo_pm25

ETAPAS = [
    ("Análisis exploratorio", "Esta entrega: conocer los datos y la variable objetivo", True),
    ("Preprocesamiento", "Corregir lo que encontró el EDA", False),
    ("Modelo", "Clasificar estaciones según su riesgo de excedencia", False),
    ("Dashboard", "Explorar los datos y consultar el modelo", False),
]


def layout():
    r = resumen_general()
    pm25 = cambio_porcentual("PM2.5")
    obj = objetivo_pm25()
    return html.Div([
        html.Section([
            html.Img(src="/assets/huella.svg", className="hero-huella",
                     alt=f"Huella del dataset: {len(obj)} registros de PM2.5 por estación y año, coloreados según si "
                         "superaron el límite diario."),
            html.P(["Cada línea es una estación en un año. Rojo: al menos un día con PM2.5 sobre el límite diario. "
                    "Azul: ningún día. El ancho de cada año muestra cuánto creció la red."], className="hero-caption"),
            html.H1("Calidad del aire en Colombia, 2011–2024"),
            html.P("¿Qué estaciones superarán el límite diario de PM2.5? Este tablero explora los datos que usará el modelo "
                   "para predecirlo: qué tan confiables son, qué muestran y qué hay que corregir antes de entrenarlo."),
            dcc.Link("Empezar por el planteamiento", href="/introduccion", className="hero-cta"),
        ], className="hero"),

        html.Div([
            kpi(fmt(r["filas_unicas"], 0), "Registros únicos", f"de {fmt(r['filas_originales'], 0)} en el archivo"),
            kpi(str(r["estaciones"]), "Estaciones", f"{r['deptos']} departamentos"),
            kpi(f"{fmt(pm25['cambio'])} %", "Cambio del PM2.5 promedio", "entre 2011 y 2024"),
            kpi(f"{fmt(obj['Excede'].mean() * 100, 0)} %", "Registros que exceden", "el límite diario de PM2.5"),
        ], className="grid-4"),

        html.H2("El proyecto en cuatro etapas", className="section"),
        html.Section(html.Ol([
            html.Li([html.Span(str(i), className="n"), html.Strong(t), html.Span(d)],
                    className="actual" if actual else "")
            for i, (t, d, actual) in enumerate(ETAPAS, start=1)
        ], className="etapas"), className="card"),

        html.H2("Por dónde empezar", className="section"),
        html.Div([
            dcc.Link(html.Div([html.H4("Planteamiento"),
                               html.P("El problema, la norma de calidad del aire, la pregunta y los objetivos.")],
                              className="ruta-card"), href="/problema"),
            dcc.Link(html.Div([html.H4("Calidad de los datos"),
                               html.P("Duplicados, nombres inconsistentes, unidades y representatividad.")],
                              className="ruta-card"), href="/dataset"),
            dcc.Link(html.Div([html.H4("Variable objetivo"),
                               html.P("Qué es una excedencia, dónde ocurre y qué la predice.")],
                              className="ruta-card"), href="/variable-objetivo"),
            dcc.Link(html.Div([html.H4("Conclusiones"),
                               html.P("La respuesta a cada objetivo y lo que el modelo debe tener en cuenta.")],
                              className="ruta-card"), href="/conclusiones"),
        ], className="ruta"),
    ])
