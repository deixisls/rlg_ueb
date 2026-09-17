from pathlib import Path
import pandas as pd

# Define el directorio y el nombre del archivo
directorio = Path("/Users/barreto/Positron_Projects/py_RLG")
archivo_excel = directorio / "editable_datarlg_180926.xlsx"
archivo_csv = directorio / "_datarlg_190926.csv"

# Leer Excel y exportar a CSV (encoding 'utf-8-sig' preserva tildes y caracteres especiales)
df = pd.read_excel(archivo_excel, sheet_name=0)  # Lee la primera hoja
df.to_csv(archivo_csv, index=False, encoding="utf-8-sig")

print(f"Archivo guardado exitosamente en: {archivo_csv}")

df.columns
