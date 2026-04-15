# ============================================
# Common -> pdf_utils
# ============================================

# Importar librerías
import tempfile
from PIL import Image
import unicodedata

# Importar rutas de configuración
from common.config import (
    ASSETSIMG, ASSETSWATERMHIELDS
)

# Función para generar un watermark (marca de agua) a partir de un logo
def get_watermark(alpha: int = 30, user_obj=None, logo_filename: str = None) -> str:
        
    # Determinar el origen del logo a utilizar para el watermark
    if logo_filename:
        
        # Construir ruta del logo desde el archivo proporcionado
        logo_path = ASSETSIMG / logo_filename
    else:
        
        # Obtener ruta del logo del equipo del usuario
        logo_path = get_team_logo_path(user_obj, ASSETSWATERMHIELDS)

    # Abrir imagen del logo desde disco
    watermark = Image.open(logo_path).convert("RGBA")

    # Convertir imagen a RGBA para habilitar canal de transparencia

    # Aplicar nivel de transparencia definido por parámetro alpha
    watermark.putalpha(alpha)

    # Crear archivo temporal para almacenar el watermark generado
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")

    # Guardar imagen con transparencia en el archivo temporal
    watermark.save(tmp_file.name, format="PNG")

    # Cerrar archivo temporal para liberar recursos del sistema
    tmp_file.close()

    # Devolver ruta del archivo temporal generado
    return tmp_file.name

# Función para obtener la ruta del logo del equipo del usuario
def get_team_logo_path(user_obj, assets_folder):

    # Verificar si existe usuario o si tiene equipo asignado
    if not user_obj or not user_obj.team:
        
        # Devolver logo por defecto si no hay usuario o equipo
        return ASSETSIMG / "Logo_DataLab.png"

    # Obtener nombre del equipo del usuario
    team_name = user_obj.team

    # Normalizar nombre del equipo para estandarizar formato de archivos
    team_name_norm = ''.join(
        c for c in unicodedata.normalize('NFD', team_name)
        
        # Eliminar caracteres diacríticos (acentos)
        if unicodedata.category(c) != 'Mn'
    )

    # Convertir nombre a formato compatible con nombres de archivo
    team_name_norm = team_name_norm.lower().replace(" ", "_")

    # Construir ruta esperada del logo del equipo
    logo_path = assets_folder / f"Logo_{team_name_norm}.png"

    # Verificar si el archivo del logo existe en el sistema
    if not logo_path.exists():
        
        # Si no existe, devolver logo por defecto
        return ASSETSIMG / "Logo_DataLab.png"

    # Devolver ruta del logo del equipo si existe
    return logo_path