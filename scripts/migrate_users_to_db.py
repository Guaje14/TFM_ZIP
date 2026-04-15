# ============================================
# Scripts -> migratie_users_to_db
# ============================================

# Importar librerías 
import pandas as pd
import bcrypt
import tomllib
from pathlib import Path
from sqlalchemy import create_engine, text

# Configuración de paths y archivos
BASE_DIR = Path(__file__).resolve().parents[1]
SECRETS_FILE = BASE_DIR / ".streamlit" / "secrets.toml"
USERS_XLSX = BASE_DIR / "data" / "users.xlsx"

# Leer la URL de conexión desde .streamlit/secrets.toml
with open(SECRETS_FILE, "rb") as f:
    secrets = tomllib.load(f)

# Obtener URL de conexión a la base de datos desde secrets.toml
db_url = secrets["connections"]["users_db"]["url"]

# Crear engine SQLAlchemy
engine = create_engine(db_url)

# Leer usuarios desde el Excel
df = pd.read_excel(USERS_XLSX)

# Limpiar nombres de columnas por seguridad
df.columns = [str(col).strip() for col in df.columns]

# Validar que las columnas necesarias estén presentes
required_cols = {"user", "password", "role", "team"}
missing = required_cols - set(df.columns)

if missing:
    raise ValueError(f"Faltan columnas en users.xlsx: {missing}")

# Crear tablas si no existen
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer',
    team TEXT
);
"""

create_access_log_table = """
CREATE TABLE IF NOT EXISTS access_log (
    id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    role TEXT,
    team TEXT,
    hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

# Insertar usuarios del Excel con hash de contraseña
insert_user_sql = """
INSERT INTO users (username, password_hash, role, team)
VALUES (:username, :password_hash, :role, :team)
ON CONFLICT (username)
DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    team = EXCLUDED.team;
"""

# Ejecutar migración dentro de una transacción
with engine.begin() as conn:
    
    # Crear tablas si no existen
    conn.execute(text(create_users_table))
    conn.execute(text(create_access_log_table))

    # Iterar sobre filas del DataFrame para insertar/actualizar usuarios
    for _, row in df.iterrows():
        
        # Limpiar y preparar datos
        username = str(row["user"]).strip()
        raw_password = str(row["password"]).strip()
        role = str(row["role"]).strip() if pd.notna(row["role"]) else "viewer"
        team = str(row["team"]).strip() if pd.notna(row["team"]) else ""

        # Generar hash de la contraseña
        password_hash = bcrypt.hashpw(
            raw_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # Insertar o actualizar usuario en la base de datos
        conn.execute(
            text(insert_user_sql),
            {
                "username": username,
                "password_hash": password_hash,
                "role": role,
                "team": team,
            }
        )

print("Migración completada correctamente.")