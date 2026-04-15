# ============================================
# Notebooks -> create_audios
# ============================================

# Importar librerías 
import os
import edge_tts

# Definir guion de audios para cada sección de la aplicación
guion = {
    "1_Login": "Al acceder a la aplicación, podemos iniciar sesión o entrar como visitante escribiendo admin en usuario y contraseña.",

    "2_Home": "Una vez dentro, encontramos la página de inicio, con un mensaje de bienvenida disponible en varios idiomas y una introducción general a DataLab y a sus funcionalidades principales.",

    "3_Overview": "A partir de aquí, la aplicación permite visualizar y filtrar de forma centralizada toda la base de datos de jugadores. El usuario puede seleccionar distintos modos de score, aplicar filtros personalizados según sus necesidades y consultar la información en una tabla interactiva muy fácil de usar. Además, esta sección se complementa con gráficos y mapas que ofrecen una visión más global del mercado, facilitando una lectura rápida de los datos y ayudando a detectar perfiles interesantes de forma mucho más eficiente.",

    "4_Ranking": "Además, podemos generar rankings personalizados según la estadística que más nos interese analizar en cada momento. Esto permite ordenar a los jugadores de forma dinámica, comparar rápidamente su rendimiento y detectar de manera mucho más ágil qué perfiles destacan en cada indicador. Una vez obtenido el ranking, los resultados también pueden descargarse para seguir trabajando con ellos fuera de la plataforma.",

    "5_Radar": "Otra de las funciones más útiles de la aplicación es la comparación visual entre jugadores mediante un radar interactivo. En esta sección podemos seleccionar dos futbolistas, definir las métricas que queremos analizar y comparar su rendimiento de una forma mucho más clara, visual e intuitiva. Esto permite detectar rápidamente fortalezas, diferencias y similitudes entre perfiles, algo especialmente útil en procesos de scouting y toma de decisiones. Además, la herramienta permite cambiar el método de análisis según el contexto, adaptando la comparación a distintas necesidades, y finalmente exportar el resultado en PDF para compartirlo, presentarlo o incorporarlo a informes profesionales.",

    "6_Lineup": "La aplicación también ofrece la posibilidad de construir un once ideal de forma totalmente visual. Podemos elegir el sistema táctico, seleccionar la jornada y asignar jugadores a cada posición para representar la alineación directamente sobre el campo. Esta funcionalidad resulta muy útil para transformar el análisis de datos en una propuesta táctica concreta, ayudando a visualizar cómo encajan los perfiles seleccionados dentro de una estructura real de juego. Una vez creada, la alineación puede guardarse, imprimirse, exportarse en PDF e incluso consultarse más adelante junto a otras propuestas ya registradas dentro de la plataforma.",

    "7_List": "Por otro lado, podemos crear listas de seguimiento de jugadores, añadir observaciones de scouting y clasificar perfiles según su prioridad. De esta forma, la aplicación no solo permite analizar, sino también organizar y dar continuidad al trabajo de seguimiento, manteniendo toda la información reunida en un mismo entorno y con posibilidad de exportarla cuando sea necesario.",

    "8_NewLeague": "Si el usuario detecta que falta una competición en la base de datos, puede solicitar su incorporación indicando la liga, el nivel de prioridad y una breve justificación.",

    "9_RequestsAdmin": "Estas solicitudes llegan al panel de administración, donde pueden revisarse, filtrarse y gestionarse de forma rápida, permitiendo aprobar o eliminar cada petición.",

    "10_Admin": "Por último, la aplicación incluye una sección de administración de usuarios desde la que es posible crear cuentas, asignar roles, vincular equipos y gestionar de forma centralizada el acceso a la plataforma. Esto permite mantener un mayor control interno, adaptar permisos según el perfil de cada usuario y asegurar un entorno de trabajo más ordenado, seguro y profesional."
}

# Carpeta donde se guardarán los audios
output_folder = "audios"
os.makedirs(output_folder, exist_ok=True)

# Voz para la síntesis de los audios
VOICE = "es-ES-AlvaroNeural"

# Función asíncrona para generar los audios a partir del guion
async def generar_audios():
    for nombre, texto in guion.items():
        ruta_salida = os.path.join(output_folder, f"{nombre}.mp3")
        communicate = edge_tts.Communicate(texto, VOICE)
        await communicate.save(ruta_salida)
        print(f"Guardado: {ruta_salida}")