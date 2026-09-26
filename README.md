# Base de datos y código — Tema 40

**Autora:** Andrea Nicolle Sinche De La Cruz
**Código de matrícula:** 2024200529I
**Curso:** Finanzas I (055D) — Escuela Profesional de Economía, UNCP — 2026-II — Unidad I
**Docente:** Dr. Ciro Iván Machacuay Meza

**Tema 40:** Bonos nominales frente a bonos indexados (VAC): expectativas de inflación implícitas.

**Objetivo empírico:** medir cuánto de la inflación esperada se incorpora en el rendimiento de los bonos soberanos nominales en soles (efecto Fisher), Perú, enero 2010 – julio 2026.

---

## 1. Fuente y vía de extracción

Vía API (única vía exigida en la Unidad I): **BCRPData — API para desarrolladores** del Banco Central de Reserva del Perú.

Endpoint: `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{código}/json/{inicio}/{fin}/esp`

| Variable | Código BCRP | Serie |
|---|---|---|
| `rend_bono10a` | PD31895MM | Rendimiento del bono del gobierno peruano a 10 años (en S/) |
| `expect_infl_12m` | PD12912AM | Expectativa de inflación a 12 meses |
| `inflacion_12m` | PN01273PM | Índice de precios Lima Metropolitana (var. % 12 meses) |
| `tasa_referencia` | PD04722MM | Tasa de referencia de la política monetaria |

El detalle de cada variable está en `diccionario_variables.md`.
Los bonos VAC no se usaron por falta de datos y por el bloqueo de la fuente alternativa: ver `incidencias_fuente.md`.

## 2. Parámetros congelados

- `FECHA_INICIO = "2010-1"` (enero de 2010)
- `FECHA_CORTE = "2026-7"` (julio de 2026)
- Fecha y hora de la extracción original: 24/09/2026, 01:33–01:34 (ver `log_ejecucion.txt`)
- Observaciones: **199 meses** por variable, sin datos faltantes.

## 3. Estructura de la carpeta

```
3_BaseDatos_Andrea_Sinche/
├── codigo/
│   ├── 01_extraccion_api.py
│   ├── 03_limpieza_datos.py
│   └── 04_analisis.py
├── datos_crudos/          (respuestas originales de la API, sin editar)
├── datos_procesados/      (datos_procesados_2024200529I.csv)
├── salidas/               (tablas y figuras del artículo)
├── diccionario_variables.md
├── incidencias_fuente.md
├── log_ejecucion.txt
├── requirements.txt
├── .env.example
└── README.md
```

El script `02_scraping_web.py` no se incluye: en la Unidad I la segunda vía es opcional.

## 4. Orden de ejecución

Desde la carpeta `3_BaseDatos_Andrea_Sinche`:

```
py -m pip install -r requirements.txt
py codigo/01_extraccion_api.py
py codigo/03_limpieza_datos.py
py codigo/04_analisis.py
```

1. `01_extraccion_api.py` descarga las 4 series y guarda los crudos y el log.
2. `03_limpieza_datos.py` convierte fechas y números, revisa faltantes y outliers, calcula la tasa real ex ante y guarda el archivo procesado con su hash.
3. `04_analisis.py` genera las tablas 1 a 7 y las figuras 1 a 3 en `/salidas`.

## 5. Entorno

- Lenguaje: **Python 3.14.1** (Windows, 64 bits)
- Librerías y versiones exactas: `requirements.txt`
- Todas las rutas son relativas a la carpeta del proyecto.

**Clave de API:** BCRPData no requiere clave. El archivo `.env.example` se incluye por exigencia de la consigna y no contiene variables obligatorias.

**Nota técnica (certificado SSL):** en la red de la autora, un intermediario (antivirus o red WiFi) reemplaza el certificado de seguridad del portal y Python rechaza la conexión. Como los datos son públicos y solo se leen, el script desactiva la verificación del certificado (`ssl._create_unverified_context()`). En otra red el script funciona igual.

## 6. Verificación de integridad

Hash SHA-256 de `datos_procesados/datos_procesados_2024200529I.csv` (entregado):

```
7c0f1afb6834ab09a0345ec2c1f7f4f91a6b0eb82eb47660f2a4b1e7db30a651
```

Este hash corresponde al archivo entregado. BCRPData puede revisar sus series después de la fecha de corte; si una reejecución produce otro hash, la fecha y hora de la extracción original constan en `log_ejecucion.txt`.

## 7. Uso de inteligencia artificial

Se utilizó un asistente de IA (Claude, de Anthropic) para escribir y depurar el código. La autora ejecutó cada script, revisó los resultados y puede explicar cada bloque del código.

## 8. Repositorio

GitHub: https://github.com/Andreaa-nsd/finanzas1-tema40-sinche
