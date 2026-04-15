# ============================================
# Common -> filters
# ============================================

# Importar librerías
import pandas as pd
import streamlit as st

# Función para dividir valores separados por comas en una lista limpia
def split_multi_value(value):
    
    # Si el valor es nulo, devolver lista vacía
    if pd.isna(value):
        return []

    # Separar por comas, limpiar espacios y eliminar vacíos
    return [v.strip() for v in str(value).split(",") if v.strip()]

# Función para construir un mapa fiable equipo -> liga
def build_team_league_map(df, comp_col="stats_Comp", team_col="stats_Squad"):
    
    # Diccionario final equipo -> liga
    team_to_league = {}

    # Recorrer filas del dataframe
    for _, row in df.iterrows():
        comps = split_multi_value(row.get(comp_col))
        teams = split_multi_value(row.get(team_col))

        # Guardar solo relaciones simples y fiables
        if len(comps) == 1 and len(teams) == 1:
            team_to_league[teams[0]] = comps[0]

    return team_to_league

# Función para obtener opciones únicas de ligas
def get_league_options(df, comp_col="stats_Comp", team_col="stats_Squad"):
    
    # Construir mapa fiable
    team_to_league = build_team_league_map(df, comp_col, team_col)

    # Obtener ligas únicas ordenadas
    leagues = sorted(set(team_to_league.values()))

    return ["All"] + leagues

# Función para obtener equipos válidos para una liga seleccionada
def get_team_options(df, selected_league="All", comp_col="stats_Comp", team_col="stats_Squad"):
    
    # Construir mapa fiable
    team_to_league = build_team_league_map(df, comp_col, team_col)

    # Si no hay liga seleccionada, devolver todos los equipos conocidos
    if selected_league == "All":
        return ["All"] + sorted(team_to_league.keys())

    # Filtrar equipos cuya liga coincida con la seleccionada
    teams = sorted([
        team for team, league in team_to_league.items()
        if league == selected_league
    ])

    return ["All"] + teams

# Función para filtrar el dataframe por liga y equipo
def filter_df_by_league_team(df, selected_league="All", selected_team="All", comp_col="stats_Comp", team_col="stats_Squad"):
   
    # Si no hay filtros activos, devolver copia completa
    if selected_league == "All" and selected_team == "All":
        return df.copy()

    # Construir mapa fiable equipo -> liga
    team_to_league = build_team_league_map(df, comp_col, team_col)

    # Función auxiliar para comprobar si una fila cumple el filtro
    def row_matches(row):
        
        # Obtener todos los equipos de la fila
        row_teams = split_multi_value(row.get(team_col))

        # Si no hay equipos, la fila no sirve
        if not row_teams:
            return False

        # Caso: solo liga
        # Basta con que algún equipo de la fila pertenezca a esa liga
        if selected_league != "All" and selected_team == "All":
            return any(team_to_league.get(team) == selected_league for team in row_teams)

        # Caso: solo equipo
        if selected_league == "All" and selected_team != "All":
            return selected_team in row_teams

        # Caso: liga + equipo
        # La fila entra si contiene ese equipo y ese equipo pertenece a esa liga
        if selected_league != "All" and selected_team != "All":
            return (
                selected_team in row_teams and
                team_to_league.get(selected_team) == selected_league
            )

        return True
    
    # Aplicar filtro fila a fila
    return df[df.apply(row_matches, axis=1)].copy()

# Función principal para filtros de overview / ranking
def apply_player_filters_overview_rk(df, col1, col2, col3, col4, col5, prefix, checkbox=False):
    
    # Crear claves únicas para session_state
    minutes_key = f"{prefix}_minutes_filter"
    user_league_key = f"{prefix}_user_league_filter"
    league_key = f"{prefix}_league_filter"
    team_key = f"{prefix}_team_filter"
    age_key = f"{prefix}_age_filter"
    pos_key = f"{prefix}_pos_filter"

    # Crear copia del dataframe y convertir columnas numéricas clave
    df_base = df.copy()
    df_base["stats_Min"] = pd.to_numeric(df_base["stats_Min"], errors="coerce")
    df_base["stats_Age"] = pd.to_numeric(df_base["stats_Age"], errors="coerce")

    # Slider para porcentaje mínimo de minutos jugados
    with col5:
        minutes_filter = st.slider("% Min Played", 0, 100, key=minutes_key)

    # Aplicar filtro de minutos respecto al máximo del dataset
    max_min = df_base["stats_Min"].max()
    df_base = df_base[df_base["stats_Min"] >= max_min * minutes_filter / 100]

    # Inicializar variables para filtro opcional de liga del usuario
    comp_user = None
    use_user_league = False

    # Si se activa el checkbox, buscar la liga del equipo del usuario
    if checkbox:
        user_obj = st.session_state.get("user")
        
        if user_obj and user_obj.team:
            team_to_league = build_team_league_map(df)
            comp_user = team_to_league.get(user_obj.team)

    # Selector de liga
    with col1:
        leagues = get_league_options(df_base)
        st.selectbox("League", leagues, key=league_key)

    # Recuperar liga seleccionada
    selected_league = st.session_state.get(league_key, "All")

    # Checkbox opcional para usar la liga del equipo del usuario
    if checkbox and comp_user:
        use_user_league = st.checkbox(
            "Show only players of my team league",
            key=user_league_key
        )

    # Aplicar filtro de liga
    if use_user_league and comp_user:
        df_league = filter_df_by_league_team(df_base, selected_league=comp_user)
        selected_league_for_team = comp_user
    else:
        df_league = filter_df_by_league_team(df_base, selected_league=selected_league)
        selected_league_for_team = selected_league

    # Selector de equipo
    with col2:
        teams = get_team_options(df_base, selected_league_for_team)
        current_team = st.session_state.get(team_key, "All")

        # Resetear equipo si ya no está disponible
        if current_team not in teams:
            st.session_state[team_key] = "All"
            current_team = "All"

        selected_team = st.selectbox("Team", teams, key=team_key)

    # Aplicar filtro de equipo
    df_team = filter_df_by_league_team(
        df_league,
        selected_league=selected_league_for_team,
        selected_team=selected_team
    )

    # Selector de edad
    with col3:
        ages = sorted(df_team["stats_Age"].dropna().unique())
        st.selectbox("Age", ["All"] + ages, key=age_key)

    # Aplicar filtro de edad
    df_age = df_team.copy()
    if st.session_state[age_key] != "All":
        df_age = df_age[df_age["stats_Age"] == st.session_state[age_key]]

    # Selector de posición
    with col4:
        available_pos = df_age["stats_Pos"].dropna().unique()
        pos_options = ["All"] + [p for p in ["GK", "DF", "MF", "FW"] if p in available_pos]
        st.selectbox("Position", pos_options, key=pos_key)

    # Aplicar filtro de posición
    df_final = df_age.copy()
    if st.session_state[pos_key] != "All":
        df_final = df_final[df_final["stats_Pos"] == st.session_state[pos_key]]

    # Devolver dataframe final
    return df_final

# Función principal para filtros de lineup / list
def apply_player_filters_lineup_list(df, league_key, team_key, pos_key, player_key, pos_order=None):
    
    # Definir orden lógico de posiciones si no se proporciona
    if pos_order is None:
        pos_order = ["GK", "DF", "MF", "FW"]

    # Obtener opciones de liga
    league_options = get_league_options(df)
    current_league = st.session_state.get(league_key, "All")

    # Resetear liga si ya no está disponible
    if current_league not in league_options:
        st.session_state[league_key] = "All"
        current_league = "All"

    # Selector de liga
    selected_league = st.selectbox(
        "League",
        league_options,
        index=league_options.index(current_league),
        key=league_key
    )

    # Obtener equipos válidos solo para la liga seleccionada
    team_options = get_team_options(df, selected_league)
    current_team = st.session_state.get(team_key, "All")

    # Resetear equipo si ya no está disponible
    if current_team not in team_options:
        st.session_state[team_key] = "All"
        current_team = "All"

    # Selector de equipo
    selected_team = st.selectbox(
        "Team",
        team_options,
        index=team_options.index(current_team),
        key=team_key
    )

    # Aplicar filtros de liga y equipo
    df_filtered = filter_df_by_league_team(df, selected_league, selected_team)

    # Obtener posiciones disponibles tras los filtros anteriores
    available_positions = df_filtered["stats_Pos"].dropna().unique().tolist()
    pos_options = ["All"] + [p for p in pos_order if p in available_positions]

    current_pos = st.session_state.get(pos_key, "All")

    # Resetear posición si ya no está disponible
    if current_pos not in pos_options:
        st.session_state[pos_key] = "All"
        current_pos = "All"

    # Selector de posición
    selected_pos = st.selectbox(
        "Position",
        pos_options,
        index=pos_options.index(current_pos),
        key=pos_key
    )

    # Aplicar filtro de posición
    if selected_pos != "All":
        df_filtered = df_filtered[df_filtered["stats_Pos"] == selected_pos]

    # Obtener jugadores disponibles tras todos los filtros
    player_options = ["Select"] + sorted(df_filtered["Player"].dropna().unique().tolist())

    current_player = st.session_state.get(player_key, "Select")

    # Resetear jugador si ya no está disponible
    if current_player not in player_options:
        st.session_state[player_key] = "Select"
        current_player = "Select"

    # Selector de jugador
    selected_player = st.selectbox(
        "Player",
        player_options,
        index=player_options.index(current_player),
        key=player_key
    )

    # Devolver filtros seleccionados y dataframe filtrado final
    return selected_league, selected_team, selected_pos, selected_player, df_filtered

# Función para aplicar filtros de liga, equipo y posición
def apply_player_filters_radar(df, league_key, team_key, pos_key, league_label, team_label, pos_label, pos_order=None):
    
    # Definir orden lógico por defecto
    if pos_order is None:
        pos_order = ["GK", "DF", "MF", "FW"]

    # Obtener opciones de liga
    league_options = get_league_options(df)
    current_league = st.session_state.get(league_key, "All")

    # Resetear liga si ya no está disponible
    if current_league not in league_options:
        st.session_state[league_key] = "All"
        current_league = "All"

    # Selector de liga
    selected_league = st.selectbox(
        league_label,
        league_options,
        index=league_options.index(current_league),
        key=league_key
    )

    # Obtener equipos válidos para la liga elegida
    team_options = get_team_options(df, selected_league)
    current_team = st.session_state.get(team_key, "All")

    # Resetear equipo si ya no está disponible
    if current_team not in team_options:
        st.session_state[team_key] = "All"
        current_team = "All"

    # Selector de equipo
    selected_team = st.selectbox(
        team_label,
        team_options,
        index=team_options.index(current_team),
        key=team_key
    )

    # Aplicar filtro de liga y equipo
    df_filtered = filter_df_by_league_team(df, selected_league, selected_team)

    # Obtener posiciones disponibles
    available_positions = df_filtered["stats_Pos"].dropna().unique().tolist()
    pos_options = ["All"] + [p for p in pos_order if p in available_positions]

    current_pos = st.session_state.get(pos_key, "All")

    # Resetear posición si ya no está disponible
    if current_pos not in pos_options:
        st.session_state[pos_key] = "All"
        current_pos = "All"

    # Selector de posición
    selected_pos = st.selectbox(
        pos_label,
        pos_options,
        index=pos_options.index(current_pos),
        key=pos_key
    )

    # Aplicar filtro de posición
    if selected_pos != "All":
        df_filtered = df_filtered[df_filtered["stats_Pos"] == selected_pos]

    return selected_league, selected_team, selected_pos, df_filtered