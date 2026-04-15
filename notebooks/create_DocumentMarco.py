# ============================================
# Notebooks -> create_DocumentMarco
# ============================================

# Importar librerías 
import os                          
from fpdf import FPDF, XPos, YPos  
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle


# Función para generar la imagen del Gantt
def generate_gantt_table_style(output_path="gantt_table_style.png"):

    # Definir semanas
    weeks = ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5", "Semana 6"]

    # Definir fases y semanas activas (índices empezando en 0)
    phases = [
        ("Data Collection", [0, 1]),
        ("Data Cleaning", [1, 2]),
        ("Model (PCA + Score)", [2, 3]),
        ("App Development", [3, 4]),
        ("Deployment", [4, 5]),
    ]

    n_rows = len(phases) + 1   # +1 por cabecera
    n_cols = len(weeks) + 1    # +1 por columna de nombre de fase

    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    ax.axis("off")

    # Tamaño de columnas
    first_col_width = 2.8
    other_col_width = 1.2

    # Posiciones X acumuladas
    x_positions = [0]
    x_positions.append(first_col_width)
    for _ in weeks:
        x_positions.append(x_positions[-1] + other_col_width)

    # Ajustar límites reales del gráfico
    ax.set_xlim(0, x_positions[-1])
    ax.set_ylim(0, n_rows)
    ax.axis("off")

    # Dibujar cabecera
    header_y = n_rows - 1
    ax.add_patch(Rectangle((0, header_y), first_col_width, 1, fill=False, edgecolor="black", linewidth=1))
    for i, week in enumerate(weeks):
        ax.add_patch(Rectangle((x_positions[i + 1], header_y), other_col_width, 1, fill=False, edgecolor="black", linewidth=1))
        ax.text(
            x_positions[i + 1] + other_col_width / 2,
            header_y + 0.5,
            week,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold"
        )

    # Dibujar filas
    for row_idx, (phase, active_weeks) in enumerate(phases):
        y = n_rows - 2 - row_idx

        # Celda del nombre de la fase
        ax.add_patch(Rectangle((0, y), first_col_width, 1, fill=False, edgecolor="black", linewidth=1))
        ax.text(
            0.1,
            y + 0.5,
            phase,
            ha="left",
            va="center",
            fontsize=10
        )

        # Celdas de semanas
        for col_idx in range(len(weeks)):
            x = x_positions[col_idx + 1]

            # Dibujar celda base
            ax.add_patch(Rectangle((x, y), other_col_width, 1, fill=False, edgecolor="black", linewidth=1))

            # Rellenar si la fase está activa en esa semana
            if col_idx in active_weeks:
                ax.add_patch(
                    Rectangle(
                        (x + 0.08, y + 0.18),
                        other_col_width - 0.16,
                        0.64,
                        facecolor="black"
                    )
                )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Gantt guardado en: {output_path}")

# Función para crear el PDF con todos los elementos
def create_pdf(
    logo1, logo2, logo3, logo4, centeredtext, 
    title, subtitle1, subtitle2, subtitle3, thanks = False, thanks_text = None, 
    titlepage1 = None, subtitlepage1 = None, titlepage2 = None, subtitlepage2 = None,
    titlepage3 = None, subtitlepage3 = None, titlepage4 = None, subtitlepage4 = None,
    titlepage5 = None, subtitlepage5 = None, titlepage6 = None, subtitlepage6 = None,
    titlepage7 = None, subtitlepage7 = None, titlepage8 = None, subtitlepage8 = None,
    titlepage9 = None, subtitlepage9 = None, titlepage10 = None, subtitlepage10 = None,
    textpage1 = None, textpage2 = None, textpage3 = None, textpage4 = None, textpage5 = None, 
    textpage6 = None, textpage7 = None, textpage8 = None, textpage9 = None, textpage10 = None, 
    timeline_values = None, imagepage1 = None, imagepage2 = None, imagepage3 = None, imagepage4 = None, 
    imagepage5 = None, imagepage6 = None, imagepage7 = None, imagepage8 = None, imagepage9 = None, 
    imagepage10 = None, imagepage11 = None, colorbar1 = None, colorbar2 = None, output = None, outpath = None
):

    # Crear una clase personalizada que herede de FPDF
    class PDF(FPDF):
        
        # Función auxiliar para definir el encabezado que aparecerá en todas las páginas
        def header(self):
            logo_izquierdo = logo1
            logo_centro_izquierdo = logo2
            logo_centro_derecho = logo3
            logo_derecho = logo4
            margen_superior = 10

            # Agregar logos en las posiciones especificadas
            for logo, x, y, h in [
                (logo_izquierdo, 10, margen_superior, 15),
                (logo_centro_izquierdo, 40, margen_superior + 1.5, 10),
                (logo_centro_derecho, self.w - 33 - 28, margen_superior + 2.8, 6),  
                (logo_derecho, self.w - 26, margen_superior, 9.5)
            ]:
                try:
                    self.image(logo, x=x, y=y, h=h)
                except Exception as e:
                    print(f"No se pudo cargar logo: {e}")

            # Agregar texto centrado en el encabezado
            self.set_font("times", "B", 12)
            self.set_y(12)
            self.cell(0, 10, centeredtext, border=0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(15)

    # Crear instancia del PDF
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_left_margin(25)
    pdf.set_right_margin(25)
    pdf.set_top_margin(25)

    # Obtener el ancho máximo utilizable
    max_width = pdf.w - pdf.l_margin - pdf.r_margin

    
    # --- 
    # Portada 
    # ---
    
    # Agregar página de portada
    pdf.add_page()
    
    pdf.set_font("times", "B", 40)
    titulo_width = pdf.get_string_width(title)
    pdf.set_y((pdf.h - 70)/2)
    
    # Título principal
    if titulo_width > max_width:
        pdf.multi_cell(max_width, 20, title, 0, "C")
    else:
        pdf.set_x((pdf.w - titulo_width)/2)
        pdf.cell(titulo_width, 20, title, border=0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(4)


    # --- 
    # Subtítulos 
    # ---

    # Subtítulo 1
    pdf.set_font("times", "", 23)
    subtitle_max_width = max_width * 0.75
    subtitulo1_width = pdf.get_string_width(subtitle1)
    
    if subtitulo1_width > subtitle_max_width:
        x_start = pdf.l_margin + (max_width - subtitle_max_width)/2
        pdf.set_x(x_start)
        pdf.multi_cell(subtitle_max_width, 13, subtitle1, 0, "C")
    else:
        pdf.set_x((pdf.w - subtitulo1_width)/2)
        pdf.cell(subtitulo1_width, 13, subtitle1, border=0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(2)

    # Subtítulo 2
    pdf.set_font("times", "", 18)
    subtitulo2_width = pdf.get_string_width(subtitle2)
    if subtitulo2_width > max_width:
        pdf.multi_cell(max_width, 13, subtitle2, 0, "C")
    else:
        pdf.set_x((pdf.w - subtitulo2_width)/2)
        pdf.cell(subtitulo2_width, 13, subtitle2, border=0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(70)

    pdf.set_font("times", "", 12)
    subtitulo3_width = pdf.get_string_width(subtitle3)
    if subtitulo3_width > max_width:
        pdf.multi_cell(max_width, 13, subtitle3, 0, "C")
    else:
        pdf.set_x((pdf.w - subtitulo3_width)/2)
        pdf.cell(subtitulo3_width, 13, subtitle3, border=0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


    # --- 
    # Timeline 
    # ---
    
    if timeline_values:
        pdf.add_page()
        centro_x = pdf.w / 2
        y_start = 65
        y_end = pdf.h - 65
        max_points = min(len(timeline_values), 15)
        spacing = (y_end - y_start) / (max_points - 1) if max_points > 1 else 0

        pdf.set_line_width(1)
        pdf.set_draw_color(colorbar1)
        
        # Dibujar línea central discontinua
        for i in range(max_points-1):
            y_line_start = y_start + spacing*i
            y_line_end = y_start + spacing*(i+1)
            num_segments = 10
            segment_length = (y_line_end - y_line_start) / (2*num_segments)
            for s in range(num_segments):
                y_seg_start = y_line_start + 2*s*segment_length
                y_seg_end = y_seg_start + segment_length
                pdf.line(centro_x, y_seg_start, centro_x, y_seg_end)

        # Dibujar puntos y bloques de texto 
        radius = 2
        
        # Calcular ancho máximo para bloques de texto
        max_block_width = pdf.w * 0.28
        
        # Iterar sobre los valores de la línea de tiempo
        for idx, (step, explanation) in enumerate(list(timeline_values.items())[:max_points]):
            y = y_start + spacing * idx
            pdf.set_fill_color(colorbar2)
            pdf.ellipse(centro_x - radius, y - radius, radius * 2, radius * 2, style="F")

            block_x_center = (pdf.l_margin + centro_x) / 2 if idx % 2 == 0 else (centro_x + (pdf.w - pdf.r_margin)) / 2

            # ----- Título del bloque con wrap -----
            pdf.set_font("times", "B", 12)
            step_wrap_width = max_block_width * 0.8
            step_x = block_x_center - step_wrap_width / 2
            pdf.set_xy(step_x, y - 6)
            pdf.multi_cell(step_wrap_width, 5, step, border=0, align="C")

            # ----- Explicación debajo del título -----
            pdf.set_font("times", "", 9)
            wrap_width = min(max_block_width * 0.8, pdf.w - pdf.l_margin - pdf.r_margin)
            wrap_x = block_x_center - wrap_width / 2
            pdf.set_xy(wrap_x, pdf.get_y() + 1)
            pdf.multi_cell(wrap_width, 6, explanation, align="C")

    # --- 
    # Página de Gracias
    # ---
    
    if thanks:
        pdf.add_page()
        pdf.set_font("times", "B", 40)
        pdf.multi_cell(pdf.w - 2 * pdf.l_margin, 15, "Agradecimientos", 0, "C")

        if thanks_text:
            pdf.set_font("times", "", 12)
            pdf.ln(7)  # espacio debajo del título

            # Separar párrafos por línea en blanco
            paragraphs = [p.strip() for p in thanks_text.split("\n\n") if p.strip()]

            for paragraph in paragraphs:
                pdf.multi_cell(pdf.w - 2 * pdf.l_margin, 8, paragraph, 0, "J")
                pdf.ln(4)  # espacio entre párrafos

    # --- 
    # Páginas adicionales 
    # ---

    # Lista de textos, títulos e imágenes para las páginas adicionales
    textpages = [textpage1, textpage2, textpage3, textpage4, textpage5, textpage6, textpage7, textpage8, textpage9, textpage10]
    titulos = [(titlepage1, subtitlepage1), (titlepage2, subtitlepage2), (titlepage3, subtitlepage3), 
               (titlepage4, subtitlepage4), (titlepage5, subtitlepage5), (titlepage6, subtitlepage6), 
               (titlepage7, subtitlepage7), (titlepage8, subtitlepage8), (titlepage9, subtitlepage9), 
               (titlepage10, subtitlepage10)]
    imagepages = [
        imagepage1, imagepage2, imagepage3, imagepage4, imagepage5, imagepage6, imagepage7, imagepage8,
        imagepage9, imagepage10, imagepage11
    ]

    # Iterar sobre las páginas de texto y títulos
    for i, texto in enumerate(textpages):
        imagen = imagepages[i]

        # Crear página si hay texto o imagen
        if texto or imagen:
            pdf.add_page()
            y_centro = 50
            area_centro_x = pdf.w / 2
            ancho_util = pdf.w - 2 * pdf.l_margin

            # Dibujar barras decorativas si se especifican colores
            if i < 9 and colorbar1 and colorbar2:
                barra_lila_x = area_centro_x - 86.5
                pdf.set_line_width(5)
                pdf.set_draw_color(*colorbar1)
                pdf.line(barra_lila_x, y_centro, barra_lila_x, y_centro + 8)
                pdf.line(barra_lila_x, y_centro, barra_lila_x, y_centro - 8)
                barra_naranja_x = area_centro_x - 84
                pdf.set_line_width(2.5)
                pdf.set_draw_color(*colorbar2)
                pdf.line(barra_naranja_x, y_centro, barra_naranja_x, y_centro + 200)

            # Agregar título y subtítulo si existen
            if i < len(titulos):
                titulo_principal = str(titulos[i][0]).replace("\t", " ").strip() if titulos[i][0] else ""
                subtitulo_sec = str(titulos[i][1]).replace("\t", " ").strip() if titulos[i][1] else ""

                # Dibujar título principal
                if titulo_principal:
                    pdf.set_font("times", "B", 30)
                    pdf.set_y(y_centro - 10)
                    pdf.multi_cell(ancho_util, 10, titulo_principal, 0, "L")

                # Dibujar subtítulo solo si existe
                if subtitulo_sec:
                    pdf.set_font("times", "", 17)
                    pdf.ln(2)
                    pdf.multi_cell(ancho_util, 10, subtitulo_sec, 0, "L")
                    pdf.ln(6)
                else:
                    # Si no hay subtítulo, dejar menos espacio
                    pdf.ln(6)
                        
            pdf.set_font("times", "", 12)

            line_height = 8   # interlineado 1,5 para fuente 12
            indent = 5        # sangría 0,5 cm (5 mm)

            texto_limpio = str(texto).replace("\t", " ").strip().replace("\r\n", "\n")

            # Separar párrafos por doble salto de línea
            paragraphs = [p.strip() for p in texto_limpio.split("\n\n") if p.strip()]

            for j, paragraph in enumerate(paragraphs):
                
                # Aplicar sangría solo al primer renglón de cada párrafo
                pdf.set_x(pdf.l_margin + indent)
                pdf.multi_cell(ancho_util - indent, line_height, paragraph, 0, "J")
    
                # Añadir espacio entre párrafos
                if j < len(paragraphs) - 1:
                    pdf.ln(4)
                    
            # Añadir imagen si existe
            if imagen:
                pdf.ln(6)

                # Posición y tamaño de la imagen
                img_x = pdf.l_margin
                img_y = pdf.get_y()
                img_w = ancho_util

                try:
                    pdf.image(imagen, x=img_x, y=img_y, w=img_w)
                except Exception as e:
                    print(f"No se pudo cargar la imagen de la página {i+1}: {e}")

    # --- 
    # Guardar PDF 
    # ---
    if output:
        full_path = os.path.join(outpath, output) if outpath else output
        if outpath:
            os.makedirs(outpath, exist_ok=True)
        pdf.output(full_path)
        print(f"PDF creado y guardado en: {full_path}")
    else:
        print("No se proporcionó un nombre de archivo para guardar el PDF.")
        
# Agradecimientos 
thanks_text = """ 
Quiero expresar mi más sincero agradecimiento a todas las personas y recursos que han contribuido, de una forma u otra, al desarrollo de este trabajo.

En primer lugar, deseo agradecer a Lucas Bracamonte y al conjunto de profesores del Máster de Python Avanzado Aplicado al Deporte, así como a toda la familia de Sports Data Campus, por la formación recibida, el acompañamiento durante el proceso y la transmisión de conocimientos que han sido fundamentales para poder llevar a cabo este proyecto. Su enfoque práctico, su dedicación y su capacidad para acercar el análisis de datos al ámbito deportivo han sido una referencia constante a lo largo de este camino.

También quiero reconocer la utilidad de los contenidos divulgativos de Soy Dalto, cuyos tutoriales han servido de apoyo en distintos momentos del desarrollo técnico del proyecto. La claridad de sus explicaciones y su enfoque didáctico han facilitado la comprensión de herramientas y conceptos clave.

Del mismo modo, agradezco a FBref su labor al ofrecer datos de fútbol en abierto, haciendo posible que estudiantes, analistas y desarrolladores puedan acceder a una base de información amplia y valiosa para la investigación y la construcción de proyectos como este.

Asimismo, quiero destacar la contribución de LanusStats, que pone a disposición en GitHub código de scraping muy útil para la obtención y tratamiento de datos. Este tipo de iniciativas abiertas resultan esenciales para fomentar el aprendizaje, la experimentación y el desarrollo de nuevas aplicaciones en el ámbito del análisis deportivo.

Por último, agradezco a todas las personas que, de manera directa o indirecta, me han acompañado durante este proceso de aprendizaje y elaboración del trabajo. Este proyecto no habría sido posible sin el conocimiento compartido, los recursos accesibles y la generosidad de quienes contribuyen a que el aprendizaje tecnológico sea cada vez más abierto y colaborativo.
"""

# Recursos asociados al proyecto
textpage1 = """
A continuación, se detallan los enlaces a los principales recursos asociados al proyecto, que permiten su consulta, reproducción y evaluación:

* Link de la aplicación desplegada:
        https://datalab-tfm.streamlit.app/

* Link del repositorio de Github:
        https://github.com/Guaje14/TFM_ZIP

* Link del video explicativo subida a youtube:
        https://youtu.be/mDXXKegEm2Q
  
* Link del zip de código de la aplicación:
        https://drive.google.com/file/d/1oaJ6ldDAN_XdiBO6VoBeJAgygq1OTNsC/view?usp=sharing
  
"""

# Resumen Ejectuivo
textpage2 = """
El presente proyecto tiene como finalidad el diseño, desarrollo y despliegue de una aplicación web orientada al análisis de datos de jugadores de fútbol a partir de estadísticas procedentes de fuentes abiertas. Su objetivo principal es ofrecer una herramienta funcional e intuitiva que facilite la consulta, comparación y exploración de perfiles de jugadores, integrando en un mismo entorno distintos recursos de análisis y visualización útiles para tareas de scouting y evaluación de rendimiento.

Para ello, se ha desarrollado una aplicación en Streamlit conectada a una base de datos estructurada, incorporando filtros avanzados, rankings, comparativas visuales, radares de rendimiento, generación de alineaciones y espacios de gestión diferenciados según el tipo de usuario. El proyecto transforma un conjunto amplio de datos deportivos en una solución aplicada, permitiendo pasar del análisis técnico en entornos de desarrollo a una herramienta accesible para el usuario final, con una orientación práctica y centrada en la interpretación clara de la información.

El impacto potencial del proyecto radica en su capacidad para apoyar la toma de decisiones basada en datos dentro del ámbito futbolístico, al centralizar información, agilizar la búsqueda de jugadores y mejorar la comprensión del rendimiento mediante visualizaciones interactivas. Entre los principales resultados alcanzados destacan el desarrollo de una aplicación plenamente operativa, la automatización de procesos de filtrado y selección, y la validación de una arquitectura funcional construida con tecnologías accesibles, datos abiertos y un enfoque aplicado a necesidades reales.
"""

# Introducción
textpage3 = """
En el fútbol actual existe una gran cantidad de datos sobre el rendimiento de los jugadores, pero no siempre resulta fácil transformarlos en información útil. En muchos casos, los datos están dispersos, poco estructurados o requieren conocimientos técnicos para poder analizarlos correctamente. Esto genera la necesidad de herramientas que faciliten su interpretación y uso práctico.

Esta situación es especialmente relevante en el scouting y en el análisis de rendimiento, donde comparar jugadores de forma rápida y objetiva resulta fundamental. Disponer de una aplicación que centralice filtros, métricas y visualizaciones permite mejorar la eficiencia del análisis y apoyar una toma de decisiones más clara y fundamentada dentro del sector deportivo.

El objetivo de este proyecto es desarrollar una aplicación web que permita explorar, comparar y evaluar jugadores de fútbol a partir de datos abiertos. Entre los beneficios esperados destacan la mejora en el acceso a la información, la agilización de los procesos de búsqueda y comparación, y la creación de un entorno útil para apoyar tareas de análisis deportivo de forma más visual, ordenada y funcional.
"""

# Objetivos
textpage4 = """
El objetivo principal de este trabajo es diseñar, desarrollar y desplegar una aplicación web orientada al análisis de jugadores de fútbol a partir de datos abiertos. La finalidad es convertir un conjunto amplio de estadísticas en una herramienta funcional, visual e intuitiva que facilite la consulta y comparación de perfiles de rendimiento.

De forma específica, el proyecto busca estructurar y almacenar los datos de manera adecuada, implementar filtros avanzados para segmentar jugadores según distintos criterios, desarrollar visualizaciones que mejoren la interpretación de la información y habilitar funcionalidades prácticas como rankings, radares comparativos, alineaciones y listas personalizadas.

Además, se pretende optimizar la experiencia de usuario mediante una interfaz clara y accesible, que permita interactuar con los datos sin necesidad de conocimientos técnicos avanzados. Esto implica diseñar una navegación sencilla, asegurar la coherencia entre filtros y resultados, y garantizar que la información se presente de forma comprensible y útil.

Por último, el proyecto busca demostrar la viabilidad de construir una herramienta de análisis deportivo completa utilizando tecnologías accesibles y datos abiertos, validando su utilidad tanto en entornos formativos como en contextos aplicados al análisis y scouting futbolístico.
"""

# Escenario Temporal
textpage5 = """
El proyecto se ha desarrollado en varias fases secuenciales, representadas en el diagrama de Gantt. En primer lugar, se realizó la recopilación y preparación de los datos, seguida de su limpieza, transformación y almacenamiento. Posteriormente, se llevó a cabo la fase de modelado, incluyendo la reducción de la dimensionalidad para construir un sistema de scoring de jugadores. Finalmente, se desarrolló la aplicación, se validó su funcionamiento y se completó su despliegue.

La temporalidad de estas etapas ha estado condicionada por distintas reglas del negocio. Entre ellas, destacan la dependencia de fuentes de datos abiertas, la necesidad de asegurar coherencia entre competiciones, equipos y jugadores, y el tiempo adicional requerido para validar el scoring generado. Asimismo, la estabilidad de la aplicación, la experiencia de usuario y la correcta integración de funcionalidades también han influido en la planificación temporal del proyecto.
"""

imagepage5 = "../TFM other documents/gantt_table_style.png"

# Arquitectura Conceptual y Tecnología del proyecto
textpage6 = """
La arquitectura del proyecto se basa en una estructura modular desarrollada en Python, organizada en distintas capas funcionales para separar la gestión de datos, la lógica de negocio, la visualización y el control de usuarios. La fuente principal de información procede de FBref, complementada con procesos de obtención y tratamiento de datos apoyados en código de scraping disponible en abierto. A partir de esta base, los datos son procesados mediante librerías como Pandas y NumPy, lo que permite su limpieza, transformación y preparación para el análisis posterior.

En la capa de almacenamiento, el sistema utiliza una base de datos local SQLite para gestionar las estadísticas de jugadores y optimizar su consulta dentro de la aplicación. Paralelamente, la autenticación y la gestión de usuarios y accesos se apoyan en una base de datos remota en Neon, integrando SQLAlchemy para la comunicación con la base y bcrypt para el cifrado y validación segura de contraseñas. Esta separación entre datos analíticos y datos de usuario aporta mayor claridad estructural, escalabilidad y mantenibilidad al sistema.

La capa de presentación se ha desarrollado con Streamlit, framework que permite construir una aplicación web interactiva centrada en la exploración y comparación de jugadores. Para la representación visual se han utilizado herramientas como Plotly y Matplotlib, mientras que SciPy se ha empleado en cálculos estadísticos y comparativos. Además, se han incorporado librerías como Pillow y FPDF para el tratamiento de imágenes y la generación de documentos PDF. Finalmente, el proyecto se gestiona mediante GitHub y se despliega en Streamlit Community Cloud, lo que garantiza accesibilidad, portabilidad y facilidad de uso en un entorno real.
"""

# Metodología CRISP-DM
textpage7 = """
Para el desarrollo del proyecto se ha seguido como marco de trabajo la metodología CRISP-DM (Cross Industry Standard Process for Data Mining), al tratarse de un enfoque estructurado y adecuado para proyectos basados en datos. Esta metodología ha permitido organizar el trabajo en fases claras, desde la comprensión inicial del problema hasta la implantación de una solución funcional, manteniendo una relación constante entre los objetivos del negocio, el tratamiento de los datos y el desarrollo técnico de la aplicación.

La primera fase, comprensión del negocio, se centró en identificar la necesidad principal del proyecto: disponer de una herramienta que facilitara el análisis, filtrado y comparación de jugadores de fútbol a partir de datos abiertos. En esta etapa se definieron los objetivos funcionales de la aplicación, su utilidad para tareas de scouting y análisis de rendimiento, y los beneficios esperados en términos de acceso a la información, rapidez de consulta y apoyo a la toma de decisiones.

La segunda fase, comprensión de los datos, consistió en analizar la información disponible procedente de fuentes abiertas, especialmente FBref, y evaluar su estructura, calidad y utilidad para el proyecto. En esta etapa se identificaron variables relevantes, posibles limitaciones de los datos, relaciones entre competiciones, equipos y jugadores, y necesidades adicionales de tratamiento para poder trabajar con la información de forma coherente y fiable.

La fase de preparación de los datos incluyó los procesos de limpieza, transformación, normalización y organización de la información. Se trabajó en la corrección de inconsistencias, el tratamiento de valores nulos, la adecuación de formatos y la estructuración de los datos en una base preparada para su explotación analítica. Dentro de esta fase también se desarrolló la lógica necesaria para gestionar filtros complejos sobre competiciones, equipos, posiciones y jugadores.

En la fase de modelado, se aplicaron técnicas de análisis orientadas a sintetizar la información disponible y construir métricas más interpretables. En particular, se utilizó una reducción de la dimensionalidad para elaborar un sistema de scoring que permitiera resumir el rendimiento de los jugadores a partir de múltiples variables estadísticas. Esta etapa fue clave para transformar los datos originales en una base más útil para la comparación y evaluación de perfiles.

La fase de evaluación se centró en comprobar que tanto los datos como el modelo y la aplicación respondían a los objetivos planteados. Se validó la coherencia de los filtros, la consistencia de las visualizaciones, la utilidad del scoring generado y el correcto funcionamiento de las distintas funcionalidades desarrolladas. Esta revisión permitió introducir ajustes técnicos y mejorar la fiabilidad general de la herramienta.

Por último, la fase de despliegue consistió en integrar todo el trabajo previo en una aplicación web operativa desarrollada con Streamlit y accesible en entorno cloud. Esta etapa incluyó la conexión con las bases de datos, la implementación de la interfaz de usuario, la gestión de accesos y la publicación final del sistema. De este modo, el proyecto dejó de ser únicamente un ejercicio de análisis de datos para convertirse en una solución funcional, utilizable y orientada a un contexto real.
"""

# Discuisión de Resultados
textpage8 = """
Los resultados obtenidos muestran que el proyecto ha logrado construir una herramienta funcional y útil para la exploración, comparación y visualización de jugadores de fútbol a partir de datos abiertos. La aplicación permite integrar filtros, rankings, radares, alineaciones y un sistema de scoring dentro de un mismo entorno, facilitando el análisis de perfiles de forma más accesible y ordenada. En este sentido, el balance general del proyecto es positivo, ya que se ha conseguido trasladar un proceso técnico de tratamiento de datos a una solución práctica y utilizable.

Sin embargo, el desarrollo también ha puesto de manifiesto algunas limitaciones relevantes. Una de ellas ha sido la asignación inexacta de ciertos jugadores a posiciones que no siempre representan de forma fiel su rol real en el campo. Al depender de clasificaciones ya presentes en la fuente de datos, algunos perfiles pueden quedar encuadrados en categorías demasiado generales o poco precisas, lo que afecta a la comparación entre jugadores y a la interpretación de determinadas métricas de rendimiento.

Asimismo, surgieron dificultades en el sistema de scoring construido a partir de la reducción de la dimensionalidad. En determinados casos fue necesario revisar y corregir su comportamiento para mejorar la coherencia de los resultados y evitar interpretaciones poco consistentes. Este proceso de ajuste ha sido importante no solo para mejorar la calidad del score final, sino también para evidenciar que la utilidad de este tipo de métricas depende tanto del tratamiento estadístico aplicado como de la calidad, estructura y contextualización de los datos de partida.
"""

# Conclusiones y Líneas de Trabajo Futuro
textpage9 = """
El proyecto ha permitido desarrollar una aplicación web funcional orientada al análisis de jugadores de fútbol a partir de datos abiertos, integrando procesos de recopilación, tratamiento, modelado y visualización en un mismo entorno. A lo largo del trabajo se ha demostrado la viabilidad de construir una herramienta útil para tareas de scouting y evaluación de rendimiento mediante tecnologías accesibles, una arquitectura modular y un enfoque práctico centrado en el usuario.

Desde una perspectiva crítica, el desarrollo también ha evidenciado que la calidad del resultado final depende en gran medida de la fiabilidad de los datos, de la correcta clasificación de los jugadores y de la validación constante de los modelos empleados. Las dificultades encontradas en la asignación posicional de algunos perfiles y en el ajuste del sistema de scoring han puesto de manifiesto la importancia de seguir refinando tanto la base de datos como la lógica analítica de la aplicación.

Como líneas de trabajo futuro, el proyecto podría ampliarse mediante la incorporación de nuevas fuentes de datos, una clasificación posicional más precisa, mejoras en el sistema de scoring y una mayor automatización en los procesos de actualización. Asimismo, sería interesante evolucionar la aplicación hacia una solución más escalable, con nuevas funcionalidades de comparación avanzada, generación de informes y análisis adaptados a distintos perfiles de usuario dentro del ámbito deportivo.
"""

# Bibliografía
textpage10 = """
FBref. (s. f.). Football statistics and history. https://fbref.com/

LanusStats. (s. f.). Repositorio de recursos y código de scraping y análisis de datos de fútbol. GitHub. https://github.com/lanusstats

Neon. (s. f.). Neon documentation. https://neon.com/

Python Software Foundation. (s. f.). Python documentation. https://docs.python.org/3/

Soy Dalto. (s. f.). Curso de Python desde cero [Vídeo]. YouTube.

Soy Dalto. (s. f.). Curso de Visual Studio Code [Vídeo]. YouTube.

Sports Data Campus. (s. f.). Apuntes y materiales docentes del Máster de Python Avanzado Aplicado al Deporte. Material docente no publicado.

Streamlit. (s. f.). Streamlit documentation. https://docs.streamlit.io/

pandas. (s. f.). pandas documentation. https://pandas.pydata.org/docs/

NumPy. (s. f.). NumPy documentation. https://numpy.org/doc/

Matplotlib. (s. f.). Matplotlib documentation. https://matplotlib.org/stable/

Plotly. (s. f.). Plotly documentation. https://plotly.com/python/

SciPy. (s. f.). SciPy documentation. https://docs.scipy.org/doc/scipy/

SQLite. (s. f.). SQLite documentation. https://www.sqlite.org/docs.html

SQLAlchemy. (s. f.). SQLAlchemy documentation. https://docs.sqlalchemy.org/

bcrypt. (s. f.). bcrypt documentation. https://pypi.org/project/bcrypt/
"""