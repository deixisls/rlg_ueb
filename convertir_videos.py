# -*- coding: utf-8 -*-
"""
Script de conversión y optimización masiva de video para Lengua de Señas Colombiana (LSC).
Diseñado para Mac Studio M1 Max (aceleración h264_videotoolbox).

Características:
- Escalado relativo al 50% garantizando dimensiones pares.
- Remoción de audio (-an).
- Compresión de tasa de bits (~800 kbps) y optimización web (-movflags +faststart).
- Réplica exacta de la estructura de carpetas de entrada (_lexrlg -> _lexrlg_low).
- Procesamiento multihilo paralelo.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# --- CONFIGURACIÓN ---
DIR_ENTRADA = Path("_lexrlg")
DIR_SALIDA = Path("_lexrlg_low")
BITRATE_OBJETIVO = "800k"
EXTENSIONES_VIDEO = {".mp4", ".mov", ".m4v", ".avi", ".mkv"}
MAX_WORKERS = 8  # Número de procesos concurrentes óptimo para M1 Max

# Códec acelerado por hardware para macOS Apple Silicon
CODEC_HW = "h264_videotoolbox"
CODEC_CPU = "libx264"


def verificar_ffmpeg():
    """Verifica si FFmpeg está instalado en el sistema."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def procesar_video(args):
    """
    Procesa un solo video aplicando escalado al 50%, remoción de audio y compresión.
    """
    archivo_in, archivo_out, usar_hw = args

    # Crear directorio padre si no existe
    archivo_out.parent.mkdir(parents=True, exist_ok=True)

    codec = CODEC_HW if usar_hw else CODEC_CPU

    # Filtro FFmpeg: escala al 50% de ancho/alto asegurando que las dimensiones sean pares
    vf_filter = "scale=trunc(iw/4)*2:trunc(ih/4)*2"

    comando = [
        "ffmpeg",
        "-y",                       # Sobrescribir archivo de salida si existe
        "-i", str(archivo_in),        # Archivo de entrada
        "-vf", vf_filter,           # Filtro de reescalado 50%
        "-c:v", codec,               # Códec de video (VideoToolbox o x264)
        "-b:v", BITRATE_OBJETIVO,    # Tasa de bits de video
        "-an",                      # Sin audio
        "-movflags", "+faststart",  # Optimización para streaming web (moov atom al inicio)
        "-loglevel", "error",       # Solo mostrar errores
        str(archivo_out)            # Archivo de salida
    ]

    try:
        resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if resultado.returncode == 0:
            return True, str(archivo_in), None
        else:
            return False, str(archivo_in), resultado.stderr.strip()
    except Exception as e:
        return False, str(archivo_in), str(e)


def main():
    print("=" * 70)
    print("  OPTIMIZADOR MASIVO DE VIDEOS LSC - UNIVERSIDAD EL BOSQUE")
    print("=" * 70)

    # 1. Validar FFmpeg
    if not verificar_ffmpeg():
        print("[ERROR] FFmpeg no está instalado o no se encuentra en el PATH.")
        print("Instálalo en tu Mac usando Homebrew ejecutando en la Terminal:")
        print("    brew install ffmpeg")
        sys.exit(1)

    # 2. Verificar carpeta de entrada
    if not DIR_ENTRADA.exists() or not DIR_ENTRADA.is_dir():
        print(f"[ERROR] La carpeta de entrada '{DIR_ENTRADA}' no existe.")
        print("Por favor ejecuta este script en la misma carpeta que contiene '_lexrlg'.")
        sys.exit(1)

    # 3. Mapear todos los videos a procesar
    todos_los_archivos = [p for p in DIR_ENTRADA.rglob("*") if p.suffix.lower() in EXTENSIONES_VIDEO]
    total_videos = len(todos_los_archivos)

    if total_videos == 0:
        print(f"[ADVERTENCIA] No se encontraron archivos de video en '{DIR_ENTRADA}'.")
        sys.exit(0)

    print(f"[INFO] Carpeta de origen: {DIR_ENTRADA.resolve()}")
    print(f"[INFO] Carpeta de destino: {DIR_SALIDA.resolve()}")
    print(f"[INFO] Videos detectados: {total_videos}")
    print(f"[INFO] Hilos de procesamiento: {MAX_WORKERS} (Apple Silicon M1 Max)")
    print("-" * 70)

    # 4. Preparar tareas
    tareas = []
    for archivo_in in todos_los_archivos:
        # Mantener la estructura de subdirectorios
        rel_path = archivo_in.relative_to(DIR_ENTRADA)
        archivo_out = DIR_SALIDA / rel_path
        tareas.append((archivo_in, archivo_out, True))

    # 5. Ejecutar procesamiento
    tiempo_inicio = time.time()
    exitosos = 0
    fallidos = []

    print("[PROCESANDO] Iniciando conversión de archivos...\n")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(procesar_video, t): t for t in tareas}

        if HAS_TQDM:
            pbar = tqdm(total=total_videos, desc="Progreso", unit="vid", ncols=80)
            for future in as_completed(futures):
                exito, ruta, err = future.result()
                if exito:
                    exitosos += 1
                else:
                    fallidos.append((ruta, err))
                pbar.update(1)
            pbar.close()
        else:
            completados = 0
            for future in as_completed(futures):
                completados += 1
                exito, ruta, err = future.result()
                if exito:
                    exitosos += 1
                else:
                    fallidos.append((ruta, err))
                print(f"Completado {completados}/{total_videos} ({completados/total_videos*100:.1f}%)", end="\r")
            print()

    tiempo_total = time.time() - tiempo_inicio

    # 6. Reporte Final
    print("\n" + "=" * 70)
    print("  RESUMEN DEL PROCESAMIENTO")
    print("=" * 70)
    print(f"• Total de videos procesados : {total_videos}")
    print(f"• Exitosos                    : {exitosos}")
    print(f"• Errores                     : {len(fallidos)}")
    print(f"• Tiempo total transcurrido   : {tiempo_total:.2f} segundos ({tiempo_total/60:.2f} minutos)")

    if fallidos:
        print("\n[ALERT] Los siguientes archivos presentaron un error:")
        for ruta, err in fallidos:
            print(f"  - {ruta}: {err}")

    print("\n[OK] ¡Proceso finalizado con éxito! Los videos comprimidos están en '_lexrlg_low'.")


if __name__ == "__main__":
    main()
