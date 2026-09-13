import unicodedata
from pathlib import Path
import json
import pandas as pd
import streamlit as st

# ==========================================
# 1. Configuración y Rutas
# ==========================================
PATH_VIDEOS_LOCAL = Path("/Users/barreto/Positron_Projects/py_RLG/_lexrlg")
PATH_CSV = Path("_datarlg_100926.csv")
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
GA_ID = "G-7692T3YF60"  # Reemplaza con tu ID real de Google Analytics

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
# Inyección silenciosa del script en el HTML
st.components.v1.html(ga_html, height=0, width=0)

# ==========================================
# Funciones de Utilidad (Normalización)
# ==========================================
def normalizar_texto(texto: str) -> str:
    """Elimina acentos y convierte a mayúsculas para búsquedas flexibles."""
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

# Extraer dinámicamente todas las etiquetas de CM únicas del corpus
etiquetas_cm_unicas = set()
for item in datos:
    for i in range(1, 6):
        val = str(item.get(f"cm{i}", "")).strip().upper()
        if val and val not in ["SIN ESPECIFICAR", "NAN", "N/A"]:
            etiquetas_cm_unicas.add(val)
lista_cms_disponibles = sorted(list(etiquetas_cm_unicas))

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
    
    # --- ENTRADA 1: Búsqueda por CM ---
    cms_seleccionadas = st.multiselect(
        "1. Buscar por Configuración Manual (CM):", 
        options=lista_cms_disponibles,
        key=f"{prefijo_id}_cm"
    )
    
    # Lógica booleana si hay más de 1 selección
    if len(cms_seleccionadas) > 1:
        logica_cm = st.radio(
            "Operador lógico para múltiples CM:", 
            ["AND (Debe contener todas)", "OR (Puede contener cualquiera)"], 
            horizontal=True, 
            key=f"{prefijo_id}_logica"
        )
    else:
        logica_cm = "OR" # Por defecto si hay 1 o 0
        
    # Renderizado visual de las CMs seleccionadas (reemplaza el menú flotante)
    if cms_seleccionadas:
        st.write("Visualización de CM:")
        cols_img = st.columns(len(cms_seleccionadas) + (5 - len(cms_seleccionadas) if len(cms_seleccionadas) < 5 else 0))
        for idx, cm_etiqueta in enumerate(cms_seleccionadas):
            with cols_img[idx]:
                ruta_img = PATH_MANOS / f"{cm_etiqueta.lower()}.png"
                if ruta_img.exists():
                    st.image(str(ruta_img), width=120)
                else:
                    st.caption(f"🖼️ [{cm_etiqueta}]")
    
    # --- ENTRADA 2: Búsqueda por Glosa/Definición ---
    texto_busqueda = st.text_input(
        "2. Buscar por Glosa o Significado:", 
        placeholder="Ej. LICENCIA o una palabra clave...",
        key=f"{prefijo_id}_texto"
    )
    texto_norm = normalizar_texto(texto_busqueda)

    # --- Lógica de Filtrado ---
    resultados = []
    for item in datos:
        match_texto = True
        match_cm = True
        
        # Filtro Texto (Glosa o Definición) - Ignora acentos y mayúsculas
        if texto_norm:
            glosa_norm = normalizar_texto(str(item.get("glosa", "")))
            def_norm = normalizar_texto(str(item.get("definicion", "")))
            match_texto = (texto_norm in glosa_norm) or (texto_norm in def_norm)
            
        # Filtro CM (Configuración Manual)
        if cms_seleccionadas:
            # Extraer las CMs de la entrada actual
            cms_item = set(str(item.get(f"cm{i}", "")).strip().upper() for i in range(1, 6))
            if "AND" in logica_cm:
                # Todas las CMs seleccionadas deben estar en los campos de la entrada
                match_cm = all(cm in cms_item for cm in cms_seleccionadas)
            else:
                # Al menos una CM seleccionada debe coincidir
                match_cm = any(cm in cms_item for cm in cms_seleccionadas)
                
        # Consolidar filtros
        if match_texto and match_cm:
            resultados.append(item)
            
    # --- Reproductor y Detalles ---
    if not resultados:
        if cms_seleccionadas or texto_norm:
            st.warning("No se encontraron resultados con los filtros actuales.")
        return

    opciones = [f"{item.get('id_entrada', '')} - {item.get('glosa', '')}" for item in resultados]
    seleccion = st.selectbox("3. Selecciona una seña para explorar:", opciones, key=f"{prefijo_id}_select")
    
    idx_seleccionado = opciones.index(seleccion)
    seña = resultados[idx_seleccionado]
    
    st.divider()
    st.subheader(seña.get("glosa", "Sin Glosa"))
    
    # Video
    nombre_vid = seña.get("nombre_video", "")
    if nombre_vid and nombre_vid != "Sin especificar":
        origen, fuente = obtener_ruta_video(nombre_vid)
        st.video(origen)
        st.caption(f"📁 Reproducción local: `{nombre_vid}`" if fuente == "local" else "🌐 Servidor remoto")
    else:
        st.warning("Sin archivo de video asociado.")
        
    # Acordeones de información
    with st.expander("📖 Definición y Detalles", expanded=True):
        st.markdown(f"**Clase Gramatical:** {seña.get('clase_gramatical', 'N/A')}")
        st.markdown(f"**Tipo de Seña:** {seña.get('tipo_de_sena', 'N/A')}")
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

# Estructura a dos columnas (Bloque 1 y Bloque 2)
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
       **Proyecto Repositorio Léxico-Gramatical para la formación de traductores e intérpretes de la Lengua de Señas Colombiana (Versión 1.0)**
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

        **Fuentes documentales**

        La selección de este repositorio partió de la revisión inicial de algunas compilaciones de léxico de la Lengua de de Señas Colombiana además de la discusión y selección del equipo de docentes sordos.

        Instituto Nacional para Sordos e Instituto Caro y Cuervo (2006): Diccionario Básico de la Lengua de Señas Colombiana
        https://educativo.insor.gov.co/diccionario/
        https://lenguasyliteraturasnativas.caroycuervo.gov.co/pdf-del-diccionario-basico-de-la-lengua-de-senas-colombiana/ 

        Federación Nacional de Sordos de Colombia (1996-2010): Glosarios de Lengua de Señas Colombiana Tomos 1 al 4.
        https://fenascol.org.co

        Semillero de Investigación Semilles Universidad Nacional de Colombia: Base de datos léxica de la LSC (LeSiCo)
        https://sites.google.com/view/semilles/lesico?authuser=0


        """)
