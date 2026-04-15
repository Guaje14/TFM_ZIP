# ============================================
# Common -> device
# ============================================

# Importar librerías 
import streamlit as st

# Detectar si el usuario usa un dispositivo móvil
def detect_mobile():
    
    # Ejecutar solo si aún no existe el valor en la sesión
    if "is_mobile" not in st.session_state:
        
        # Valor por defecto (no móvil)
        st.session_state["is_mobile"] = False
        
        # Inyectar JavaScript en la página
        st.markdown(
            """
            <script>
            // Detectar si el ancho de pantalla es menor a 768px (móvil)
            const isMobile = window.innerWidth < 768;

            // Enviar el valor a Streamlit
            window.parent.postMessage({ type: "streamlit:setComponentValue", value: isMobile }, "*");
            </script>
            """,
            unsafe_allow_html=True  
        )