# ============================================
# Controllers -> db_controller
# ============================================

# Importar librerías 
import sqlite3
import pandas as pd
import streamlit as st

# Importar rutas de configuración
from common.config import (
    DB_PATH
)

# Función para crear conexión a la base de datos SQLite
def get_connection():
    """Retorna la conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    return conn


@st.cache_data(ttl=2_592_000)  # 30 días aprox
# Función para leer y cargar los datos de Fbref
def load_stats_players_fbref():

    # Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)

    # Leer toda la tabla de estadísticas de jugadores
    df = pd.read_sql_query("SELECT * FROM stats_players_fbref", conn)

    # Cerrar conexión a la base de datos
    conn.close()

    # Columnas que deben mantenerse como texto
    text_cols = ["Player", "stats_Nation", "stats_Pos", "stats_Squad", "stats_Comp", "league"]

    # Obtener todas las columnas excepto las de texto
    numeric_cols = df.columns.difference(text_cols)

    # Convertir columnas numéricas automáticamente
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    return df  

@st.cache_data(ttl=2_592_000)  # 30 días aprox
# Función genérica para leer y cargar los datos de Fbref con una tabla de score concreta
def load_stats_players_fbref_with_score_table(table_name = None):

    # Validar input
    if table_name is None:
        raise ValueError("table_name no puede ser None.")

    # Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)

    # Consulta SQL con LEFT JOIN para añadir el score
    query = f"""
    SELECT
        s.*,
        p.player_score_raw,
        p.player_score_z,
        p.player_score_percentile,
        p.player_score_0_100,
        p.position_rank,
        p.score_model_version,
        p.min_minutes_used
    FROM stats_players_fbref s
    LEFT JOIN {table_name} p
        ON s.Id_player = p.Id_player
    """

    # Leer resultados
    df = pd.read_sql_query(query, conn)

    # Cerrar conexión
    conn.close()

    # Columnas que deben mantenerse como texto
    text_cols = [
        "Player", "stats_Nation", "stats_Pos",
        "stats_Squad", "stats_Comp", "league",
        "score_model_version"
    ]

    # Obtener columnas numéricas
    numeric_cols = df.columns.difference(text_cols)

    # Convertir columnas numéricas automáticamente
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    return df

