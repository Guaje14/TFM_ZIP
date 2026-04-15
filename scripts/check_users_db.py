# ============================================
# Scripts -> check_users_db
# ============================================

# Importar librerías 
import tomllib
from pathlib import Path
from sqlalchemy import create_engine, text

# Configuración de paths y archivos
BASE_DIR = Path(__file__).resolve().parents[1]
SECRETS_FILE = BASE_DIR / ".streamlit" / "secrets.toml"

with open(SECRETS_FILE, "rb") as f:
    secrets = tomllib.load(f)

# Obtener URL de conexión a la base de datos desde secrets.toml
db_url = secrets["connections"]["users_db"]["url"]

# Crear engine SQLAlchemy
engine = create_engine(db_url)

# Verificar conexión y mostrar usuarios
with engine.begin() as conn:
    rows = conn.execute(
        text("SELECT username, role, team FROM users ORDER BY username;")
    ).fetchall()

print("Usuarios en la base:")
for row in rows:
    print(row)