# ________________________________________________________________________________________________
# ________________________________________________________________________________________________
#Limpieza INICIAL de archivo matriz de diccionario
# ________________________________________________________________________________________________
# ________________________________________________________________________________________________

# 1. CARGA DE DATOS
# Especifica el nombre exacto de tu archivo y la extensión (.csv o .xlsx).
# Si es CSV y usa separador de punto y coma, agrega el argumento: sep=';'

import pandas as pd


ruta_archivo = "/Users/barreto/Positron_Projects/py_RLG/_datarlg.xlsx"

# Cargar el archivo en un DataFrame (df), la estructura principal de pandas.
df = pd.read_excel(ruta_archivo)
# df = pd.read_excel("_datarlg.xlsx")  # Descomentar si el archivo es Excel

# 2. INSPECCIÓN VISUAL RÁPIDA
# .head(n) muestra las primeras n filas para verificar que las columnas cargaron bien.
print("=== PRIMERAS 5 FILAS ===")
print(df.head())

# 3. ESTRUCTURA Y TIPOS DE DATOS
# .info() resume el número de filas, columnas, memoria usada, valores no nulos
# y el tipo de dato detectado (int64, float64, object/texto, datetime).
print("\n=== ESTRUCTURA DEL DATAFRAME ===")
df.info()

# 4. DIAGNÓSTICO DE VALORES FALTANTES (NULOS)
# .isnull() evalúa cada celda (True si está vacía).
# .sum() cuenta los True por columna.
print("\n=== VALORES NULOS POR COLUMNA ===")
conteo_nulos = df.isnull().sum()
# Filtramos para mostrar solo las columnas que tienen al menos un valor faltante
print(conteo_nulos[conteo_nulos > 0])

# 5. Detección de DUPLICADOS
# .duplicated() busca filas totalmente idénticas en todas sus columnas.
total_duplicados = df.duplicated().sum()
print(f"\nFilas completamente duplicadas: {total_duplicados}")

# 6. RESUMEN ESTADÍSTICO Y VALORES ÚNICOS
# .describe(include='all') genera métricas numéricas (media, min, max)
# y categóricas (cantidad de valores únicos, valor más frecuente).
print("\n=== RESUMEN DESCRIPTIVO ===")
print(df.describe(include='all'))

# 6. RESUMEN ESTADÍSTICO Y VALORES ÚNICOS
# .describe(include='all') genera métricas numéricas (media, min, max)
# y categóricas (cantidad de valores únicos, valor más frecuente).
print("\n=== RESUMEN DESCRIPTIVO ===")
print(df.describe(include='all'))



# ________________________________________________________________________________________________
# ________________________________________________________________________________________________
# TOMAR LOS BNNOMBRES DE ARCHIVOS DE CARPETAS Y COLOCARLOS EN UN DATAFRAME
# ________________________________________________________________________________________________
# ________________________________________________________________________________________________


# Incluir una columna con los nombres de los archivos de video

import pandas as pd
from pathlib import Path

# 1. CARGA DEL DATAFRAME EXISTENTE
# Reemplaza por la ruta de tu archivo actual (.csv o .xlsx)
df = pd.read_excel(ruta_archivo) 

# 2. DEFINIR LA RUTA DE LA CARPETA Y EXTENSIONES DE VIDEO
# Path() administra rutas de carpetas de forma nativa.
# Puedes usar rutas relativas ("./videos") o absolutas ("/Users/usuario/Videos")
ruta_carpeta = Path("/Users/barreto/Positron_Projects/py_RLG/_lexrlg") 

# Lista de extensiones válidas a detectar (en minúsculas)
extensiones_video = [".mp4"]

# 3. EXTRAER Y ORDENAR NOMBRES DE ARCHIVOS
# Usamos una comprensión de listas:
# - .iterdir() recorre todos los elementos dentro de la carpeta.
# - .is_file() asegura que sea un archivo y no una subcarpeta.
# - .suffix.lower() obtiene la extensión del archivo para comparar.
# - .name extrae solo el nombre del archivo con su extensión (ej: "video_01.mp4").
#   (Si solo quisieras el nombre sin extensión, usarías archivo.stem).

lista_videos = [
    archivo.name 
    for archivo in ruta_carpeta.iterdir()
    if archivo.is_file() and archivo.suffix.lower() in extensiones_video
]

# Es buena práctica ordenar la lista para mantener un criterio alfabético/numérico
lista_videos.sort()

# 4. VALIDACIÓN DE LONGITUD (Paso crítico)
# Para asignar una lista directa como nueva columna, la cantidad de archivos
# encontrados DEBE coincidir exactamente con el número de filas del DataFrame.
print(f"Filas en el DataFrame: {len(df)}")
print(f"Archivos de video encontrados: {len(lista_videos)}")

if len(lista_videos) == len(df):
    # 5. ASIGNACIÓN DE LA NUEVA COLUMNA
    df['nombre_video'] = lista_videos
    print("\n✅ Columna 'nombre_video' agregada exitosamente.")
    
    # Muestra de las primeras filas con la nueva columna
    print(df[['nombre_video']].head())
    
    # 6. EXPORTAR EL RESULTADO
    # Guardamos los cambios en un nuevo archivo para conservar el original
    df.to_csv("_datarlg_090926.csv", index=False)
    
else:
    print("\n⚠️ ALERTA: La cantidad de videos no coincide con el número de filas del DataFrame.")
    print("Revisa si faltan videos en la carpeta o si existen filas de más en la tabla antes de asignar.")

# voy a eliminar manualmente las columnas repetidas
df.iloc[0]

df = df.drop(columns=[" Composición", "Secuencia.1"])
df.iloc[0]




# ________________________________________________________________________________________________
# ________________________________________________________________________________________________

# PONER NOMBRES DE VARIABLES EN MINUSCULAS Y RELENAR NAs
# ________________________________________________________________________________________________
# ________________________________________________________________________________________________

import pandas as pd
import unicodedata
import re

# 1. CARGA DEL DATAFRAME
df = pd.read_csv("_datarlg_090926.csv")

# 2. FUNCIÓN PARA CONVERTIR TEXTO A SNAKE_CASE
def limpiar_encabezado(texto):
    """
    Transforma cadenas a snake_case:
    - Remueve tildes y acentos (ej. 'Composición' -> 'Composicion')
    - Reemplaza espacios, puntos o caracteres especiales por guiones bajos
    - Convierte todo a minúsculas
    """
    # Eliminar acentos mediante normalización Unicode
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    
    # Reemplazar puntos (como los que crea Pandas en 'Secuencia.1') o caracteres especiales por '_'
    texto = re.sub(r'[^\w\s]', '_', texto)
    
    # Reemplazar espacios o guiones repetidos por un solo '_'
    texto = re.sub(r'[\s_]+', '_', texto)
    
    # Llevar a minúsculas y quitar guiones al inicio/final si existen
    return texto.lower().strip('_')


# 3. MANEJO PREVIO DE COLUMNAS DUPLICADAS
# Si la segunda columna 'Composición' o 'Secuencia.1' tienen información distinta,
# las renombramos explícitamente antes del filtrado general para no perder contexto.
df = df.rename(columns={
    'Composición': 'composicion_principal',
    'Secuencia': 'secuencia_1',
    'Secuencia.1': 'secuencia_2'
})

# 4. APLICAR SNAKE_CASE A TODAS LAS COLUMNAS
# Usamos una comprensión de listas para iterar sobre df.columns
df.columns = [limpiar_encabezado(col) for col in df.columns]

# 5. TRATAMIENTO DE VALORES FALTANTES (NaN)
# En lingüística de LSC, las señas unimanuales o de un solo movimiento dejan CM2 a CM5 vacías.
# En lugar de dejar 'NaN', imputamos un valor explícito como 'N/A' o vacíos limpios ''.
columnas_cm = [col for col in df.columns if col.startswith('cm')]

# .fillna() reemplaza únicamente los nulos en las columnas seleccionadas
df[columnas_cm] = df[columnas_cm].fillna('N/A')

# Si deseas limpiar espacios en blanco sobrantes en las columnas de texto (glosa, definicion, etc.):
columnas_texto = df.select_dtypes(include=['object']).columns
for col in columnas_texto:
    # .str.strip() remueve espacios accidentales al inicio o final de las cadenas
    df[col] = df[col].astype(str).str.strip()

# 6. VERIFICACIÓN DE RESULTADOS
print("=== NUEVOS ENCABEZADOS (SNAKE_CASE) ===")
print(df.columns.tolist())

print("\n=== VERIFICACIÓN DE NULOS EN CONFIGURACIONES MANUALES ===")
print(df[columnas_cm].head())

# 7. EXPORTAR EL ARCHIVO LIMPIO Y NORMALIZADO
df.to_csv("_datarlg_normalizado.csv", index=False)
print("\n✅ Archivo normalizado guardado exitosamente como '_datarlg_normalizado.csv'.")


# ________________________________________________________________________________________________
# ________________________________________________________________________________________________

# VERIFICAR QUE HAY CONSISTENCIA EN DATOS DE CIERTAS CATEGORIAS PRINCIPALES
# ________________________________________________________________________________________________
# ________________________________________________________________________________________________

# 1. VERIFICAR EL NUEVO ESQUEMA Y TIPOS DE DATOS
# Confirma que todos los encabezados estén en snake_case y sin duplicados
print("=== COLUMNAS NORMALIZADAS ===")
print(df.columns.tolist())

# 2. INSPECCIÓN DE CATEGORÍAS (Detección de errores de tipeo)
# Revisa los valores únicos en variables lingüísticas clave para detectar variaciones
# como 'SUSTANTIVO', 'Sustantivo', 'SUSTANTIVOO' o espacios invisibles.
columnas_clave = ['clase_gramatical', 'tipo_de_sena', 'composicion_principal']

for col in columnas_clave:
    if col in df.columns:
        print(f"\n--- Distribución en '{col}' ---")
        print(df[col].value_counts(dropna=False))

# 3. VERIFICAR QUE NO QUEDEN NULOS INESPERADOS
# Asegura que solo queden nulos en columnas donde realmente se justifique
print("\n=== REVISIÓN FINAL DE NULOS ===")
nulos_restantes = df.isnull().sum()
print(nulos_restantes[nulos_restantes > 0])

# 4. VALIDACIÓN DE LA COLUMNA DE VIDEOS
# Inspecciona los primeros y últimos registros de la relación glosa <-> archivo
print("\n=== PRIMERAS Y ÚLTIMAS FILAS (GLOSA VS VIDEO) ===")
print(df[['glosa', 'nombre_video']].head(3))
print(df[['glosa', 'nombre_video']].tail(3))

# ________________________________________________________________________________________________
# ________________________________________________________________________________________________

# CAMBIAR VALORES NULOS POR TEXTO
# ________________________________________________________________________________________________
# ________________________________________________________________________________________________


import pandas as pd

# 1. CARGA DEL DATAFRAME
df = pd.read_csv("_datarlg_100926.csv")

# 1. Lista de columnas a corregir
# columnas_objetivo = ['glosa', 'definicion', 'clase_gramatical', 'tipo_de_sena']
columnas_objetivo = ['version', 'definicion_especial', 'composicion_principal', 'secuencia_1', 'cm1', 'cm2', 'cm3', 'cm4', 'cm5', 'glosa', 'definicion', 'clase_gramatical', 'tipo_de_sena']

# 2. Imputación de valores faltantes (NaN) por 'Sin especificar'
df[columnas_objetivo] = df[columnas_objetivo].fillna('Sin especificar')

# 3. Verificación de la imputación
print("=== VALORES NULOS RESTANTES EN COLUMNAS SELECCIONADAS ===")
print(df[columnas_objetivo].isnull().sum())

# 4. Exportar la versión lista para la aplicación/diccionario
df.to_csv("_datarlg_app.csv", index=False)
df.to_csv("_datarlg_100926.csv", index=False)

print("\n✅ Dataset exportado como '_datarlg_listo_app.csv'")
print(df.describe(include='all'))


# ________________________________________________________________________________________________
# ________________________________________________________________________________________________

# 
# ________________________________________________________________________________________________
# ________________________________________________________________________________________________

import pandas as pd

# 1. CARGA DEL DATAFRAME
df = pd.read_csv("_datarlg_100926.csv")

print(df.describe(include='all'))

print("\n=== VALORES NULOS POR COLUMNA ===")
conteo_nulos = df.isnull().sum()
# Filtramos para mostrar solo las columnas que tienen al menos un valor faltante
print(conteo_nulos[conteo_nulos > 0])
df.iloc[0]


# ________________________________________________________________________________________________
# ________________________________________________________________________________________________

# RENOMBRADO DE ARCHIVOS DE IMAGEN BASADO EN UN EXCEL DE COTEJO DE DOS NOMBRES
# ________________________________________________________________________________________________
# ________________________________________________________________________________________________



from pathlib import Path
import pandas as pd

# ==========================================
# CONFIGURACIÓN DE RUTAS Y MODO
# ==========================================
EXCEL_PATH = Path("/Users/barreto/Positron_Projects/py_RLG/editable_cm.xlsx")
ASSETS_DIR = Path("/Users/barreto/Positron_Projects/py_RLG/assets/manos")

# True: Simula la operación y muestra el reporte en consola sin modificar el disco.
# False: Aplica el renombrado real de los archivos.
DRY_RUN = False

# ==========================================
# PROCESAMIENTO Y VALIDACIÓN
# ==========================================
def renombrar_archivos():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo Excel en: {EXCEL_PATH}")

    if not ASSETS_DIR.exists():
        raise FileNotFoundError(
            f"No se encontró la carpeta de imágenes en: {ASSETS_DIR}"
        )

    # Leer Excel y limpiar espacios en blanco
    df = pd.read_excel(EXCEL_PATH)
    df["id_insor"] = df["id_insor"].astype(str).str.strip()
    df["codigo_simplificado"] = (
        df["codigo_simplificado"].astype(str).str.strip()
    )

    # Crear mapa de equivalencias
    mapping = dict(zip(df["id_insor"], df["codigo_simplificado"]))

    # Indexar archivos existentes por su nombre base (sin extensión)
    archivos_disco = {
        f.stem: f for f in ASSETS_DIR.iterdir() if f.is_file() and not f.name.startswith(".")
    }

    procesados = 0
    no_encontrados = 0
    colisiones = 0

    print(
        f"=== MODO: {'SIMULACIÓN (DRY-RUN)' if DRY_RUN else 'EJECUCIÓN REAL'} ===\n"
    )

    for id_insor, cod_nuevo in mapping.items():
        if id_insor in archivos_disco:
            archivo_origen = archivos_disco[id_insor]
            extension = archivo_origen.suffix  # Mantiene .png, .jpg, etc.
            archivo_destino = ASSETS_DIR / f"{cod_nuevo}{extension}"

            # Verificar si el archivo de destino ya existe para evitar sobrescrituras accidentales
            if archivo_destino.exists() and archivo_destino != archivo_origen:
                print(
                    f"[ALERTA COLISIÓN] {archivo_destino.name} ya existe en disco. Omitiendo..."
                )
                colisiones += 1
                continue

            if DRY_RUN:
                print(
                    f"[SIMULACIÓN] {archivo_origen.name}  --->  {archivo_destino.name}"
                )
            else:
                archivo_origen.rename(archivo_destino)
                print(
                    f"[RENOMBRADO] {archivo_origen.name}  --->  {archivo_destino.name}"
                )

            procesados += 1
        else:
            print(
                f"[NO ENCONTRADO] ID '{id_insor}' no coincide con ningún archivo en la carpeta."
            )
            no_encontrados += 1

    print("\n" + "=" * 40)
    print("RESUMEN DE OPERACIÓN")
    print("=" * 40)
    print(f"Total registros en Excel: {len(mapping)}")
    print(f"Archivos listos para renombrar: {procesados}")
    print(f"Archivos no encontrados en disco: {no_encontrados}")
    print(f"Conflictos/Colisiones omitidas: {colisiones}")

    if DRY_RUN:
        print(
            "\n* Nota: Ningún archivo fue modificado. Si el reporte es correcto, cambia `DRY_RUN = False` y vuelve a ejecutar. *"
        )


if __name__ == "__main__":
    renombrar_archivos()



# ________________________________________________________________________________________________
# ________________________________________________________________________________________________

# RENOMBRADO DE ARCHIVOS DE IMAGEN de MAYUSCULAS A MINUSCULAS, HACIENDOLO POR PASOS PARA NO GENERAR ERROR
# ________________________________________________________________________________________________
# ________________________________________________________________________________________________




from pathlib import Path

# Ruta a la carpeta de las manos
PATH_MANOS = Path("/Users/barreto/Positron_Projects/py_RLG/assets/manos")

if PATH_MANOS.exists():
    archivos = list(PATH_MANOS.glob("*.png"))
    
    for archivo in archivos:
        nombre_original = archivo.name
        nombre_minuscula = nombre_original.lower()
        
        # Solo procesamos si el nombre contiene alguna mayúscula
        if nombre_original != nombre_minuscula:
            # Paso 1: Nombre temporal para evitar el conflicto de case-insensitivity en macOS
            temp_path = archivo.with_name(f"temp_{nombre_original}")
            archivo.rename(temp_path)
            
            # Paso 2: Nombre final completamente en minúsculas
            final_path = archivo.with_name(nombre_minuscula)
            temp_path.rename(final_path)
            
            print(f"Renombrado: {nombre_original} -> {nombre_minuscula}")
            
    print("✨ Proceso de renombrado completado.")
else:
    print(f"No se encontró la ruta: {PATH_MANOS}")