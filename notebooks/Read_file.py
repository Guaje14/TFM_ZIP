# --- Importar Librerías necesarías --- 
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from pandas import json_normalize
import os
from IPython.display import display


# --- Definir función para aplanar JSON anidado ---
def flatten_nested_structures(df, sep='_'):
    # Crear copia del DataFrame para no modificar el original
    df = df.copy()
    # Iterar hasta eliminar todas las columnas anidadas
    while True:
        nested_cols = []
        # Identificar columnas que contengan diccionarios o listas
        for col in df.columns:
            sample = df[col].dropna()
            if sample.empty:
                continue
            first_val = sample.iloc[0]
            if isinstance(first_val, dict) or isinstance(first_val, list):
                nested_cols.append(col)
        # Romper ciclo si no existen columnas anidadas
        if not nested_cols:
            break
        col = nested_cols[0]
        # Detectar listas de dos números (coordenadas u otros valores)
        if df[col].apply(lambda x: isinstance(x, list) and len(x) == 2 and all(isinstance(i, (int, float)) for i in x)).all():
            # Separar lista en columnas x e y
            df[f"{col}_x"] = df[col].apply(lambda x: x[0] if isinstance(x, list) else np.nan)
            df[f"{col}_y"] = df[col].apply(lambda x: x[1] if isinstance(x, list) else np.nan)
            # Eliminar columna original
            df = df.drop(columns=[col])
            continue
        # Explode si la columna contiene listas
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df = df.explode(col).reset_index(drop=True)
            # Reemplazar valores nulos por diccionario vacío
            df[col] = df[col].apply(lambda x: {} if pd.isna(x) else x)
        # Normalizar diccionarios en nuevas columnas
        normalized = json_normalize(df[col], sep=sep)
        # Renombrar columnas para mantener jerarquía
        def rename_col(c):
            if c.startswith(f"{col}{sep}"):
                return c
            else:
                return f"{col}{sep}{c}"
        normalized.columns = [rename_col(c) for c in normalized.columns]
        # Reordenar columnas manteniendo orden original
        original_cols = list(df.columns)
        df = df.drop(columns=[col])
        idx = original_cols.index(col)
        left = original_cols[:idx]
        right = original_cols[idx+1:]
        new_order = left + list(normalized.columns) + right
        df = pd.concat([df[left + right], normalized], axis=1)
        df = df[new_order]
    # Retornar DataFrame completamente aplanado
    return df

# --- Definir función para abrir XML jerárquico ---
def xml_instance_to_df(ruta_archivo):
    # Abrir archivo en modo binario
    with open(ruta_archivo, "rb") as f:
        contenido = f.read()
    # Intentar decodificar como UTF-16; si falla, usar UTF-8 ignorando errores
    try:
        texto = contenido.decode("utf-16")
    except UnicodeError:
        texto = contenido.decode("utf-8", errors="ignore")
    # Parsear texto XML y obtener raíz
    root = ET.fromstring(texto)
    # Inicializar lista para almacenar filas
    data = []
    # Iterar sobre cada nodo 'instance'
    for instance in root.findall(".//instance"):
        fila = {}
        # Extraer elementos básicos: ID, start, end, code
        for tag in ["ID", "start", "end", "code"]:
            elem = instance.find(tag)
            fila[tag] = elem.text if elem is not None else None
        # Concatenar etiquetas 'group' y 'text' en un mismo campo
        for label in instance.findall("label"):
            group = label.find("group")
            text = label.find("text")
            if group is not None and text is not None:
                if group.text in fila:
                    fila[group.text] += " | " + text.text
                else:
                    fila[group.text] = text.text
        # Añadir fila al conjunto de datos
        data.append(fila)
    # Convertir lista de diccionarios en DataFrame
    df = pd.DataFrame(data)
    # Retornar DataFrame resultante
    return df

# --- Definir función principal no interactiva ---
def cargar_archivo(path, type, see_sample = False, see_resum=False):
    
    # Convertir tipo a mayúsculas
    tipo = type.upper()
    
    try:
        # Cargar CSV
        if tipo == 'CSV':
            df = pd.read_csv(path)
        # Cargar JSON y aplanar estructuras anidadas
        elif tipo == 'JSON':
            df = pd.read_json(path)
            df = flatten_nested_structures(df)
        # Cargar XML jerárquico
        elif tipo == 'XML':
            df = xml_instance_to_df(path)
        elif tipo == 'EXCEL':
            df = pd.read_excel(path)
        else:
            raise ValueError("Tipo de archivo no soportado. Usar 'CSV', 'JSON', 'XML' o 'Excel'.")
        
        # Mensaje de éxito
        if see_resum:
            # Mostrar mensaje de éxito
            print(f"Archivo cargado correctamente.")
            
            # Mostrar dimensiones del DataFrame
            print(f"El DataFrame tiene {df.shape[0]} filas y {df.shape[1]} columnas.")
        
        # Mostrar primeras filas solo si el usuario lo solicita
        if see_sample:
            display(df.head())
    
    except Exception as e:
        print(f"Error al abrir el archivo: {e}")
        return None
    
    return df
    
# --- Definir función para inspeccionar archivo ---
def file_inspector(file_path = None, see_sample = False, see_resum = False):
    
    # Extensiones soportadas y su nombre legible
    supported_types = {
        ".csv":  "CSV",
        ".json": "JSON",
        ".xml":  "XML",
        ".xlsx": "EXCEL"
    }

    # Detectar extensión
    ext = os.path.splitext(file_path)[1].lower()

    # Detectar type automáticamente
    if ext in supported_types:
        file_type = supported_types[ext]
        print(f"🔍 Tipo detectado automáticamente: {file_type}")
    else:
        print(f"⚠️ Extensión '{ext}' no reconocida. No se puede detectar el tipo.")
        file_type = None  # deja que cargar_archivo gestione esto

    # Importar la función cargar_archivo
    from Read_file import cargar_archivo
    
    # Cargar el archivo usando la función existente
    df = cargar_archivo(file_path, type=file_type, see_sample=see_sample, see_resum=see_resum)

    if df is None:
        print("⚠️ No se puede analizar un DataFrame vacío o no cargado.")
        return

    print("🧩 --- RESUMEN GENERAL DEL ARCHIVO ---")
    print(f"📏 Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas\n")

    print("📚 --- Tipos de datos ---")
    type_counts = df.dtypes.value_counts()
    for tipo, count in type_counts.items():
        print(f"🔠 {tipo}: {count} columnas")

    print("\n")

    print("🧮 --- Recuento de valores nulos ---")
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    print(f"🔢 Total de valores nulos en el DataFrame: {total_nulls}")

    columnas_con_nulos = null_counts[null_counts > 0].index.tolist()
    if total_nulls > 0:
        print(f"📌 Columnas que contienen nulos ({len(columnas_con_nulos)}):")
        print(columnas_con_nulos)
    else:
        print("✅ No se encontraron valores nulos en ninguna columna")

    print("\n")

    duplicados = df.duplicated().sum()
    print("♻️ --- Filas duplicadas ---")
    print(f"⚙️ Total de duplicados: {duplicados}")

    print("\n✅ Análisis completado\n")


# --- Definir función para inspeccionar los archivos de una carpeta ---
def folder_inspector(folder_path = None, see_rows = False, see_table = True):

    # Función auxiliar para encontrar columna de minutos
    def find_minutes_column(df):
        keywords = ["min", "minute", "minutes", "minutos"]
        for c in df.columns:
            if any(k in c.lower() for k in keywords):
                return c
        return None

    # Función auxiliar para encontrar columna de posición
    def find_position_column(df):
        keywords = ["pos", "position", "posición"]
        for c in df.columns:
            if any(k in c.lower() for k in keywords):
                return c
        return None

    # Función auxiliar para encontrar columna de nombre/equipo
    def find_name_column(df):
        keywords = ["name", "team", "nombre", "jugador"]
        for c in df.columns:
            if any(k in c.lower() for k in keywords):
                return c
        return None

    # Listas para almacenar resultados
    summary = []
    players_rows = []
    teams_rows = []

    # Diccionario para mantener consistencia de equipos por “archivo padre”
    selected_teams_dict = {}

    # Iterar sobre archivos CSV en la carpeta
    for file in os.listdir(folder_path):
        if not file.endswith(".csv"):
            continue

        full_path = os.path.join(folder_path, file)
        df = pd.read_csv(full_path)

        # Resumen estadístico básico
        summary.append({
            "File": file,
            "Rows": df.shape[0],
            "Columns": df.shape[1],
            "int64": (df.dtypes == "int64").sum(),
            "float64": (df.dtypes == "float64").sum(),
            "object": (df.dtypes == "object").sum(),
            "NaN": df.isna().sum().sum(),
            "Duplicates": df.duplicated().sum()
        })

        # Selección de filas representativas
        if see_rows:
            selected_rows = pd.DataFrame()

            # Detectamos Players vs Teams según nombre del archivo
            if "player" in file.lower() or "jugador" in file.lower():
                # Players: portero + jugador de campo 
                pos_col = find_position_column(df)
                min_col = find_minutes_column(df)

                # Limpiar y convertir columna de minutos a float
                if pos_col and min_col:
                    df[min_col] = (
                        df[min_col].astype(str)
                        .str.replace(",", "", regex=False)
                        .astype(float)
                    )

                    # Portero con más minutos
                    gk_df = df[
                        df[pos_col].astype(str).str.lower().str.contains("goal", na=False)
                    ]
                    
                    # Seleccionar portero con más minutos
                    if not gk_df.empty:
                        selected_rows = pd.concat([
                            selected_rows,
                            gk_df.loc[gk_df[min_col].idxmax()].to_frame().T
                        ])

                    # Jugador de campo con más minutos
                    outfield_df = df.drop(gk_df.index)
                    if not outfield_df.empty:
                        selected_rows = pd.concat([
                            selected_rows,
                            outfield_df.loc[outfield_df[min_col].idxmax()].to_frame().T
                        ])

                if selected_rows.empty:
                    selected_rows = df.head(2)

                # Agregar filas seleccionadas a la lista
                players_rows.append((file, selected_rows.reset_index(drop=True)))

            # Teams: elegir 2 equipos consistentes
            elif "team" in file.lower() or "equip" in file.lower():
                name_col = find_name_column(df)
                if not name_col:
                    selected_rows = df.head(2)  # fallback
                else:
                    # Determinar el "archivo padre" eliminando sufijo _x90
                    parent_file = file.lower().replace("_x90", "")
                    if parent_file in selected_teams_dict:
                        teams_to_show = selected_teams_dict[parent_file]
                        selected_rows = df[df[name_col].astype(str).isin(teams_to_show)]
                    else:
                        # Elegir los primeros 2 equipos como predeterminados
                        selected_rows = df.head(2)
                        teams_to_show = selected_rows[name_col].astype(str).tolist()
                        selected_teams_dict[parent_file] = teams_to_show

                teams_rows.append((file, selected_rows.reset_index(drop=True)))

            else:
                # Archivos no identificados → se agregan a ambos
                selected_rows = df.head(2)
                players_rows.append((file, selected_rows.reset_index(drop=True)))
                teams_rows.append((file, selected_rows.reset_index(drop=True)))

    # Mostrar filas representativas
    if see_rows:
        if players_rows:
            print("\n📄 Filas representativas de Players")
            for fname, df_rows in players_rows:
                print(f"\n-- {fname} --")
                display(df_rows)
        if teams_rows:
            print("\n\n📄 Filas representativas de Teams")
            for fname, df_rows in teams_rows:
                print(f"\n-- {fname} --")
                display(df_rows)

    # Mostrar tabla resumen
    if see_table:
        summary_df = pd.DataFrame(summary)

        players_df = summary_df[
            summary_df["File"].str.contains("player|jugador", case=False, regex=True)
        ]
        teams_df = summary_df[
            summary_df["File"].str.contains("team|equipo|club", case=False, regex=True)
        ]

        print("\n📁 Tabla comparativa de Players")
        display(players_df.reset_index(drop=True))

        print("\n📁 Tabla comparativa de Teams")
        display(teams_df.reset_index(drop=True))