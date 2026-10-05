"""tabs/objetivo.py – Variable objetivo del modelo: excedencia diaria de PM2.5 (Objetivo específico 2)."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, Input, Output

from components import (encabezado, tarjeta, tabla, interpretacion, nota, kpi, grafico, estilo_figura,
                        fila, fmt, AZUL, TINTA, TINTA_2, TINTA_3)
from data.data_loader import objetivo_pm25, verificacion_excedencias

EXCEDE = "#a23b48"
NO_EXCEDE = "#8fbcce"

DIMENSIONES = {
    "Departamento": "Departamento",
    "Tipo de Estación": "Tipo de estación",
    "Cuartil de días medidos": "Días medidos en el año",
    "Región por latitud": "Región (latitud)",
}

TEXTOS = {
    "Departamento": [
        "Hay un contraste geográfico claro: Bogotá, Antioquia y Cundinamarca exceden con frecuencia, mientras que Córdoba, "
        "Magdalena y Bolívar casi no lo hacen.",
        "Una explicación física plausible: las ciudades andinas están en valles o altiplanos donde las inversiones térmicas y "
        "el poco viento atrapan los contaminantes; en la costa Caribe los vientos alisios favorecen la dispersión. La "
        "ubicación será uno de los predictores más importantes del modelo.",
    ],
    "Tipo de Estación": [
        "Las estaciones fijas exceden con mucha más frecuencia que las indicativas. Las fijas miden todo el año y suelen "
        "estar en zonas urbanas críticas; las indicativas son campañas cortas, con menos días para registrar una excedencia.",
    ],
    "Cuartil de días medidos": [
        "Es el hallazgo más importante para el modelo: mientras más días mide una estación, más probable es que capte al "
        "menos un día sobre el límite (de 21 % en el cuartil con menos días a 79 % en el de más días).",
        "La variable objetivo depende del esfuerzo de medición y no solo de la calidad del aire. El modelo debe incluir "
        "«No. de datos» como predictor de control, o confundirá «estación que mide mucho» con «estación contaminada».",
    ],
    "Región por latitud": [
        "El centro del país (entre 4° y 8° de latitud, donde están Bogotá y el Valle de Aburrá) concentra las excedencias. "
        "El sur y el Caribe exceden con mucha menos frecuencia.",
    ],
}

PREDICTORES = pd.DataFrame([
    {"Variable": "Latitud, longitud, departamento", "Uso": "Incluir", "Razón": "Fuerte contraste andino–Caribe"},
    {"Variable": "Tipo de estación", "Uso": "Incluir", "Razón": "Fijas exceden mucho más que indicativas"},
    {"Variable": "No. de datos, representatividad", "Uso": "Incluir (control)", "Razón": "Controlan el esfuerzo de medición"},
    {"Variable": "Año", "Uso": "Incluir", "Razón": "Captura el cambio de límite (2018) y la evolución de la red"},
    {"Variable": "Autoridad ambiental", "Uso": "Evaluar", "Razón": "Puede repetir la información de ubicación"},
    {"Variable": "Meteorología de la misma estación", "Uso": "Evaluar", "Razón": "Aporta física, pero solo ~30 % de las estaciones la mide"},
    {"Variable": "Promedio, mediana, P98, máximo, días de excedencias de PM2.5", "Uso": "Excluir", "Razón": "Fuga de información: definen la respuesta"},
])


def _fig_umbral(d):
    rng = np.random.default_rng(42)
    fig = go.Figure()
    for valor, color, nombre in [(0, NO_EXCEDE, "No excede"), (1, EXCEDE, "Excede")]:
        g = d[d["Excede"] == valor]
        fig.add_trace(go.Scattergl(
            x=g["Año"] + rng.uniform(-0.28, 0.28, len(g)), y=g["Máximo"], mode="markers", name=nombre,
            marker=dict(size=6, color=color, opacity=0.75, line=dict(color="white", width=0.5)),
            customdata=g[["Estación", "Municipio", "Año"]],
            hovertemplate="<b>%{customdata[0]}</b> · %{customdata[1]}<br>%{customdata[2]} · máximo diario %{y:.1f} µg/m³<extra></extra>"))
    fig.add_trace(go.Scatter(x=[2010.5, 2018.5, 2018.5, 2024.5], y=[50, 50, 37, 37], mode="lines", name="Límite diario",
                             line=dict(color=TINTA, width=2), hoverinfo="skip"))
    estilo_figura(fig, alto=420, leyenda=True)
    fig.update_xaxes(dtick=1, title=None)
    fig.update_yaxes(title="Máximo diario de PM2.5 (µg/m³)", range=[0, 150])
    fig.add_annotation(x=2011.2, y=50, text="Límite: 50 µg/m³", showarrow=False, yshift=12, xanchor="left",
                       font=dict(size=11, color=TINTA), bgcolor="rgba(255,255,255,.85)")
    fig.add_annotation(x=2024.4, y=37, text="37 µg/m³ desde julio de 2018", showarrow=False, yshift=-14, xanchor="right",
                       font=dict(size=11, color=TINTA), bgcolor="rgba(255,255,255,.85)")
    return fig


def _fig_anual(d):
    a = d.groupby("Año").agg(Tasa=("Excede", "mean"), n=("Excede", "size")).reset_index()
    fig = go.Figure(go.Bar(x=a["Año"], y=a["Tasa"] * 100, marker_color=EXCEDE, customdata=a["n"],
                           text=[f"{t * 100:.0f} %" for t in a["Tasa"]], textposition="outside", cliponaxis=False,
                           textfont=dict(size=11, color=TINTA_2),
                           hovertemplate="<b>%{x}</b><br>%{y:.0f} % de %{customdata} estaciones exceden<extra></extra>"))
    estilo_figura(fig, alto=320)
    fig.update_xaxes(dtick=1, title=None, tickangle=-45)
    fig.update_yaxes(title="Estaciones que exceden (%)", range=[0, 100])
    return fig


def _fig_mapa(d):
    e = d.groupby(["Estación", "Municipio"]).agg(Lat=("Latitud", "mean"), Lon=("Longitud", "mean"),
                                                Tasa=("Excede", "mean"), n=("Excede", "size")).reset_index()
    fig = go.Figure(go.Scattergeo(
        lat=e["Lat"], lon=e["Lon"], mode="markers",
        marker=dict(size=6 + e["n"] * 1.3, color=e["Tasa"] * 100, cmin=0, cmax=100,
                    colorscale=[[0, "#dbe8ee"], [0.5, "#d98a93"], [1, "#7d1f2c"]],
                    line=dict(color="white", width=0.6), opacity=0.9,
                    colorbar=dict(title="% años<br>con excedencia", thickness=10, len=0.6)),
        customdata=e[["Estación", "Municipio", "n"]],
        hovertemplate="<b>%{customdata[0]}</b> · %{customdata[1]}<br>%{marker.color:.0f} % de %{customdata[2]} años con excedencia<extra></extra>"))
    fig.update_geos(scope="south america", fitbounds="locations", showcountries=True, countrycolor="#cbd5e1", showland=True,
                    landcolor="#f6f8fa", showocean=True, oceancolor="#eef4f8", showlakes=False, resolution=50,
                    projection_type="mercator")
    fig.update_layout(height=520, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="white",
                      font=dict(family="Inter, Segoe UI, sans-serif", color=TINTA_2))
    return fig


def layout():
    d = objetivo_pm25()
    return html.Div([
        encabezado("Objetivo 2", "Variable objetivo: excedencia diaria de PM2.5",
                   "Lo que predecirá el modelo: ¿una estación tendrá en el año al menos un día con PM2.5 por encima del "
                   "límite diario de la Resolución 2254 de 2017?"),
        html.Div([
            kpi(fmt(len(d), 0), "Registros de 24 horas", f"{d['Estación'].nunique()} estaciones"),
            kpi(f"{fmt(d['Excede'].mean() * 100)} %", "Exceden el límite", "clases balanceadas"),
            kpi("37 µg/m³", "Límite diario actual", "50 µg/m³ hasta junio de 2018"),
            kpi("0,81", "AUC de la prueba rápida", "bosque aleatorio, validado por estación"),
        ], className="grid-4"),

        tarjeta(
            tabla(verificacion_excedencias(), decimales=1),
            interpretacion(
                "En los registros de 24 horas ninguna estación sin excedencias supera 50,2 µg/m³: la columna aplica el límite "
                "diario de la norma. En los de 1 hora hay estaciones con máximos de 3.608 µg/m³ que figuran sin excedencias; "
                "la norma no define un límite horario para PM2.5, así que esos registros no son confiables.",
                html.P([html.Strong("Decisión: "), "la variable objetivo se construye solo con los registros de 24 horas."]),
            ),
            titulo="¿Qué mide la columna de excedencias?",
            subtitulo="Verificación antes de definir la variable objetivo",
        ),

        tarjeta(
            grafico(_fig_umbral(d)),
            interpretacion(
                "Cada punto es una estación en un año. Los rojos (exceden) quedan por encima del límite y los azules por debajo, "
                "lo que confirma la definición. El límite bajó de 50 a 37 µg/m³ a mediados de 2018: la misma concentración "
                "puede ser excedencia después de 2018 y no antes. Por eso el año debe entrar al modelo.",
            ),
            titulo="Máximo diario de PM2.5 frente al límite de la norma",
            subtitulo="Pasa el cursor por los puntos para ver la estación",
        ),

        fila(
            tarjeta(
                grafico(_fig_anual(d)),
                interpretacion(
                    "La tasa de excedencia no baja con el tiempo: oscila entre 21 % (2011) y 69 % (2020). Aunque el promedio "
                    "de PM2.5 cayó 31 %, los días críticos siguen siendo frecuentes. Mejorar el promedio no elimina los episodios.",
                ),
                titulo="Estaciones que exceden el límite, por año",
            ),
            tarjeta(
                dcc.Graph(figure=_fig_mapa(d), config={"displaylogo": False, "topojsonURL": "/assets/topojson/"}),
                interpretacion("Las estaciones que exceden casi todos los años se concentran en el centro andino; las del "
                               "Caribe y el sur rara vez lo hacen. El tamaño del punto indica cuántos años reportó la estación."),
                titulo="Mapa de estaciones según frecuencia de excedencia",
            ),
        ),

        tarjeta(
            html.Div([html.Div([html.Label("Comparar según"),
                                dcc.Dropdown(id="obj-dim", value="Departamento", clearable=False,
                                             options=[{"label": v, "value": k} for k, v in DIMENSIONES.items()])],
                               className="control")], className="controls"),
            dcc.Graph(id="obj-barras", config={"displaylogo": False}),
            html.Div(id="obj-txt"),
            titulo="¿Qué se relaciona con la excedencia?",
            subtitulo="Porcentaje de registros que exceden el límite según cada predictor candidato",
        ),

        tarjeta(
            tabla(PREDICTORES),
            nota("Promedio, mediana, percentil 98, máximo y días de excedencias de PM2.5 se calculan con las mismas mediciones "
                 "que definen la excedencia. Usarlos como predictores sería fuga de información (data leakage): el modelo "
                 "acertaría aquí pero sería inútil en la práctica."),
            interpretacion("Con estos predictores, una prueba rápida con un bosque aleatorio y validación por estación (las "
                           "estaciones de entrenamiento y de prueba son distintas) alcanzó un AUC de 0,81. El problema es "
                           "viable; la etapa de modelado comparará algoritmos y evaluará qué aporta la meteorología."),
            titulo="Predictores candidatos para el modelo",
        ),
    ])


def register_callbacks(app):
    @app.callback(Output("obj-barras", "figure"), Output("obj-txt", "children"), Input("obj-dim", "value"))
    def _barras(dim):
        d = objetivo_pm25()
        g = d.groupby(dim).agg(Tasa=("Excede", "mean"), n=("Excede", "size")).reset_index()
        g = g[g["n"] >= 20]
        orden_natural = dim in ("Cuartil de días medidos", "Región por latitud")
        if orden_natural:
            g = g.sort_values(dim, key=lambda s: s.map({v: i for i, v in enumerate(
                ["Q1 · menos días", "Q2", "Q3", "Q4 · más días", "Sur (< 4°)", "Centro (4–6°)", "Centro-norte (6–8°)", "Caribe (> 8°)"])}))
        else:
            g = g.sort_values("Tasa")
        promedio = d["Excede"].mean() * 100
        fig = go.Figure(go.Bar(
            y=g[dim].astype(str).str.title() if dim == "Departamento" else g[dim].astype(str), x=g["Tasa"] * 100,
            orientation="h", marker_color=[EXCEDE if t * 100 >= promedio else NO_EXCEDE for t in g["Tasa"]],
            customdata=g["n"], text=[f"{t * 100:.0f} %" for t in g["Tasa"]], textposition="outside", cliponaxis=False,
            textfont=dict(size=11, color=TINTA_2),
            hovertemplate="<b>%{y}</b><br>%{x:.0f} % de %{customdata} registros exceden<extra></extra>"))
        fig.add_vline(x=promedio, line_dash="dot", line_color=TINTA_3,
                      annotation_text=f"Promedio {promedio:.0f} %", annotation_position="top",
                      annotation_font=dict(size=11, color=TINTA_2))
        estilo_figura(fig, alto=max(260, 34 * len(g) + 80))
        fig.update_xaxes(title="Registros que exceden el límite (%)", range=[0, 105])
        fig.update_yaxes(title=None, autorange="reversed" if orden_natural else True)
        fig.update_layout(margin=dict(l=10, r=40))
        texto = [*TEXTOS[dim], "Solo se muestran grupos con al menos 20 registros. Rojo: por encima del promedio nacional."]
        return fig, interpretacion(*texto)
