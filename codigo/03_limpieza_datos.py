# Nombre: Andrea Nicolle Sinche De La Cruz
# Código de matrícula: 2024200529I
# Tema 40: Bonos nominales frente a bonos indexados (VAC): expectativas de inflación implícitas
# Fecha de extracción: 28/09/2026

"""
03_limpieza_datos.py
Toma datos_crudos_2024200529I.csv (generado por 01_extraccion_api.py) y:
  1. convierte el periodo del BCRP (por ejemplo "Ene.2010") a una fecha (2010-01-01)
  2. convierte los valores de texto a números
  3. revisa datos faltantes y valores atípicos (outliers)
  4. calcula la tasa real ex ante (ecuación de Fisher): rend_bono10a - expect_infl_12m
  5. guarda datos_procesados_2024200529I.csv y muestra su hash SHA-256
El archivo crudo NO se modifica.
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

CODIGO_MATRICULA = "2024200529I"
VARIABLES = ["rend_bono10a", "expect_infl_12m", "inflacion_12m", "tasa_referencia"]

# ------------- RUTAS RELATIVAS A LA CARPETA DEL PROYECTO -------------
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
ARCHIVO_CRUDO = CARPETA_PROYECTO / "datos_crudos" / f"datos_crudos_{CODIGO_MATRICULA}.csv"
CARPETA_PROCESADOS = CARPETA_PROYECTO / "datos_procesados"
ARCHIVO_PROCESADO = CARPETA_PROCESADOS / f"datos_procesados_{CODIGO_MATRICULA}.csv"
ARCHIVO_LOG = CARPETA_PROYECTO / "log_ejecucion.txt"
CARPETA_PROCESADOS.mkdir(exist_ok=True)

# Meses tal como los escribe el BCRP (incluye "Set" y "Sep" para setiembre)
MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7,
         "ago": 8, "set": 9, "sep": 9, "oct": 10, "nov": 11, "dic": 12}


def escribir_log(mensaje):
    """Muestra el mensaje en pantalla y lo agrega, con fecha y hora, a log_ejecucion.txt."""
    linea = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | " + mensaje
    print(linea)
    with open(ARCHIVO_LOG, "a", encoding="utf-8") as log:
        log.write(linea + "\n")


def periodo_a_fecha(texto):
    """Convierte un periodo del BCRP como 'Ene.2010' en la fecha 2010-01-01."""
    partes = re.match(r"([A-Za-z]+)\W*(\d{4})", str(texto).strip())
    mes = MESES[partes.group(1)[:3].lower()]
    anio = int(partes.group(2))
    return pd.Timestamp(year=anio, month=mes, day=1)


escribir_log("INICIO de limpieza")

# 1) Leer el archivo crudo (todo como texto, tal como vino de la API)
datos = pd.read_csv(ARCHIVO_CRUDO, dtype=str)
escribir_log(f"Archivo crudo leído: {len(datos)} filas y {len(datos.columns)} columnas")

# 2) Convertir el periodo a fecha y ordenar de la más antigua a la más reciente
datos["fecha"] = datos["periodo"].apply(periodo_a_fecha)
datos = datos.drop(columns=["periodo"]).sort_values("fecha").reset_index(drop=True)

# 3) Convertir los valores a números ("n.d." u otro texto se vuelve vacío = NaN)
for variable in VARIABLES:
    datos[variable] = pd.to_numeric(datos[variable], errors="coerce")

# 4) Revisar faltantes: si hubiera, se registran y se eliminan esos meses
faltantes = datos[VARIABLES].isna().sum()
escribir_log("Faltantes por variable: " + ", ".join(f"{v}={faltantes[v]}" for v in VARIABLES))
filas_antes = len(datos)
datos = datos.dropna(subset=VARIABLES).reset_index(drop=True)
escribir_log(f"Meses eliminados por faltantes: {filas_antes - len(datos)}")

# 5) Revisar outliers con el criterio del rango intercuartílico (IQR).
#    Solo se reportan y NO se eliminan: son datos oficiales reales
#    (por ejemplo, la inflación alta de 2022 es un hecho económico, no un error).
for variable in VARIABLES:
    q1, q3 = datos[variable].quantile([0.25, 0.75])
    iqr = q3 - q1
    atipicos = ((datos[variable] < q1 - 1.5 * iqr) | (datos[variable] > q3 + 1.5 * iqr)).sum()
    escribir_log(f"Outliers (IQR) en {variable}: {atipicos} (se conservan)")

# 6) Variable calculada: tasa real ex ante (ecuación de Fisher)
datos["tasa_real_exante"] = (datos["rend_bono10a"] - datos["expect_infl_12m"]).round(4)

# 7) Ordenar columnas y guardar el archivo procesado
columnas = ["fecha"] + VARIABLES + ["tasa_real_exante"]
datos = datos[columnas].copy()
datos["fecha"] = datos["fecha"].dt.strftime("%Y-%m-%d")
datos.to_csv(ARCHIVO_PROCESADO, index=False, encoding="utf-8")
escribir_log(f"Guardado {ARCHIVO_PROCESADO.name}: {len(datos)} filas y {len(columnas)} columnas")

# 8) Hash SHA-256 del archivo procesado (se copia al README)
sha256 = hashlib.sha256(ARCHIVO_PROCESADO.read_bytes()).hexdigest()
escribir_log(f"SHA-256 de {ARCHIVO_PROCESADO.name}: {sha256}")

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 10)
print("\nPrimeras 5 filas:")
print(datos.head())
print("\nÚltimas 5 filas:")
print(datos.tail())
