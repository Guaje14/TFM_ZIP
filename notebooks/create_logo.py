# ============================================
# Notebooks -> create_logo
# ============================================

# Importar librerías 
from PIL import Image, ImageDraw, ImageFont  # Manipulación de imágenes y textos
import os
import numpy as np
import sqlite3
import pandas as pd
from rapidfuzz import process
import unicodedata

# Función para convertir los escudos con fondo oscuro a blanco, manteniendo la transparencia
def convert_shields_white(input_folder = None, output_folder = None, threshold = None):
     
    # Crear la carpeta de salida si no existe, para guardar los archivos modificados
    os.makedirs(output_folder, exist_ok=True)

    # Recorrer todos los archivos en la carpeta de entrada
    for filename in os.listdir(input_folder):
        
        # Procesar solo archivos PNG
        if filename.lower().endswith(".png"):
            
            # Construir rutas completas de entrada y salida
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Abrir la imagen y convertirla a formato RGBA (Red, Green, Blue, Alpha)
            img = Image.open(input_path).convert("RGBA")
            
            # Convertir la imagen a un array de numpy para manipulación de píxeles
            data = np.array(img)

            # Separar los canales de color y el canal alpha (transparencia)
            r, g, b, a = data.T

            # Crear una máscara donde los píxeles sean "oscuros" según el umbral
            mask = (r < threshold) & (g < threshold) & (b < threshold)

            # Cambiar los píxeles oscuros a blanco, manteniendo el canal alpha (transparencia)
            data[..., :-1][mask.T] = [255, 255, 255]

            # Guardar la imagen modificada en la carpeta de salida
            Image.fromarray(data).save(output_path)

    # Mensaje de confirmación al finalizar el proceso
    print(f"✅ Escudos convertidos y guardados en: {output_folder}")

# Función para identificar los nombres de los equipos de "La Liga" en todas las tablas de una base de datos
def identify_teamsName(db_path = None):
    
    try:
        # Conectar a la base de datos SQLite especificada por db_path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Obtener los nombres de todas las tablas de la base de datos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()

        # Si no hay tablas, mostrar mensaje y salir
        if not tablas:
            print("❌ No hay tablas en la base de datos")
            return

        # Mostrar las tablas encontradas
        print(f"✅ Tablas encontradas: {[t[0] for t in tablas]}\n")

        # Iterar sobre cada tabla de la base de datos
        for (tabla,) in tablas:
            print(f"📊 Tabla: {tabla}")
            
            # Leer toda la tabla en un DataFrame de pandas
            df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
            
            # Filtrar filas donde la columna 'stats_Comp' es "La Liga" y obtener nombres únicos de equipos
            list_of_teams = df[df["stats_Comp"] == "La Liga"]["stats_Squad"].unique().tolist()
            print(f"Equipos de La Liga: {list_of_teams}")

        # Cerrar la conexión a la base de datos
        conn.close()

    except Exception as e:
        # Captura cualquier error que ocurra y lo imprime
        print(f"❌ Error: {e}")
        
    return list_of_teams

# Función para actualizar el nombre de los escudos con el nombre de los equipos encontrados
def update_name_shields(list_teamsName = None, folder_shields = None, threshold = None):
    
    # Función auxiliar para normalizar textos
    def normalizar(texto):
        return ''.join(
            
            # Descompone caracteres acentuados
            c for c in unicodedata.normalize('NFD', texto) 
            
            # Elimina marcas diacríticas (acentos)
            if unicodedata.category(c) != 'Mn'
        
        # Convierte a minúsculas y elimina espacios al inicio/final
        ).lower().strip()                                   
        
    # Función auxiliar para limpiar la lista de equipos
    def limpiar_equipos(lista_equipos):
        
        # Crear una lista vacía que almacenará los nombres de equipos ya procesados
        equipos_limpios = []
        
        # Iterar sobre cada elemento de la lista original de equipos
        for item in lista_equipos:
        
            # Separar posibles nombres múltiples en un solo string
            partes = item.split(",")            
        
            # Iterar sobre cada parte separada
            for p in partes:
        
                # Eliminar espacios al inicio y final, y agregar a la lista limpia
                equipos_limpios.append(p.strip())  
        
        # Eliminar duplicados convirtiendo la lista en un conjunto y luego de nuevo a lista
        return list(set(equipos_limpios))  

    print("🚀 INICIANDO PROCESO DE RENOMBRADO...\n")

    try:
        # Validar que la carpeta de escudos exista
        if not os.path.exists(folder_shields):
            print("❌ La carpeta no existe")
            return

        # Limpiar y preparar lista de equipos únicos
        equipos_limpios = limpiar_equipos(list_teamsName)

        if not equipos_limpios:
            print("❌ No hay equipos para procesar")
            return

        # Listar archivos PNG dentro de la carpeta
        archivos = [f for f in os.listdir(folder_shields) if f.lower().endswith(".png")]

        if not archivos:
            print("❌ No hay archivos PNG en la carpeta")
            return
        
        # Crear diccionario de archivos normalizados sin extensión
        archivos_norm = {
            normalizar(os.path.splitext(f)[0]): f  # Quitamos '.png' antes de normalizar
            for f in archivos
        }

        # Contadores para el resumen final
        encontrados = 0
        no_encontrados = []
        
        # Bucle principal de renombrado con dos intentos
        for intento, th in enumerate([threshold, threshold - 10], start=1):

            # Selecciona los equipos a procesar
            equipos_a_procesar = no_encontrados[:] if intento > 1 else equipos_limpios

            # Actualizar lista de archivos PNG que aún existen en la carpeta
            archivos_existentes = [f for f in os.listdir(folder_shields) if f.lower().endswith(".png")]

            # Normalizar los nombres de los archivos existentes
            archivos_norm = {normalizar(os.path.splitext(f)[0]): f for f in archivos_existentes}

            # Iterar sobre cada equipo a procesar en este intento
            for equipo in equipos_a_procesar:
                
                try:
                    # Normalizar nombre del equipo 
                    equipo_norm = normalizar(equipo)

                    # Buscar el archivo más parecido usando fuzzy matching
                    match_norm, score, _ = process.extractOne(equipo_norm, archivos_norm.keys())

                    # Obtener el nombre original del archivo correspondiente al match
                    archivo_original = archivos_norm[match_norm]

                    # Construir rutas completas de archivo original y archivo de destino
                    old_path = os.path.join(folder_shields, archivo_original)
                    new_name = f"{equipo}.png"                  # Nombre final del archivo
                    new_path = os.path.join(folder_shields, new_name)

                    # Mostrar información en consola
                    print(f"\n🔎 Equipo: {equipo}")
                    print(f"   → Match: {archivo_original}")
                    print(f"   → Similitud: {score:.2f}%")

                    # Si la similitud supera el threshold para este intento
                    if score >= th:
                        
                        # Verificar que el archivo original aún exista
                        if os.path.exists(old_path):
                            
                            # Renombrar (reemplaza si ya existe)
                            os.replace(old_path, new_path)

                            # Mostrar mensaje según sea primer o segundo intento
                            print(f"   ✅ {'SEGUNDO INTENTO ' if intento>1 else ''}RENOMBRADO → {new_name}")

                            # Quitar el equipo de la lista de no renombrados
                            no_encontrados.remove(equipo)

                            # Incrementar contador de encontrados
                            encontrados += 1
                        else:
                            # Si el archivo original ya no está en la carpeta
                            print(f"   ❌ Archivo original no encontrado: {archivo_original}")

                    else:
                        # Si la similitud es baja, no se renombra
                        if intento == 1:
                            no_encontrados.append(equipo)
                        print("   ❌ Similitud baja, no se renombra")

                except Exception as e:
                    # Captura errores específicos para cada equipo
                    print(f"   ❌ Error con equipo '{equipo}': {e}")

                    # En el primer intento, aseguramos que los equipos con error queden en no_encontrados
                    if intento == 1 and equipo not in no_encontrados:
                        no_encontrados.append(equipo)

        # Resumen final del proceso
        print("\n" + "="*50)
        print("📊 RESUMEN FINAL")
        print(f"Equipos únicos procesados: {len(equipos_limpios)}")
        print(f"Renombrados correctamente: {encontrados}")
        print(f"No renombrados / errores: {len(no_encontrados)} → {no_encontrados}")
        print("="*50)

    except Exception as e:
        # Captura cualquier error general del proceso
        print(f"❌ Error general: {e}")
        
# Función para crear el logo vertical con la imagen del escudo del equipo
def create_logo_vertical(path_shield = None, color_hex = None, start_text = None, end_text = None, size_shield = None, outpath = None, scale_vertical = 1.2):
    
    # Cargar escudo con transparencia
    escudo = Image.open(path_shield).convert("RGBA")

    # Redimensionar escudo
    factor = size_shield / escudo.height
    new_w = int(escudo.width * factor)
    new_h = int(escudo.height * factor)
    escudo_v = escudo.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Escalar extra para vertical
    new_w_v = int(new_w * scale_vertical)
    new_h_v = int(new_h * scale_vertical)
    escudo_v = escudo_v.resize((new_w_v, new_h_v), Image.Resampling.LANCZOS)

    # Crear lienzo vertical dinámico
    lienzo_v_ancho = max(new_w_v + 40, 400)
    lienzo_v_alto = new_h_v + 150
    lienzo_v = Image.new("RGBA", (lienzo_v_ancho, lienzo_v_alto), (255, 255, 255, 0))
    draw_v = ImageDraw.Draw(lienzo_v)

    # Pegar escudo centrado arriba
    pos_x_escudo_v = (lienzo_v_ancho - new_w_v) // 2
    lienzo_v.paste(escudo_v, (pos_x_escudo_v, 0), escudo_v)

    # Cargar fuentes
    try:
        f_grande = ImageFont.truetype("arialbd.ttf", 53)
        f_pequena = ImageFont.truetype("arial.ttf", 28)
    except:
        f_grande = ImageFont.load_default()
        f_pequena = ImageFont.load_default()

    # Textos centrados debajo del escudo (puedes ajustar distancias si quieres)
    draw_v.text((lienzo_v_ancho // 2, new_h_v - 15), start_text, font=f_grande, fill=color_hex, anchor="ma")
    draw_v.text((lienzo_v_ancho // 2, new_h_v + 45), end_text, font=f_pequena, fill=color_hex, anchor="ma")

    # Guardar logo vertical
    lienzo_v.save(outpath, "PNG")
    print(f"✅ Logo vertical generado: {outpath}\n")
    
#Función para crear un logo dimple
def create_simple_logo(start_text = None, end_text = None, color_hex = None, outpath = None, canvas_size = None):

    # Crear lienzo transparente
    lienzo = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(lienzo)

    # Cargar fuentes
    try:
        f_grande = ImageFont.truetype("arialbd.ttf", 80)  # Texto principal
        f_pequena = ImageFont.truetype("arial.ttf", 30)   # Texto secundario
    except:
        f_grande = ImageFont.load_default()
        f_pequena = ImageFont.load_default()

    # Medir texto usando textbbox
    bbox_start = draw.textbbox((0,0), start_text, font=f_grande)
    w_start = bbox_start[2] - bbox_start[0]
    h_start = bbox_start[3] - bbox_start[1]

    bbox_end = draw.textbbox((0,0), end_text, font=f_pequena)
    w_end = bbox_end[2] - bbox_end[0]
    h_end = bbox_end[3] - bbox_end[1]

    # Calcular posición vertical centrada
    total_height = h_start + 10 + h_end  
    y_start = (canvas_size[1] - total_height) // 2
    y_end = y_start + h_start + 10

    # Texto centrado horizontalmente
    x_start = (canvas_size[0] - w_start) // 2
    x_end = (canvas_size[0] - w_end) // 2

    # Dibujar textos con offset manual
    draw.text((x_start, y_start - 15), start_text, font=f_grande, fill=color_hex)
    draw.text((x_end, y_end + 15), end_text, font=f_pequena, fill=color_hex)

    # Guardar imagen
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    lienzo.save(outpath, "PNG")
    print(f"✅ Logo creado y guardado en {outpath}")
    
# Función para generar los logos que serán utilizados como marcas de agua
def create_watermark_vertical(path_shield = None, color_hex = None, start_text = None, end_text = None, size_shield = None, outpath = None, scale_vertical = 1.2, recolor = True):
    
    # Cargar escudo
    escudo = Image.open(path_shield).convert("RGBA")
    
    # Función auxiliar para recolorear el escudo
    def recolor_shield(img: Image.Image, target_color=(0, 0, 0)):

        data = np.array(img.convert("RGBA"))

        # Mantener alpha
        alpha = data[..., 3]

        # Aplicar color a todos los píxeles visibles
        data[..., 0] = target_color[0]
        data[..., 1] = target_color[1]
        data[..., 2] = target_color[2]

        # Restaurar alpha
        data[..., 3] = alpha

        return Image.fromarray(data)

    # Recolorear a negro si se activa
    if recolor:
        escudo = recolor_shield(
            escudo,
            target_color=(0, 0, 0)
        )

    # Redimensionar escudo
    factor = size_shield / escudo.height
    new_w = int(escudo.width * factor)
    new_h = int(escudo.height * factor)
    escudo_v = escudo.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Escala vertical extra
    new_w_v = int(new_w * scale_vertical)
    new_h_v = int(new_h * scale_vertical)
    escudo_v = escudo_v.resize((new_w_v, new_h_v), Image.Resampling.LANCZOS)

    # Lienzo
    lienzo_v_ancho = max(new_w_v + 40, 400)
    lienzo_v_alto = new_h_v + 150
    lienzo_v = Image.new("RGBA", (lienzo_v_ancho, lienzo_v_alto), (255, 255, 255, 0))
    draw_v = ImageDraw.Draw(lienzo_v)

    # Pegar escudo centrado
    pos_x = (lienzo_v_ancho - new_w_v) // 2
    lienzo_v.paste(escudo_v, (pos_x, 0), escudo_v)

    # Fuentes
    try:
        f_grande = ImageFont.truetype("arialbd.ttf", 53)
        f_pequena = ImageFont.truetype("arial.ttf", 28)
    except:
        f_grande = ImageFont.load_default()
        f_pequena = ImageFont.load_default()

    # Textos
    draw_v.text((lienzo_v_ancho // 2, new_h_v - 15), start_text, font=f_grande, fill=color_hex, anchor="ma")
    draw_v.text((lienzo_v_ancho // 2, new_h_v + 45), end_text, font=f_pequena, fill=color_hex, anchor="ma")

    # Guardar
    lienzo_v.save(outpath, "PNG")

    return outpath

