# ============================================
# App - DataLab
# ============================================

# Importar librerías 
import streamlit as st
from datetime import datetime
from PIL import Image

# Importar el modelo de usuario
from models.user import User

# Importar rutas de configuración
from common.config import (
    ASSETSIMG, ASSETSLOGOSHIELDS
)

# Importar funciones de usuarios
from controllers.user_controller import authenticate_user, log_access

# Importar funciones de common
from common.fonts import load_fonts
from common.device import detect_mobile
from common.pdf_utils import get_team_logo_path

# Importar las funciones para generar las páginas
from app_pages.page_home import page_home
from app_pages.page_overview import page_overview
from app_pages.page_rk import page_rk
from app_pages.page_radar import page_radar
from app_pages.page_lineup import page_lineup
from app_pages.page_list import page_list
from app_pages.page_admin import page_admin
from app_pages.page_newleague import page_newleague
from app_pages.page_message import page_league_requests_admin

# Cargar fuente personalizada
load_fonts() 

# Antes de cualquier UI
detect_mobile()

# Global App Configuration
st.set_page_config(
    page_title="Data Lab",  
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función que genera la pantalla de login de la aplicación Streamlit
def login_screen():

    # Imagen del Logo de la App
    logo_streamlit = Image.open(ASSETSIMG / "Logo_DataLab.png")

    is_mobile = st.session_state.get("is_mobile", False)

    if not is_mobile:
        
        # Desktop: columnas anidadas
        row_logo_col1, row_logo_col2, row_logo_col3 = st.columns([1, 3, 1])
        with row_logo_col2:
            inner_col1, inner_col2, inner_col3 = st.columns([2.5, 4, 1])
            with inner_col2:
                st.image(logo_streamlit, width=250)
    else:
        st.image(logo_streamlit, width=150)  
    
    # Crear columnas para centrar el contenido
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col2:
    
        # Campo de entrada para el usuario
        user = st.text_input(
            "User",
            placeholder="Insert User",
            key="User"
        )

        # Campo de entrada para la contraseña (oculta)
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Insert Password",
            key="Password"
        )

        # Mensaje informativo para acceso como visitante
        st.markdown(
            "<p style='text-align:center; font-size:15px; color:#e2e8f0;'>"
            "* To access as a Visitor enter 'admin' in User and Password"
            "</p>",
            unsafe_allow_html=True
        )

        # Botón de acceso
        if st.button("Access"):

            # Acceso como visitante
            if user == "admin" and password == "admin":
                st.session_state["logged"] = True
                st.session_state["user"] = User(username="Guest", password="", role="viewer")
                st.session_state["is_admin"] = False  
                st.session_state["login_time"] = datetime.now()
                log_access("Guest")  
                
            # Acceso como usuario registrado
            else:
                
                # Intentar autenticar al usuario con las credenciales proporcionadas
                match = authenticate_user(user, password)

                # Si se encuentra una coincidencia, iniciar sesión y registrar el acceso
                if match:
                    st.session_state["logged"] = True
                    st.session_state["user"] = match
                    st.session_state["is_admin"] = match.is_admin()
                    st.session_state["login_time"] = datetime.now()
                    log_access(match.username)
                else:
                    st.error("User or Password incorrects")

# Función que genera un menú lateral de navegación de la aplicación
def sidebar_menu():
    
    # Obtener objeto usuario
    user_obj = st.session_state.get("user")
    
    # Obtener logo en función del equipo del usuario 
    logo_path = get_team_logo_path(user_obj, ASSETSLOGOSHIELDS)

    # Mostrar logo personalizado
    logo_streamlit = Image.open(logo_path)
    st.sidebar.image(logo_streamlit, width=200)
    
    # Diccionario: valor interno -> etiqueta visible
    tags = {
        "home": "🏠 Home",
        "overview": "📄 Overview",
        "rk": "🏆 Ranking",
        "radar": "📊 Plot",
        "lineup": "👤 Team Lineup",
        "list": "📝 List",
        "newleague": "📥 Message"
    }
    
    if st.session_state.get("is_admin", False):
        tags["message"] = "📮 User Request"
        tags["admin"] = "⚙️ Admin"
    
    st.session_state.setdefault("pagina", "visionado")
    
    # Mostrar cada tag como botón estilo pill
    for key, label in tags.items():
        
        # Resaltar tag seleccionado
        color = "#2563eb" if st.session_state["pagina"] == key else "#e2e8f0"
        text_color = "white" if st.session_state["pagina"] == key else "black"
        
        # Botón estilo tag
        if st.sidebar.button(label, key=f"tag_{key}"):
            st.session_state["pagina"] = key
        
        # Aplicar CSS para que parezca un tag/pill
        st.sidebar.markdown(
            f"""
            <style>
            div[data-testid="stSidebar"] button[kind="primary"][key="tag_{key}"] {{
                background-color: {color} !important;
                color: {text_color} !important;
                border-radius: 20px;
                margin: 5px auto !important;
                display: block !important;
                width: 100%;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Función principal de la app Streamlit
def main():

    # CSS personalizado
    st.markdown("""
    <style>
    input[type="text"], input[type="number"], input[type="password"] {
        background-color: #e2e8f0 !important;
        color: black !important;
    }
    input[type="text"]::placeholder,
    input[type="number"]::placeholder,
    input[type="password"]::placeholder{
        color: grey !important;
        opacity: 1 !important;
    }
    div.stSelectbox > div[data-baseweb="select"] > div,
    div.stMultiSelect > div[data-baseweb="select"] > div {
        background-color: #e2e8f0 !important;
        color: black !important;
    }
    div.stSelectbox > div[data-baseweb="select"] > div > div,
    div.stMultiSelect > div[data-baseweb="select"] > div > div {
        color: black !important;
    }
    div.stSlider > div > div[data-baseweb="slider"] > div[data-baseweb="slider-track"] {
        background-color: #ccc !important;
    }
    div.stSlider > div > div[data-baseweb="slider"] > div[data-baseweb="slider-thumb"] {
        background-color: white !important;
        border: 1px solid #888 !important;
    }
    /* Botón emoji reloj */
    div.stButton > button[kind="primary"][key="renew_timer"] {
        background: none;
        border: none;
        padding: 0;
        margin: 0;
        font-size: 28px;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    # Inicialización de session_state 
    st.session_state.setdefault("logged", False)
    st.session_state.setdefault("pagina", "home")
    st.session_state.setdefault("login_time", datetime.now())

    # Pantalla de login 
    if not st.session_state["logged"]:
        login_screen()
        return  
    
    # Configuración de sesión 
    SESSION_DURATION = 30 * 60  # 30 minutos
    RENEW_WINDOW = 5 * 60       # 5 minutos antes para renovar

    # Sidebar: usuario y menú 
    sidebar_menu()
    st.sidebar.markdown("---")
    st.sidebar.caption("Usuario actual:")
    
    # Obtener el objeto User
    user_obj = st.session_state.get("user")  

    # Extraer solo el nombre, si no hay usuario mostrar "Desconocido"
    user_name = user_obj.username if user_obj else "Desconocido"
    st.sidebar.markdown(
        f"<p style='font-size:30px; font-weight:bold; text-align:center;'>{user_name}</p>",
        unsafe_allow_html=True
    )
    
    # Botones de sesión en una misma fila
    session_col1, session_col2 = st.sidebar.columns(2)

    # Botón renovar sesión
    with session_col1:
        renew_clicked = st.button("🔄  ⏱", key="renew_timer")

    # Botón logout
    with session_col2:
        logout_clicked = st.button("🚪 👋", key="logout_button")

    # Contenedor para mostrar la cuenta atrás debajo
    timer_placeholder = st.sidebar.empty()

    # Cálculo del tiempo restante de sesión
    elapsed = (datetime.now() - st.session_state["login_time"]).total_seconds()
    remaining = SESSION_DURATION - elapsed

    # Acción del botón renovar sesión
    if renew_clicked:
        if remaining <= RENEW_WINDOW:
            st.session_state["login_time"] = datetime.now()
            st.success("Session renewed for 30 more minutes")
            remaining = SESSION_DURATION
        else:
            st.warning(f"You can renew only when ≤ {RENEW_WINDOW//60} min remaining")

    # Acción del botón logout
    if logout_clicked:
        st.session_state["logged"] = False
        st.session_state["user"] = None
        st.session_state["is_admin"] = False
        st.session_state["pagina"] = "home"
        st.rerun()

    # Logout automático si la sesión expira
    if remaining <= 0:
        st.warning("Session expired. Please log in again.")
        st.session_state["logged"] = False
        st.rerun()

    # Mostrar cuenta atrás debajo de los botones
    minutes = int(remaining // 60)
    seconds = int(remaining % 60)
    timer_placeholder.markdown(
        f"⏳ **Session expires in {minutes:02d}:{seconds:02d}**"
    )

    # Temporizador visual en tiempo real
    minutes = int(remaining // 60)
    seconds = int(remaining % 60)
    timer_placeholder.markdown(f"**Session expires in {minutes:02d}:{seconds:02d}**")

    # Páginas de la app
    if st.session_state["pagina"] == "home":
        page_home()
    elif st.session_state["pagina"] == "overview":
        page_overview()
    elif st.session_state["pagina"] == "rk":
        page_rk()
    elif st.session_state["pagina"] == "radar":
        page_radar()
    elif st.session_state["pagina"] == "lineup":
        page_lineup()
    elif st.session_state["pagina"] == "list":
        page_list()
    elif st.session_state["pagina"] == "newleague":
        page_newleague()
    elif st.session_state["pagina"] == "message":
        page_league_requests_admin()
    elif st.session_state["pagina"] == "admin":
        page_admin()

# Ejecutar la app       
if __name__ == "__main__":
    main()  

