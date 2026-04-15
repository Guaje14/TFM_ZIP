# ============================================
# Page Ranking
# ============================================

# Importar librerías 
import streamlit as st
from PIL import Image
import difflib
import pandas as pd
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
from controllers.db_controller import load_stats_players_fbref
from common.filters import apply_player_filters_overview_rk
from controllers.logs_export_csv import log_download_event

# Función que da cómo resultado la página Ranking
def page_rk():

    # Crear columnas para centrar la imagen
    rk_imgcol1, rk_imgcol2, rk_imgcol3 = st.columns([3, 2, 3])

    with rk_imgcol2:

        # Cargar imagen de cabecera desde assets
        rk_img_podium = Image.open(ASSETSIMG / "Freepick Podium.png")

        # Mostrar imagen en la interfaz
        st.image(rk_img_podium, width=120)

    # Mostrar título de la página
    st.header("Interactive Player Filtering")
    
    # Cargar dataset de jugadores
    rk_df_players = load_stats_players_fbref()

    # Definir valores por defecto de filtros
    rk_defaults = {
        "rk_age_filter": "All",
        "rk_pos_filter": "All",
        "rk_team_filter": "All",
        "rk_league_filter": "All",
        "rk_minutes_filter": 0,
        "rk_num_players_filter": 100,
        "rk_do_reset": False,
        "rk_typed_stat": "",
        "rk_selected_stat": None,
        "rk_user_league_filter": False
    }

    # Inicializar variables en session_state si no existen
    for key, value in rk_defaults.items():
        st.session_state.setdefault(key, value)

    # Reiniciar filtros si se activa el flag de reset
    if st.session_state["rk_do_reset"]:
        
        # Restaurar filtros a valores por defecto
        st.session_state["rk_age_filter"] = "All"
        st.session_state["rk_pos_filter"] = "All"
        st.session_state["rk_team_filter"] = "All"
        st.session_state["rk_league_filter"] = "All"
        st.session_state["rk_minutes_filter"] = 0
        st.session_state["rk_num_players_filter"] = 100
        st.session_state["rk_typed_stat"] = ""
        st.session_state["rk_selected_stat"] = None
        st.session_state["rk_user_league_filter"] = False

        # Desactivar bandera de reset
        st.session_state["rk_do_reset"] = False

        # Recargar aplicación
        st.rerun()

    # Crear layout de filtros principales
    rk_col1, rk_col2, rk_col3, rk_col4, rk_col5, rk_col6 = st.columns([2,2,2,2,2,2])

    # Aplicar filtros reutilizables de jugadores
    df_rk = apply_player_filters_overview_rk(
        rk_df_players,
        rk_col1,
        rk_col2,
        rk_col3,
        rk_col4,
        rk_col5,
        prefix="rk",
        checkbox=True
    )

    # Crear slider para limitar número de jugadores
    with rk_col6:

        rk_num_players = st.slider(
            "N° Players",
            0,
            100,
            key="rk_num_players_filter"
        )

    # Limitar número de jugadores mostrados
    rk_filtered_df = df_rk.head(rk_num_players)

    # Crear input para definir estadística de ranking
    rk_typed_stat = st.text_input(
        "Enter the stat to sort:",
        value=st.session_state["rk_typed_stat"],
        placeholder="Write a stat..."
    )

    # Mostrar categorías de estadísticas disponibles
    st.caption(
        "Categories: possession_, defense_, misc_, stats_, playingtime_, passing_, shooting_, gca_"
    )

    # Guardar input en session_state
    st.session_state["rk_typed_stat"] = rk_typed_stat

    # Obtener columnas numéricas del dataset
    rk_all_stats = rk_df_players.select_dtypes(include="number").columns.tolist()
    
    # Generar sugerencias de estadística si el usuario escribe algo
    if rk_typed_stat:
        
        rk_closest = difflib.get_close_matches(
            rk_typed_stat,
            rk_all_stats,
            n=7,
            cutoff=0.7
        )

        if rk_closest:

            # Mostrar sugerencias disponibles
            st.info("Select stat:")

            # Adaptar UI según dispositivo
            if st.session_state["is_mobile"]:

                # Mostrar selectbox en móvil
                rk_selected = st.selectbox(
                    "Suggestions",
                    rk_closest,
                    index=None,
                    placeholder="Select stat..."
                )

                if rk_selected:
                    st.session_state["rk_selected_stat"] = rk_selected
                    st.session_state["rk_typed_stat"] = rk_selected

            else:

                # Mostrar botones en escritorio
                rk_cols_btn = st.columns(min(len(rk_closest), 6))

                for i, c in enumerate(rk_closest[:6]):

                    if rk_cols_btn[i].button(c):
                        st.session_state["rk_selected_stat"] = c
                        st.session_state["rk_typed_stat"] = c

    # Obtener estadística seleccionada final
    rk_stat_col = st.session_state["rk_selected_stat"]

    # Mostrar estadística seleccionada
    if rk_stat_col:
        st.success(f"Will be used: **{rk_stat_col}**")

    # Generar ranking según estadística seleccionada
    if rk_stat_col and rk_stat_col in rk_filtered_df.columns:

        rk_filtered_df["rk_rank_num"] = rk_filtered_df[rk_stat_col].rank(
            ascending=False,
            method="min"
        )

    else:

        # Usar primera columna numérica si no hay estadística seleccionada
        rk_num_cols = rk_filtered_df.select_dtypes(include="number").columns.tolist()

        if rk_num_cols:

            rk_filtered_df["rk_rank_num"] = rk_filtered_df[rk_num_cols[0]].rank(
                ascending=False,
                method="min"
            )

        else:

            # Asignar ranking secuencial si no hay datos numéricos
            rk_filtered_df["rk_rank_num"] = range(1, len(rk_filtered_df)+1)

    # Ordenar DataFrame por ranking
    rk_filtered_df = rk_filtered_df.sort_values("rk_rank_num")
    
    # Función para convertir ranking en emoji
    def rk_ranking_emoji(r):
        if r == 1:
            return "🥇"
        elif r == 2:
            return "🥈"
        elif r == 3:
            return "🥉"
        else:
            return int(r)

    # Aplicar formato visual al ranking
    rk_filtered_df["Rk"] = rk_filtered_df["rk_rank_num"].apply(rk_ranking_emoji)

    # Reordenar columnas para mostrar ranking primero
    rk_cols = rk_filtered_df.columns.tolist()
    rk_cols.insert(0, rk_cols.pop(rk_cols.index("Rk")))
    rk_filtered_df = rk_filtered_df[rk_cols]

    # Eliminar columna auxiliar de ranking
    rk_filtered_df = rk_filtered_df.drop(columns=["rk_rank_num"])

    # Insertar separador visual
    st.divider()

    # Mostrar tabla interactiva de jugadores
    st.dataframe(
        rk_filtered_df,
        hide_index=True,
        column_config={
            "Rk": st.column_config.Column(pinned="left"),
            "Player": st.column_config.Column(pinned="left"),
        }
    )
    
    # Exportar datos a CSV
    csv_buffer = io.StringIO()
    rk_filtered_df.to_csv(csv_buffer, index=False)

    # Crear botón de descarga con logging
    st.download_button(
        label="📥 Download CSV",
        data=csv_buffer.getvalue(),
        file_name="players_ranking.csv",
        mime="text/csv",
        on_click=log_download_event,
        kwargs={
            "page_name": "ranking",
            "prefix": "rk",
            "extra_data": {
                "selected_stat": st.session_state.get("rk_selected_stat")
            }
        }
    )
        
    # Reiniciar filtros si se solicita
    if st.button("🔄 Reset filters"):

        # Activar flag de reset
        st.session_state["rk_do_reset"] = True

        # Recargar aplicación
        st.rerun()
        
    # Insertar separador visual
    st.divider()

    # Generar mapa de nacionalidades
    fig_map = plot_nationality_choropleth(df_rk)
    st.plotly_chart(fig_map, use_container_width=True)

    # Insertar separador visual
    st.divider()

    # Crear layout de gráficos
    plots_ovierview_col1, plots_ovierview_col2, plots_ovierview_col3, plots_ovierview_col4, plots_ovierview_col5 = st.columns([2.3, 0.7, 2, 0.7, 2.5])

    # Mostrar distribución de edad
    with plots_ovierview_col1:
        fig_age = plot_age_distribution(df_rk)
        st.plotly_chart(fig_age, use_container_width=True)

    # Mostrar distribución de posición
    with plots_ovierview_col3:
        fig_pos = plot_positions(df_rk)
        st.plotly_chart(fig_pos, use_container_width=True)

    # Mostrar distribución de competición
    with plots_ovierview_col5:
        fig_comp = plot_competitions_pie(df_rk)
        st.plotly_chart(fig_comp, use_container_width=True)