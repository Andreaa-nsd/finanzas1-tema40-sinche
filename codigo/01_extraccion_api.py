# Nombre: Andrea Nicolle Sinche De La Cruz
# Código de matrícula: 2024200529I
# Tema 40: Bonos nominales frente a bonos indexados (VAC): expectativas de inflación implícitas
# Fecha de extracción: 28/09/2026

"""
01_extraccion_api.py
Descarga 4 series mensuales desde la API de BCRPData y guarda:
  - la respuesta original (JSON) de cada serie en /datos_crudos (sin editar)
  - datos_crudos_2024200529I.csv con los valores tal como los entrega la API
  - una línea por consulta en log_ejecucion.txt (fecha, hora, código HTTP y filas)
"""

import csv
import json
import ssl
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# ------------- PARÁMETROS CONGELADOS (si se cambian, actualizar el README) -------------
FECHA_INICIO = "2010-1"   # enero de 2010
FECHA_CORTE = "2026-8"    # agosto de 2026: último mes publicado para las 4 series al 28/09/2026
CODIGO_MATRICULA = "2024200529I"

# Variables del estudio: nombre de la variable -> código de la serie en BCRPData
SERIES = {
    "rend_bono10a": "PD31895MM",     # Rendimiento del bono del gobierno peruano a 10 años (S/), en %
    "expect_infl_12m": "PD12912AM",  # Expectativa de inflación a 12 meses (encuesta BCRP), en %
    "inflacion_12m": "PN01273PM",    # IPC Lima Metropolitana, variación % 12 meses
    "tasa_referencia": "PD04722MM",  # Tasa de referencia de la política monetaria, en %
}

# Endpoint de la API de BCRPData: /api/{código}/json/{inicio}/{fin}/esp
ENDPOINT = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{codigo}/json/{inicio}/{fin}/esp"
USER_AGENT = "Mozilla/5.0 (Tarea academica UNCP Finanzas I - Andrea Sinche, cod. 2024200529I)"
PAUSA_SEGUNDOS = 1.5  # pausa entre solicitudes (la consigna exige mínimo 1 segundo)

# ------------- RUTAS RELATIVAS A LA CARPETA DEL PROYECTO -------------
# El script está en /codigo, así que la carpeta del proyecto es la carpeta "padre".
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_CRUDOS = CARPETA_PROYECTO / "datos_crudos"
ARCHIVO_LOG = CARPETA_PROYECTO / "log_ejecucion.txt"
CARPETA_CRUDOS.mkdir(exist_ok=True)

# En la red de la estudiante, un intermediario (antivirus o red WiFi) reemplaza el
# certificado de seguridad del portal y Python rechaza la conexión. Como los datos son
# públicos y solo se leen, se desactiva la verificación del certificado (ver README).
CONTEXTO_SSL = ssl._create_unverified_context()


def escribir_log(mensaje):
    """Muestra el mensaje en pantalla y lo agrega, con fecha y hora, a log_ejecucion.txt."""
    linea = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | " + mensaje
    print(linea)
    with open(ARCHIVO_LOG, "a", encoding="utf-8") as log:
        log.write(linea + "\n")


def descargar_serie(codigo):
    """Consulta la API para un código de serie y devuelve (código HTTP, texto de la respuesta)."""
    url = ENDPOINT.format(codigo=codigo, inicio=FECHA_INICIO, fin=FECHA_CORTE)
    pedido = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(pedido, timeout=60, context=CONTEXTO_SSL) as respuesta:
        return respuesta.status, respuesta.read().decode("utf-8-sig")


# ------------- PROGRAMA PRINCIPAL -------------
escribir_log(f"INICIO de extracción | periodo {FECHA_INICIO} a {FECHA_CORTE}")

tabla = {}            # periodo -> {variable: valor}
orden_periodos = []   # para guardar los meses en el mismo orden en que llegan

for variable, codigo in SERIES.items():
    try:
        estado, texto = descargar_serie(codigo)
        datos = json.loads(texto)

        # 1) Guardar la respuesta original sin editar (evidencia primaria)
        archivo_json = CARPETA_CRUDOS / f"respuesta_{codigo}_{CODIGO_MATRICULA}.json"
        archivo_json.write_text(texto, encoding="utf-8")

        # 2) Pasar los valores a la tabla, tal como vienen de la API (como texto)
        for periodo in datos["periods"]:
            nombre_periodo = periodo["name"]
            if nombre_periodo not in tabla:
                tabla[nombre_periodo] = {}
                orden_periodos.append(nombre_periodo)
            tabla[nombre_periodo][variable] = periodo["values"][0]

        escribir_log(f"{codigo} ({variable}) | HTTP {estado} | {len(datos['periods'])} filas")

    except Exception as error:
        escribir_log(f"{codigo} ({variable}) | ERROR: {error}")

    time.sleep(PAUSA_SEGUNDOS)

# 3) Guardar el CSV crudo (una fila por mes, una columna por variable)
archivo_csv = CARPETA_CRUDOS / f"datos_crudos_{CODIGO_MATRICULA}.csv"
with open(archivo_csv, "w", newline="", encoding="utf-8") as salida:
    escritor = csv.writer(salida)
    escritor.writerow(["periodo"] + list(SERIES.keys()))
    for periodo in orden_periodos:
        fila = [periodo] + [tabla[periodo].get(v, "") for v in SERIES.keys()]
        escritor.writerow(fila)

escribir_log(f"FIN | {len(orden_periodos)} periodos guardados en {archivo_csv.name}")
