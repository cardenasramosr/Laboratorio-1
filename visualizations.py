
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Laboratorio 1. Inversión de Capital                                                        -- #
# -- script: visualizations.py : script de python con las funciones para la visualización de datos       -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# Configuraciones
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def visualEstrategia(datos : "DataFrame que contiene el desempeño de la estrategia de inversión"):
    """
    visualEstrategia es una función que devuelve un gráfico interactivo para el desempeño de la estrategia de inversión ingresada.
    
    """

    fig = make_subplots(specs = [[{"secondary_y" : False}]])
    fig.add_trace(go.Scatter(x = datos.index, y = datos["Evolución Capital Invertido"], name = "Capital Invertido"), secondary_y = False,)
    fig.update_layout(title = "Desempeño Estrategia Inversión", xaxis_title = "Fecha", yaxis_title = "MXN")
    
    return fig