"""
è stato spostato su matlab
"""

import TriangolazionePrototipo
# Import the matlab module only after you have imported
# MATLAB Compiler SDK generated Python modules.
import matlab

import plotly.express as px
import numpy as np
import pandas as pd


import numpy as np


from scipy import interpolate

import matplotlib.pyplot as plt


def interpolazione(x,y,numx):
    
    #x = np.arange(0, 5, 0.25)
    #x = np.array([1,2,3,4,5,6])
    x = [x[0], x[round(len(x)/2)], x[len(x)-1]]
    y = [y[0], y[round(len(y)/2)], y[len(y)-1]]
    
    #y = np.arange(2, 7, 0.25)
    #y = np.array([13,24,5,4,52,6])

    x_interp = np.linspace(np.min(x), np.max(x), numx)

    #x_interp = np.round(x_interp,3)
    
    f = interpolate.interp1d(x, y, kind="quadratic")
    #print(x_interp.tolist(), f(x_interp).tolist())
    
    y_interp = f(x_interp)
    #y_interp = np.round(y_interp,3)
    print(x_interp.tolist(), y_interp.tolist())
    return x_interp.tolist(), y_interp.tolist()

def calcola_curvatura(x,y):
    
    # Calcola le derivate prime di x e y
    dx = np.diff(x)
    dy = np.diff(y)
    
    # Calcola le derivate seconde di x e y
    d2x = np.diff(dx)
    d2y = np.diff(dy)
    
    # Calcola la curvatura
    numeratore = dx[1:] * d2y - dy[1:] * d2x
    denominatore = (dx[1:]**2 + dy[1:]**2)**(3/2)
    curvatura = numeratore / denominatore
    
    # Gestione dei valori NaN
    curvatura[np.isnan(curvatura)] = 0
    
    return curvatura


def triangolazione(posizioni,numeroConi,maxConi):
    
    
    print("aaaaaaaaaaaaaaaa")
    
    my_TriangolazionePrototipo = TriangolazionePrototipo.initialize()
    
    x = []
    for i in range(numeroConi):    
        x.append(posizioni[i][0])
    y = []
    for i in range(numeroConi):    
        y.append(posizioni[i][1])
    colori = []
    for i in range(numeroConi):
        if(posizioni[i][2]=='blu'):
            colori.append("blu")
        else:
            colori.append("giallo")
    maxConesIn = matlab.double([float(maxConi)], size=(1, 1))
    xIn = matlab.double(x, size=(1, numeroConi))
    yIn = matlab.double(y, size=(1, numeroConi))

    risOut, sOut = my_TriangolazionePrototipo.TriangolazionePrototipo(xIn, yIn, colori, maxConesIn, nargout=2)
    
    risarr = np.array(risOut)
    risOutT = risarr.transpose()
    xa = risOutT[0].tolist()
    ya = risOutT[1].tolist()
    
    numwayp = 1000
    xa, ya = interpolazione(xa,ya,numwayp)


    out = int(sOut)
    my_dataframe = {
        'x' : x + xa + [0]
        ,'y' : y + ya + [0]
        ,'colore' : colori + numwayp*["traiettoria"] + ["macchina"]
    }

    #print(my_dataframe)
    df = pd.DataFrame(my_dataframe)


    fig = px.scatter(df, x="x", y="y", color='colore')

    #fig = px.scatter(x=xa,y=ya)
    fig.show()
    
    curvatura = calcola_curvatura(xa,ya)
    print(curvatura)
    my_TriangolazionePrototipo.terminate()
    
    return xa, ya