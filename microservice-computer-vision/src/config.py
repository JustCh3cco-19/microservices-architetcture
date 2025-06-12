# Config file per computer vision

import os
import numpy as np

### RICONOSCIMENTO DEL COLORE ###
#
# usato nel vecchio algoritmo con il riconoscimento del colore tramite un singolo
# pixel e per colorare le bb
class ConeColors:
	YELLOW = [39, 76, 103]
	BLUE = [59, 44, 2]
#
# Lista dei coni con i relativi colori
#
# id -> stringa che identifica il colore che viene poi usata anche in altre
#		parti del codice, ad esempio in matlab.
# 		quindi ogni modifica deve essere fatta con cura
# bgr -> colore in formato bgr usato per il confronto
#		 viene usato nel single point color detector
# cone_hsv -> limiti per la maschera in formato hsv
#			si potrebbe migliorare calcolando i limiti in modo più preciso
#			viene usato nel mask color detector
#			sono da usare np.array di dimensione 3 con i valori hsv
#			può essere utile: https://colorpicker.me/
CONES = [
	{
		'id': 1,
		'bgr': ConeColors.BLUE,
		'cone_hsv': (np.array([90, 60, 30]), np.array([130, 255, 255])),
		# 'band_hsv': (np.array([90, 60, 30]), np.array([130, 255, 255])),
	},
	{
		'id': 2,
		'bgr': ConeColors.YELLOW,
		'cone_hsv': (np.array([10, 80, 50]), np.array([75, 255, 255])), # range di giallo
		# 'band_hsv': (np.array([0, 0, 0]), np.array([180, 255, 25])), # range di nero
	},
]
#
# Valore di default per il colore 
# 
# è stato scelto il colore blu perché ... #TODO
# il valore di default è da implementare in ogni algorimo di identificazione
# da usare solo nei return e non per confronti
DEFAULT_CONE = CONES[0]
#
# dim (un lato) massima della bb per il calcolo della confidence per il colore
BB_DIM_COLOR_CONF = 100

### CALCOLO DELLA DISTANZA ###
#
# percentuale di distanza massima e minima dal centro della bb per il calcolo
# della distanza
DIST_MAX_X_PERCENT = 0.9 # >= 0.5
DIST_MIN_X_PERCENT = 1 - DIST_MAX_X_PERCENT
DIST_MAX_Y_PERCENT = 0.95 # >= 0.3
# distanza massima e minima in metri
MAX_DISTANCE = 50
MIN_DISTANCE = 0.5
# punti usati per fare la media della distanza
MAX_POINTS = 10

### DISCRIMINAZIONE DEI CONI ###
#
# Larghezza e altezza minima e massima della bb (in pixel)
MIN_BB_WIDTH = 5
MIN_BB_HEIGHT = 10
MAX_BB_WIDTH = 200
MAX_BB_HEIGHT = 250
#
# Rapporto tra altezza/largezza della bb massimo e minimo
MIN_BB_RATIO = 0.9
MAX_BB_RATIO = 4
#
# Larghezza e altezza minima e massima reale della bb (in metri)
#
MIN_REAL_BB_WIDTH = 0.08
MIN_REAL_BB_HEIGHT = 0.20
MAX_REAL_BB_WIDTH = 0.60
MAX_REAL_BB_HEIGHT = 1.0
#
# Percentuale di compenetrazione tra le bb
BB_COMPENETRATION_PERCENT = 0.4
#
# Confidence minima della distanza
DISTANCE_MIN_CONFIDENCE = 0 # TODO
#
# Distanza massima da un bordo del frame per la bb in pixel
BB_MAX_DISTANCE_FROM_BORDER = 2


### RICONOSCIMENTO DEI CONI ###
#
WEIGHTS = 'models/640x32.pt' # pesi di yolo
CONF_THRESHOLD = 0.25 # soglia di confidenza
IOU_THRESHOLD = 0.45 # soglia di iou

### CONFIGURAZIONE DELLA CAMERA ###
#
# Config per il frame
# dimensioni del frame passato a yolo
FRAME_WIDTH = 640 * 2
FRAME_HEIGHT = 640
#
# parametri d455 #
# posizione della camera rispetto al baricentro macchina
CAMERA_POS = [0, 0, 0]
# scala della profondità della camera
CAMERA_DEPTH_SCALE = 0.001 # usa una scala in millimetri #  0.0010000000474974513
# risoluzione della camera
CAMERA_RESOLUTION = [1280, 720]
# centro della camera asse orizzontale e verticale
CAMERA_CENTER = [646.953, 348.2] # spostato a destra per la banda a sinistra usata dalla d455
# distanza focale in pixel
CAMERA_FOCAL = [641.746, 641.746]
#
# parametri simulazione per il SIL #
# CAMERA_POS = [0, 0, 1]
# CAMERA_DEPTH_SCALE = 1 # in metri
# CAMERA_CENTER = [640, 360] # esattamente il centro
# CAMERA_FOCAL = [643, 643]

### OUTPUTS ###
#
# Log level
LOGLEVEL = "INFO"
#
# Path base
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
# path base per gli output
OUTPUT_PATH = os.path.join(BASE_PATH, "outputs")
# path per i video bag
BAG_VIDEO_PATH = os.path.join(OUTPUT_PATH, "bags")
# path per i video cv
CV_VIDEO_PATH = os.path.join(OUTPUT_PATH, "cv")
# path per i file con i coni
CONES_PATH = os.path.join(OUTPUT_PATH, "cones")
# log file path
LOGPATH = os.path.join(OUTPUT_PATH, "logs")
