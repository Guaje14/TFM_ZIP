# ============================================
# Models -> user
# ============================================

# Importar librerías 
from dataclasses import dataclass

@dataclass
class User:
    username: str          # Nombre del Usuario
    password: str          # Contraseña
    role: str = "viewer"   # Por defecto usuario normal
    team: str = ""         # Nombre del Equipo

    def is_admin(self) -> bool:
        return self.role == "admin"