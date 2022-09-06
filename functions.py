
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Laboratorio 1. Inversión de Capital                                                        -- #
# -- script: functions.py : script de python con las funciones generales                                 -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# Configuraciones
import pandas as pd
pd.set_option('display.float_format', lambda x: '%.4f' % x)
import yfinance as yf
import numpy as np
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

def descargaPrecios(fechaInicio : "Fecha de inicio del backtest", fechaFin : "Fecha de fin del backtest", 
                    datos : "Posiciones del NAFTRAC"):
    """
    descargaPrecios es una función que devuelve los precios históricos en temporalidad diaria y mensual para los tickers que componen al índice NAFTRAC en la fecha ingresada.
    
    """
    
    tickers = {}
    tickersFiltro = ["KOFL", "KOFUBL", "USD", "MXN", "BSMXB", "NMKA"]
    
    for i in range(len(datos)):
            if datos["Ticker"][i] not in tickersFiltro:
                tickers[datos["Ticker"][i].replace("*", "").replace(".", "-") + ".MX"] = datos["Peso (%)"][i] / 100 
                
    precios = pd.DataFrame()
    for ticker in list(tickers.keys()):
        precios[ticker] = yf.download(ticker, start = fechaInicio, end = fechaFin, progress = False)["Adj Close"]
        
    precios.dropna(axis = 1, inplace = True)
    preciosMensuales = pd.DataFrame(columns = precios.columns)

    for i in range(len(precios)):
        if i != len(precios) - 1:
            if precios.index[i + 1].month - precios.index[i].month != 0:
                preciosMensuales.loc[precios.index[i], :] = precios.iloc[i, :]
            
        else:   
            preciosMensuales.loc[precios.index[i], :] = precios.iloc[i, :]
        
    return precios, preciosMensuales, tickers

def inversionPasiva(precios : "Precios mensuales", tickers : "Componentes del NAFTRAC", 
                    capital : "Capital inicial", comision : "Comisión"):
    """
    inversionPasiva es una función que elabora la estrategia de inversión pasiva.
    
    """
    
    # Posiciones iniciales
    df_pasiva_info = pd.DataFrame(index = precios.columns, columns = ["Títulos", "Costo de Compra Bruto", "Comisión",
                                                                      "Costo de Compra Total"]) 
    for ticker in precios.columns:
        df_pasiva_info.loc[ticker, "Títulos"] = np.floor((capital * tickers[ticker]) / (precios[ticker][0] * (1 + comision)))
        df_pasiva_info.loc[ticker, "Costo de Compra Bruto"] = df_pasiva_info.loc[ticker, "Títulos"] * precios[ticker][0]
        df_pasiva_info.loc[ticker, "Comisión"] = df_pasiva_info.loc[ticker, "Títulos"] * precios[ticker][0] * comision
        df_pasiva_info.loc[ticker, "Costo de Compra Total"] = df_pasiva_info.loc[ticker, "Títulos"] * precios[ticker][0] * (1 + comision)
        df_pasiva_info.loc[ticker, "Ponderación"] = (df_pasiva_info.loc[ticker, "Títulos"] * precios[ticker][0]) / capital
     
    df_pasiva = pd.DataFrame(index = precios.index, columns = ["Evolución Capital Invertido", "Rendimiento Mensual", 
                                                               "Rendimiento Mensual Acumulado"])
    
    # Backtest
    df_pasiva["Evolución Capital Invertido"] = np.dot(precios * (1 - comision), df_pasiva_info["Títulos"])
    df_pasiva["Rendimiento Mensual"] = df_pasiva["Evolución Capital Invertido"].pct_change().dropna()
    df_pasiva["Rendimiento Mensual Acumulado"] = (df_pasiva["Rendimiento Mensual"] + 1).cumprod() - 1 
     
    capitalInvertido = df_pasiva_info["Costo de Compra Total"].sum()
    df_pasiva_metricas = pd.DataFrame({"Capital Inicial" : capital, "Capital Invertido" : capitalInvertido, 
                               "Efectivo" : capital - capitalInvertido, 
                               "Capital Final" : capital - capitalInvertido + df_pasiva["Evolución Capital Invertido"][-1],
                               "Rendimiento Efectivo %" : df_pasiva["Rendimiento Mensual Acumulado"][-1] * 100}, 
                              index = ["Estrategia Pasiva"])
        
    return df_pasiva_info, df_pasiva, df_pasiva_metricas

def inversionActiva(fecha : "Fecha para la partición de datos (portafolio de Markowitz)", 
                    precios : "Precios diarios", preciosMensuales : "Precios mensuales", capital : "Capital", comision : "Comisión"):
    """
    inversionActiva es una función que elabora la estrategia de inversión activa.
    
    """
    
    # Portafolio eficiente (Sharpe estándar)
    precios_ = precios[precios.index <= fecha]
    mu = expected_returns.mean_historical_return(precios_, compounding = False, log_returns = True)
    S = risk_models.sample_cov(precios_, log_returns = True)
    ef = EfficientFrontier(mu, S)
    pesos = ef.max_sharpe()
    pesos = pd.DataFrame(pesos, columns = list(pesos.keys()), index = ["Ponderaciones"])
    pesos = pesos[pesos > 0].dropna(axis = 1)
    
    # Posiciones iniciales
    df_activa_info = pd.DataFrame(index = pesos.columns, columns = ["Títulos", "Costo de Compra Bruto", "Comisión",
                                                                      "Costo de Compra Total"])
    precios_2 = precios.loc[precios.index > fecha, list(pesos.keys())]
    preciosMensuales = preciosMensuales.loc[preciosMensuales.index > fecha, list(pesos.keys())]
    preciosMensuales_ = pd.DataFrame()
    preciosMensuales_.loc[precios_2.index[0], preciosMensuales.columns] = precios_2.iloc[0, :]

    for i in range(len(preciosMensuales)):
        preciosMensuales_.loc[preciosMensuales.index[i], preciosMensuales.columns] = preciosMensuales.iloc[i, :]
        
    for ticker in pesos.columns:
        df_activa_info.loc[ticker, "Títulos"] = np.floor((capital * pesos[ticker][0]) / (precios_2[ticker][0] * (1 + comision)))
        df_activa_info.loc[ticker, "Costo de Compra Bruto"] = df_activa_info.loc[ticker, "Títulos"] * precios_2[ticker][0]
        df_activa_info.loc[ticker, "Comisión"] = df_activa_info.loc[ticker, "Títulos"] * precios_2[ticker][0] * comision
        df_activa_info.loc[ticker, "Costo de Compra Total"] = df_activa_info.loc[ticker, "Títulos"] * precios_2[ticker][0] * (1 + comision)
        df_activa_info.loc[ticker, "Ponderación"] = (df_activa_info.loc[ticker, "Títulos"] * precios_2[ticker][0]) / capital
        
    # Backtest
    retornosMensuales = preciosMensuales_.pct_change().dropna()
    df_activa = pd.DataFrame(index = preciosMensuales_.index, columns = ["Evolución Capital Invertido", "Rendimiento Mensual", 
                                                               "Rendimiento Mensual Acumulado"])
    df_activa.iloc[0, 0] = np.dot(preciosMensuales_.iloc[0, :], df_activa_info["Títulos"])
    
    titulos = dict(df_activa_info["Títulos"])
    numeroTitulos = df_activa_info["Títulos"].sum()
    capitalInvertido = df_activa_info["Costo de Compra Total"].sum()
    efectivo = capital - capitalInvertido
    
    df_operaciones = pd.DataFrame(columns = ["Timestamp", "Ticker", "Títulos", "Títulos Compra (Venta)", "Títulos Totales", "Comisión"])
    op = 0
    
    for i in range(len(retornosMensuales)):
        compras = list(retornosMensuales[retornosMensuales >= 0.05].iloc[i].dropna().sort_values(ascending = False).index)
        ventas = list(retornosMensuales[retornosMensuales <= -0.05].iloc[i].dropna().sort_values().index)
        
        if len(ventas) != 0:
            for ticker in ventas:
                titulosVenta = np.ceil(titulos[ticker] * 0.025)
                titulos[ticker] = titulos[ticker] - titulosVenta
                efectivo = efectivo + titulosVenta * preciosMensuales_.loc[retornosMensuales.index[i], ticker] * (1 - comision)
                df_operaciones.loc[op, "Timestamp"] = retornosMensuales.index[i]
                df_operaciones.loc[op, "Ticker"] = ticker
                df_operaciones.loc[op, "Títulos"] = numeroTitulos
                df_operaciones.loc[op, "Títulos Compra (Venta)"] = -titulosVenta
                df_operaciones.loc[op, "Títulos Totales"] = df_operaciones.loc[op, "Títulos"] +  df_operaciones.loc[op, "Títulos Compra (Venta)"]
                df_operaciones.loc[op, "Comisión"] = titulosVenta * preciosMensuales_.loc[retornosMensuales.index[i], ticker] * comision
                numeroTitulos = df_operaciones.loc[op, "Títulos Totales"] 
                op += 1
                
        if len(compras) != 0:
            for ticker in compras:
                if (efectivo - (np.ceil(titulos[ticker] * 0.025) * preciosMensuales_.loc[retornosMensuales.index[i], ticker] * (1 + comision))) > 0:
                    titulosCompra = np.ceil(titulos[ticker] * 0.025)
                    titulos[ticker] = titulos[ticker] + titulosCompra
                    efectivo = efectivo - titulosCompra * preciosMensuales_.loc[retornosMensuales.index[i], ticker] * (1 + comision)
                    df_operaciones.loc[op, "Timestamp"] = retornosMensuales.index[i]
                    df_operaciones.loc[op, "Ticker"] = ticker
                    df_operaciones.loc[op, "Títulos"] = numeroTitulos
                    df_operaciones.loc[op, "Títulos Compra (Venta)"] = titulosCompra
                    df_operaciones.loc[op, "Títulos Totales"] = df_operaciones.loc[op, "Títulos"] +  df_operaciones.loc[op, "Títulos Compra (Venta)"]
                    df_operaciones.loc[op, "Comisión"] = titulosCompra * preciosMensuales_.loc[retornosMensuales.index[i], ticker] * comision
                    numeroTitulos = df_operaciones.loc[op, "Títulos Totales"] 
                    op += 1
                    
        df_activa.loc[retornosMensuales.index[i], "Evolución Capital Invertido"] = np.dot(preciosMensuales_.loc[retornosMensuales.index[i], :], [*titulos.values()]) 
        
    df_activa["Rendimiento Mensual"] = df_activa["Evolución Capital Invertido"].pct_change().dropna()
    df_activa["Rendimiento Mensual Acumulado"] = (df_activa["Rendimiento Mensual"] + 1).cumprod() - 1 
    df_operaciones["Comisión Acumulada"] = df_operaciones["Comisión"].cumsum()
    
    capitalInvertido = df_activa_info["Costo de Compra Total"].sum()
    df_activa_metricas = pd.DataFrame({"Capital Inicial" : capital, "Capital Invertido" : capitalInvertido, 
                               "Efectivo" : efectivo, 
                               "Capital Final" : efectivo + df_activa["Evolución Capital Invertido"][-1],
                               "Rendimiento Efectivo %" : df_activa["Rendimiento Mensual Acumulado"][-1] * 100}, 
                              index = ["Estrategia Activa"])
    
    return df_activa_info, df_activa, df_operaciones, df_activa_metricas
    
def atribucionDesempeño(df_pasiva : "Estrategia Pasiva", df_activa : "Estrategia Activa", tasaLibreRiesgo : "Tasa libre riesgo"):
    """
    atribucionDesempeño es una función que devuelve las medidas de atribución al desempeño de las estrategias de inversión pasiva
    y activa.
    
    """
    
    medidas = pd.DataFrame(index = ["rend_m", "rend_c", "sharpe"], columns = ["Descripción", "Inversión Pasiva", "Inversión Activa"])
    medidas.loc["rend_m", "Descripción"] = "Rendimiento promedio mensual"
    medidas.loc["rend_c", "Descripción"] = "Rendimiento mensual acumulado"
    medidas.loc["sharpe", "Descripción"] = "Sharpe ratio"
    
    medidas.loc["rend_m", "Inversión Pasiva"] = df_pasiva["Rendimiento Mensual"].dropna().mean()
    medidas.loc["rend_c", "Inversión Pasiva"] = df_pasiva["Rendimiento Mensual Acumulado"][-1]
    medidas.loc["sharpe", "Inversión Pasiva"] = (df_pasiva["Rendimiento Mensual"].dropna().mean() - tasaLibreRiesgo) / df_pasiva["Rendimiento Mensual"].dropna().std() 
    
    medidas.loc["rend_m", "Inversión Activa"] = df_activa["Rendimiento Mensual"].dropna().mean()
    medidas.loc["rend_c", "Inversión Activa"] = df_activa["Rendimiento Mensual Acumulado"][-1]
    medidas.loc["sharpe", "Inversión Activa"] = (df_activa["Rendimiento Mensual"].dropna().mean() - tasaLibreRiesgo) / df_activa["Rendimiento Mensual"].dropna().std() 
    
    return medidas 


