import cv2
from typing import Optional

import config


class DetectorType:
	"""
	Enum per identificare il tipo di detector da utilizzare

	- SINGLE_POINT: utilizza un solo punto all'interno della bounding box
	- MASK: utilizza una maschera
	"""

	SINGLE_POINT = 0
	MASK = 1

def colorDetector(cone, detector_type: Optional[DetectorType] = DetectorType.MASK):
	"""
	Identifica il colore di un cono

	- color_frame: frame di colore in formato bgr
	- color_frame_cp: copia del frame di colore in formato bgr per essere modificato
	- x1: ascissa iniziale bounding box
	- y1: ordinata iniziale bounding box
	- x2: ascissa finale bounding box
	- y2: ordinata finale bounding box
	- detector_type: tipo di algoritmo da utilizzare per l'identificazione del colore

	:return: colore del cono in formato stringa, il colore in formato bgr e mask per DetectorType.MASK
	"""

	if detector_type == DetectorType.SINGLE_POINT:
		return _singlePointColorDetector(cone)
	elif detector_type == DetectorType.MASK:
		return _maskColorDetector(cone)


# Algoritmi di identificazione del colore #

# Single Point Color Detector
#
# L'algoritmo più semplice e veloce, prende un punto e trova quello con la 
# minima differenza per ogni valore bgr tra il colore del punto e i colori dei coni
#     /\
#    /__\
#   /____\
#  /  xx  \
# /________\
# -----------
# Il punto è scelto prendendo orizzontalmente
# la metà della bounding box e verticalmente prendendo
# un punto al 30% dell'altezza della BB partendo dal basso
# le due x indicano circa la posizione del cono
def _singlePointColorDetector(cone):
	"""
	Identifica il colore di un cono utilizzando un solo punto all'interno della bounding box
	"""

	x_mid = round((cone.x1 + cone.x2) / 2)
	y_min = round(cone.y1 + cone.height * 0.7)

	# punto nel formato bgr
	point_color = cone.get_color(x_mid, y_min)

	# Trova il colore con la minima differenza dal colore del cono
	color_id, color_bgr, error =  min(
		[(
			cone['id'],
			cone['bgr'],
			sum(abs(val1 - val2) for val1, val2 in zip(point_color, cone['bgr']))
		) for cone in config.CONES],
		key=lambda x: x[2],
		default=(config.DEFAULT_CONE['id'], config.DEFAULT_CONE['bgr'], -1)
	)

	if cone.frames.color_frame_cp:
		# Visualizzazione del punto utilizzato per l'identificazione del colore
		# viene colorato il punto usato con il rosso e viene disegnata una croce verde
		cv2.line(cone.frames.color_frame_cp, (x_mid - 5, y_min), (x_mid + 5, y_min), (0, 255, 0), 1)
		cv2.line(cone.frames.color_frame_cp, (x_mid, y_min - 5), (x_mid, y_min + 5), (0, 255, 0), 1)
		cone.frames.color_frame_cp[y_min, x_mid] = [0, 0, 255]
	
	# la confidence dipende dall'errore normalizzato tra 0 e 1
	if error == -1:
		color_confidence = 0
	else:
		color_confidence = 1 - (error / (255 * 3))

	return color_id, color_bgr, None, color_confidence

# Mask Color Detector
#
# Viene creata una maschera per ogni colore e viene calcolata la percentuale
# di pixel che combaciano con la maschera
#
# Si potrebbe migliorare eliminando il colore di sfondo
# inoltre si potrebbe segmentare il cono in modo da applicare la maschera solo al cono
# Anche un utilizzo consapevole della banda del cono può essere utile per minimizzare
# l'errore
def _maskColorDetector(cone):
	"""
	Identifica il colore di un cono utilizzando una maschera
	"""

	# Converto in hsv
	hsv = cv2.cvtColor(cone.bb_color, cv2.COLOR_BGR2HSV)

	# Calcolo la maschera per ogni cono
	masks = [cv2.inRange(hsv, lower, upper)
				for lower, upper in [c['cone_hsv'] for c in config.CONES]]

	# Calcolo la percentuale di pixel che combaciano con la maschera
	# per ogni colore
	percents = [cv2.countNonZero(mask) / (mask.shape[0] * mask.shape[1])
				for mask in masks]

	# Prendo il colore con la percentuale più alta
	color_id, color_bgr, perc, mask = max(
		[(cone['id'], cone['bgr'], percent, mask) for cone, percent, mask in 
			zip(config.CONES, percents, masks)],
		key=lambda x: x[2],
		default=(config.DEFAULT_CONE['id'], config.DEFAULT_CONE['bgr'], 0, config.DEFAULT_CONE['cone_hsv']),
	)

	if perc == 0:
		color_confidence = 0
	else:
		# la confidence dipende da
		# quanto la % del colore è vicino al 60% q
		# quanto le altre percentuali del colore sono vicine a 0%
		# quanto l'area della bounding box è vicina a BB_DIM_COLOR_CONF
		color_perc_conf = (1 - abs(perc - 0.60)) 
		other_perc = perc / sum(percents)
		area_conf = min(cone.width, cone.height, config.BB_DIM_COLOR_CONF) / config.BB_DIM_COLOR_CONF
		color_confidence = color_perc_conf * other_perc * area_conf

	if cone.frames.color_frame_cp is not None:
		# Visualizzazione delle maschere
		# viene visualizzata la maschera per ogni colore
		# for i, mask in enumerate(masks):
		# 	cv2.imshow(f"Mask {CONES[i]['id']}", mask)
		
		# Visualizzazione della percentuale di pixel che combaciano con la maschera
		# all'interno della bounding box
		# for i, p in enumerate(percents):
		# 	cv2.putText(cone.frames.color_frame_cp, f"{round(p * 100, 2)}%",
		# 		(cone.x2 + 5, round((cone.y1 + cone.y2) / 2) + 20 * i), 
		# 		cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
		
		# assegno un numero ai coni per riconoscerli
		# rand_id = np.random.randint(0, 100)
		# cv2.putText(cone.color_frame, "#" + str(rand_id),
		# 	(x2 + 20, y2), 
		# 	cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 2)
		# print("cono", rand_id, "percentuali:\nGiallo:", round(percents[0] * 100, 2), "%\nBlu:", round(percents[1] * 100, 2), "%\n")

		# mostro il frame su un altra finestra

		# cv2.imshow(f"CONO {rand_id}", masks[0])

		# mostro il frame con la maschera
		# hsvImage = cv2.cvtColor(color_frame, cv2.COLOR_BGR2HSV)
		# cv2.imshow("Mask Stream", cv2.inRange(hsvImage, config.CONES[1]['cone_hsv'][0], config.CONES[1]['cone_hsv'][1]))
		pass

	return color_id, color_bgr, mask, color_confidence

