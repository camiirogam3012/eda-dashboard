"""tabs/problema.py"""

from dash import html

from components import encabezado, tarjeta, fmt
from data.data_loader import resumen_general


def layout():
    r = resumen_general()
    return html.Div([
        encabezado("Planteamiento", "Planteamiento del problema"),
        tarjeta(
            html.P("Colombia cuenta con más de una década de mediciones de calidad del aire, pero esa información "
                   "llega de decenas de autoridades con estaciones que entran y salen de operación, tiempos de "
                   "exposición distintos y criterios de registro no homogéneos. Antes de usarla para tomar "
                   "decisiones o construir modelos, hace falta saber qué contiene realmente, qué tan completa es "
                   "y qué patrones muestra."),
            html.P(["Sin esa caracterización se corre el riesgo de sacar conclusiones de artefactos de los datos. "
                    "Un ejemplo de este mismo dataset: los nombres de los departamentos aparecen escritos de varias formas, "
                    f"de modo que un conteo directo arroja {r['deptos_crudos']} departamentos cuando en realidad hay ",
                    html.Strong(str(r["deptos"])), "."]),
            titulo="Situación",
        ),
        tarjeta(
            html.P("¿Es posible anticipar, a partir de la ubicación, el tipo de estación y las características del monitoreo, "
                   "qué estaciones registrarán días con PM2.5 por encima del límite diario de la norma? Y, como paso previo, "
                   "¿qué tan confiable y representativa es la información disponible para construir ese modelo?",
                   className="pregunta"),
            html.P("Predecir las excedencias tiene valor práctico: permite priorizar dónde reforzar el monitoreo, emitir "
                   "alertas tempranas y focalizar medidas de control en las zonas con mayor riesgo para la salud.",
                   style={"marginTop": "14px"}),
            titulo="Pregunta de investigación",
        ),
        html.Div([
            tarjeta(html.Ul([
                html.Li("¿Qué problemas de calidad tiene el dataset y cómo afectan el análisis?"),
                html.Li("¿Dónde y cuándo se concentra el monitoreo?"),
                html.Li("¿Han disminuido o aumentado los contaminantes? ¿Están cerca de la norma?"),
            ]), titulo="Preguntas orientadoras (1)"),
            tarjeta(html.Ul([
                html.Li("¿Cómo varían las condiciones meteorológicas en el periodo?"),
                html.Li("¿Qué variables se asocian entre sí y qué tan confiables son esas asociaciones?"),
                html.Li("¿Hay valores extremos que puedan distorsionar los resultados?"),
                html.Li("¿Qué mide exactamente la variable objetivo y qué se relaciona con ella?"),
            ]), titulo="Preguntas orientadoras (2)"),
        ], className="grid-2"),
    ])
