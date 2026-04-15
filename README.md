# DataLab

**DataLab** es una aplicación desarrollada en **Streamlit** orientada al **análisis de jugadores de fútbol** desde una perspectiva de **dirección deportiva, scouting y rendimiento**. La plataforma centraliza datos, visualizaciones y herramientas analíticas en un único entorno, facilitando la comparación de jugadores, la exploración de perfiles y la toma de decisiones basada en datos.

Además de las funcionalidades clásicas de filtrado, ranking y comparación, DataLab incorpora un sistema de **player scoring por posición** construido mediante técnicas de **machine learning no supervisado**, concretamente a través de **reducción de dimensionalidad con PCA**.

---

## Objetivo

El objetivo de la aplicación es resolver el problema de trabajar con múltiples herramientas de forma dispersa, centralizando en una sola plataforma el acceso a datos, visualizaciones y métricas avanzadas. De este modo, el cuerpo técnico o la dirección deportiva pueden trabajar sobre una **misma base de información**, mejorando la coordinación del análisis y la consistencia en la evaluación de jugadores.

Entre las posibilidades que ofrece la aplicación se incluyen:

* Creación de **tierlists** para evaluar jugadores de interés.
* Generación de **onces ideales** de diferentes competiciones a lo largo de las jornadas.
* Aplicación de **filtros de datos**, ordenamiento y creación de **rankings por estadística**.
* Visualización de **radares comparativos** entre dos jugadores.
* Integración de un **player score por posición** para defensas, centrocampistas y delanteros.
* Posibilidad de consultar tanto un **score oficial** entrenado sobre jugadores con una muestra estable de minutos, como un **score extendido** aplicado al conjunto completo del dataset.
* Solicitud de importación de **nuevas competiciones** para ampliar la base de datos.

---

## Dependencias

La aplicación ha sido desarrollada en **Python** y utiliza las siguientes librerías principales:

* **Streamlit** para la interfaz web.
* **SQLite** como base de datos local.
* **pandas** y **numpy** para procesamiento de datos.
* **plotly** y **matplotlib** para visualización.
* **Pillow** para gestión de imágenes.
* **LanusStats** para la extracción de datos desde **Fbref**.
* **openpyxl**, **fpdf2**, **requests**, **scipy**, **python-dotenv** e **IPython** como librerías auxiliares para exportación, peticiones, cálculos complementarios, gestión de configuración y trabajo interactivo.
* **sqlalchemy**, **psycopg2-binary** e **bcrypt** para conexión y gestión de bases de datos, integración con PostgreSQL y cifrado seguro de contraseñas.


Las dependencias se pueden instalar con:
 
```bash
pip install -r requirements.txt
```

---

## Cómo ejecutar la aplicación

##### Clonar el repositorio y situarse en la carpeta del proyecto:

```bash
git clone <url-del-repo>
cd <nombre-del-proyecto>
```

##### Instalar las dependencias:

```bash
pip install -r requirements.txt
```

##### Ejecutar la aplicación con Streamlit:

```bash
streamlit run app.py
```

##### Abrir la URL que muestra Streamlit en el navegador para acceder a la app.

---

## Funcionalidades principales

**Gestión de usuarios:** Control de acceso a la aplicación y permisos.

**Lineups:** Incluye herramientas para generar alineaciones, analizar estructuras de equipo y construir onces ideales de competiciones concretas.

**Listas de jugadores:** Permite organizar jugadores en listas personalizadas para procesos de scouting, seguimiento o priorización deportiva.

**Overview y filtros:** Permite visualizar el conjunto de jugadores disponibles, aplicar filtros por edad, posición, equipo, competición o minutos jugados, y exportar los resultados en formato CSV.

**Rankings y comparación de jugadores:** Facilita la creación de rankings por estadística y la comparación de perfiles de jugadores a través de tablas y radares comparativos.

**Radares comparativos:** Comparar visualmente el rendimiento de dos jugadores.

**Solicitud de nuevas competiciones:** Los usuarios pueden solicitar la incorporación de nuevas competiciones a la base de datos para ampliar el alcance de la plataforma.

**Player Score por posición:** DataLab incorpora una métrica derivada de **PCA** que permite asignar una **puntuación sintética por posición** a defensas, centrocampistas y delanteros. El sistema incluye:

* un **score oficial**, calculado sobre una muestra robusta de jugadores con mayor estabilidad estadística;
* y un **score extendido**, proyectado sobre una muestra más amplia para facilitar la exploración de perfiles con menos minutos.

---

## Arquitectura de datos

La aplicación trabaja sobre una **base de datos SQLite** que centraliza las estadísticas de jugadores y las métricas derivadas utilizadas en la interfaz.

La tabla principal de trabajo es:

* `stats_players_fbref`

Además, el sistema puede incorporar tablas derivadas con métricas avanzadas, como las tablas de **player score** generadas a partir del modelo PCA.

Esto permite que las métricas calculadas fuera del entorno de Streamlit puedan integrarse como una **nueva stat operativa** dentro de la aplicación sin necesidad de recalcular el pipeline en cada ejecución.

---

## Fuente de los datos

Los datos provienen de **Fbref** y han sido obtenidos mediante la librería **LanusStats**.

Posteriormente, los datos han sido procesados, depurados y almacenados en una base de datos SQLite para su uso en la aplicación.

---

## Notas adicionales

* La aplicación está orientada a un uso **exploratorio y comparativo**, como apoyo al scouting y al análisis de jugadores.

* El **player score** debe interpretarse como una **métrica sintética no supervisada**, construida a partir de variables estadísticas seleccionadas por posición.

* La utilidad del score depende de la calidad del dataset, de la selección de variables y de la agrupación posicional disponible.

* Actualmente, el modelo está centrado en **jugadores de campo** y no incluye una evaluación específica para **porteros**, debido a la ausencia de métricas especializadas para esa posición en el modelo desplegado.

* Para la visualización de campos y alineaciones se han utilizado herramientas de visualización compatibles con Python, incluyendo recursos gráficos integrados en la app.

---

## Estado del proyecto

DataLab se encuentra en una fase funcional de desarrollo, con un sistema ya operativo para:

* consulta de estadísticas,
* filtros avanzados,
* comparación de jugadores,
* visualización de rankings,
* y despliegue de un **player score por posición** integrado en la aplicación.

El sistema está preparado para seguir creciendo con futuras mejoras, como una categorización posicional más fina, nuevas competiciones, métricas específicas para porteros y validaciones adicionales del scoring.