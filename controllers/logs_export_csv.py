# ============================================
# Controllers -> logs_export_csv
# ============================================

# Importar librerías 
from datetime import datetime
import streamlit as st
import pandas as pd
from pathlib import Path
import os

# Importar rutas de configuración
from common.config import (
    LOG_FILE
)

# Importar el modelo de usuario
from models.user import User

# Función para generar un registro de la descarga
def build_download_log(page_name: str, prefix: str, extra_data: dict = None):
    
    # Obtener el usuario desde session_state
    user_obj = st.session_state.get("user", None)  # Puede ser un objeto User o None

    if isinstance(user_obj, User):
        username = user_obj.username
        is_admin = user_obj.is_admin()
    else:
        # Si no hay usuario, usar valores por defecto
        username = "anonymous"
        is_admin = False

    # Construcción del log base
    log_data = {
        
        # Usuario 
        "user": username,
        
        # Timestamp del momento de la descarga
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        # Página desde donde se realiza la acción
        "page": page_name,

        # Filtros dinámicos (dependen del prefijo)
        "age_filter": st.session_state.get(f"{prefix}_age_filter"),
        "pos_filter": st.session_state.get(f"{prefix}_pos_filter"),
        "team_filter": st.session_state.get(f"{prefix}_team_filter"),
        "league_filter": st.session_state.get(f"{prefix}_league_filter"),
        "minutes_filter": st.session_state.get(f"{prefix}_minutes_filter"),
        "num_players": st.session_state.get(f"{prefix}_num_players_filter"),
    }

    # Añadir información extra si existe (ej: estadísticas, ranking, etc.)
    if extra_data:
        log_data.update(extra_data)

    return log_data
    
# Función para guardar registros de logs en un archivo Excel
def save_log_to_excel(log_data: dict):

    # Convertir el log en un DataFrame de una sola fila
    new_row = pd.DataFrame([log_data])

    # Si el archivo existe → añadir datos
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        existing_df = pd.read_excel(LOG_FILE, engine='openpyxl')
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
    else:
        # Si no existe → crear nuevo archivo
        updated_df = new_row

    # Guardar en Excel
    updated_df.to_excel(LOG_FILE, index=False)

# Función para generar y registrar un evento de descarga
def log_download_event(page_name: str, prefix: str, extra_data: dict = None):
    
    # Generar log con toda la información
    log_data = build_download_log(page_name, prefix, extra_data)

    # Guardar en Excel
    save_log_to_excel(log_data)

    # Mostrar en consola (útil para debugging)
    print("LOG EXPORT:", log_data)