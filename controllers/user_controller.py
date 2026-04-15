# ============================================
# Controllers -> user_controller
# ============================================

# Importar librerías 
import streamlit as st
import bcrypt
from sqlalchemy import text
from models.user import User

# Función para obtener conexión a la base de datos de usuarios
def get_conn():
    return st.connection("users_db", type="sql")

# Función para gestionar contraseñas
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Función para verificar contraseña ingresada contra el hash almacenado
def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

# Función para cargar usuarios desde la base de datos
def load_users():
    
    # Obtener conexión a la base de datos de usuarios
    conn = get_conn()

    # Ejecutar consulta para obtener todos los usuarios con su username, hash de contraseña, rol y equipo
    with conn.session as session:
        rows = session.execute(
            text("""
                SELECT username, password_hash, role, COALESCE(team, '') AS team
                FROM users
                ORDER BY username
            """)
        ).fetchall()

    # Crear lista de usuarios a partir de los resultados obtenidos
    users = []
    
    # Iterar sobre las filas obtenidas y crear instancias de User para cada una
    for row in rows:
        username, password_hash, role, team = row
        users.append(
            User(
                username=username,
                password=password_hash,
                role=role,
                team=team
            )
        )

    return users

# Función para guardar usuarios en la base de datos
def create_user(username, password, role="viewer", team=""):
    
    # Obtener conexión a la base de datos de usuarios
    conn = get_conn()
    
    # Crear hash de la contraseña antes de almacenarla
    password_hash = hash_password(password)

    # Verificar si el usuario ya existe antes de crear uno nuevo
    with conn.session as session:
        
        # Verificar existencia previa del usuario
        exists = session.execute(
            text("SELECT 1 FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()

        if exists:
            return False, "The user already exists"

        # Insertar nuevo usuario en la base de datos
        session.execute(
            text("""
                INSERT INTO users (username, password_hash, role, team)
                VALUES (:username, :password_hash, :role, :team)
            """),
            {
                "username": username,
                "password_hash": password_hash,
                "role": role,
                "team": team
            }
        )
        session.commit()

    return True, f"User '{username}' created successfully"

# Función para actualizar rol o equipo de un usuario existente
def update_user(username, role=None, team=None):
    
    # Obtener conexión a la base de datos de usuarios
    conn = get_conn()

    # Construir dinámicamente la consulta de actualización según los campos proporcionados
    fields = []
    params = {"username": username}

    if role is not None:
        fields.append("role = :role")
        params["role"] = role

    if team is not None:
        fields.append("team = :team")
        params["team"] = team

    if not fields:
        return

    sql = f"""
        UPDATE users
        SET {", ".join(fields)}
        WHERE username = :username
    """

    with conn.session as session:
        session.execute(text(sql), params)
        session.commit()

# Función para eliminar un usuario por su username
def delete_user(username):
    
    # Obtener conexión a la base de datos de usuarios
    conn = get_conn()

    # Ejecutar consulta para eliminar usuario por username
    with conn.session as session:
        session.execute(
            text("DELETE FROM users WHERE username = :username"),
            {"username": username}
        )
        session.commit()

# Función para autenticar usuario durante login
def authenticate_user(username, password):
    
    # Obtener conexión a la base de datos de usuarios
    conn = get_conn()

    # Ejecutar consulta para obtener usuario por username
    with conn.session as session:
        row = session.execute(
            text("""
                SELECT username, password_hash, role, COALESCE(team, '') AS team
                FROM users
                WHERE username = :username
            """),
            {"username": username}
        ).fetchone()

    if not row:
        return None

    # Desempaquetar valores de la fila obtenida
    username_db, password_hash, role, team = row

    # Verificar contraseña ingresada contra el hash almacenado
    if verify_password(password, password_hash):
        return User(
            username=username_db,
            password=password_hash,
            role=role,
            team=team
        )

    return None

# Función para registrar accesos de usuarios en el log
def log_access(username):
    
    # Obtener conexión a la base de datos de usuarios
    conn = get_conn()

    # Ejecutar consulta para obtener rol y equipo del usuario, luego insertar registro en access_log
    with conn.session as session:
        row = session.execute(
            text("""
                SELECT role, COALESCE(team, '') AS team
                FROM users
                WHERE username = :username
            """),
            {"username": username}
        ).fetchone()

        if not row:
            role = "viewer"
            team = ""
        else:
            role, team = row

        # Insertar registro de acceso con username, rol, equipo y timestamp actual
        session.execute(
            text("""
                INSERT INTO access_log (username, role, team)
                VALUES (:username, :role, :team)
            """),
            {
                "username": username,
                "role": role,
                "team": team
            }
        )
        session.commit()