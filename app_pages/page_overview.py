# ============================================
# Page Overview
# ============================================

# Importar librerías 
import streamlit as st
from PIL import Image
import io

# Importar rutas de configuración
from common.config import (
    ASSETSIMG
)

# Importar funciones para generar plots
from common.plots import (
    plot_nationality_choropleth,
    plot_competitions_pie,
    plot_age_distribution,
    plot_positions
)

# Importar funciones de datos y filtros
from controllers.db_controller import load_stats_players_fbref, load_stats_players_fbref_with_score_table
from common.filters import apply_player_filters
from controllers.logs_export_csv import log_download_event

# Función que da cómo resultado la página Overview
def page_overview():

    # Crear columnas para centrar la imagen
    overview_imgcol1, overview_imgcol2, overview_imgcol3 = st.columns([3, 2, 3])

    with overview_imgcol2:

        # Cargar imagen de cabecera desde assets
        overview_img_filter = Image.open(ASSETSIMG / "Freepick Filter.png")

        # Mostrar imagen en la interfaz
        st.image(overview_img_filter, width=120)

    # Mostrar título de la página
    st.header("Player Visualization and Filtering")
    
    # Selector único para decidir qué dataset cargar
    overview_score_mode = st.selectbox(
        "Score mode",
        options = [
            "No score",
            "Official score (1500+ min)",
            "Extended score (all sample)"
        ],
        index = 0,
        key = "overview_score_mode"
    )

    # Cargar dataset según la opción elegida
    if overview_score_mode == "No score":
        overview_df_players = load_stats_players_fbref()

    elif overview_score_mode == "Official score (1500+ min)":
        overview_df_players = load_stats_players_fbref_with_score_table(
            table_name = "player_scores_pca_train1500"
        )

    else:
        overview_df_players = load_stats_players_fbref_with_score_table(
            table_name = "player_scores_pca"
        )
    
    # Definir valores por defecto de los filtros
    overview_defaults = {
        "overview_age_filter": "All",
        "overview_pos_filter": "All",
        "overview_team_filter": "All",
        "overview_league_filter": "All",
        "overview_minutes_filter": 0,
        "overview_num_players_filter": 100,
        "overview_do_reset": False,
    }

    # Inicializar filtros en session_state si no existen
    for key, value in overview_defaults.items():
        st.session_state.setdefault(key, value)

    # Verificar si se ha activado el reset de filtros
    if st.session_state["overview_do_reset"]:

        # Restaurar filtros a valores por defecto
        st.session_state["overview_age_filter"] = "All"
        st.session_state["overview_pos_filter"] = "All"
        st.session_state["overview_team_filter"] = "All"
        st.session_state["overview_league_filter"] = "All"
        st.session_state["overview_minutes_filter"] = 0
        st.session_state["overview_num_players_filter"] = 100

        # Desactivar flag de reset
        st.session_state["overview_do_reset"] = False

        # Recargar aplicación
        st.rerun()

    # Crear layout de filtros
    overview_col1, overview_col2, overview_col3, overview_col4, overview_col5, overview_col6 = st.columns([2,2,2,2,2,2])

    # Aplicar filtros de jugadores reutilizables
    df_overview = apply_player_filters(
        overview_df_players,
        overview_col1,
        overview_col2,
        overview_col3,
        overview_col4,
        overview_col5,
        prefix="overview",
        checkbox=False
    )

    # Crear slider para limitar número de jugadores
    with overview_col6:

        overview_num_players = st.slider(
            "N° Players",
            0,
            100,
            key="overview_num_players_filter"
        )

    # Limitar número de jugadores mostrados
    overview_filtered_df = df_overview.head(overview_num_players)

    # Separar visualmente sección de tabla
    st.divider()

    # Mostrar tabla interactiva de jugadores
    st.dataframe(
        overview_filtered_df,
        hide_index=True,

        # Configurar columnas fijas para mejor UX
        column_config={
            "Id_player": st.column_config.Column(pinned="left"),
            "Player": st.column_config.Column(pinned="left"),
        }
    )

    # Crear buffer CSV en memoria
    csv_buffer = io.StringIO()
    overview_filtered_df.to_csv(csv_buffer, index=False)

    # Crear botón de descarga de datos
    st.download_button(
        label="📥 Download CSV",
        data=csv_buffer.getvalue(),
        file_name="players_overview.csv",
        mime="text/csv",
        on_click=log_download_event,
        kwargs={
            "page_name": "overview",
            "prefix": "overview"
        }
    )

    # Activar reset de filtros
    if st.button("🔄 Reset filters"):

        # Activar flag de reinicio
        st.session_state["overview_do_reset"] = True

        # Recargar aplicación
        st.rerun()

    # Separar visualmente sección de gráficos
    st.divider()

    # Generar mapa de nacionalidades
    fig_map = plot_nationality_choropleth(df_overview)
    st.plotly_chart(fig_map, use_container_width=True)

    # Separar sección de gráficos secundarios
    st.divider()

    # Crear layout de gráficos
    plots_ovierview_col1, plots_ovierview_col2, plots_ovierview_col3, plots_ovierview_col4, plots_ovierview_col5 = st.columns([2.3, 0.7, 2, 0.7, 2.5])

    # Mostrar distribución de edades
    with plots_ovierview_col1:
        fig_age = plot_age_distribution(df_overview)
        st.plotly_chart(fig_age, use_container_width=True)

    # Mostrar distribución por posición
    with plots_ovierview_col3:
        fig_pos = plot_positions(df_overview)
        st.plotly_chart(fig_pos, use_container_width=True)

    # Mostrar distribución por competición
    with plots_ovierview_col5:
        fig_comp = plot_competitions_pie(df_overview)
        st.plotly_chart(fig_comp, use_container_width=True)