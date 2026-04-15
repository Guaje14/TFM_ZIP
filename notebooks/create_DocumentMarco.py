# ============================================
# Notebooks -> create_DocumentMarco
# ============================================

# Importar librerías 
import os                          
from fpdf import FPDF, XPos, YPos  

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