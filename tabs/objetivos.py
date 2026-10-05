"""tabs/objetivos.py"""

from dash import html, dcc

from components import encabezado

OBJETIVOS = [
    ("Realizar el análisis exploratorio",
     "Evaluar la calidad del dataset y caracterizar la cobertura del monitoreo, los contaminantes, la meteorología, "
     "sus asociaciones y sus valores atípicos.",
     "/dataset", "Dataset, exploración, contaminantes, meteorología, correlaciones y atípicos", True),
    ("Caracterizar la variable objetivo",
     "Definir la excedencia del límite diario de PM2.5 y estudiar su relación con los posibles predictores.",
     "/variable-objetivo", "Variable objetivo", True),
    ("Identificar los problemas de los datos",
     "Señalar lo que debe resolver el preprocesamiento antes de entrenar el modelo, incluida la fuga de información.",
     "/conclusiones", "Conclusiones", True),
    ("Entrenar y comparar modelos de clasificación",
     "Comparar algoritmos con validación por estación y reportar AUC, recall y matriz de confusión.",
     None, "Siguiente etapa", False),
    ("Construir el dashboard final",
     "Integrar el análisis exploratorio y el modelo para estimar el riesgo de excedencia de una estación.",
     None, "Siguiente etapa", False),
]


def layout():
    return html.Div([
        encabezado("Planteamiento", "Objetivos",
                   "Lo que el proyecto se propone lograr. Esta entrega cubre los tres primeros objetivos específicos."),
        html.Div([
            html.Div("Objetivo general", className="eyebrow"),
            html.P("Desarrollar un modelo de clasificación que prediga si una estación de monitoreo registrará excedencias "
                   "del límite diario de PM2.5 establecido en la Resolución 2254 de 2017, e integrarlo en un dashboard "
                   "interactivo, a partir del análisis exploratorio de los datos de calidad del aire de Colombia (2011–2024)."),
        ], className="obj-general"),

        html.H2("Objetivos específicos", className="section"),
        html.Div([
            html.Section(html.Div([
                html.Div(str(i), className="obj-num"),
                html.Div([
                    html.H4(t), html.P(d),
                    dcc.Link(f"Ver en: {seccion}", href=ruta, className="obj-link") if ruta
                    else html.Span(seccion, className="chip"),
                ]),
            ], className="obj-item"), className="card" if activo else "card card-futuro")
            for i, (t, d, ruta, seccion, activo) in enumerate(OBJETIVOS, start=1)
        ], className="grid-2"),
    ])
