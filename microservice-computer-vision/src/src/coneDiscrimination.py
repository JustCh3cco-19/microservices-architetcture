import cv2
import logging
from typing import List

import config
from utils.colors import Colors
from src.positionRT import position

def validateCone(cone, cones: List) -> bool:
	"""
	Valida il cono

	Controlla:
	- le dimensioni della bounding box
		- larghezza minima e massima
		- altezza minima e massima
		- rapporto altezza/larghezza
	- la posizione della bounding box
		- non deve toccare i bordi del frame
	- la compenetrazione con gli altri coni
		- non deve compenetrarsi con gli altri coni
		- se si compenetrano, il cono più grande è valido
	- controllo della distanza
		- controlla che la distanza sia valida e che la confidenza sia maggiore di un certo valore `config.DISTANCE_MIN_CONFIDENCE`

	Parametri:
	- cone: cono da validare (oggetto Cone)
	- cones: lista dei coni successivi (oggetti Cone) ancora da validare
	"""

	if cone.deleted:
		return False

	if (not _validateBBposition(cone) # validazione della posizione della bounding box
		  or not _validateDistance(cone) # controllo della distanza
		  or not _validateBBdimensions(cone) # validazione delle dimensioni della bounding box
		  or not _validateBBoverlap(cone, cones) # validazione della compenetrazione con gli altri coni
		):
		
		cone.deleted = True
		return False

	return True

def error(cone, s: str) -> bool:
	"""
	se `cone.color_frame_cp` è diverso da None,
	scrive sul frame la stringa `s` al centro della bounding box del cono
	return: false
	"""

	logging.debug(f"Cono [{cone.x1} - {cone.y1}] scartato: {s}")

	if cone.frames.color_frame_cp is not None:
		cv2.putText(cone.frames.color_frame_cp, s,
			(cone.x1 + 2, cone.y1 + cone.height // 2),
			cv2.FONT_HERSHEY_SIMPLEX, 0.3, Colors.RED, 1)
	return False

def _validateDistance(cone) -> bool:
	"""
	Valida la distanza del cono

	- cone: cono
	- return: True se la distanza è valida, False altrimenti
	"""

	# controlla se la distanza è valida
	if cone.distance is None:
		return error(cone, "Dist not valid")

	# controlla se la confidenza della distanza è maggiore di un certo valore
	if cone.distance_confidence < config.DISTANCE_MIN_CONFIDENCE:
		return error(cone, "Dist Conf not valid")

	return True

def _validateBBdimensions(cone) -> bool:
	"""
	Valida le dimensioni della bounding box

	- bb: bounding box
	- return: True se le dimensioni sono valide, False altrimenti
	"""

	# controlla se la larghezza è compresa tra i valori minimi e massimi
	if not (config.MIN_BB_WIDTH <= cone.width <= config.MAX_BB_WIDTH):
		return error(cone, "W not valid")
	
	# controlla se l'altezza è compresa tra i valori minimi e massimi
	if not (config.MIN_BB_HEIGHT <= cone.height <= config.MAX_BB_HEIGHT):
		return error(cone, "H not valid")
	
	# controlla se il rapporto tra altezza e larghezza è compreso tra i valori minimi e massimi
	if not (config.MIN_BB_RATIO <= cone.height/cone.width <= config.MAX_BB_RATIO):
		return error(cone, "H/W not valid")
	
	# calcolo la larghezza reale del cono in metri
	pos_x1y1 = position(*cone.frames.get_original_pos(cone.x1, cone.y1), cone.distance)
	pos_x2y1 = position(*cone.frames.get_original_pos(cone.x2, cone.y1), cone.distance)
	width = pos_x1y1[1] - pos_x2y1[1]
	cone.real_width = width
	if not (config.MIN_REAL_BB_WIDTH <= width <= config.MAX_REAL_BB_WIDTH):
		return error(cone, "Real W not valid")
	
	# calcolo l'altezza reale del cono in metri
	pos_x1y2 = position(*cone.frames.get_original_pos(cone.x1, cone.y2), cone.distance)
	height = pos_x1y1[2] - pos_x1y2[2]
	cone.real_height = height
	if not (config.MIN_REAL_BB_HEIGHT <= height <= config.MAX_REAL_BB_HEIGHT):	
		return error(cone, "Real H not valid")

	return True

def _validateBBposition(cone) -> bool:
	"""
	Valida la posizione della bounding box

	- bb: bounding box
	- return: True se la posizione è valida, False altrimenti
	"""

	# controlla se la bounding box tocca il bordo sinistro
	if cone.x1 <= config.BB_MAX_DISTANCE_FROM_BORDER:
		return error(cone, "X = 0")
	
	# controlla se la bounding box tocca il bordo destro
	if cone.x2 >= config.FRAME_WIDTH - config.BB_MAX_DISTANCE_FROM_BORDER:
		return error(cone, "X = W")
	
	# controlla se la bounding box tocca il bordo superiore
	if cone.y1 <= config.BB_MAX_DISTANCE_FROM_BORDER:
		return error(cone, "Y = 0")
	
	# controlla se la bounding box tocca il bordo inferiore
	if cone.y2 >= config.FRAME_HEIGHT - config.BB_MAX_DISTANCE_FROM_BORDER:
		return error(cone, "Y = H")
	
	return True

def _validateBBoverlap(cone, cones) -> bool:
	"""
	Controlla se due coni si compenetrano di una certa percentuale `config.BB_COMPENETRATION_PERCENT`
	Se si compenetrano, ritrona True se cone è più grande, False altrimenti

	- cone: cono da controllare
	- cones: lista di coni
	- return: True se il cono è valido, False altrimenti
			  viene ritornato l'indice del cono da eliminare dalla lista
			  -1 per il cono corrente, altrimenti l'indice del cono
			  che sarà da aggiustare visto che è stato eliminato un cono dalla lista
	"""

	def overlap1D(a1: int, a2: int, b1: int, b2: int) -> int:
		"""
		Controlla se due segmenti si sovrappongono
		dati due punti A e B con le loro ascisse iniziali e finali
		- ax1: ascissa iniziale di A
		- ax2: ascissa finale di A
		- bx1: ascissa iniziale di B
		- bx2: ascissa finale di B

		- return: di quanti pixel si sovrappongono i due segmenti, 0 se non si sovrappongono
		"""

		if a1 <= b1 <= a2:
			# se B è dentro A
			return min(a2, b2) - b1 or 1
		elif a1 <= b2 <= a2:
			# se B è dentro A
			return b2 - max(a1, b1) or 1
		elif b1 <= a1 <= b2:
			# se A è dentro B
			return min(b2, a2) - a1 or 1
		elif b1 <= a2 <= b2:
			# se A è dentro B
			return a2 - max(a1, b1) or 1
		# se non si sovrappongono, ritorna 0
		return 0
	
	def overlap2D(a, b) -> bool:
		"""
		Controlla se due rettangoli si sovrappongono di una certa percentuale `config.BB_COMPENETRATION_PERCENT`
		"""

		# controllo se i rettangoli si sovrappongono sull'asse x
		if ((diff1 := overlap1D(a.x1, a.x2, b.x1, b.x2)) and
			# controllo se i rettangoli si sovrappongono sull'asse y
			 (diff2 := overlap1D(a.y1, a.y2, b.y1, b.y2))):

			# calcolo l'area minima tra i due rettangoli
			minConeArea = min(a.area, b.area)

			# controllo se la compenetrazione è maggiore della percentuale
			if diff1 * diff2 >= config.BB_COMPENETRATION_PERCENT * minConeArea:
				return True
		return False

	if not cones:
		return True

	for c in cones:
		# if c.deleted:
		# 	continue
		# controllo se i rettangoli si sovrappongono
		if overlap2D(cone, c):
			# controllo se il cono è più piccolo
			if cone.area <= c.area:
				# se è più piccolo, non è valido
				return error(cone, "Overlap")
			else:
				# se è più grande, elimina il cono dalla lista
				c.deleted = True
				error(c, "Overlap")

	return True
