
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Laboratorio 1. Inversión de Capital                                                        -- #
# -- script: data.py : script de python para la recolección de datos                                     -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# Configuraciones
import pandas as pd
import numpy as np

def lecturaDatos(fecha : "Ingresar la fecha para la lectura del archivo de Excel que contiene las posiciones del NAFTRAC (yyyy-mm-dd)"):
    """
    lecturaDatos es una función que lee el archivo de Excel que contiene las posiciones del NAFTRAC para la fecha deseada.
    
    """
    
    datos = pd.read_csv("files/NAFTRAC_" + fecha.replace("-", "") + ".csv", skiprows = 2).dropna()
    
    return datos
    

