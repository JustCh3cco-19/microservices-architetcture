import cv2
import numpy as np


# Colori BGR standard
class Colors:
	WHITE = [255, 255, 255]
	GRAY = [128, 128, 128]
	GREEN = [0, 255, 0]
	RED = [0, 0, 255]
	BLACK = [0, 0, 0]

# Funzione per ottenere i limiti per la maschera dato un colore in formato bgr
# restituisce i limiti in formato hsv
# funzione da usare per test, magari in produzione sarebbe da definire in modo
# più preciso i limiti
# fonte: https://github.com/computervisioneng/color-detection-opencv/blob/master/util.py
def hsv_get_limits(color):
	"""
	Get the lower and upper HSV limits for a color
	- color: BGR value
	:return: lowerLimit, upperLimit
	"""

	c = np.uint8([[color]])  # BGR values
	hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)

	hue = hsvC[0][0][0]  # Get the hue value

	# Handle red hue wrap-around
	if hue >= 165:  # Upper limit for divided red hue
		lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
		upperLimit = np.array([180, 255, 255], dtype=np.uint8)
	elif hue <= 15:  # Lower limit for divided red hue
		lowerLimit = np.array([0, 100, 100], dtype=np.uint8)
		upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)
	else:
		lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
		upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)

	return lowerLimit, upperLimit

def rgb2bgr(color):
	"""
	Convert a color from RGB to BGR
	- color: RGB value
	:return: BGR value
	"""
	return color[::-1]

def bgr2hsv(color):
	"""
	Convert a color from BGR to HSV
	- color: BGR value
	:return: HSV value
	"""
	c = np.uint8([[color]])  # BGR values
	return cv2.cvtColor(c, cv2.COLOR_BGR2HSV)[0][0]


