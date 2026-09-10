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
# 4. Carga de Datos
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

def obtener_ruta_video(nombre_video: str) -> tuple[str, str]:
    ruta_local = PATH_VIDEOS_LOCAL / str(nombre_video)
    if ruta_local.exists():
        return str(ruta_local), "local"
    
    # Asegurar la barra diagonal '/' entre el dominio base y el nombre del archivo
    nombre_limpio = str(nombre_video).lstrip("/")
    return f"{URL_BASE_REMOTE}/{nombre_limpio}", "remota"

# ==========================================
# 5. Buscador y Consulta (Con soporte CM)
# ==========================================
st.caption(f"Corpus cargado: {len(datos)} entradas")

busqueda = st.text_input(
    "Buscar por glosa, definición o código CM (ej. P, W):",
    placeholder="Ej. LICENCIA, SUSTANTIVO, P..."
).strip().upper()

# Filtro que evalúa glosa, definición y códigos cm1 a cm5
if busqueda:
    resultados = [
        item for item in datos
        if busqueda in str(item.get("glosa", "")).upper()
        or busqueda in str(item.get("definicion", "")).upper()
        or any(busqueda == str(item.get(f"cm{i}", "")).strip().upper() for i in range(1, 6))
    ]
else:
    resultados = datos

if resultados:
    opciones = [f"{item.get('id_entrada', '')} - {item.get('glosa', '')}" for item in resultados]
    seleccion = st.selectbox("Selecciona una seña para explorar:", opciones)
    
    idx_seleccionado = opciones.index(seleccion)
    seña = resultados[idx_seleccionado]
    
    col_vid, col_info = st.columns([1.3, 1])
    
    with col_vid:
        st.subheader(seña.get("glosa", "Sin Glosa"))
        nombre_vid = seña.get("nombre_video", "")
        
        if nombre_vid and nombre_vid != "Sin especificar":
            origen, fuente = obtener_ruta_video(nombre_vid)
            st.video(origen)
            st.caption(f"📁 Reproducción local: `{nombre_vid}`" if fuente == "local" else "🌐 Servidor remoto")
        else:
            st.warning("Sin archivo de video asociado.")

    with col_info:
        st.markdown("### Detalles Lingüísticos")
        st.markdown(f"**Clase Gramatical:** {seña.get('clase_gramatical', 'N/A')}")
        st.markdown(f"**Tipo de Seña:** {seña.get('tipo_de_sena', 'N/A')}")
        st.markdown(f"**Curso:** {seña.get('curso', 'N/A')}")
        
        with st.expander("📖 Definición Completa", expanded=True):
            st.write(seña.get("definicion", "Sin definición."))
            
        with st.expander("🖐️ Configuraciones Manuales (CM)", expanded=False):
            cms = [
                ("CM1", seña.get('cm1', 'N/A')),
                ("CM2", seña.get('cm2', 'N/A')),
                ("CM3", seña.get('cm3', 'N/A')),
                ("CM4", seña.get('cm4', 'N/A')),
                ("CM5", seña.get('cm5', 'N/A'))
            ]
            
            for etiqueta, valor in cms:
                if valor and valor != "Sin especificar" and valor != "N/A":
                    nombre_archivo = f"{valor.strip().lower()}.png"
                    ruta_imagen_mano = PATH_MANOS / nombre_archivo
                    
                    col_img, col_txt = st.columns([1, 3])
                    with col_img:
                        if ruta_imagen_mano.exists():
                            st.image(str(ruta_imagen_mano), width=50)
                        else:
                            st.caption("🖼️ [S/I]")
                    with col_txt:
                        st.markdown(f"**{etiqueta}:** {valor}")
                    st.divider()
else:
    st.warning("No se encontraron resultados para la búsqueda ingresada.")