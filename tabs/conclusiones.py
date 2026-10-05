"""tabs/conclusiones.py – Respuesta a la pregunta y a los objetivos de esta entrega."""

import pandas as pd
from dash import html, dcc

from components import encabezado, tarjeta, tabla, fmt
from data.data_loader import resumen_general, cambio_porcentual, objetivo_pm25

ACCIONES = pd.DataFrame([
    {"Problema encontrado": "Filas duplicadas (47 %)", "Acción en el preprocesamiento": "Eliminarlas (ya aplicado)"},
    {"Problema encontrado": "Nombres de departamento y municipio inconsistentes", "Acción en el preprocesamiento": "Normalizar sin tildes y en mayúsculas"},
    {"Problema encontrado": "Excedencias no confiables en registros de 1 hora", "Acción en el preprocesamiento": "Usar solo registros de 24 horas"},
    {"Problema encontrado": "Promedio, máximo, P98 y días de excedencias definen la respuesta", "Acción en el preprocesamiento": "Excluirlos: fuga de información"},
    {"Problema encontrado": "La excedencia depende de los días medidos", "Acción en el preprocesamiento": "Incluir «No. de datos» como control"},
    {"Problema encontrado": "El límite cambió en 2018 (50 → 37 µg/m³)", "Acción en el preprocesamiento": "Incluir el año como predictor"},
    {"Problema encontrado": "Una misma estación aparece en varios años", "Acción en el preprocesamiento": "Validar separando estaciones (GroupKFold)"},
    {"Problema encontrado": "Presión en hPa y RUVb con otra escala", "Acción en el preprocesamiento": "Corregir si se usa la meteorología"},
])


def layout():
    r = resumen_general()
    c = {v: cambio_porcentual(v)["cambio"] for v in ["PM10", "PM2.5", "NO2", "O3", "SO2"]}
    obj = objetivo_pm25()

    hallazgos = [
        ("Análisis exploratorio", "/dataset",
         f"El dataset requiere depuración: {fmt(r['pct_duplicados'])} % de filas duplicadas, {r['deptos_crudos']} nombres "
         f"para {r['deptos']} departamentos, presión en dos unidades y RUVb con dos escalas. La red se triplicó pero se "
         f"concentra en la región Andina. PM10 ({fmt(c['PM10'])} %) y PM2.5 ({fmt(c['PM2.5'])} %) bajaron; el ozono subió "
         f"({fmt(c['O3'])} %). La única correlación fuerte y confiable es PM10–PM2.5 (r = 0,97)."),
        ("Variable objetivo", "/variable-objetivo",
         f"La excedencia solo es confiable en los registros de 24 horas: {fmt(len(obj), 0)} registros de "
         f"{obj['Estación'].nunique()} estaciones, con clases balanceadas ({fmt(obj['Excede'].mean() * 100)} % excede). "
         "Aunque el promedio de PM2.5 bajó, la tasa de excedencia no disminuyó. La ubicación (Andes frente al Caribe), el "
         "tipo de estación y los días medidos son los factores que más se relacionan con ella."),
        ("Problemas para el modelo", "/conclusiones",
         "El preprocesamiento debe usar solo registros de 24 horas, excluir las variables que definen la respuesta (fuga de "
         "información), controlar el esfuerzo de medición y validar separando estaciones. La tabla de abajo resume cada acción."),
    ]

    return html.Div([
        encabezado("Cierre", "Conclusiones", "La respuesta a la pregunta de investigación y a los objetivos de esta entrega."),

        tarjeta(
            html.P("¿Es posible anticipar qué estaciones registrarán días con PM2.5 por encima del límite diario?",
                   className="pregunta"),
            html.P(["Sí. Las excedencias tienen un patrón claro: se concentran en las ciudades andinas (Bogotá 65 %, Antioquia "
                    "57 %), son raras en la costa Caribe (Córdoba 5 %) y son más frecuentes en estaciones fijas. Una prueba "
                    "preliminar con validación por estación alcanzó un ", html.Strong("AUC de 0,81"), ". Pero la información ",
                    html.Strong("requiere preprocesamiento antes de modelar"),
                    ": hay duplicados, nombres inconsistentes, errores de unidades, excedencias no confiables en los "
                    "registros horarios y una variable objetivo que depende del esfuerzo de medición."],
                   style={"marginTop": "16px"}),
            titulo="Respuesta a la pregunta de investigación",
        ),

        html.H2("Hallazgos por objetivo", className="section"),
        html.Div([
            html.Section(html.Div([
                html.Div(str(i), className="obj-num"),
                html.Div([html.H4(t), html.P(texto), dcc.Link("Ver evidencia", href=ruta, className="obj-link")]),
            ], className="obj-item"), className="card")
            for i, (t, ruta, texto) in enumerate(hallazgos, start=1)
        ], className="grid-3"),

        tarjeta(tabla(ACCIONES), titulo="Lo que el preprocesamiento debe resolver",
                subtitulo="Objetivo específico 3: cada problema encontrado y la acción que corresponde"),
    ])
