# ============================================
# Common -> fonts
# ============================================

# Importar librerías
import streamlit as st

# Importar rutas de configuración
from common.config import (
    ASSETSFONTS
)

# Cargar fuentes personalizadas en Streamlit
def load_fonts():
    
    # Inyectar CSS para registrar y usar las fuentes
    st.markdown(f"""
    <style>

    /* Registrar fuente normal */
    @font-face {{
        font-family: "DejaVuSans";
        src: url("{ASSETSFONTS / 'DejaVuSans.ttf'}");
        font-weight: normal;
    }}

    /* Registrar fuente en negrita */
    @font-face {{
        font-family: "DejaVuSans";
        src: url("{ASSETSFONTS / 'DejaVuSans-Bold.ttf'}");
        font-weight: bold;
    }}

    /* Aplicar fuente a toda la app */
    html, body, [class*="css"] {{
        font-family: "DejaVuSans", sans-serif;
    }}

    </style>
    """, unsafe_allow_html=True)  
