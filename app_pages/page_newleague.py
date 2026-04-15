# ============================================
# Page New League Request
# ============================================

# Importar librerías
import streamlit as st
import pandas as pd
import os
from PIL import Image
from datetime import datetime

# Importar funciones de datos
from controllers.db_controller import load_stats_players_fbref

# Importar rutas de configuración
from common.config import (
    ASSETSIMG, DATA_DIR
)

# Función que da como resultado la página New League
def page_newleague():

    # Crear columnas para centrar la imagen
    newleague_imgcol1, newleague_imgcol2, newleague_imgcol3 = st.columns([3,2,3])

    with newleague_imgcol2:

        # Cargar imagen de cabecera desde assets
        header_img = Image.open(ASSETSIMG / "Freepick NewLeague.png")

        # Mostrar imagen en la interfaz
        st.image(header_img, width=120)

    # Mostrar título de la página
    st.header("Request a New Competition")

    # Mostrar descripción de la sección
    st.caption("Suggest a new league to be added to the scouting database")

    # Insertar separador visual
    st.markdown("---")

    # Definir ruta del archivo de solicitudes
    MESSAGE_FILE = DATA_DIR / "message_from_users.xlsx"

    # Función auxiliar para cargar mensajes existentes
    def load_messages():

        # Definir columnas esperadas del archivo
        columns = ["User","League","Priority","Message","Date"]

        # Verificar si el archivo existe
        if not os.path.exists(MESSAGE_FILE):
            return pd.DataFrame(columns=columns)

        # Cargar archivo Excel existente
        return pd.read_excel(MESSAGE_FILE)

    # Función auxiliar para guardar mensaje
    def save_message(data):
        
        # Convertir diccionario en DataFrame
        df_new = pd.DataFrame([data])

        # Crear archivo si no existe
        if not os.path.exists(MESSAGE_FILE):
            with pd.ExcelWriter(MESSAGE_FILE, engine="openpyxl") as writer:
                df_new.to_excel(writer, index=False)

        # Si existe, añadir nueva fila
        else:
            # Leer el Excel existente
            df_old = pd.read_excel(MESSAGE_FILE)

            # Concatenar los datos antiguos con los nuevos, ignorando los índices antiguos
            df_final = pd.concat([df_old, df_new], ignore_index=True)

            # Guardar de nuevo todo el DataFrame en el mismo archivo (sobrescribiendo)
            with pd.ExcelWriter(MESSAGE_FILE, engine="openpyxl", mode="w") as writer:
                df_final.to_excel(writer, index=False)

    # Función que devuelve un diccionario con todas las ligas posibles para distintas fuentes
    @st.cache_data(show_spinner=False)
    def load_leagues():
        
        # Definir lista de competiciones disponibles
        lista_ligas = [
            "Copa de la Liga",
            "Primera Division Argentina",
            "Primera Division Uruguay",
            "Brasileirao",
            "Brasileirao B",
            "Primera Division Colombia",
            "Primera Division Chile",
            "Primera Division Peru",
            "Primera Division Venezuela",
            "Primera Division Ecuador",
            "Primera Division Bolivia",
            "Primera Division Paraguay",
            "Brasileirao F",
            "MLS",
            "USL Championship",
            "Premier League",
            "La Liga",
            "Ligue 1",
            "Bundesliga",
            "Serie A",
            "Big 5 European Leagues",
            "Danish Superliga",
            "Eredivisie",
            "Primeira Liga Portugal",
            "Copa America",
            "Euros",
            "Saudi League",
            "EFL Championship",
            "La Liga 2",
            "Belgian Pro League",
            "Challenger Pro League",
            "2. Bundesliga",
            "Ligue 2",
            "Serie B",
            "J1 League",
            "NWSL",
            "Womens Super League",
            "Liga F",
            "Premier Division South Africa",
            "Champions League",
            "Europa League",
            "Conference League",
            "Copa Libertadores",
            "Liga MX"
        ]
        
        # Devolver dict con la misma estructura que LanusStats esperaba
        return {"Fbref": {liga: {} for liga in lista_ligas}}
        
    # Cargar estructura de ligas
    ligas = load_leagues()

    # Extraer ligas de FBref
    ligas_fbref = ligas["Fbref"]

    # Ordenar lista de ligas disponibles
    lista_ligas = sorted(list(ligas_fbref.keys()))

    # Cargar dataset de jugadores
    newleague_df_players = load_stats_players_fbref()

    # Extraer competiciones existentes en la base de datos
    existing_comps = newleague_df_players["stats_Comp"].apply(
        lambda x: str(x).split(",")[0].strip()
    )

    # Obtener valores únicos ordenados
    existing_comps = sorted(existing_comps.unique())

    # Filtrar ligas no existentes en la base de datos
    lista_ligas_filtrada = [l for l in lista_ligas if l not in existing_comps]

    # Crear layout de formulario e información
    newleague_form_col, newleague_info_col = st.columns([1,1])

    # Construir formulario de solicitud
    with newleague_form_col:

        # Mostrar título del formulario
        st.subheader("Submit Request")

        # Crear selector de competición
        selected_league = st.selectbox(
            "Select Competition",
            ["Select"] + lista_ligas_filtrada,
            key="new_league_select"
        )

        # Crear selector de prioridad
        priority = st.radio(
            "Priority Level",
            ["Low","Medium","High"],
            key="league_priority"
        )

        # Crear campo de texto para justificación
        message = st.text_area(
            "Why should this league be added?",
            max_chars=300,
            placeholder="Explain why this competition would be useful for scouting...",
            key="league_message"
        )

        # Procesar envío de solicitud
        if st.button("Send Request"):

            # Validar selección de liga
            if selected_league == "Select":
                st.warning("Please select a competition")

            # Validar mensaje obligatorio
            elif not message:
                st.warning("Please write a justification")

            # Guardar solicitud si es válida
            else:
                data = {
                    "User": st.session_state.get("user").username,
                    "League": selected_league,
                    "Priority": priority,
                    "Message": message,
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }

                # Guardar solicitud en archivo
                save_message(data)

                # Mostrar confirmación
                st.success("Your request has been sent to the administrator")

                # Recargar aplicación
                st.rerun()

    # Mostrar panel informativo
    with newleague_info_col:

        # Mostrar título de sección
        st.subheader("Available Competitions")

        # Mostrar número total de competiciones
        st.info(f"Total competitions available in FBref: {len(lista_ligas)}")

        # Mostrar lista completa de ligas
        with st.expander("View all competitions"):
            for league in lista_ligas:
                st.write("ℹ", league)

        # Mostrar competiciones ya existentes en la app
        with st.expander("View competitions in app"):
            if existing_comps:
                for comp in existing_comps:
                    st.write("✅", comp)
            else:
                st.write("No competitions in the app yet")

        # Separador visual
        st.markdown("---")

        # Cargar mensajes de usuarios
        df_messages = load_messages()

        # Mostrar estadísticas si existen solicitudes
        if not df_messages.empty:

            # Mostrar título de ranking
            st.subheader("Most Requested Leagues")

            # Contar solicitudes por liga
            league_counts = (
                df_messages["League"]
                .value_counts()
                .reset_index()
            )

            # Renombrar columnas
            league_counts.columns = ["League","Requests"]

            # Mostrar top solicitudes
            st.dataframe(
                league_counts.head(5),
                use_container_width=True
            )

        # Mostrar mensaje si no hay solicitudes
        else:
            st.caption("No league requests yet")