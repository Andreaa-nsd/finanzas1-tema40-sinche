# Nombre: Andrea Nicolle Sinche De La Cruz
# Código de matrícula: 2024200529I
# Tema 40: Bonos nominales frente a bonos indexados (VAC): expectativas de inflación implícitas
# Fecha de extracción: 28/09/2026

"""
04_analisis.py
Genera, a partir de datos_procesados_2024200529I.csv, todas las tablas y figuras del artículo
y las guarda en /salidas:
  Tabla 1: estadísticos descriptivos
  Tabla 2: matriz de correlaciones
  Tabla 3: prueba de raíz unitaria (Dickey-Fuller aumentada)
  Tabla 4: regresión MCO con errores robustos Newey-West (HAC)
  Tabla 5: prueba de Fisher (H0: coeficiente de las expectativas = 1)
  Tabla 6: prueba de cointegración de Engle-Granger
  Tabla 7: regresión en primeras diferencias (variables estacionarias) + prueba de Fisher
  Figura 1: evolución de las 4 variables
  Figura 2: rendimiento del bono vs expectativa de inflación
  Figura 3: tasa real ex ante
Modelo:  rend_bono10a = b0 + b1*expect_infl_12m + b2*inflacion_12m + b3*tasa_referencia + e
"""

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # guarda los gráficos como imagen sin abrir ventanas
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson, jarque_bera
from statsmodels.tsa.stattools import adfuller, coint

# Oculta avisos de versiones futuras de las librerías (no afectan los resultados)
warnings.filterwarnings("ignore", category=FutureWarning)

CODIGO_MATRICULA = "2024200529I"
Y = "rend_bono10a"
X = ["expect_infl_12m", "inflacion_12m", "tasa_referencia"]
NOMBRES = {
    "rend_bono10a": "Rendimiento bono 10 años (%)",
    "expect_infl_12m": "Expectativa de inflación 12 meses (%)",
    "inflacion_12m": "Inflación IPC 12 meses (%)",
    "tasa_referencia": "Tasa de referencia BCRP (%)",
    "tasa_real_exante": "Tasa real ex ante (%)",
}
REZAGOS_NW = 12  # rezagos de Newey-West: 12 meses (datos mensuales)

# ------------- RUTAS RELATIVAS A LA CARPETA DEL PROYECTO -------------
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
ARCHIVO_PROCESADO = CARPETA_PROYECTO / "datos_procesados" / f"datos_procesados_{CODIGO_MATRICULA}.csv"
SALIDAS = CARPETA_PROYECTO / "salidas"
SALIDAS.mkdir(exist_ok=True)

# 1) Leer los datos procesados
datos = pd.read_csv(ARCHIVO_PROCESADO, parse_dates=["fecha"])
print(f"Datos leídos: {len(datos)} meses, de {datos['fecha'].min():%Y-%m} a {datos['fecha'].max():%Y-%m}")
todas = [Y] + X + ["tasa_real_exante"]

# 2) Tabla 1: estadísticos descriptivos
tabla1 = datos[todas].describe().T[["count", "mean", "std", "min", "max"]]
tabla1.columns = ["Observaciones", "Media", "Desv. estándar", "Mínimo", "Máximo"]
tabla1.index = [NOMBRES[v] for v in tabla1.index]
tabla1.round(3).to_csv(SALIDAS / "tabla1_descriptivos.csv", encoding="utf-8-sig")

# 3) Tabla 2: correlaciones entre las variables del modelo
tabla2 = datos[[Y] + X].corr().round(3)
tabla2.to_csv(SALIDAS / "tabla2_correlaciones.csv", encoding="utf-8-sig")

# 4) Tabla 3: prueba ADF (¿la serie es estacionaria?) en niveles y en primeras diferencias
filas = []
for v in [Y] + X:
    for version, serie in [("Nivel", datos[v]), ("Primera diferencia", datos[v].diff().dropna())]:
        estadistico, p_valor = adfuller(serie, autolag="AIC")[:2]
        filas.append([NOMBRES[v], version, round(estadistico, 3), round(p_valor, 4),
                      "Estacionaria" if p_valor < 0.05 else "No estacionaria"])
tabla3 = pd.DataFrame(filas, columns=["Variable", "Serie", "Estadístico ADF", "p-valor", "Conclusión (5%)"])
tabla3.to_csv(SALIDAS / "tabla3_adf.csv", index=False, encoding="utf-8-sig")

# 5) Tabla 4: regresión MCO con errores Newey-West (corrigen autocorrelación y heterocedasticidad)
modelo = sm.OLS(datos[Y], sm.add_constant(datos[X])).fit(cov_type="HAC", cov_kwds={"maxlags": REZAGOS_NW})
with open(SALIDAS / "tabla4_regresion.txt", "w", encoding="utf-8") as archivo:
    archivo.write(modelo.summary().as_text())

tabla4 = pd.DataFrame({
    "Coeficiente": modelo.params,
    "Error estándar (NW)": modelo.bse,
    "Estadístico z": modelo.tvalues,
    "p-valor": modelo.pvalues,
}).round(4)
matriz_x = sm.add_constant(datos[X]).values
tabla4["VIF"] = [None] + [round(variance_inflation_factor(matriz_x, i), 2) for i in range(1, matriz_x.shape[1])]
tabla4.to_csv(SALIDAS / "tabla4_regresion.csv", encoding="utf-8-sig")

# Indicadores de ajuste y diagnóstico del modelo
jb_estadistico, jb_p = jarque_bera(modelo.resid)[:2]
diagnostico = pd.DataFrame({
    "Indicador": ["Observaciones", "R cuadrado", "R cuadrado ajustado", "Durbin-Watson", "Jarque-Bera (p-valor)"],
    "Valor": [int(modelo.nobs), round(modelo.rsquared, 4), round(modelo.rsquared_adj, 4),
              round(durbin_watson(modelo.resid), 4), round(jb_p, 4)],
})
diagnostico.to_csv(SALIDAS / "tabla4b_diagnostico.csv", index=False, encoding="utf-8-sig")

# 6) Tabla 5: prueba de Fisher. Si b1 = 1, las expectativas pasan completas a la tasa del bono
prueba = modelo.t_test("expect_infl_12m = 1")
tabla5 = pd.DataFrame({
    "Hipótesis nula": ["b1 (expectativas) = 1"],
    "Coeficiente estimado": [round(modelo.params["expect_infl_12m"], 4)],
    "Estadístico": [round(np.asarray(prueba.tvalue).item(), 4)],
    "p-valor": [round(np.asarray(prueba.pvalue).item(), 4)],
})
tabla5.to_csv(SALIDAS / "tabla5_prueba_fisher.csv", index=False, encoding="utf-8-sig")

# 6b) Tabla 6: cointegración de Engle-Granger.
#     El rendimiento y las expectativas no son estacionarios en nivel (Tabla 3). Si están
#     cointegrados, la regresión en niveles mide una relación de largo plazo y no es espuria.
filas = []
for relacion, regresores in [("Bono vs expectativas de inflación", ["expect_infl_12m"]),
                             ("Bono vs las 3 variables explicativas", X)]:
    estadistico, p_valor, _ = coint(datos[Y], datos[regresores], trend="c", autolag="aic")
    filas.append([relacion, round(estadistico, 3), round(p_valor, 4),
                  "Cointegradas" if p_valor < 0.05 else "No cointegradas"])
tabla6 = pd.DataFrame(filas, columns=["Relación", "Estadístico Engle-Granger", "p-valor", "Conclusión (5%)"])
tabla6.to_csv(SALIDAS / "tabla6_cointegracion.csv", index=False, encoding="utf-8-sig")

# 6c) Tabla 7: regresión en PRIMERAS DIFERENCIAS (cambios mes a mes).
#     Como no hay cointegración (Tabla 6), la regresión en niveles podría ser espuria.
#     En diferencias todas las variables son estacionarias (Tabla 3), así que esta
#     estimación es válida: mide cómo responde el CAMBIO del rendimiento a los CAMBIOS
#     de las demás variables.
dif = datos[[Y] + X].diff().dropna()
modelo_d = sm.OLS(dif[Y], sm.add_constant(dif[X])).fit(cov_type="HAC", cov_kwds={"maxlags": REZAGOS_NW})
with open(SALIDAS / "tabla7_regresion_diferencias.txt", "w", encoding="utf-8") as archivo:
    archivo.write(modelo_d.summary().as_text())
tabla7 = pd.DataFrame({
    "Coeficiente": modelo_d.params,
    "Error estándar (NW)": modelo_d.bse,
    "Estadístico z": modelo_d.tvalues,
    "p-valor": modelo_d.pvalues,
}).round(4)
tabla7.index = ["const"] + ["d_" + v for v in X]
tabla7.to_csv(SALIDAS / "tabla7_regresion_diferencias.csv", encoding="utf-8-sig")
prueba_d = modelo_d.t_test("expect_infl_12m = 1")
tabla7b = pd.DataFrame({
    "Indicador": ["Observaciones", "R cuadrado", "Durbin-Watson",
                  "Prueba H0: b1 = 1 (estadístico)", "Prueba H0: b1 = 1 (p-valor)"],
    "Valor": [int(modelo_d.nobs), round(modelo_d.rsquared, 4), round(durbin_watson(modelo_d.resid), 4),
              round(np.asarray(prueba_d.tvalue).item(), 4), round(np.asarray(prueba_d.pvalue).item(), 4)],
})
tabla7b.to_csv(SALIDAS / "tabla7b_diagnostico_diferencias.csv", index=False, encoding="utf-8-sig")

# 7) Figura 1: evolución de las 4 variables del modelo
fig, ax = plt.subplots(figsize=(10, 5))
for v in [Y] + X:
    ax.plot(datos["fecha"], datos[v], label=NOMBRES[v])
ax.set_xlabel("Fecha")
ax.set_ylabel("Porcentaje (%)")
ax.legend(loc="upper left", fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(SALIDAS / "figura1_series.png", dpi=300)
plt.close(fig)

# 8) Figura 2: rendimiento del bono frente a la expectativa de inflación, con recta ajustada
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(datos["expect_infl_12m"], datos[Y], s=15, alpha=0.7)
recta = sm.OLS(datos[Y], sm.add_constant(datos["expect_infl_12m"])).fit()
x_orden = datos["expect_infl_12m"].sort_values()
ax.plot(x_orden, recta.params["const"] + recta.params["expect_infl_12m"] * x_orden, color="red")
ax.set_xlabel(NOMBRES["expect_infl_12m"])
ax.set_ylabel(NOMBRES[Y])
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(SALIDAS / "figura2_dispersion.png", dpi=300)
plt.close(fig)

# 9) Figura 3: tasa real ex ante (ecuación de Fisher)
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(datos["fecha"], datos["tasa_real_exante"], color="green")
ax.axhline(datos["tasa_real_exante"].mean(), color="gray", linestyle="--", label="Promedio")
ax.set_xlabel("Fecha")
ax.set_ylabel(NOMBRES["tasa_real_exante"])
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(SALIDAS / "figura3_tasa_real.png", dpi=300)
plt.close(fig)

# 10) Resumen en pantalla
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 10)
print("\nTABLA 4 - Regresión (errores Newey-West):")
print(tabla4)
print("\nDiagnóstico:")
print(diagnostico.to_string(index=False))
print("\nTABLA 5 - Prueba de Fisher (H0: b1 = 1):")
print(tabla5.to_string(index=False))
print("\nTABLA 6 - Cointegración de Engle-Granger:")
print(tabla6.to_string(index=False))
print("\nTABLA 7 - Regresión en primeras diferencias (errores Newey-West):")
print(tabla7)
print(tabla7b.to_string(index=False))
print(f"\nListo: tablas y figuras guardadas en la carpeta '{SALIDAS.name}'.")
