# ============================================
# Page Radar
# ============================================

# Importar librerías 
import streamlit as st
from PIL import Image
import difflib
import plotly.graph_objects as go
import numpy as np
from scipy import stats
import pandas as pd
import streamlit.components.v1 as components
from fpdf import FPDF
import io
import base64
import matplotlib.pyplot as plt

# Importar rutas de configuración
from common.config import (
    ASSETSIMG, ASSETSFONTS
)

# Importar funciones de datos y filtros
from controllers.db_controller import load_stats_players_fbref
from common.pdf_utils import get_watermark
from common.plots import generate_radar_matplotlib
from common.filters import apply_player_filters_radar
    
# Función que da cómo resultado la página Radar
def page_radar(): 
    
    # Añadir CSS de impresión
    st.markdown(
    """
    <style>

    /* estilos solo cuando se imprime */
    @media print {
        
        body {
            zoom: 0.7;
        }

        /* ocultar sidebar */
        section[data-testid="stSidebar"] {
            display: none;
        }

        /* ocultar menú superior de streamlit */
        header {
            display: none;
        }

        /* ocultar footer */
        footer {
            display: none;
        }

        /* expandir contenido principal */
        .main {
            margin-left: 0px;
            width: 100%;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
    )
    
    # Crear 3 columnas para centrar la imagen
    radar_imgcol1, radar_imgcol2, radar_imgcol3 = st.columns([3, 2, 3])
    
    with radar_imgcol2:
    
        # Cargar imagen desde la carpeta assets
        freepick_pieChart = Image.open(ASSETSIMG / "Freepick PieChart.png")
        
        # Mostrar imagen en Streamlit
        st.image(freepick_pieChart, width=120) 
    
    # Mostrar título de la página
    st.header("Player Performance Radar")  
    
    # Cargar datos desde la base de datos
    radar_df = load_stats_players_fbref()
    
    # Rellenar valores faltantes
    radar_df = radar_df.fillna(0)
        
    # Definir valores por defecto para session_state 
    radar_defaults = {
        "leagueA": "All",
        "teamA": "All",
        "posA": "All",
        "playerA": "Select",
        "leagueB": "All",
        "teamB": "All",
        "posB": "All",
        "playerB": "Select",
        "radar_do_reset": False,          
        "chart_type": "",
        "method": "",
        "typed_stat": "",           
        "selected_stats": [],       
        "is_mobile": False,         
    } 
    
    # Inicializar session_state si no existe
    for key, value in radar_defaults.items():
        if key not in st.session_state or st.session_state[key] is None:
            st.session_state[key] = value

    # Aplicar reset si está activado 
    if st.session_state["radar_do_reset"]:
        # Reiniciar filtros
        st.session_state["leagueA"] = "All"
        st.session_state["teamA"] = "All"
        st.session_state["posA"] = "All"
        st.session_state["playerA"] = "Select"
        st.session_state["leagueB"] = "All"
        st.session_state["teamB"] = "All"
        st.session_state["posB"] = "All"
        st.session_state["playerB"] = "Select"
        
        # Reiniciar input de stat
        st.session_state["typed_stat_radar"] = ""
        st.session_state["selected_stats_radar"] = []

        # Desactivar flag de reset
        st.session_state["radar_do_reset"] = False

        # Recargar página para actualizar widgets
        st.rerun()

    # Crear layout de la página
    radar_col1, radar_col2, radar_col3 = st.columns([1.5, 2.5, 1.5])

    # Definir orden de posiciones
    pos_order = ["GK", "DF", "MF", "FW"]

    # Construir formularios de jugadores A y B
    with radar_col1:
        st.subheader("Player A")

        # Aplicar filtros para jugador A y obtener DataFrame filtrado
        leagueA, teamA, posA, playersA_df = apply_player_filters_radar(
            df=radar_df,
            league_key="leagueA",
            team_key="teamA",
            pos_key="posA",
            league_label="League A",
            team_label="Team A",
            pos_label="Position A",
            pos_order=pos_order
        )

        # Agrupar jugadores y sumar minutos
        players_info_A = (
            playersA_df
            .groupby("Player", as_index=False)["stats_Min"]
            .sum()
        )

        # Crear etiqueta de jugador
        players_info_A["label"] = (
            players_info_A["Player"] + " | " +
            players_info_A["stats_Min"]
                .fillna(0)
                .round(0)
                .astype(int)
                .astype(str)
            + " min"
        )

        # Crear diccionario label → Player
        label_to_player_A = dict(zip(players_info_A["label"], players_info_A["Player"]))

        # Seleccionar jugador A
        playerA_label = st.selectbox(
            "Player A",
            ["Select"] + list(label_to_player_A.keys()),
            index=0,
            key="playerA"
        )

        playerA = label_to_player_A[playerA_label] if playerA_label != "Select" else None

    with radar_col3:
        st.subheader("Player B")

        # Aplicar filtros para jugador B y obtener DataFrame filtrado
        leagueB, teamB, posB, playersB_df = apply_player_filters_radar(
            df=radar_df,
            league_key="leagueB",
            team_key="teamB",
            pos_key="posB",
            league_label="League B",
            team_label="Team B",
            pos_label="Position B",
            pos_order=pos_order
        )

        # Agrupar jugadores y sumar minutos
        players_info_B = (
            playersB_df
            .groupby("Player", as_index=False)["stats_Min"]
            .sum()
        )

        # Crear etiqueta de jugador
        players_info_B["label"] = (
            players_info_B["Player"] + " | " +
            players_info_B["stats_Min"]
                .fillna(0)
                .round(0)
                .astype(int)
                .astype(str)
            + " min"
        )

        # Crear diccionario label → Player
        label_to_player_B = dict(zip(players_info_B["label"], players_info_B["Player"]))

        # Seleccionar jugador B
        playerB_label = st.selectbox(
            "Player B",
            ["Select"] + list(label_to_player_B.keys()),
            index=0,
            key="playerB"
        )

        playerB = label_to_player_B[playerB_label] if playerB_label != "Select" else None

    # Espacio para el gráfico
    with radar_col2:
        st.subheader("Pizza Chart")

        # Definir opciones con placeholder como primer valor
        chart_type_options = ["-- Select type --", "Compare Players", "The Best Player"]
        method_options = ["-- Select method --", "Standard", "Percentil"]

        # Crear selectboxes
        chart_type = st.selectbox("Select type of plot", chart_type_options, index=0, key="chart_type")
        method = st.selectbox("Select Method", method_options, index=0, key="method")

        # Convertir placeholder a None para lógica interna
        chart_type_val = None if chart_type == chart_type_options[0] else chart_type
        method_val = None if method == method_options[0] else method
        
        # Definir explicaciones según método
        method_explanations = {
            "Standard": "Shows the accumulated absolute values for each player. Reflects the total impact over the season, so it is strongly influenced by minutes played. Recommended for comparing players with a similar volume of minutes.",
            "Percentil": "Indicates the player's relative position (0–100) compared to other players in the same position and with similar minutes played. Allows evaluating performance within their actual role (starter, rotation, or substitute). A high percentile does not imply higher total impact, but better relative performance in context."
        }

        # Mostrar explicación si existe método seleccionado
        if method_val:
            st.info(method_explanations[method_val])
        
        # Crear placeholder del gráfico
        radar_placeholder = st.empty()

        st.info("Select up to 6 stats")

    # Seleccionar estadísticas a comparar
    st.subheader("Select statistics to compare (max 6)")

    # Crear input de estadística
    typed_stat_radar = st.text_input(
        "Write a stat:",
        value=st.session_state.get("typed_stat_radar", ""),
        placeholder="Write a stat..."
    )

    st.session_state["typed_stat_radar"] = typed_stat_radar

    st.caption("Categories: possession_, defense_, misc_, stats_, playingtime_, passing_, shooting_, gca_")

    # Inicializar lista de estadísticas seleccionadas si no existe
    if "selected_stats_radar" not in st.session_state:
        st.session_state["selected_stats_radar"] = []

    selected_stats = st.session_state["selected_stats_radar"]

    # Obtener columnas numéricas válidas
    common_stats = radar_df.select_dtypes(include="number").columns.tolist()
    common_stats = [c for c in common_stats if c not in ["stats_Min", "stats_Age"]]

    # Autocompletar estadísticas y permitir selección con botones
    if typed_stat_radar and common_stats:
        
        # Buscar coincidencias cercanas con lo escrito por el usuario
        closest = difflib.get_close_matches(typed_stat_radar, common_stats, n=6, cutoff=0.5)
        
        if closest:
            st.info("Select stat to add:")
            
            # Crear hasta 6 columnas de botones
            cols_btn = st.columns(min(len(closest), 6))
            
            for i, c in enumerate(closest[:6]):
                
                # Crear botón por cada estadística sugerida
                if cols_btn[i].button(c):
                    
                    # Añadir estadística si no existe y no se supera el límite
                    if c not in selected_stats and len(selected_stats) < 6:
                        selected_stats.append(c)
                        
                        # Actualizar session_state
                        st.session_state["selected_stats_radar"] = selected_stats
                        st.session_state["typed_stat_radar"] = ""  # Limpiar input tras añadir
                        
    # Mostrar estadísticas seleccionadas
    if selected_stats:
        st.success(f"Stats selected: {', '.join(selected_stats)}")

    # Generar radar si hay configuración completa
    if chart_type_val and selected_stats and playerA and playerB:

        # Definir parámetros visuales del radar
        RADAR_MAX = 100        # Definir límite máximo visual
        RADAR_PAD = 18         # Añadir espacio extra para textos
        TEXT_PAD = 6           # Definir separación texto-barra

        r_min_global = 0
        r_max_global = RADAR_MAX + RADAR_PAD

        rA_vals, rB_vals = [], []  # Inicializar valores normalizados
        textA, textB = [], []      # Inicializar textos de valores

        for stat in selected_stats:
            
            # Obtener valores de cada estadística para ambos jugadores
            valA = radar_df.loc[radar_df["Player"] == playerA, stat].values[0]
            valB = radar_df.loc[radar_df["Player"] == playerB, stat].values[0]

            # Obtener minutos jugados de ambos jugadores
            minA = radar_df.loc[radar_df["Player"] == playerA, "stats_Min"].values[0]
            minB = radar_df.loc[radar_df["Player"] == playerB, "stats_Min"].values[0]

            # Aplicar método Standard
            if method_val == "Standard":
                textA.append(f"{valA:.2f}")  
                textB.append(f"{valB:.2f}")

                stat_series = pd.to_numeric(radar_df[stat], errors="coerce")
                stat_min = stat_series.min()
                stat_max = stat_series.max()

                if stat_max > stat_min:
                    rA = (valA - stat_min) / (stat_max - stat_min) * 100
                    rB = (valB - stat_min) / (stat_max - stat_min) * 100
                else:
                    rA = rB = 0

                r_min, r_max = 0, 100

            # Aplicar método Percentil
            elif method_val == "Percentil":
                
                # Calcular promedio de minutos entre jugadores
                min_avg = (minA + minB) / 2

                # Filtrar base por minutos
                df_baseA = radar_df[radar_df["stats_Min"] >= min_avg]
                df_baseB = radar_df[radar_df["stats_Min"] >= min_avg]

                # Calcular percentiles
                rA = stats.percentileofscore(df_baseA[stat], valA, kind="rank") if not df_baseA.empty else 50
                rB = stats.percentileofscore(df_baseB[stat], valB, kind="rank") if not df_baseB.empty else 50
                
                # Guardar texto de percentiles
                textA.append(f"{rA:.0f}")
                textB.append(f"{rB:.0f}")

                r_min, r_max = 0, 100

            # Guardar valores normalizados
            rA_vals.append(rA)
            rB_vals.append(rB)

        # Definir ángulos del radar
        n = len(selected_stats)
        angles = np.linspace(0, 360, n, endpoint=False)
        widths = [360/n*0.9]*n

        # Crear figura de Plotly
        fig = go.Figure()

        # Seleccionar tipo de gráfico: comparación de jugadores
        if chart_type_val == "Compare Players":
            
            # Calcular opacidades dinámicas para resaltar al jugador dominante en cada estadística
            opacities_A = [0.85 if a >= b else 0.5 for a, b in zip(rA_vals, rB_vals)]
            opacities_B = [0.85 if b >= a else 0.5 for a, b in zip(rA_vals, rB_vals)]

            # Añadir barras polares del jugador A
            fig.add_trace(go.Barpolar(
                r=rA_vals,           
                base=[0] * n,          
                theta=angles,        
                width=widths,        
                name=playerA,        
                marker=dict(
                    color="#1f77b4",     
                    opacity=opacities_A 
                )
            ))
            
            # Añadir barras polares del jugador B
            fig.add_trace(go.Barpolar(
                r=rB_vals, 
                base=[0] * n,
                theta=angles, 
                width=widths,
                name=playerB, 
                marker=dict(
                    color="#d62728",     
                    opacity=opacities_B
                )
            ))

            # Añadir textos con valores de cada estadística
            ANGLE_OFFSET = 3  

            for i in range(n):
                
                # Añadir texto del jugador A
                fig.add_trace(go.Scatterpolar(
                    r=[min(rA_vals[i] + TEXT_PAD, RADAR_MAX + RADAR_PAD - 2)],  
                    theta=[angles[i] - ANGLE_OFFSET],  
                    mode="text", 
                    text=[textA[i]],                  
                    showlegend=False,                  
                    textfont=dict(size=11, color="#1f77b4")
                ))

                # Añadir texto del jugador B
                fig.add_trace(go.Scatterpolar(
                    r=[min(rB_vals[i] + TEXT_PAD, RADAR_MAX + RADAR_PAD - 2)],
                    theta=[angles[i] + ANGLE_OFFSET],  
                    mode="text",
                    text=[textB[i]],
                    showlegend=False,
                    textfont=dict(size=11, color="#d62728")
                ))

        # Seleccionar tipo de gráfico: mejor jugador por estadística
        elif chart_type_val == "The Best Player":
            
            # Inicializar set para controlar leyenda
            plotted_players = set()  

            for i in range(n):

                # Determinar jugador ganador en cada estadística
                if rA_vals[i] >= rB_vals[i]:
                    color, val, text = "#1f77b4", rA_vals[i], textA[i]
                    player_name = playerA
                else:
                    color, val, text = "#d62728", rB_vals[i], textB[i]
                    player_name = playerB

                # Controlar aparición de la leyenda por jugador
                show_legend = False
                if player_name not in plotted_players:
                    show_legend = True
                    plotted_players.add(player_name)

                # Añadir barra polar del jugador ganador en la estadística
                fig.add_trace(go.Barpolar(
                    r=[val], 
                    theta=[angles[i]], 
                    width=[widths[i]],
                    name=player_name, 
                    marker_color=color, 
                    opacity=0.85,
                    showlegend=show_legend
                ))
                
                # Añadir texto del valor del jugador ganador
                fig.add_trace(go.Scatterpolar(
                    r=[val + r_max_global * 0.05],   
                    theta=[angles[i]],
                    mode="text", 
                    text=[text], 
                    showlegend=False,
                    textfont=dict(size=11, color="black")
                ))

        # Configurar layout general del radar
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    range=[0, RADAR_MAX + RADAR_PAD],  
                    showticklabels=True,                
                    showline=False,                     
                    gridcolor="rgba(0,0,0,0.1)"       
                ),
                angularaxis=dict(
                    tickmode="array",
                    tickvals=angles,       
                    ticktext=selected_stats, 
                    showline=False
                )
            ),
            legend=dict(
                orientation="h",     
                yanchor="bottom",
                y=1.15,              
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=90, b=40)  
        )

        # Mostrar gráfico en Streamlit
        radar_placeholder.plotly_chart(fig, use_container_width=True)

    # Reiniciar formularios si se solicita
    if st.button("🔄 Reset Forms"):
        st.session_state["radar_do_reset"] = True  
        st.rerun()      

    # Renderizar botón de impresión
    components.html(
    """
    <button onclick="parent.window.print()" style="
        padding:8px 14px;
        font-size:14px;
        cursor:pointer;
        background-color:#2563eb;
        color:white;
        border:none;
        border-radius:6px;">
        🖨️ Print Page
    </button>
    """,
    height=55
    )                           

    # Generar PDF si se solicita y existen datos válidos
    if st.button("⚙️ Prepare PDF") and chart_type_val and playerA and playerB:

        # Generar figura Matplotlib del radar
        fig_mat = generate_radar_matplotlib(
            rA_vals=rA_vals,
            rB_vals=rB_vals,
            selected_stats=selected_stats,
            playerA=playerA,
            playerB=playerB,
            chart_type_val=chart_type_val,
            textA=textA,
            textB=textB
        )

        # Guardar figura en buffer como imagen PNG
        radar_buffer = io.BytesIO()
        fig_mat.savefig(radar_buffer, format="png", bbox_inches='tight', dpi=200)
        plt.close(fig_mat)          
        radar_buffer.seek(0)        

        # Crear documento PDF
        pdf_radar = FPDF()
        pdf_radar.add_page()

        # Configurar fuente del PDF
        pdf_radar.add_font("DejaVu", "", str(ASSETSFONTS / "DejaVuSans.ttf"), uni=True)
        pdf_radar.set_font("DejaVu", "", 12)

        # Generar título del PDF
        usuario_radar = st.session_state.get("user").username if st.session_state.get("user") else "Desconocido"
        title_radar = f"User: {usuario_radar} | Radar Type: {chart_type_val} | Method: {method_val or 'N/A'}"
        pdf_radar.multi_cell(0, 10, title_radar, align="C")
        pdf_radar.ln(5)             
        
        # Insertar imagen del radar en el PDF
        pdf_radar.image(radar_buffer, x=30, w=150)

        # Añadir marca de agua o logo
        logo_path_radar = get_watermark(alpha=10, user_obj=st.session_state.get("user"))
        pdf_radar.image(logo_path_radar, x=55, y=100, w=100)

        # Convertir PDF a bytes y codificar en base64
        pdf_bytes_radar = pdf_radar.output(dest="S")
        pdf_base64_radar = base64.b64encode(pdf_bytes_radar).decode("utf-8")

        # Crear botón de descarga del PDF
        components.html(
            f"""
            <a href="data:application/pdf;base64,{pdf_base64_radar}" download="radar.pdf">
                <button style="
                    padding:8px 14px;
                    font-size:14px;
                    cursor:pointer;
                    background-color:#dc2626;
                    color:white;
                    border:none;
                    border-radius:6px;">
                    📄 Export Radar to PDF
                </button>
            </a>
            """,
            height=55
        )