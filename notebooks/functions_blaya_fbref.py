# ============================================
# Notebooks -> functions_blaya_fbref
# ============================================

# Importar librerías 
import pandas as pd             
import numpy as np              
import re                  
from tqdm.notebook import tqdm 
from difflib import get_close_matches
from IPython.display import display

# Mostrar todas las columnas del DataFrame
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

# Función para analizar la estructura general de un DataFrame
def analyze_dataframe_structure(df):
    
    # Resumen del dataset de Fbref
    print("\n=== Número de filas y columnas ===")
    print(f"Filas: {df.shape[0]}")
    print(f"Columnas: {df.shape[1]}")

    print("\n=== Columnas y tipos de datos ===")
    for col, dtype in df.dtypes.items():
        print(f"{col:30} : {dtype}")

    print("\n=== Información resumida del DataFrame ===")
    df.info()
    
# Función para identificar y visualizar jugadores duplicados en el DataFrame
def identify_duplicates_fbref(df):
    
    # Filtrar solo los registros duplicados según las 3 columnas
    df_duplicados = df[df.duplicated(subset=["Player", "stats_Nation", "stats_Born"], keep=False)]

    # Ordenar el DataFrame por esas columnas para que las filas duplicadas queden agrupadas
    df_duplicados = df_duplicados.sort_values(by=["Player", "stats_Nation", "stats_Born"]).reset_index(drop=True)

    # Mostrar una muestra de los duplicados encontrados (primeras filas)
    if not df_duplicados.empty:
        print(f"🔁 Se han encontrado {len(df_duplicados)} filas duplicadas. Mostrando muestra:")
        display(df_duplicados.head(10))  # Puedes ajustar el número de filas a mostrar
    else:
        print("✅ No se encontraron jugadores duplicados en el dataset.")
    
    return df_duplicados

# Función para transformar y limpiar el Dataframe
def process_fbref_dataset_verbose(dataset_stats_fbref, verbose=True):

    # Copiar dataset original para no modificarlo
    try:
        df = dataset_stats_fbref.copy()
    except Exception as e:
        print(f"❌ Error al copiar el dataset: {e}")
        return pd.DataFrame(), pd.DataFrame()

    # 1️⃣ Limpieza inicial
    try:
        # Identificar columnas irrelevantes y eliminar
        drop_cols = [
            col for col in df.columns 
            if not col.startswith('stats_') and 
            any(p in col for p in ['_Nation', '_Squad', '_Pos', '_Comp', '_Age', '_Born'])
        ]
        df = df.drop(columns=drop_cols, errors='ignore')

        # Convertir columnas numéricas a tipo float
        exclude_cols = ['Player', 'stats_Nation', 'stats_Pos', 'stats_Squad', 'stats_Comp', 'league']
        for col in df.columns:
            if col not in exclude_cols:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

        
        # ---------------------------------------------------------
        # Función para renombrar columnas con sufijos (_1, _2, _3) a nombres descriptivos de periodos por 90 minutos
        # ---------------------------------------------------------
        def rename_suffix(col_name):
            match = re.search(r'_(1|2|3)$', col_name)
            if match:
                suffix = match.group(1)
                if suffix == "1":
                    return col_name.replace("_1", "short/90")
                elif suffix == "2":
                    return col_name.replace("_2", "medium/90")
                elif suffix == "3":
                    return col_name.replace("_3", "long/90")
            return col_name

        # Renombrar columnas con sufijos a nombres descriptivos por periodo (/90)
        df.columns = [rename_suffix(col) for col in df.columns]

        # Rellenar valores nulos con 0
        df = df.fillna(0)

        # Reordenar columna 'league' después de 'stats_Comp'
        if 'league' in df.columns and 'stats_Comp' in df.columns:
            cols = df.columns.tolist()
            cols.remove('league')
            idx = cols.index('stats_Comp')
            cols.insert(idx + 1, 'league')
            df = df[cols]

        # Asignar Id único a cada jugador
        df["Id_player"] = range(1, len(df) + 1)
        df = df[["Id_player"] + [col for col in df.columns if col != "Id_player"]]

        if verbose:
            print(f"✅ Limpieza inicial completada con {len(df)} filas y {len(df.columns)} columnas.\n")

    except Exception as e:
        print(f"❌ Error durante la limpieza inicial: {e}")
        return pd.DataFrame(), pd.DataFrame()

    # 2️⃣ Identificación de duplicados
    try:
        # Identificar jugadores duplicados según columnas clave
        key_cols = ['Player', 'stats_Nation', 'stats_Born']
        counts = df.groupby(key_cols).size().reset_index(name='count')
        duplicados = counts[counts['count'] > 1].drop(columns='count')

        # Crear DataFrame con filas duplicadas
        df_duplicados = df.merge(duplicados, on=key_cols, how='inner')
        df_duplicados = df_duplicados.sort_values(by=key_cols).reset_index(drop=True)

        if verbose:
            print(f"🔎 Se detectaron {len(df_duplicados)} filas duplicadas correspondientes a {len(duplicados)} jugadores.\n")

        # Retornar si no hay duplicados
        if df_duplicados.empty:
            if verbose: print("No se detectaron duplicados. Devolviendo dataset limpio.")
            return df, pd.DataFrame()
    except Exception as e:
        print(f"❌ Error durante la identificación de duplicados: {e}")
        return df, pd.DataFrame()

    # 3️⃣ Crear filas colapsadas
    try:
        # Eliminar Id_player de duplicados para crear filas colapsadas
        df_duplicados_sin_id = df_duplicados.copy()
        df_duplicados_sin_id.drop(columns=["Id_player"], inplace=True)

        # Definir columnas a resumir y columnas identificadoras
        resumen_cols = ['stats_Squad', 'stats_Comp', 'stats_Pos']
        id_cols = ['stats_Nation', 'stats_Squad', 'stats_Comp', 'league', 'stats_Pos', 'stats_Born', 'stats_Age']

        # Inicializar lista para filas colapsadas
        result_rows = []

        # Recorrer duplicados por jugador y crear fila única combinando valores
        for player, group in df_duplicados_sin_id.groupby("Player"):
            row = {"Player": player}
            for col in id_cols:
                unique_vals = group[col].dropna().unique()
                if len(unique_vals) == 1:
                    row[col] = unique_vals[0]
                else:
                    if col in resumen_cols:
                        row[col] = ", ".join(sorted(map(str, set(unique_vals))))
                    else:
                        row[col] = np.nan
            for col in df_duplicados_sin_id.columns:
                if col not in id_cols and col != "Player":
                    row[col] = np.nan
            result_rows.append(row)

        # Crear DataFrame colapsado
        df_colapsado = pd.DataFrame(result_rows)

        if verbose:
            print(f"📄 Se crearon {len(df_colapsado)} filas colapsadas para los duplicados.\n")
    except Exception as e:
        print(f"❌ Error al crear filas colapsadas: {e}")
        return df, df_duplicados

    # 4️⃣ Rellenar estadísticas colapsadas
    try:
        # Crear copia para rellenar estadísticas
        df_filled = df_colapsado.copy()

        # Identificar columnas numéricas
        num_cols = [col for col in df.columns if col not in ['Player'] + id_cols + ['Id_player']]

        # Agrupar por jugador para sumar o promediar estadísticas
        grouped = df.groupby("Player")

        # Rellenar estadísticas numéricas: sumar totales o promediar por 90
        for i, row in df_filled.iterrows():
            player = row["Player"]
            if player not in grouped.groups:
                continue
            group = grouped.get_group(player)
            for col in num_cols:
                if pd.api.types.is_numeric_dtype(group[col]):
                    if col.endswith("/90"):
                        df_filled.at[i, col] = group[col].mean(skipna=True)
                    else:
                        df_filled.at[i, col] = group[col].sum(skipna=True)

        if verbose:
            print(f"🤖 Estadísticas de duplicados completadas.\n")
    except Exception as e:
        print(f"❌ Error al rellenar estadísticas colapsadas: {e}")
        return df, df_duplicados

    # 5️⃣ Unificar dataset final
    try:
        # Filtrar DataFrame original para eliminar duplicados
        id_list = df_duplicados["Id_player"].unique().tolist()
        df = df[~df["Id_player"].isin(id_list)]

        # Preparar DataFrame colapsado para concatenar
        if "Id_player" in df_filled.columns:
            df_filled.drop(columns="Id_player", inplace=True)
        df_filled.insert(0, "Id_player", 0)

        # Concatenar DataFrames y reasignar Id único
        df_final = pd.concat([df, df_filled], ignore_index=True)
        df_final["Id_player"] = range(1, len(df_final) + 1)

        if verbose:
            print(f"🔗 Dataset final unificado con {len(df_final)} filas.\n")
    except Exception as e:
        print(f"❌ Error al unificar dataset final: {e}")
        return df, df_duplicados

    # 6️⃣ Limpieza final de columnas de texto
    try:
        # Limpiar columna 'stats_Nation' para quedarse solo con última palabra
        if 'stats_Nation' in df_final.columns:
            df_final['stats_Nation'] = df_final['stats_Nation'].astype(str).apply(lambda x: x.split()[-1] if pd.notna(x) else x)

        # Limpiar columna 'stats_Pos' para quedarse solo con primer rol principal
        if 'stats_Pos' in df_final.columns:
            df_final['stats_Pos'] = df_final['stats_Pos'].astype(str).apply(lambda x: x.split(',')[0].strip() if pd.notna(x) else x)

        if verbose:
            print("🎉 Proceso de transformación y limpieza completado con éxito.\n")
    except Exception as e:
        print(f"❌ Error durante la limpieza final: {e}")

    # Retornar dataset final limpio 
    return df_final

# Función para filtrar jugadores por posición y rango de edad
def filter_players(
    df,                        # DataFrame con los datos de jugadores
    player_name,               # Nombre del jugador de referencia
    age_min,                   # Edad mínima para el filtro
    age_max,                   # Edad máxima para el filtro
    top_by = None,             # Columna usada para ordenar y obtener los mejores
    n_top5 = 5,                # Cantidad de jugadores del top5
    n_top50 = 50               # Cantidad de jugadores del top50
):

    # Validaciones básicas
    if df is None or df.empty:
        raise ValueError("El DataFrame proporcionado está vacío o es None.")
    if not isinstance(player_name, str) or not player_name.strip():
        raise ValueError("Debe proporcionar un nombre de jugador válido.")
    if age_min > age_max:
        raise ValueError("El valor mínimo de edad no puede ser mayor que el máximo.")
    if top_by is None or top_by not in df.columns:
        raise ValueError(f"Debe indicar una columna existente para top_by. Columnas disponibles: {df.columns.tolist()}")

    #  Buscar jugador por similitud
    jugadores = df['Player'].astype(str).tolist()                               # Lista de nombres
    coincidencias = get_close_matches(player_name, jugadores, n=1, cutoff=0.6)  # Coincidencia más cercana
    if not coincidencias:
        raise ValueError(f"No se encontró ningún jugador similar a '{player_name}' en el dataset.")
    
    jugador_encontrado = coincidencias[0]               # Nombre exacto encontrado
    fila = df.loc[df['Player'] == jugador_encontrado]   # Fila del jugador
    posicion = fila['stats_Pos'].values[0]              # Obtener posición del jugador

    # Filtrar jugadores por misma posición y rango de edad 
    jugadores_filtrados = df[
        (df['stats_Pos'] == posicion) & 
        (df['stats_Age'] >= age_min) & 
        (df['stats_Age'] <= age_max)
    ].copy()
    if jugadores_filtrados.empty:
        raise ValueError(f"No se encontraron jugadores en la posición '{posicion}' y rango de edad {age_min}-{age_max}.")

    # Ordenar por la columna indicada 
    jugadores_filtrados_sorted = jugadores_filtrados.sort_values(by=top_by, ascending=False)

    # Generar top50 
    top50 = jugadores_filtrados_sorted.head(n_top50)

    # Generar top5 asegurando que el jugador seleccionado esté incluido 
    top5_temp = jugadores_filtrados_sorted.head(n_top5)
    if jugador_encontrado not in top5_temp['Player'].values:
        # Si el jugador no está, tomar los primeros n_top5-1 y añadirlo como último
        top5_temp = pd.concat([top5_temp.head(n_top5-1), fila], ignore_index=True)
    
    top5 = top5_temp

    # Validación final: mostrar resultados
    print("✅ Top 5 jugadores seleccionados:")
    display(top5)  # Mostrar el DataFrame completo del top5
    print("\n✅ Primeros 10 del Top 50:")
    display(top50.head(10))  # Mostrar solo los primeros 10 del top50
    
    # Retornar DataFrames filtrados 
    return jugadores_filtrados, top5, top50