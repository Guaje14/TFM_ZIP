# ============================================
# Page Home
# ============================================

# Importar librerías 
import streamlit as st
from PIL import Image

# Importar rutas de configuración
from common.config import (
    ASSETSIMG
)

# Función que da cómo resultado la página Home
def page_home():
    
    # Obtener usuario desde la sesión
    user_obj = st.session_state.get("user")
    
    # Definir nombre del usuario o asignar "Invitado" por defecto
    user_name = user_obj.username if user_obj else "Invitado"

    # Inicializar idioma en la sesión si no existe
    st.session_state.setdefault("home_lang", "ESP")

    # Crear columnas para centrar la imagen
    welcome_imgcol1, welcome_imgcol2, welcome_imgcol3 = st.columns([3.7, 2.5, 3])

    with welcome_imgcol2:
        
        # Cargar imagen desde la carpeta de assets
        welcome_img_header = Image.open(ASSETSIMG / "Freepick House.png")
        
        # Mostrar imagen en la aplicación
        st.image(welcome_img_header, width=120)
        
        # Insertar espacio vertical
        st.write("")  
    
    # Crear columnas para centrar el mensaje informativo
    welcome_msg_col1, welcome_msg_col2, welcome_msg_col3 = st.columns([1.5, 2, 2])
    
    with welcome_msg_col2:
    
        # Mostrar mensaje informativo sobre selección de idioma
        st.markdown(
            "<p style='text-align: center; color: gray;'>You can select a language to display the welcome message.</p>",
            unsafe_allow_html=True
        )
    
    # Crear columnas para centrar botones de idioma
    welcome_col1, welcome_col2, welcome_col3 = st.columns([1, 4, 1])  
    
    with welcome_col2:
        
        # Crear columnas internas para organizar botones de idioma
        welcome_cols_btn = st.columns(5)
        
        # Crear botón para seleccionar Español
        with welcome_cols_btn[0]:
            if st.button("ESP"):
                # Actualizar idioma en la sesión a Español
                st.session_state["home_lang"] = "ESP"
        
        # Crear botón para seleccionar Inglés
        with welcome_cols_btn[2]:
            if st.button("ENG"):
                # Actualizar idioma en la sesión a Inglés
                st.session_state["home_lang"] = "ENG"
        
        # Crear botón para seleccionar Italiano
        with welcome_cols_btn[4]:
            if st.button("ITA"):
                # Actualizar idioma en la sesión a Italiano
                st.session_state["home_lang"] = "ITA"

        # Definir diccionario de mensajes de bienvenida según idioma
        messages = {        
            "ESP": f"""
            ### 👋 ¡Bienvenido, {user_name}!

            **DataLab** es una aplicación de **Streamlit** diseñada para facilitar el **análisis de jugadores de fútbol** desde la perspectiva de la **dirección deportiva y el scouting**.

            Con esta herramienta, podrás centralizar **estadísticas de jugadores**, generar **rankings personalizados**, comparar jugadores de manera individual o grupal, y crear **listas y alineaciones ideales** de forma rápida y eficiente.

            Los datos utilizados provienen de **Fbref**, fueron extraídos mediante **LanusStats** y tratados con **Python**, garantizando una base sólida y confiable para tus análisis.

            💡 Esta aplicación está pensada para **optimizar la gestión de datos** y facilitar la **toma de decisiones** en tu equipo, permitiendo que todo el personal trabaje de manera coordinada y centralizada.

            Para cualquier consulta, sugerencia o comentario, puedes escribirme a: **marcoinsigne14@gmail.com**
            """,
            "ITA": f"""
            ### 👋 Benvenuto, {user_name}!

            **DataLab** è un'applicazione **Streamlit** progettata per facilitare l'**analisi dei giocatori di calcio** dal punto di vista della **direzione sportiva e dello scouting**.

            Con questo strumento potrai centralizzare le **statistiche dei giocatori**, creare **classifiche personalizzate**, confrontare i giocatori individualmente o in gruppo e generare rapidamente **liste e formazioni ideali**.

            I dati utilizzati provengono da **Fbref**, sono stati estratti tramite **LanusStats** e trattati con **Python**, garantendo una base solida e affidabile per le tue analisi.

            💡 Questa applicazione è pensata per **ottimizzare la gestione dei dati** e facilitare il **processo decisionale** nella tua squadra, permettendo a tutto lo staff di lavorare in maniera coordinata e centralizzata.

            Per qualsiasi domanda, suggerimento o commento, puoi scrivermi a: **marcoinsigne14@gmail.com**
            """,
            "ENG": f"""
            ### 👋 Welcome, {user_name}!

            **DataLab** is a **Streamlit** application designed to facilitate **football player analysis** from the perspective of **sports management and scouting**.

            With this tool, you can centralize **player statistics**, create **custom rankings**, compare players individually or in groups, and quickly generate **ideal lists and lineups**.

            The data comes from **Fbref**, extracted via **LanusStats** and processed with **Python**, providing a solid and reliable foundation for your analyses.

            💡 This application is designed to **optimize data management** and facilitate **decision-making** for your team, allowing all staff to work in a coordinated and centralized way.

            For any questions, suggestions, or comments, you can email me at: **marcoinsigne14@gmail.com**
            """,
        }

        # Mostrar mensaje de bienvenida según idioma seleccionado
        st.markdown(messages[st.session_state["home_lang"]])