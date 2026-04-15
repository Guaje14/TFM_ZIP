# ============================================
# Page League Requests 
# ============================================

# Importar librerías
import streamlit as st
import pandas as pd
import os
from PIL import Image

# Importar rutas de configuración
from common.config import (
    ASSETSIMG, DATA_DIR
)

# Función que da como resultado la página Message
def page_league_requests_admin():

    # Verificar permisos de administrador
    if not st.session_state.get("is_admin"):
        st.error("Access denied. Admin only.")
        st.stop()
        
    # Crear columnas para centrar la imagen
    message_imgcol1, message_imgcol2, message_imgcol3 = st.columns([3,2,3])
    
    with message_imgcol2:
    
        # Cargar imagen de cabecera desde assets
        header_img = Image.open(ASSETSIMG / "Freepick Message.png")
    
        # Mostrar imagen en la aplicación
        st.image(header_img, width=120)

    # Mostrar título de la página
    st.header("League Requests Management")
    
    # Mostrar descripción de la sección
    st.caption("Review and manage league requests from users")
    
    # Insertar separador visual
    st.markdown("---")

    # Definir ruta del archivo de solicitudes
    MESSAGE_FILE = DATA_DIR / "message_from_users.xlsx"
    
    # Función auxiliar para cargar solicitudes de ligas desde el Excel
    def load_requests():
        
        # Definir columnas esperadas
        columns = ["User","League","Priority","Message","Date","Status"]
        
        # Verificar existencia del archivo
        if not os.path.exists(MESSAGE_FILE):
            return pd.DataFrame(columns=columns)
        
        # Cargar datos desde Excel
        df_message_requests = pd.read_excel(MESSAGE_FILE)
        
        # Añadir columna de estado si no existe
        if "Status" not in df_message_requests.columns:
            df_message_requests["Status"] = "Pending"
        
        # Devolver el DataFrame cargado
        return df_message_requests

    # Función auxiliar para guardar solicitudes
    def save_requests(df_message_requests):
        
        # Guardar DataFrame en archivo Excel
        with pd.ExcelWriter(MESSAGE_FILE, engine="openpyxl", mode="w") as writer:
            df_message_requests.to_excel(writer, index=False)
        
    # Cargar solicitudes existentes
    df_requests = load_requests()
    
    # Verificar si existen solicitudes
    if df_requests.empty:
        st.info("No league requests available")
        return
    
    # Crear copia del DataFrame para filtros
    df_requests_copy = df_requests.copy()

    # Convertir columna de fecha a formato datetime
    df_requests_copy["Date"] = pd.to_datetime(df_requests_copy["Date"], errors="coerce")

    # Crear layout de filtros centrado
    request_1, request_2, request_3 = st.columns([1,2,1])
    
    with request_2:
        
        # Crear subcolumnas para filtros
        request_c1, request_c2, request_c3 = st.columns(3)

        # Generar opciones de usuarios y ligas
        users = ["All"] + sorted(df_requests_copy["User"].dropna().unique())
        leagues = ["All"] + sorted(df_requests_copy["League"].dropna().unique())

        # Crear selectores de filtro
        selected_user = request_c1.selectbox("User", users)
        selected_league = request_c2.selectbox("League", leagues)

        # Crear selector de rango de fechas
        date_range = request_c3.date_input(
            "Date range",
            []
        )
        
    # Filtrar por usuario seleccionado
    if selected_user != "All":
        df_requests_copy = df_requests_copy[df_requests_copy["User"] == selected_user]

    # Filtrar por liga seleccionada
    if selected_league != "All":
        df_requests_copy = df_requests_copy[df_requests_copy["League"] == selected_league]

    # Filtrar por rango de fechas si está definido
    if len(date_range) == 2:
        start, end = date_range
        df_requests_copy = df_requests_copy[
            (df_requests_copy["Date"] >= pd.to_datetime(start)) &
            (df_requests_copy["Date"] <= pd.to_datetime(end))
        ]
        
    # Definir tamaño de página
    PAGE_SIZE = 5

    # Inicializar paginación en sesión
    if "req_page" not in st.session_state:
        st.session_state.req_page = 0
        
    # Crear controles de paginación
    col_prev, col_info, col_next = st.columns([1,2,1])

    # Calcular número máximo de páginas
    max_pages = max(1, (len(df_requests_copy) - 1) // PAGE_SIZE + 1)

    # Botón página anterior
    with col_prev:
        if st.button("⬅️"):
            st.session_state.req_page = max(0, st.session_state.req_page - 1)

    # Botón página siguiente
    with col_next:
        if st.button("➡️"):
            st.session_state.req_page = min(max_pages - 1, st.session_state.req_page + 1)

    # Mostrar información de paginación
    with col_info:
        st.write(f"Page {st.session_state.req_page + 1} / {max_pages}")

    # Calcular índices de paginación
    start_idx = st.session_state.req_page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    # Obtener datos de la página actual
    df_page = df_requests_copy.iloc[start_idx:end_idx]

    # Mostrar solicitudes una por una
    for i, row in df_page.iterrows():

        # Crear columnas para cada fila
        page_col1, page_col2, page_col3, page_col4, page_col5, page_col6 = st.columns([2,3,2,3,3,1])

        # Mostrar usuario
        with page_col1:
            st.markdown(f"👤 {row['User']}")

        # Mostrar liga
        with page_col2:
            st.markdown(f"🏆 {row['League']}")

        # Mostrar prioridad
        with page_col3:
            priority_icon = {"Low":"🟢","Medium":"🟡","High":"🔴"}.get(row["Priority"], "⚪")
            st.markdown(f"{priority_icon} {row['Priority']}")

        # Mostrar fecha formateada
        with page_col4:
            date_val = pd.to_datetime(row["Date"]).strftime("%Y-%m-%d %H:%M")
            st.markdown(f"📅 {date_val}")

        # Gestionar estado de solicitud
        with page_col5:
            is_approved = row["Status"] == "Approved"

            # Crear checkbox de estado
            checked = st.checkbox(
                "Status",
                value=is_approved,
                key=f"status_{row.name}"
            )

            # Mostrar estado visual
            st.markdown("✅ Approved" if checked else "⏳ Pending")

            # Actualizar estado si cambia
            if checked != is_approved:
                df_requests.loc[row.name, "Status"] = "Approved" if checked else "Pending"
                save_requests(df_requests)
                st.rerun()
                
        # Eliminar solicitud
        with page_col6:
            if st.button("🗑️", key=f"delete_{row.name}"):
                df_requests.drop(index=row.name, inplace=True)
                save_requests(df_requests)
                st.rerun()

        # Mostrar mensaje completo en desplegable
        with st.expander("💬 View message"):
            st.write(row["Message"])

        # Separar visualmente cada solicitud
        st.divider()