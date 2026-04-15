# ============================================
# Common -> config
# ============================================

# Importar librerías 
from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

# Raíz del proyecto
BASE_DIR = Path(__file__).resolve().parents[1]

# Assets
ASSETSIMG = BASE_DIR / "assets" / "img"
ASSETSSHIELDS = BASE_DIR / "assets" / "shields"
ASSETSLOGOSHIELDS = BASE_DIR / "assets" / "logo shields"
ASSETSWATERMHIELDS = BASE_DIR / "assets" / "logo watermark"
ASSETSFONTS = BASE_DIR / "assets" / "font"

# Data
DATA_DIR = BASE_DIR / "data"

# Base de datos local de stats de jugadores
DB_PATH = BASE_DIR / Path(os.getenv("DB_PATH", "data/players_stats.db"))

# Logs de exportación
LOG_FILE = BASE_DIR / Path(os.getenv("LOG_FILE", "data/logs_exports.xlsx"))

