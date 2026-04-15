# ============================================
# Page Admin
# ============================================

# Importar librerías
import streamlit as st
from PIL import Image

# Importar rutas de configuración
from common.config import ASSETSIMG, ASSETSSHIELDS

# Importar funciones de usuarios
from controllers.user_controller import (
    load_users,
    create_user,
    update_user,
    delete_user
)

# Función que da como resultado la página Admin
def page_admin():

    # Obtener usuario desde la sesión
    user = st.session_state.get("user")

    # Validar acceso solo para administradores
    if not user or not user.is_admin():
        st.error("Access denied. Admin only.")
        st.stop()

    # Crear columnas para centrar la imagen
    admin_imgcol1, admin_imgcol2, admin_imgcol3 = st.columns([3.7, 2.5, 3])

    with admin_imgcol2:

        # Cargar imagen desde la carpeta de assets
        admin_img_header = Image.open(ASSETSIMG / "Freepick Admin.png")

        # Mostrar imagen en la aplicación
        st.image(admin_img_header, width=120)

    # Definir layout de la página en columnas
    admin_col1, admin_col2, admin_col3 = st.columns([1.5, 2.8, 2.2])

    # Cargar usuarios desde la base de datos
    admin_users = load_users()

    # Obtener nombres de equipos desde archivos PNG
    teams_list = [f.stem for f in ASSETSSHIELDS.glob("*.png")]
    teams_list = sorted(teams_list)

    # Crear formulario de gestión de usuarios
    with admin_col2:
        st.header("Create / Manage Users")

        # Capturar datos para nuevo usuario
        new_user = st.text_input(
            "New User",
            placeholder="Insert new User",
            key="new_user"
        )

        new_pass = st.text_input(
            "New Password",
            placeholder="Insert new Password",
            type="password",
            key="new_pass"
        )

        new_role = st.selectbox(
            "Role",
            ["viewer", "admin"],
            key="new_role"
        )

        new_team = st.selectbox(
            "Team",
            teams_list,
            key="new_team"
        )

        # Crear botón para registrar nuevo usuario
        if st.button("Create New User"):

            # Validar campos obligatorios
            if not new_user or not new_pass:
                st.error("User and Password required")

            else:
                # Crear usuario en base de datos
                ok, msg = create_user(
                    username=new_user.strip(),
                    password=new_pass,
                    role=new_role,
                    team=new_team
                )

                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.warning(msg)

        # Insertar separador visual
        st.markdown("---")
        st.subheader("Users Created:")

        # Mostrar usuario logueado
        st.write("Logged user:", user.username)

        # Inicializar página actual de administración en session_state
        st.session_state.setdefault("admin_page", 0)

        # Definir tamaño de página
        PAGE_SIZE = 5

        # Calcular rango de filas a mostrar en la página actual
        start = st.session_state.admin_page * PAGE_SIZE
        end = start + PAGE_SIZE

        # Obtener subconjunto de usuarios correspondiente a la página actual
        df_page = admin_users[start:end]

        # Calcular número total de páginas
        total_pages = max(1, (len(admin_users) - 1) // PAGE_SIZE + 1)

        # Crear layout de navegación de páginas
        admin_nav1, admin_nav2, admin_nav3 = st.columns([1, 3, 1])

        # Botón para ir a la página anterior
        with admin_nav1:
            if st.button("⬅️", disabled=st.session_state.admin_page == 0):
                st.session_state.admin_page -= 1
                st.rerun()

        # Mostrar información de paginación centrada
        with admin_nav2:
            st.markdown(
                f"<div style='text-align:center'>Page {st.session_state.admin_page + 1} / {total_pages}</div>",
                unsafe_allow_html=True
            )

        # Botón para ir a la página siguiente
        with admin_nav3:
            if st.button("➡️", disabled=end >= len(admin_users)):
                st.session_state.admin_page += 1
                st.rerun()

        # Iterar sobre usuarios de la página actual
        for i, u in enumerate(df_page, start=start):

            # Crear columnas para mostrar información del usuario
            admin_c1, admin_c2, admin_c3, admin_c4 = st.columns([2.2, 2.2, 3, 1.5])

            # Mostrar nombre de usuario (solo lectura)
            with admin_c1:
                st.selectbox(
                    "User",
                    options=[u.username],
                    index=0,
                    disabled=True,
                    key=f"user_{i}"
                )

            # Gestionar cambio de rol
            with admin_c2:
                new_role_user = st.selectbox(
                    "Role",
                    ["viewer", "admin"],
                    index=["viewer", "admin"].index(u.role),
                    key=f"role_{i}"
                )

                # Actualizar rol si cambia
                if new_role_user != u.role:
                    update_user(username=u.username, role=new_role_user)
                    st.rerun()

            # Gestionar cambio de equipo
            with admin_c3:
                teams_with_none = ["No Team"] + teams_list
                current_team = u.team if u.team else "No Team"

                new_team_user = st.selectbox(
                    "Team",
                    teams_with_none,
                    index=teams_with_none.index(current_team) if current_team in teams_with_none else 0,
                    key=f"team_{i}"
                )

                # Actualizar equipo si cambia
                if new_team_user != current_team:
                    update_user(
                        username=u.username,
                        team=None if new_team_user == "No Team" else new_team_user
                    )
                    st.rerun()

            # Gestionar eliminación de usuario
            with admin_c4:

                # Comprobar si el usuario mostrado es el mismo que el usuario logueado
                if u.username == st.session_state["user"].username:

                    # Mostrar botón deshabilitado para evitar auto-eliminación
                    st.button("🛡️", disabled=True, key=f"lock_{i}")

                else:

                    # Mostrar botón de eliminación para otros usuarios
                    if st.button("🗑️", key=f"delete_user_{i}"):

                        # Eliminar usuario de la base de datos
                        delete_user(u.username)

                        # Mostrar mensaje de confirmación de eliminación
                        st.warning(f"User {u.username} deleted")

                        # Reiniciar paginación de administración
                        st.session_state.admin_page = 0

                        # Recargar la aplicación para reflejar cambios
                        st.rerun()

            # Separar visualmente usuarios
            st.divider()