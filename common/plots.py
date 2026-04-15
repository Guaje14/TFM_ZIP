# ============================================
# Common -> plots
# ============================================

# Importar librerías
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pycountry
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Función para generar un radar según el tipo y método seleccionado
def generate_radar_matplotlib(rA_vals, rB_vals, selected_stats, playerA, playerB, chart_type_val, textA, textB):

    # Obtener número de estadísticas a representar en el radar
    n = len(selected_stats)

    # Generar ángulos equiespaciados para distribuir las variables en círculo
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)

    # Calcular ancho de cada barra del radar (ligeramente reducido para separación visual)
    width = (2*np.pi / n) * 0.9

    # Crear figura y eje en coordenadas polares
    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))

    # Si el tipo de gráfico es comparar jugadores
    if chart_type_val == "Compare Players":
        
        for i in range(n):
            
            # Dibujar barra para el jugador A
            ax.bar(
                angles[i],
                rA_vals[i],
                width=width,
                color="#1f77b4",
                alpha=0.6
            )

            # Dibujar barra para el jugador B
            ax.bar(
                angles[i],
                rB_vals[i],
                width=width,
                color="#d62728",
                alpha=0.6
            )

            # Añadir etiquetas para el jugador A
            ax.text(
                angles[i],
                rA_vals[i] + 5,
                textA[i],
                color="#1f77b4",
                fontsize=9,
                ha="center"
            )

            # Añadir etiquetas para el jugador B
            ax.text(
                angles[i],
                rB_vals[i] + 10,
                textB[i],
                color="#d62728",
                fontsize=9,
                ha="center"
            )

        # Leyenda dummy para colores de jugadores
        ax.bar(0, 0, color="#1f77b4", label=playerA)
        ax.bar(0, 0, color="#d62728", label=playerB)

    # Si el tipo de gráfico es "El mejor jugador" (selecciona solo la mejor barra)
    elif chart_type_val == "The Best Player":
        
        # Crear conjunto para evitar duplicar etiquetas en la leyenda
        plotted = set() 

        for i in range(n):
            
            # Seleccionar el jugador con mejor valor en cada estadística
            if rA_vals[i] >= rB_vals[i]:
                val = rA_vals[i]
                color = "#1f77b4"
                name = playerA
                text = textA[i]
            else:
                val = rB_vals[i]
                color = "#d62728"
                name = playerB
                text = textB[i]

            # Añadir etiqueta solo la primera vez que aparece cada jugador
            label = name if name not in plotted else None
            plotted.add(name)

            # Dibujar barra del jugador dominante en esa estadística
            ax.bar(
                angles[i],
                val,
                width=width,
                color=color,
                alpha=0.8,
                label=label
            )

            # Añadir valor numérico sobre la barra# Añadir texto sobre la barra
            ax.text(
                angles[i],
                val + 5,
                text,
                color="black",
                fontsize=9,
                ha="center"
            )

    # Definir posiciones de las etiquetas en el eje angular
    ax.set_xticks(angles)

    # Asignar nombres de las estadísticas al eje angular
    ax.set_xticklabels(selected_stats, fontsize=10)

    # Ajustar separación de etiquetas respecto al gráfico
    ax.tick_params(axis='x', pad=35)

    # Definir ticks del eje radial en intervalos de 20
    ax.set_yticks(range(0, 101, 20))

    # Fijar rango del radar de 0 a 100
    ax.set_ylim(0, 100)

    # Activar cuadrícula del gráfico
    ax.grid(True)

    # Configurar leyenda centrada en la parte superior del gráfico
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.15),
        ncol=2,
        frameon=False
    )

    # Devolver figura final generada
    return fig

# Añadir códigos ISO
COUNTRY_MAP = {
    "ENG": "GBR",
    "SCO": "GBR",
    "WAL": "GBR",
    "NIR": "GBR",
    "GER": "DEU",
    "DEN": "DNK",
    "SUI": "CHE",
    "CZE": "CZE",
    "SVK": "SVK",
    "CIV": "CIV",
    "COD": "COD",
    "CGO": "COG",
    "USA": "USA",
    "KOR": "KOR",
    "KVX": "XKX",
}

# Función para convertir un código de país en su código ISO3 
@st.cache_data(show_spinner=False)
def get_iso3(code):

    # Validar si el código de país es nulo o inexistente
    if pd.isna(code):
        return None

    # Comprobar si el código existe en el diccionario manual de países
    if code in COUNTRY_MAP:
        
        # Devolver directamente el código ISO3 desde el mapeo manual
        return COUNTRY_MAP[code]

    try:
        # Intentar resolver el código de país usando la librería pycountry
        return pycountry.countries.lookup(code).alpha_3
    
    except:
        # Capturar cualquier error de resolución del país
        return None

# Función para generar el Plot del Choropleth (mapa de distribución por nacionalidad)
def plot_nationality_choropleth(df: pd.DataFrame):

    # Crear copia del dataframe para evitar modificar el original
    df = df.copy()
    
    # Verificar si el dataframe está vacío para evitar errores en el gráfico
    if df.empty:
        return go.Figure()

    # Contar número de jugadores por nacionalidad
    nat_counts = df["stats_Nation"].value_counts().reset_index()

    # Renombrar columnas para estandarizar el formato
    nat_counts.columns = ["stats_Nation", "count"]

    # Convertir nombres de nacionalidades a códigos ISO3
    nat_counts["iso"] = nat_counts["stats_Nation"].apply(get_iso3)

    # Eliminar filas donde no se haya podido obtener el código ISO válido
    nat_counts = nat_counts.dropna(subset=["iso"])

    # Validar nuevamente si quedan datos después del filtrado
    if nat_counts.empty:
        return go.Figure()

    # Obtener el valor máximo de jugadores por país (para escalado visual)
    max_count = nat_counts["count"].max()

    # Crear figura principal del mapa
    fig = go.Figure()

    # Capa base del mapa 
    fig.add_trace(
        go.Choropleth(
            locations=nat_counts["iso"],
            
            # Asignar valor constante para crear base visual neutra
            z=[1] * len(nat_counts),

            # Definir escala de color prácticamente transparente
            colorscale=[[0, "rgba(255,255,255,0.01)"], [1, "rgba(255,255,255,0.01)"]],

            # Ocultar barra de color
            showscale=False,

            # Configurar bordes de países
            marker_line_color="rgba(255,255,255,0.8)",
            marker_line_width=0.4,

            # Desactivar tooltip en capa base
            hoverinfo="skip"
        )
    )

    # Capa de puntos 
    fig.add_trace(
        go.Scattergeo(
            locationmode="ISO-3",
            locations=nat_counts["iso"],
            
            # Usar nombre de país como texto de hover
            text=nat_counts["stats_Nation"],
            
            # Definir modo de visualización como puntos
            mode="markers",

            # Configurar tamaño y color de los puntos según número de jugadores
            marker=dict(
                size=nat_counts["count"],
                sizemode="area",

                # Escalar tamaños para evitar sobreposición excesiva
                sizeref=2. * max_count / (30.**2),

                # Usar color variable según cantidad de jugadores
                color=nat_counts["count"],
                colorscale="Turbo",

                # Ajustar transparencia de los puntos
                opacity=0.95,

                # Añadir borde visual a los puntos
                line=dict(width=0.4, color="rgba(255,255,255,0.6)")
            ),

            # Configurar tooltip personalizado
            hovertemplate="<b>%{text}</b><br>Players: %{marker.color}<extra></extra>"
        )
    )

    # Configuración del mapa 
    fig.update_geos(
        showframe=False,        
        showcoastlines=False,   
        showcountries=False,    
        showland=False,         
        showocean=False,       
        bgcolor="rgba(0,0,0,0)" 
    )

    # Layout general del gráfico
    fig.update_layout(
        title="Players by Nationality",
        
        # Configurar estilo de fuente global
        font=dict(color="white"),

        # Definir fondo transparente del canvas
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        # Ajustar márgenes del gráfico
        margin=dict(l=0, r=0, t=40, b=0)
    )

    return fig

# Función para generar el Plot de la Distribución de competiciones
def plot_competitions_pie(df: pd.DataFrame):

    # Crear una copia del dataframe
    df = df.copy()
    
    # Separar múltiples competiciones por jugador y contarlas
    comp_counts = (
        df["stats_Comp"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .reset_index()
    )
    comp_counts.columns = ["competition", "count"]

    # Generar gráfico tipo pie chart con agujero central
    fig = px.pie(
        comp_counts,
        names="competition",
        values="count",
        hole=0.4,
        title="Players by Competition"
    )

    # Aplicar estilo general al gráfico
    fig.update_layout(
        font=dict(color="white"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            itemwidth=40
        ),
        height=400
    )

    # Establecer color del texto dentro del gráfico
    fig.update_traces(textfont_color="white")

    return fig

# Función para generar el Plot del Historiograma de edades de los jugadores
def plot_age_distribution(df: pd.DataFrame):

    # Crear una copia del dataframe
    df = df.copy()

    # Convertir edad a numérico para asegurar consistencia
    df["stats_Age"] = pd.to_numeric(df["stats_Age"], errors="coerce")

    # Eliminar valores nulos y filtrar jugadores menores de 16 años
    df = df.dropna(subset=["stats_Age"])
    df = df[df["stats_Age"] >= 16]

    # Contar jugadores por edad
    age_counts = (
        df["stats_Age"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    age_counts.columns = ["age", "count"]

    # Obtener valor máximo de frecuencia
    y_max = age_counts["count"].max()

    # Generar gráfico de barras
    fig = px.bar(
        age_counts,
        x="age",
        y="count",
        text="count",
        title="Age Distribution of Players"
    )

    # Aplicar estilo a las barras
    fig.update_traces(
        marker=dict(color="lightgray", line=dict(color="white", width=1)),
        textposition="outside"
    )

    # Configurar layout general
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Age",
        yaxis_title="Number of Players",
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=False,
            range=[0, y_max * 1.15]
        ),
        height=400
    )

    return fig

# Función para generar el Plot de la Distribución de posiciones 
def plot_positions(df: pd.DataFrame):

    # Crear copia del dataframe
    df = df.copy()
    
    # Definir orden lógico de posiciones
    pos_order = ["GK", "DF", "MF", "FW"]

    # Contar jugadores por posición
    pos_counts = df["stats_Pos"].value_counts().reset_index()
    pos_counts.columns = ["position", "count"]

    # Convertir a categoría ordenada
    pos_counts["position"] = pd.Categorical(
        pos_counts["position"],
        categories=pos_order,
        ordered=True
    )

    # Ordenar según orden definido
    pos_counts = pos_counts.sort_values("position")
    
    # Obtener valor máximo de frecuencia
    y_max = pos_counts["count"].max()

    # Generar gráfico de barras
    fig = px.bar(
        pos_counts,
        x="position",
        y="count",
        text="count",
        title="Players by Position"
    )

    # Aplicar estilo a las barras
    fig.update_traces(
        marker=dict(color="lightgray", line=dict(color="white", width=1)),
        textposition="outside"
    )

    # Configurar layout general
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Position",
        yaxis_title="Number of Players",
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=False,
            range=[0, y_max * 1.15]  
        ),
        height=400
    )

    return fig