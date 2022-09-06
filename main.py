
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Laboratorio 1. Inversión de Capital                                                        -- #
# -- script: main.py : script de python con la funcionalidad main                                        -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# Configuraciones
import data, functions, visualizations

def estrategiaInversionPasiva(capital : "Capital inicial", comision : "Comisión", 
                              fechaInicio : "Fecha de inicio del backtest", fechaFin : "Fecha de fin del backtest"):
    """
    estrategiaInversionPasiva es una función que elabora el testeo de la estrategia de inversión pasiva.
    
    """
    
    datos = data.lecturaDatos(fechaInicio)
    precios, preciosMensuales, tickers = functions.descargaPrecios(fechaInicio, fechaFin, datos)
    df_pasiva_info, df_pasiva, df_pasiva_metricas = functions.inversionPasiva(preciosMensuales, tickers, capital, comision)
    fig = visualizations.visualEstrategia(df_pasiva)
    
    return df_pasiva_info, df_pasiva, df_pasiva_metricas, fig

def estrategiaInversionActiva(capital : "Capital inicial", comision : "Comisión", 
                              fecha : "Fecha para la partición de datos (portafolio de Markowitz)", 
                              fechaInicio : "Fecha de inicio del backtest", fechaFin : "Fecha de fin del backtest"):
    """
    estrategiaInversionActiva es una función que elabora el testeo de la estrategia de inversión activa.
    
    """
    
    datos = data.lecturaDatos(fechaInicio)
    precios, preciosMensuales, tickers = functions.descargaPrecios(fechaInicio, fechaFin, datos)
    df_activa_info, df_activa, df_operaciones, df_activa_metricas = functions.inversionActiva(fecha, precios, preciosMensuales, capital, comision)
    fig = visualizations.visualEstrategia(df_activa)
    
    return df_activa_info, df_activa, df_operaciones, df_activa_metricas, fig

def atribucionDesempeño(df_pasiva : "Estrategia Pasiva", df_activa : "Estrategia Activa", tasaLibreRiesgo : "Tasa libre riesgo"):
    """
    atribucionDesempeño es una función que devuelve las medidas de atribución al desempeño de las estrategias de inversión pasiva
    y activa.
    
    """
    
    medidas = functions.atribucionDesempeño(df_pasiva, df_activa, tasaLibreRiesgo)
    
    return medidas
