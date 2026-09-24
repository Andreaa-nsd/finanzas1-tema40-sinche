# Registro de incidencias de fuente

Autora: Andrea Nicolle Sinche De La Cruz (2024200529I) — Tema 40 — Unidad I
Fecha de las pruebas: 24/09/2026

## Incidencia 1: serie VAC de BCRPData sin datos suficientes

- **Serie:** PN01116MM — Tasas de interés, bonos en S/ indexados al VAC (bonos del sector privado)
- **URL:** `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01116MM/json/2010-1/2026-7/esp`
- **Respuesta:** HTTP 200
- **Hallazgo:** de 199 meses consultados (enero 2010 – julio 2026), solo **8** tienen un valor mayor que cero; los demás figuran como 0.0 o "n.d.", porque estos bonos casi no se negocian.
- BCRPData no publica una serie mensual de rendimientos de bonos **soberanos** VAC. Su grupo "Tasas de interés de bonos del gobierno peruano" contiene solo dos series: el bono a 10 años en soles nominales (PD31895MM) y en dólares (PD31896MM).

## Incidencia 2: Reporte Diario del MEF bloquea la descarga programática

- **Fuente:** MEF, *Perú: Reporte Diario / Daily Report* (PDF con rendimientos de bonos soberanos nominales y VAC)
- **URL probada:** `https://www.mef.gob.pe/contenidos/english/report/2025/Daily_12_12_25.pdf`
- **Respuesta:** HTTP 200, pero con tipo `text/html` y 212 bytes en lugar del PDF
- **Mensaje del portal:** página de verificación anti-bots (Imperva *Incapsula*: script `/_Incapsula_Resource`, etiqueta `META NAME="robots" CONTENT="noindex,nofollow"`)
- **Evidencia:** captura de pantalla `captura_mef_incapsula.png`
- La consigna (numeral 2.4.8) prohíbe vulnerar accesos restringidos, por lo que **no se intentó evadir** la verificación.

## Decisión

El rendimiento de los bonos VAC no pudo obtenerse de forma programática y verificable. Por ello, el estudio se reformuló con variables disponibles íntegramente en la API de BCRPData: el rendimiento del bono soberano nominal a 10 años (variable endógena), la expectativa de inflación a 12 meses, la inflación observada y la tasa de referencia. La inflación esperada implícita se analiza mediante la ecuación de Fisher sobre el bono nominal.

La vía exigida en la Unidad I (al menos una API) se cumple con BCRPData. Esta incidencia explica el cambio de variables y no reemplaza ninguna vía.
