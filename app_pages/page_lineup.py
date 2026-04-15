# ============================================
# Page Lineup
# ============================================

# Importar librerías 
import streamlit as st
import pandas as pd
import os
from PIL import Image
import matplotlib.pyplot as plt
import uuid  
import base64
import streamlit.components.v1 as components
from fpdf import FPDF
from io import BytesIO

# Importar rutas de configuración
from common.config import (
    ASSETSIMG, DATA_DIR, ASSETSFONTS
)

# Importar funciones de datos y marca de agua
from controllers.db_controller import load_stats_players_fbref
from common.pdf_utils import get_watermark
    
# Función que da cómo resultado la página Lineup
def page_lineup():
    
    # Se define la ruta del archivo "lineups_register.xlsx" 
    filename = DATA_DIR / "lineups_register.xlsx"
    
    # Verificar existencia del archivo y cargar datos o inicializar DataFrame vacío
    if os.path.exists(filename):
        df_save = pd.read_excel(filename, engine="openpyxl")
    else:
        df_save = pd.DataFrame()
                
    # Añadir estilos CSS para impresión
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
    
    # Crear columnas para centrar la imagen
    lineup_imgcol1, lineup_imgcol2, lineup_imgcol3 = st.columns([3, 2, 3])

    with lineup_imgcol2:

        # Cargar imagen desde la carpeta de assets
        lineup_img_header = Image.open(ASSETSIMG / "Freepick Select.png")
        
        # Mostrar imagen en la aplicación
        st.image(lineup_img_header, width=120)

    # Mostrar título de la página
    st.header("Weekly Best XI")

    # Cargar datos de jugadores desde la base de datos
    lineup_df_players = load_stats_players_fbref()

    # Definir lista de sistemas tácticos disponibles
    lineup_sistemas = [
        "1-4-4-2","1-4-3-3","1-3-5-2","1-4-2-3-1","1-5-3-2",
        "1-4-3-2-1","1-3-4-3","1-4-1-4-1","1-3-6-1","1-4-5-1"
    ]

    # Definir coordenadas normalizadas para cada sistema táctico
    lineup_posiciones = {

        "1-4-4-2": [
            (0.5, 0.1),                                   # GK
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),      # DEF
            (0.2,0.5),(0.4,0.5),(0.6,0.5),(0.8,0.5),      # MID
            (0.4,0.7),(0.6,0.7)                           # FW
        ],

        "1-4-3-3": [
            (0.5,0.1),
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),
            (0.3,0.5),(0.5,0.5),(0.7,0.5),
            (0.25,0.75),(0.5,0.8),(0.75,0.75)
        ],

        "1-3-5-2": [
            (0.5,0.1),
            (0.3,0.3),(0.5,0.3),(0.7,0.3),
            (0.15,0.5),(0.35,0.5),(0.5,0.5),(0.65,0.5),(0.85,0.5),
            (0.4,0.75),(0.6,0.75)
        ],

        "1-4-2-3-1": [
            (0.5,0.1),
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),
            (0.4,0.45),(0.6,0.45),
            (0.3,0.65),(0.5,0.7),(0.7,0.65),
            (0.5,0.85)
        ],

        "1-5-3-2": [
            (0.5,0.1),
            (0.1,0.3),(0.3,0.3),(0.5,0.3),(0.7,0.3),(0.9,0.3),
            (0.3,0.55),(0.5,0.55),(0.7,0.55),
            (0.4,0.75),(0.6,0.75)
        ],

        "1-4-3-2-1": [
            (0.5,0.1),
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),
            (0.3,0.5),(0.5,0.5),(0.7,0.5),
            (0.4,0.65),(0.6,0.65),
            (0.5,0.85)
        ],

        "1-3-4-3": [
            (0.5,0.1),
            (0.3,0.3),(0.5,0.3),(0.7,0.3),
            (0.2,0.5),(0.4,0.5),(0.6,0.5),(0.8,0.5),
            (0.25,0.75),(0.5,0.8),(0.75,0.75)
        ],

        "1-4-1-4-1": [
            (0.5,0.1),
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),
            (0.5,0.45),
            (0.2,0.6),(0.4,0.6),(0.6,0.6),(0.8,0.6),
            (0.5,0.85)
        ],

        "1-3-6-1": [
            (0.5,0.1),
            (0.3,0.3),(0.5,0.3),(0.7,0.3),
            (0.1,0.5),(0.3,0.5),(0.5,0.5),(0.7,0.5),(0.9,0.5),(0.5,0.65),
            (0.5,0.85)
        ],

        "1-4-5-1": [
            (0.5,0.1),
            (0.2,0.3),(0.4,0.3),(0.6,0.3),(0.8,0.3),
            (0.1,0.5),(0.3,0.5),(0.5,0.5),(0.7,0.5),(0.9,0.5),
            (0.5,0.85)
        ]
    }
    
    # Definir orden fijo de posiciones
    pos_order = ["All", "GK", "DF", "MF", "FW"]  

    # Definir diccionario con valores por defecto de la alineación
    lineup_defaults = {
        "lineup_sistema": lineup_sistemas[0],
        "lineup_league_filter": "All",
        "lineup_team_filter": "All",
        "lineup_pos_filter": "All",
        "lineup_players": [None]*11,
        "lineup_player_to_add": "Select",
        "lineup_matchday": 1,
        "lineup_selected_pos": None,
        
        "lineup_do_reset": False
    }

    # Inicializar variables en sesión si no existen
    for key, value in lineup_defaults.items():
        st.session_state.setdefault(key, value)

    # Verificar si se solicita reseteo de la alineación
    if st.session_state["lineup_do_reset"]:
        
        # Restablecer valores por defecto en sesión
        for key in lineup_defaults:
            st.session_state[key] = lineup_defaults[key]
        
        # Desactivar bandera de reseteo
        st.session_state["lineup_do_reset"] = False
        
        # Recargar aplicación para aplicar cambios
        st.rerun()

    # Cargar imagen del campo
    lineup_pitch_img = Image.open(ASSETSIMG / "picth_vertical.png")
    w, h = lineup_pitch_img.size

    # Definir layout de la página
    lineup_form_col, lineup_field_col = st.columns([1,2])

    # Crear formulario de asignación de jugadores
    with lineup_form_col:

        st.subheader("Assign Player")
        
        # Crear selector de sistema táctico
        lineup_sistema = st.selectbox(
            "Select system",
            lineup_sistemas,
            index=lineup_sistemas.index(st.session_state.get("lineup_sistema", lineup_sistemas[0]))
        )
        
        # Guardar sistema seleccionado en sesión
        st.session_state["lineup_sistema"] = lineup_sistema
        
        # Obtener coordenadas según sistema seleccionado
        lineup_pos_coords = lineup_posiciones[lineup_sistema]
        
        # Crear selector de liga
        league_options = ["All"] + sorted(lineup_df_players["stats_Comp"].unique())
        league_index = league_options.index(st.session_state.get("lineup_league_filter", "All"))
        
        lineup_league = st.selectbox(
            "League",
            league_options,
            index=league_index
        )
        
        # Guardar liga seleccionada en sesión
        st.session_state["lineup_league_filter"] = lineup_league

        # Obtener lista de equipos filtrados por liga
        teams = sorted(lineup_df_players[lineup_df_players["stats_Comp"]==lineup_league]["stats_Squad"].unique()) \
                if lineup_league != "All" else sorted(lineup_df_players["stats_Squad"].unique())
        
        # Definir opciones de equipos
        team_options = ["All"] + teams
        
        # Validar índice del equipo seleccionado previamente
        team_index = team_options.index(st.session_state["lineup_team_filter"]) \
            if st.session_state.get("lineup_team_filter") in team_options else 0
        
        # Crear selector de equipo
        lineup_team = st.selectbox(
            "Team",
            team_options,
            index=team_index
        )
        
        # Guardar equipo seleccionado en sesión
        st.session_state["lineup_team_filter"] = lineup_team

        # Filtrar jugadores por liga y equipo
        filtered_players = lineup_df_players.copy()
        if lineup_league != "All":
            filtered_players = filtered_players[filtered_players["stats_Comp"] == lineup_league]
        if lineup_team != "All":
            filtered_players = filtered_players[filtered_players["stats_Squad"] == lineup_team]

        # Crear selector de posición
        available_positions = [p for p in pos_order if p in filtered_players["stats_Pos"].unique()]
        pos_options = ["All"] + available_positions
        
        # Validar índice de posición seleccionado
        pos_index = pos_options.index(st.session_state.get("lineup_pos_filter", "All")) \
            if st.session_state.get("lineup_pos_filter") in pos_options else 0
        
        lineup_pos = st.selectbox(
            "Position",
            pos_options,
            index=pos_index
        )
        
        # Guardar posición seleccionada en sesión
        st.session_state["lineup_pos_filter"] = lineup_pos

        # Filtrar jugadores por posición
        if lineup_pos != "All":
            filtered_players = filtered_players[filtered_players["stats_Pos"] == lineup_pos]

        # Crear selector de jugador
        players_list = ["Select"] + list(filtered_players["Player"])
        
        # Validar índice del jugador seleccionado
        player_index = players_list.index(st.session_state["lineup_player_to_add"]) \
            if st.session_state.get("lineup_player_to_add") in players_list else 0
        
        lineup_player = st.selectbox(
            "Player",
            players_list,
            index=player_index
        )
        
        # Guardar jugador seleccionado en sesión
        st.session_state["lineup_player_to_add"] = lineup_player

        # Crear selector de jornada
        lineup_matchday = st.slider(
            "Gameday",
            1, 38,
            st.session_state.get("lineup_matchday", 1)
        )
        
        # Guardar jornada seleccionada en sesión
        st.session_state["lineup_matchday"] = lineup_matchday

        # Crear selector de posición dentro de la alineación
        lineup_pos_options = [f"Pos {i+1}" for i in range(len(lineup_pos_coords))]
        selected_pos_index = st.session_state.get("lineup_selected_pos", 0)
        
        lineup_selected_pos_label = st.selectbox(
            "Select position to assign",
            lineup_pos_options,
            index=selected_pos_index
        )
        
        # Actualizar posición seleccionada en sesión
        if lineup_selected_pos_label in lineup_pos_options:
            st.session_state["lineup_selected_pos"] = lineup_pos_options.index(lineup_selected_pos_label)
        else:
            st.session_state["lineup_selected_pos"] = 0

        # Crear botón para asignar jugador con validación previa
        if st.button("Assign players"):
            if lineup_league=="All" or lineup_team=="All" or lineup_pos=="All" or lineup_player=="Select":
                st.warning("Please select League, Team, Position, and Player before assigning.")
            else:
                # Asignar jugador a la posición seleccionada
                st.session_state["lineup_players"][st.session_state["lineup_selected_pos"]] = lineup_player
                st.rerun()

        # Crear botón para guardar alineación
        if st.button("Save lineup"):

            # Preparar estructura de datos para almacenar la alineación
            lineup_data = []

            # Generar identificador único para la alineación
            lineup_id = str(uuid.uuid4())

            # Recorrer jugadores seleccionados en la sesión
            for i, p in enumerate(st.session_state.get("lineup_players", [])):
                
                if p:
                    # Obtener coordenadas de la posición
                    coord = lineup_pos_coords[i]
                    
                    # Añadir registro de jugador a la lista
                    lineup_data.append({
                        "Lineup_Id": lineup_id,
                        "Jornada": lineup_matchday,
                        "Sistema": lineup_sistema,
                        "Jugador": p,
                        "Posición": i + 1,
                        "Coordenada X": coord[0],
                        "Coordenada Y": coord[1],
                        "Liga": lineup_league,
                        "Equipo": lineup_team,
                        "Usuario": st.session_state["user"].username
                    })

            # Concatenar nuevos datos con los existentes si el DataFrame no está vacío
            if not df_save.empty:
                df_save = pd.concat([df_save, pd.DataFrame(lineup_data)], ignore_index=True)
            else:
                # Crear nuevo DataFrame si no existen datos previos
                df_save = pd.DataFrame(lineup_data)

            # Guardar datos en archivo Excel
            df_save.to_excel(filename, index=False, engine="openpyxl")

            # Mostrar mensaje de confirmación
            st.success(f"Lineup saved with ID: {lineup_id}")

            # Preparar archivo Excel en memoria para descarga
            with BytesIO() as output:
                df_save.to_excel(output, index=False, engine="openpyxl")
                output.seek(0)
                
                # Crear botón de descarga del archivo Excel
                st.download_button(
                    "📥 Download Excel",
                    data=output,
                    file_name="lineups_register.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # Crear botón para reiniciar la alineación
        if st.button("🔄 Reset"):
            
            # Restablecer valores por defecto en la sesión
            st.session_state["lineup_sistema"] = lineup_sistemas[0]
            st.session_state["lineup_league_filter"] = "All"
            st.session_state["lineup_team_filter"] = "All"
            st.session_state["lineup_pos_filter"] = "All"
            st.session_state["lineup_players"] = [None]*11
            st.session_state["lineup_player_to_add"] = "Select"
            st.session_state["lineup_matchday"] = 1
            st.session_state["lineup_selected_pos"] = 0
            
            # Recargar aplicación
            st.rerun()

    with lineup_field_col:

        # Crear figura para representar la alineación
        fig_lineup, ax_lineup = plt.subplots(figsize=(w/100, h/100))
        
        # Mostrar imagen del campo como fondo
        ax_lineup.imshow(lineup_pitch_img)
        
        # Ocultar ejes
        ax_lineup.axis('off')

        # Dibujar posiciones y jugadores
        for idx, pos in enumerate(lineup_pos_coords):
            x = pos[0]*w
            y = pos[1]*h
            
            # Definir color según si hay jugador asignado
            color = "green" if st.session_state["lineup_players"][idx] else "red"
            
            # Dibujar círculo de la posición
            ax_lineup.add_patch(plt.Circle((x,y), 25, color=color))
            
            # Mostrar número de posición
            ax_lineup.text(x, y, str(idx+1), color='white', ha='center', va='center', fontsize=15, fontweight='bold')

            # Mostrar nombre del jugador si está asignado
            if st.session_state["lineup_players"][idx]:
                nombre = st.session_state["lineup_players"][idx]
                
                # Dividir nombre en varias líneas
                palabras = nombre.split()
                lineas = [" ".join(palabras[i:i+2]) for i in range(0, len(palabras),2)]
                nombre_wrap = "\n".join(lineas)
                
                ax_lineup.text(x, y+50, nombre_wrap, color="black", ha='center', va='top', fontsize=18)

        # Mostrar gráfico en Streamlit
        st.pyplot(fig_lineup)

    # Crear botón HTML para imprimir la página
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

    # Crear botón para generar PDF del lineup
    if st.button("⚙️ Prepare PDF"):

        # Crear figura para exportación en PDF
        fig_lineup, ax_lineup = plt.subplots(figsize=(6,9))  
        
        # Mostrar campo de fútbol
        ax_lineup.imshow(lineup_pitch_img)                   
        ax_lineup.axis("off")

        # Dibujar jugadores en el campo
        for idx, pos in enumerate(lineup_pos_coords):
            x = pos[0]*w  
            y = pos[1]*h  

            # Definir color según disponibilidad de jugador
            color = "green" if st.session_state["lineup_players"][idx] else "red"

            # Dibujar círculo
            ax_lineup.add_patch(plt.Circle((x,y), 25, color=color))

            # Mostrar número de posición
            ax_lineup.text(x, y, str(idx+1), color='white', ha='center', va='center', fontsize=7, fontweight='bold')

            # Mostrar nombre del jugador si existe
            if st.session_state["lineup_players"][idx]:
                nombre = st.session_state["lineup_players"][idx]
                ax_lineup.text(x, y+50, nombre, color="black", ha='center', va='top', fontsize=7)

        # Guardar imagen en memoria
        img_buffer = BytesIO()
        fig_lineup.savefig(img_buffer, format="png", bbox_inches='tight', dpi=150)  
        plt.close(fig_lineup)  
        img_buffer.seek(0)

        # Crear documento PDF
        pdf_lineup = FPDF()
        
        # Añadir página
        pdf_lineup.add_page()  
        
        # Añadir fuente personalizada
        pdf_lineup.add_font("DejaVu", "", str(ASSETSFONTS / "DejaVuSans.ttf"), uni=True)  

        # Obtener datos del usuario y alineación
        user_obj = st.session_state.get("user")
        usuario = user_obj.username if user_obj else "Desconocido"  
        sistema = st.session_state.get("lineup_sistema","1-4-4-2")
        jornada = st.session_state.get("lineup_matchday",1)
        title = f"Username: {usuario}    System: {sistema}    Matchday: {jornada}"

        # Añadir título al PDF
        pdf_lineup.set_font("DejaVu", "", 16)
        pdf_lineup.cell(0, 12, title, ln=True, align="C")
        pdf_lineup.ln(8)  

        # Insertar imagen del lineup
        pdf_lineup.image(img_buffer, x=15, w=180)  
        
        # Insertar marca de agua
        logo_buffer = get_watermark(alpha=10, user_obj=st.session_state.get("user"))
        pdf_lineup.image(logo_buffer, x=55, y=100, w=100)

        # Generar PDF en memoria
        pdf_bytes_lineup = pdf_lineup.output(dest="S")

        # Codificar PDF en base64
        b64_pdf_lineup = base64.b64encode(pdf_bytes_lineup).decode()

        # Crear botón HTML para descarga del PDF
        components.html(
            f"""
            <a href="data:application/pdf;base64,{b64_pdf_lineup}" download="lineup.pdf">
                <button style="
                    padding:8px 14px;
                    font-size:14px;
                    cursor:pointer;
                    background-color:#dc2626;  
                    color:white;
                    border:none;
                    border-radius:6px;">
                    📄 Export to PDF
                </button>
            </a>
            """,
            height=55
        )

    # Insertar separador visual
    st.divider()

    # Inicializar variable de visualización en sesión
    st.session_state.setdefault("view_lineup_id", None)

    # Generar resumen de alineaciones agrupadas por ID
    df_summary_lineupsid = (
        df_save
        .sort_values("Posición")
        .groupby("Lineup_Id")
        .first()
        .reset_index()
    )

    # Definir columnas para filtros y visualización
    col_filters_lineupid, col_space_lineupid, col_view_lineupid = st.columns([1, 0.5, 2])

    # Crear sección de filtros de alineaciones
    with col_filters_lineupid:

        # Mostrar título del explorador de alineaciones
        st.subheader("Lineups Explorer")

        # Crear filtro por usuario
        users = ["All"] + sorted(df_summary_lineupsid["Usuario"].dropna().unique())
        selected_user = st.selectbox("User", users)

        # Filtrar DataFrame por usuario seleccionado
        if selected_user != "All":
            df_summary_lineupsid = df_summary_lineupsid[df_summary_lineupsid["Usuario"] == selected_user]

        # Crear slider para porcentaje de alineaciones a mostrar
        percent = st.slider("Show % lineups", 0, 100, 100)

        # Calcular número de filas a mostrar según porcentaje
        n_rows = int(len(df_summary_lineupsid) * percent / 100)
        
        # Aplicar límite de filas
        df_summary_lineupsid = df_summary_lineupsid.head(n_rows)
        
        # Crear vista simplificada del DataFrame
        df_view = df_summary_lineupsid.copy()
        df_view = df_view[["Lineup_Id", "Usuario", "Jornada"]]

        # Inicializar variable de selección en sesión
        st.session_state.setdefault("view_lineup_id", None)

        # Mostrar tabla interactiva con selección de fila
        event = st.dataframe(
            df_view,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Detectar fila seleccionada en la tabla
        if event.selection.rows:
            selected_index = event.selection.rows[0]
            
            # Obtener ID de la alineación seleccionada
            selected_id = df_view.iloc[selected_index]["Lineup_Id"]

            # Guardar alineación seleccionada en sesión
            st.session_state["view_lineup_id"] = selected_id
                
            # Botón para eliminar la alineación seleccionada
            if st.button("🗑️ Delete selected lineup"):

                # Filtrar el dataframe eliminando la alineación seleccionada por ID
                df_save = df_save[df_save["Lineup_Id"] != selected_id]

                # Guardar el dataframe actualizado en el archivo Excel
                df_save.to_excel(filename, index=False)

                # Mostrar mensaje de confirmación al usuario
                st.success("Deleted")

                # Recargar la app para reflejar los cambios inmediatamente
                st.rerun()

    # Crear sección de visualización de alineación
    with col_view_lineupid:

        # Mostrar título del visor
        st.subheader("Lineup Viewer")

        # Mostrar mensaje si no hay alineación seleccionada
        if st.session_state.view_lineup_id is None:
            st.info("Select a lineup to view")

        else:

            # Filtrar alineación seleccionada
            df_selected = df_save[
                df_save["Lineup_Id"] == st.session_state.view_lineup_id
            ]

            # Cargar imagen del campo
            pitch_img = Image.open(ASSETSIMG / "picth_vertical.png")
            w, h = pitch_img.size

            # Crear figura para dibujar alineación
            fig, ax = plt.subplots(figsize=(w/100, h/100))
            
            # Mostrar campo como fondo
            ax.imshow(pitch_img)
            ax.axis("off")

            # Dibujar jugadores de la alineación
            for _, r in df_selected.iterrows():

                # Calcular posición en píxeles
                x = r["Coordenada X"] * w
                y = r["Coordenada Y"] * h
                player = r["Jugador"]
                pos = r["Posición"]

                # Dibujar círculo del jugador
                ax.add_patch(
                    plt.Circle((x, y), 25, color="green")
                )

                # Mostrar número de posición
                ax.text(
                    x, y,
                    str(pos),
                    color="white",
                    ha="center",
                    va="center",
                    fontsize=12,
                    fontweight="bold"
                )

                # Mostrar nombre del jugador
                ax.text(
                    x, y + 40,
                    player,
                    ha="center",
                    va="top",
                    fontsize=10,
                    color="black"
                )

            # Mostrar gráfico en Streamlit
            st.pyplot(fig)