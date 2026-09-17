import unicodedata
from pathlib import Path
import json
import pandas as pd
import streamlit as st
import re

# ==========================================
# 1. Configuración y Rutas
# ==========================================
PATH_VIDEOS_LOCAL = Path("/Users/barreto/Positron_Projects/py_RLG/_lexrlg")
PATH_CSV = Path("_datarlg_190926.csv")  # Nombre del archivo actualizado
PATH_JSON = Path("datosrlg.json")
PATH_LOGO = Path("logocueb.png")
PATH_MANOS = Path("assets/manos")

URL_BASE_REMOTE = "https://deixisls.alexgbarreto-3c4.workers.dev"

st.set_page_config(
    page_title="Diccionario LSC | Universidad El Bosque",
    page_icon="🤟",
    layout="wide"
)

# ==========================================
# Métricas de Tráfico (Google Analytics 4)
# ==========================================
GA_ID = "G-7692T3YF60"

ga_html = f"""
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_ID}');
    </script>
"""
st.components.v1.html(ga_html, height=0, width=0)

# ==========================================
# Funciones de Utilidad (Normalización)
# ==========================================
def normalizar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    texto_sin_acentos = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto_sin_acentos.upper().strip()

# ==========================================
# 2. Estilos CSS Institucionales (El Bosque)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown {
        font-family: 'Montserrat', sans-serif !important;
    }

    .header-bosque {
        border-bottom: 4px solid #FDBA12;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }
    
    .titulo-principal {
        color: #004F2D;
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
    }

    .subtitulo-bosque {
        color: #555555;
        font-weight: 600;
        font-size: 1.0rem;
    }

    .stExpander {
        border: 1px solid #D0D7DE !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. Encabezado con Logo
# ==========================================
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    if PATH_LOGO.exists():
        st.image(str(PATH_LOGO), width=160)
    else:
        st.write("🟢 **[Logo U. El Bosque]**")

with col_titulo:
    st.markdown("""
        <div class="header-bosque">
            <h1 class="titulo-principal">Repositorio Léxico-Gramatical UEB</h1>
            <span class="subtitulo-bosque" style="display: block;">Diccionario para la formación de estudiantes del programa Intérprete Profesional de la LSC</span>
            <span class="subtitulo-bosque" style="display: block;">Laboratorio de Traducción e Interpretación de Lenguas de Señas (TILS LAB UEB)</span>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. Carga de Datos y Procesamiento Inicial
# ==========================================
@st.cache_data
def obtener_datos(ruta_csv: Path, ruta_json: Path) -> list[dict]:
    if ruta_json.exists():
        with open(ruta_json, "r", encoding="utf-8") as f:
            return json.load(f)
    
    if not ruta_csv.exists():
        st.error(f"No se encontró `{ruta_csv}` ni `{ruta_json}`.")
        st.stop()

    df = pd.read_csv(ruta_csv, encoding="utf-8").fillna("Sin especificar")
    datos = df.to_dict(orient="records")
    
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
        
    return datos

datos = obtener_datos(PATH_CSV, PATH_JSON)
st.caption(f"Corpus cargado: {len(datos)} entradas")

etiquetas_cm_unicas = set()
for item in datos:
    for i in range(1, 6):
        val = str(item.get(f"cm{i}", "")).strip().upper()
        if val and val not in ["SIN ESPECIFICAR", "NAN", "N/A"]:
            etiquetas_cm_unicas.add(val)
lista_cms_disponibles = sorted(list(etiquetas_cm_unicas))

cursos_unicos = sorted(list(set(str(item.get("curso", "")) for item in datos if str(item.get("curso", "")).upper() not in ["SIN ESPECIFICAR", "NAN", "N/A", ""])))
niveles_unicos = sorted(list(set(str(item.get("nivel", "")) for item in datos if str(item.get("nivel", "")).upper() not in ["SIN ESPECIFICAR", "NAN", "N/A", ""])))

def obtener_ruta_video(nombre_video: str) -> tuple[str, str]:
    ruta_local = PATH_VIDEOS_LOCAL / str(nombre_video)
    if ruta_local.exists():
        return str(ruta_local), "local"
    nombre_limpio = str(nombre_video).lstrip("/")
    return f"{URL_BASE_REMOTE}/{nombre_limpio}", "remota"

# ==========================================
# 5. Módulo de Búsqueda y Visualización
# ==========================================
def renderizar_bloque_busqueda(prefijo_id: str, titulo_bloque: str):
    st.markdown(f"### {titulo_bloque}")
    
    # --- BÚSQUEDA RÁPIDA ---
    texto_glosa = st.text_input(
        "🔍 Búsqueda rápida (Glosa):", 
        placeholder="Ej. YO, FAMILIA...",
        key=f"{prefijo_id}_glosa"
    )
    glosa_norm = normalizar_texto(texto_glosa)
    
    # --- BÚSQUEDA AVANZADA ---
    with st.expander("⚙️ Búsqueda Avanzada"):
        texto_def = st.text_input(
            "Filtrar por definición:", 
            placeholder="Palabra clave en el significado...",
            key=f"{prefijo_id}_def"
        )
        def_norm = normalizar_texto(texto_def)
        
        col_filtros1, col_filtros2 = st.columns(2)
        with col_filtros1:
            filtro_curso = st.multiselect("Filtrar por Curso:", options=cursos_unicos, key=f"{prefijo_id}_curso")
        with col_filtros2:
            filtro_nivel = st.multiselect("Filtrar por Nivel:", options=niveles_unicos, key=f"{prefijo_id}_nivel")
            
        cms_seleccionadas = st.multiselect(
            "Configuración Manual (CM):", 
            options=lista_cms_disponibles,
            key=f"{prefijo_id}_cm"
        )
        
        logica_cm = "OR"
        if len(cms_seleccionadas) > 1:
            logica_cm = st.radio(
                "Operador lógico CM:", 
                ["AND (Todas)", "OR (Cualquiera)"], 
                horizontal=True, 
                key=f"{prefijo_id}_logica"
            )
            
        if cms_seleccionadas:
            cols_img = st.columns(len(cms_seleccionadas) + (5 - len(cms_seleccionadas) if len(cms_seleccionadas) < 5 else 0))
            for idx, cm_etiqueta in enumerate(cms_seleccionadas):
                with cols_img[idx]:
                    ruta_img = PATH_MANOS / f"{cm_etiqueta.lower()}.png"
                    if ruta_img.exists():
                        st.image(str(ruta_img), width=80)
                    else:
                        st.caption(f"🖼️ [{cm_etiqueta}]")

    # --- LÓGICA DE FILTRADO ESTRICTO (\b) ---
    resultados = []
    for item in datos:
        # 1. Filtro Glosa Rápida (Usa glosa_limpia)
        match_glosa = True
        if glosa_norm:
            valor_glosa = normalizar_texto(str(item.get("glosa_limpia", "")))
            if not re.search(rf"\b{re.escape(glosa_norm)}\b", valor_glosa):
                match_glosa = False

        # 2. Filtro Definición (Usa definicion)
        match_def = True
        if def_norm:
            valor_def = normalizar_texto(str(item.get("definicion", "")))
            if not re.search(rf"\b{re.escape(def_norm)}\b", valor_def):
                match_def = False
                
        # 3. Filtros Curso y Nivel
        match_curso = True
        if filtro_curso:
            valor_curso = str(item.get("curso", ""))
            if valor_curso not in filtro_curso:
                match_curso = False
                
        match_nivel = True
        if filtro_nivel:
            valor_nivel = str(item.get("nivel", ""))
            if valor_nivel not in filtro_nivel:
                match_nivel = False

        # 4. Filtro CM
        match_cm = True
        if cms_seleccionadas:
            cms_item = set(str(item.get(f"cm{i}", "")).strip().upper() for i in range(1, 6))
            if "AND" in logica_cm:
                match_cm = all(cm in cms_item for cm in cms_seleccionadas)
            else:
                match_cm = any(cm in cms_item for cm in cms_seleccionadas)

        # Consolidar validaciones
        if match_glosa and match_def and match_curso and match_nivel and match_cm:
            resultados.append(item)
            
    # --- INTERFAZ DE RESULTADOS ---
    if not resultados:
        if glosa_norm or def_norm or filtro_curso or filtro_nivel or cms_seleccionadas:
            st.warning("No se encontraron señas con los filtros aplicados.")
        return

    # Usar glosa_limpia (y glosa_estandar como respaldo) para menús e interfaz
    opciones = [f"{item.get('id_entrada', '')} - {item.get('glosa_limpia', item.get('glosa_estandar', ''))}" for item in resultados]
    seleccion = st.selectbox("👉 Selecciona una seña para explorar:", opciones, key=f"{prefijo_id}_select")
    
    idx_seleccionado = opciones.index(seleccion)
    seña = resultados[idx_seleccionado]
    
    st.divider()
    st.subheader(seña.get("glosa_limpia", seña.get("glosa_estandar", "Sin Glosa")))
    
    nombre_vid = seña.get("nombre_video", "")
    if nombre_vid and nombre_vid != "Sin especificar":
        origen, fuente = obtener_ruta_video(nombre_vid)
        st.video(origen)
        st.caption(f"📁 Local: `{nombre_vid}`" if fuente == "local" else "🌐 Nube")
    else:
        st.warning("Sin archivo de video asociado.")
        
    with st.expander("📖 Definición y Detalles", expanded=True):
        st.markdown(f"**Curso:** {seña.get('curso', 'N/A')} | **Nivel:** {seña.get('nivel', 'N/A')}")
        st.markdown(f"**Clase Gramatical:** {seña.get('clase_gramatical', 'N/A')}")
        # Ajustado a 'tipo_sena' basado en tu archivo
        st.markdown(f"**Tipo de Seña:** {seña.get('tipo_sena', 'N/A')}")
        st.write(seña.get("definicion", "Sin definición."))
        
    with st.expander("🖐️ Configuraciones Manuales (CM)", expanded=False):
        for i in range(1, 6):
            valor_cm = str(seña.get(f'cm{i}', 'N/A')).strip()
            if valor_cm and valor_cm.upper() not in ["SIN ESPECIFICAR", "NAN", "N/A"]:
                ruta_img_cm = PATH_MANOS / f"{valor_cm.lower()}.png"
                c1, c2 = st.columns([2, 5])
                with c1:
                    if ruta_img_cm.exists():
                        st.image(str(ruta_img_cm), width=120)
                with c2:
                    st.write(f"**CM{i}:** {valor_cm.upper()}")

col_b1, col_b2 = st.columns(2)

with col_b1:
    renderizar_bloque_busqueda("b1", "Buscador 1")

with col_b2:
    renderizar_bloque_busqueda("b2", "Buscador 2 (Contraste)")


# ==========================================
# 6. Bloque 3: Créditos de Aplicación
# ==========================================
st.divider()

with st.container():
    col_cred_1, col_cred_2 = st.columns(2)
    
    with col_cred_1:
        st.markdown("""
       **Proyecto Repositorio Léxico-Gramatical para la formación de traductores e intérpretes de la Lengua de Señas Colombiana** 
       **(Versión 1.0 *prueba beta*)**
       **Universidad El Bosque (2026 ©)**

        **Departamento de Humanidades**
        
        Dr. Camilo Duque, *Director de departamento*  
        
        **Programa Intérprete Profesional de la Lengua de Señas Colombiana**

        Yenny Cortes, Mg. *Directora de programa*  
        
        **Laboratorio de Traducción e Interpretación de Lengua de señas (TILS-LAB UEB)**

        Alex G. Barreto, Phd. Msc.
        *Coordinador de TILS-LAB y Semillero de Investigación SABILES*

        Jose F. Lesmes, Mg. 
        *Coordinador Área Curricular y Estudios de Traducción e Interpretación*

        **Comentarios observaciones o sugerencias**
        *¿Algún dato es incorrecto o incompleto? ¿Deseas hacer una contribución o comentario?*
        Escribenos a: interpretacion@unbosque.edu.co o agbarretom@unbosque.edu.co
        """)
        
    with col_cred_2:
        st.markdown("""
        **Área de Estudios de Lengua de Señas**  
        Coordinador: Alex G. Barreto, Phd. Msc.  
        
        **Equipo de docentes sordos que participaron en el modelaje y selección de los videos de las señas:**  
        - Lic. Omar Bustos, Esp. (2024-2026)  
        - Adm. Johana Balaguera, Mg. (2024-2026)  
        - Lic. Álvaro Herrán, Mg. (2024-2026)  
        - Lic. Juliana Rocha (2025-2026)  
        - Lic. Daniel Hincapie (2026)  
        - Lic. Teresa Garzón, Mg. (2024-2025)  
        - Lic. Hugo Lopez, Mg. (2024)

        **Equipo de asistentes de investigación del semillero SABILES que participaron en la limpieza y anotación de los datos:**  
        - Valentina Barrera, Intérprete profesional (2025)  
        - Nataly Navarro, Intérprete profesional (2026)  
        - Paola Ramirez, Intérprete Profesional (2026) 
        - Yakeline Cárdenas, Intérprete Profesional (2026) 
        - Yajaira Valencia, Intérprete Profesional (2026) 
        - Angie Salinas, , Intérprete Profesional (2026)
    

        **Fuentes documentales**

        La selección de este repositorio partió de la revisión inicial de algunas compilaciones de léxico de la Lengua de de Señas Colombiana además de la discusión y selección por parte del equipo de docentes sordos.

        Instituto Nacional para Sordos e Instituto Caro y Cuervo (2006): Diccionario Básico de la Lengua de Señas Colombiana
        https://educativo.insor.gov.co/diccionario/
        https://lenguasyliteraturasnativas.caroycuervo.gov.co/pdf-del-diccionario-basico-de-la-lengua-de-senas-colombiana/ 

        Federación Nacional de Sordos de Colombia (1996-2010): Glosarios de Lengua de Señas Colombiana Tomos 1 al 4.
        https://fenascol.org.co

        Semillero de Investigación Semilles Universidad Nacional de Colombia: Base de datos léxica de la LSC (LeSiCo)
        https://sites.google.com/view/semilles/lesico?authuser=0


        """)
