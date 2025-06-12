import cv2
import pyrealsense2 as rs
from depthCamera import *
import positionRT as posizione
import time
import test.Triangolazione as tr

# Import the required Libraries
from tkinter import *
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile
import os
    
# Dichiarazione variabili globali a valori di default per evitare errori di lettura
point = (400, 300)
coloreCono = ""
matriceConi = [[0 for x in range(3)] for y in range(10)]
numeroConi = 0
distance = 1
giallo = [255, 255, 0]
blu = [51, 51, 255]
arancione = [255, 102, 0]

def individuaColore(x,y):
    rgb = color_frame[x,y]
    print(rgb)
    subGiallo = rgb - giallo
    subBlu = rgb - blu
    subArancione = rgb - arancione
    difGiallo = 0
    difBlu = 0
    difArancione = 0
    for e in subGiallo:
        difGiallo += abs(e)
    for e in subBlu:
        difBlu += abs(e)
    for e in subArancione:
        difArancione += abs(e)
    match = min(difArancione, difBlu, difGiallo)
    if(match == difArancione):
        return "Arancione"
    if(match == difBlu):
        return "Blu"
    if(match == difGiallo):
        return "Giallo"
    
def Triangola(color_frame, depth_frame, coniIndividuati[]): 
    # Interfaccia grafica a linea di comando
    print("-----TrajectoryInference-----")


    # Assegnazione della distanza accedendo all'elemento desiderato della Depth Matrix
    # distance = depth_frame[point[1], point[0]]
    numeroConi = 0
    # Acquisizione frame più recente

    matriceConi = [10][3]
    for row in coniIndividuati:
        bouBoxAlto = [row[0], row[1]]
        bouBoxBasso = [row[2], row[3]]
        
        centroBB = [((bouBoxBasso[0]-bouBoxAlto[0])/2+bouBoxAlto[0]), ((bouBoxBasso[1]-bouBoxAlto[1])/2+bouBoxAlto[1])]
        # Calcolo posizione del cono rispetto alla terna centrata nel baricentro
        # Del veicolo
        
        ## TROVA IL COLORE 
        coloreCono = individuaColore(centroBB[0], centroBB[1])
        ##
        
        distance = depth_frame[centroBB[1],centroBB[0]]
        
        X, Y, Z = posizione.posizionee(centroBB[0],centroBB[1],distance/1000)
        # Inserimento nella matrice
        matriceConi[numeroConi] = [X, Y, coloreCono]
        print("cono salvato")
        numeroConi+=1
        if numeroConi==6:
            break
        
    risultato = tr.triangolazione(matriceConi,numeroConi,6)
            
                    
                