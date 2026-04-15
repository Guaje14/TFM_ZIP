# ============================================
# Common -> filters
# ============================================

# Importar librerías
import pandas as pd
import streamlit as st

# Aplicar filtros encadenados a un dataframe de jugadores
def apply_player_filters(df, col1, col2, col3, col4, col5, prefix, checkbox = False):

    # Función auxiliar para comprobar si un valor buscado está incluido dentro de una celda con múltiples valores separados por comas
    def contains_value(cell_value, target_value):

        # Si alguno de los valores es nulo, no hay coincidencia
        if pd.isna(cell_value) or pd.isna(target_value):
            return False

        # Separar los valores por coma y eliminar espacios sobrantes
        values = [v.strip() for v in str(cell_value).split(",")]

        # Comprobar si el valor buscado está dentro de la lista
        return str(target_value).strip() in values

    # Función auxiliar para construir una lista única y limpia a partir de una columna que puede contener varios valores por celda
    def extract_unique_split_values(series):

        # Inicializar conjunto para evitar duplicados
        unique_values = set()

        # Recorrer valores no nulos de la serie
        for val in series.dropna():

            # Separar por comas y limpiar espacios
            split_vals = [v.strip() for v in str(val).split(",")]

            # Añadir cada valor limpio al conjunto
            unique_values.update(split_vals)

        # Devolver lista ordenada
        return sorted(unique_values)

    # Función auxiliar para construir un diccionario equipo -> competición usando únicamente filas simples (un solo equipo y una sola competición)
    def build_team_league_map(local_df):

        # Inicializar diccionario
        team_to_league = {}

        # Recorrer filas del dataframe
        for _, row in local_df.iterrows():

            squad_value = row.get("stats_Squad")
            comp_value = row.get("stats_Comp")

            # Ignorar valores nulos
            if pd.isna(squad_value) or pd.isna(comp_value):
                continue

            squad_str = str(squad_value).strip()
            comp_str = str(comp_value).strip()

            # Usar solo filas simples
            if "," not in squad_str and "," not in comp_str:
                team_to_league[squad_str] = comp_str

        return team_to_league

    # Función auxiliar para obtener los equipos de una competición a partir del diccionario equipo -> competición
    def get_teams_for_league_from_map(team_to_league, target_league):

        # Si no hay liga objetivo, devolver lista vacía
        if pd.isna(target_league):
            return []

        # Filtrar equipos cuya competición asociada coincide con la buscada
        teams = [
            team for team, league in team_to_league.items()
            if league == str(target_league).strip()
        ]

        return sorted(teams)

    # Crear claves únicas para guardar filtros en session_state
    minutes_key = f"{prefix}_minutes_filter"
    user_league_key = f"{prefix}_user_league_filter"
    league_key = f"{prefix}_league_filter"
    team_key = f"{prefix}_team_filter"
    age_key = f"{prefix}_age_filter"
    pos_key = f"{prefix}_pos_filter"

    # Crear slider de % de minutos jugados
    with col5:
        minutes_filter = st.slider(
            "% Min Played",
            0,
            100,
            key = minutes_key
        )

    # Crear copia del dataframe original para no modificarlo
    df_base = df.copy()

    # Convertir columnas a formato numérico para evitar errores en filtros
    df_base["stats_Min"] = pd.to_numeric(df_base["stats_Min"], errors = "coerce")
    df_base["stats_Age"] = pd.to_numeric(df_base["stats_Age"], errors = "coerce")

    # Construir diccionario equipo -> competición a partir del dataset original
    team_to_league = build_team_league_map(df)

    # Obtener el valor máximo de minutos del dataset
    max_min = df_base["stats_Min"].max()

    # Filtrar jugadores según porcentaje de minutos jugados respecto al máximo
    df_base = df_base[
        df_base["stats_Min"] >= max_min * minutes_filter / 100
    ]

    # Inicializar flags de filtro por liga del usuario
    use_user_league = False
    comp_user = None

    # Activar lógica especial si el checkbox está habilitado
    if checkbox:

        # Obtener usuario desde session_state
        user_obj = st.session_state.get("user")

        # Verificar si el usuario tiene equipo asignado
        if user_obj and user_obj.team:

            # Obtener equipo del usuario
            team_user = user_obj.team

            # Obtener la competición del equipo del usuario desde el diccionario
            comp_user = team_to_league.get(team_user, None)

        else:
            # Si no hay equipo asignado, no se usa esta lógica
            comp_user = None

    # Crear selector de liga en la interfaz
    with col1:

        # Obtener ligas únicas y limpias separando celdas con múltiples valores
        leagues = ["All"] + extract_unique_split_values(df_base["stats_Comp"])

        # Mostrar selectbox de liga
        st.selectbox("League", leagues, key = league_key)

    # Activar filtro automático por liga del usuario si corresponde
    if checkbox and comp_user:
        use_user_league = st.checkbox(
            "Show only players of my team league",
            key = user_league_key
        )

    # Crear copia para aplicar filtro de liga
    df_league = df_base.copy()

    # Obtener liga seleccionada desde session_state
    selected_league = st.session_state.get(league_key, "All")

    # Filtrar por liga del usuario si está activado
    if use_user_league and comp_user:
        df_league = df_league[
            df_league["stats_Comp"].apply(lambda x: contains_value(x, comp_user))
        ]

    # Filtrar por liga seleccionada manualmente
    elif selected_league != "All":
        df_league = df_league[
            df_league["stats_Comp"].apply(lambda x: contains_value(x, selected_league))
        ]

    # Crear selector de equipo
    with col2:

        # Si está activado el filtro por liga del usuario,
        # mostrar solo los equipos de esa competición
        if use_user_league and comp_user:
            teams = ["All"] + get_teams_for_league_from_map(team_to_league, comp_user)

        # Si se ha seleccionado una liga manualmente,
        # mostrar solo los equipos mapeados a esa competición
        elif selected_league != "All":
            teams = ["All"] + get_teams_for_league_from_map(team_to_league, selected_league)

        # Si no hay filtro de liga, mostrar todos los equipos conocidos
        else:
            teams = ["All"] + sorted(team_to_league.keys())

        # Mostrar selectbox de equipo
        st.selectbox("Team", teams, key = team_key)

    # Crear copia tras filtro de liga
    df_team = df_league.copy()

    # Filtrar por equipo si no está seleccionado "All"
    if st.session_state[team_key] != "All":
        df_team = df_team[
            df_team["stats_Squad"].apply(lambda x: contains_value(x, st.session_state[team_key]))
        ]

    # Crear selector de edad
    with col3:

        # Obtener edades disponibles
        ages = sorted(df_team["stats_Age"].dropna().unique())

        # Mostrar selectbox de edad
        st.selectbox("Age", ["All"] + ages, key = age_key)

    # Crear copia tras filtro de equipo
    df_age = df_team.copy()

    # Filtrar por edad si se selecciona un valor específico
    if st.session_state[age_key] != "All":
        df_age = df_age[
            df_age["stats_Age"] == st.session_state[age_key]
        ]

    # Crear selector de posición
    with col4:

        # Obtener posiciones disponibles en el dataframe actual
        available_pos = df_age["stats_Pos"].dropna().unique()

        # Ordenar posiciones en orden lógico de fútbol
        pos_options = ["All"] + [
            p for p in ["GK", "DF", "MF", "FW"] if p in available_pos
        ]

        # Mostrar selectbox de posición
        st.selectbox("Position", pos_options, key = pos_key)

    # Crear copia tras filtro de edad
    df_final = df_age.copy()

    # Filtrar por posición si no está en "All"
    if st.session_state[pos_key] != "All":
        df_final = df_final[
            df_final["stats_Pos"] == st.session_state[pos_key]
        ]

    # Devolver dataframe final con todos los filtros aplicados
    return df_final