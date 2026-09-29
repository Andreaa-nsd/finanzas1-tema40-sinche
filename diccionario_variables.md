# Diccionario de variables

Archivo: `datos_procesados/datos_procesados_2024200529I.csv` — 200 filas (enero 2010 – agosto 2026); 4 variables descargadas × 200 = 800 observaciones, 6 columnas.
Autora: Andrea Nicolle Sinche De La Cruz (2024200529I) — Tema 40.

Endpoint de todas las series descargadas:
`https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{código}/json/2010-1/2026-8/esp`

| Variable | Definición | Unidad de medida | Frecuencia | Fuente exacta | Código / endpoint |
|---|---|---|---|---|---|
| `fecha` | Primer día del mes al que corresponde el dato | AAAA-MM-DD | Mensual | Construida a partir del periodo que entrega BCRPData (p. ej., "Ene.2010") | — |
| `rend_bono10a` | Rendimiento del bono del gobierno peruano a 10 años en soles (variable endógena) | Porcentaje anual (%) | Mensual | BCRP, BCRPData — Tasas de interés de bonos del gobierno peruano (fuente original: MEF) | PD31895MM |
| `expect_infl_12m` | Expectativa de inflación a 12 meses según la Encuesta de Expectativas Macroeconómicas | Porcentaje (%) | Mensual | BCRP, BCRPData — Expectativas macroeconómicas | PD12912AM |
| `inflacion_12m` | Variación porcentual del IPC de Lima Metropolitana respecto del mismo mes del año anterior | Porcentaje (%) | Mensual | BCRP, BCRPData — Índice de precios Lima Metropolitana | PN01273PM |
| `tasa_referencia` | Tasa de interés de referencia de la política monetaria del BCRP | Porcentaje anual (%) | Mensual | BCRP, BCRPData — Tasas de interés del Banco Central de Reserva | PD04722MM |
| `tasa_real_exante` | Tasa real ex ante por la ecuación de Fisher: `rend_bono10a − expect_infl_12m` | Puntos porcentuales | Mensual | Calculada en `03_limpieza_datos.py` | — |

Fecha de consulta: 28/09/2026.
