import cv2
import numpy as np
from typing import Tuple, Optional

import config
from utils.colors import Colors


class Frames:
	"""
	Classe per rappresentare un frame di colore e profondità
	contiene molte funzionalità utili per la manipolazione dei frame

	- color_frame: frame di colore in formato RGB
	- depth_frame: frame di profondità in formato 16 bit
	- color_frame_cp: copia del frame di colore per la visualizzazione
	- default_resize: se True ridimensiona i frame alla dimensione di default
	"""

	def __init__(self, color_frame: np.ndarray, depth_frame: np.ndarray,
				enable_display: bool=False, default_resize: bool=False,
				record: bool=False, nbr: Optional[int]=None) -> None:
		assert color_frame is not None and depth_frame is not None, "I frame non possono essere None"

		self.color_frame = color_frame
		self.depth_frame = depth_frame
		self.color_frame_cp = None
		self.record = record
		
		# salva le dimensioni originali del frame
		self.original_frame_dim = (color_frame.shape[1], color_frame.shape[0])

		# ridimensiona i frame se richiesto
		if default_resize:
			self.resize(config.FRAME_WIDTH, config.FRAME_HEIGHT)
		else:
			assert color_frame.shape[1] == depth_frame.shape[1] and color_frame.shape[0] == depth_frame.shape[0], \
				"I frame devono essere della stessa dimensione"
		
		# copia del frame di colore per la visualizzazione
		if enable_display or record:
			self.color_frame_cp = np.copy(self.color_frame)
			# mette una linea per evidenzaiare la divisione tra le due immagini
			cv2.line(self.color_frame_cp, (round(config.FRAME_WIDTH/2), 0), 
				(round(config.FRAME_WIDTH/2), config.FRAME_HEIGHT), Colors.RED, 1)
			# mette due linee per evidenzaiare il frame centrale
			# cv2.line(color_frame_cp, (round(config.FRAME_WIDTH/4), 0), (round(config.FRAME_WIDTH/4), config.FRAME_HEIGHT), Colors.GREEN, 1)
			# cv2.line(color_frame_cp, (round(config.FRAME_WIDTH*3/4), 0), (round(config.FRAME_WIDTH*3/4), config.FRAME_HEIGHT), Colors.GREEN, 1)
			if nbr is not None:
				# mette il numeri del frame in alto a destra
				cv2.putText(self.color_frame_cp, f"#{nbr}", (0, 20),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, Colors.GREEN, 1)
		else:
			self.color_frame_cp = None

	@property
	def width(self) -> int:
		return self.color_frame.shape[1]

	@property
	def height(self) -> int:
		return self.color_frame.shape[0]
	
	@property
	def area(self) -> int:
		return self.width * self.height

	def resize(self, width: int, height: int) -> None:
		"""
		Ridimensiona il frame
		"""

		self.color_frame = cv2.resize(self.color_frame, (width, height), interpolation = cv2.INTER_AREA)
		self.depth_frame = cv2.resize(self.depth_frame, (width, height), interpolation = cv2.INTER_AREA)
		if self.color_frame_cp is not None:
			self.color_frame_cp = cv2.resize(self.color_frame_cp, (width, height), interpolation = cv2.INTER_AREA)

	def rgb2bgr(self) -> None:
		"""
		Converte il frame da RGB a BGR
		"""

		self.color_frame = cv2.cvtColor(self.color_frame, cv2.COLOR_RGB2BGR)
		if self.color_frame_cp is not None:
			self.color_frame_cp = cv2.cvtColor(self.color_frame_cp, cv2.COLOR_RGB2BGR)

	def get_original_pos(self, x: int, y: int) -> Tuple[int, int]:
		"""
		Ritorna le coordinate originali del frame prima del resize
		"""

		return (round(x * self.original_frame_dim[0] / self.width), 
				round(y * self.original_frame_dim[1] / self.height))

	def get_depth_error(self):
		"""
		Calcola la percentuale di pixel con errore (quanti pixel hanno valore 0)
		"""

		depth_error = np.count_nonzero(self.depth_frame == 0) / (self.width * self.height)
		return round(depth_error * 100, 2)
	
	def get_depth(self, x: int, y: int) -> float:
		"""Ritorna la distanza del punto nel frame di profondità in metri"""
		# TODO: da vedere la sensibilità della camera per la distanza, così da mettere un giusto valore in round

		return round(self.depth_frame[y, x] * config.CAMERA_DEPTH_SCALE, 2)
	
	def get_color(self, x: int, y: int) -> Tuple[int, int, int]:
		"""Ritorna il colore del punto nel frame di colore in formato BGR"""

		assert x >= self.x1 and x <= self.x2 and y >= self.y1 or y <= self.y2

		return self.color_frame[y, x]
	
	def show(self, name: str="Color Stream") -> None:
		"""
		Mostra il frame
		"""

		if self.color_frame_cp is not None:
			cv2.imshow(name, self.color_frame_cp)

	def save_frame(self, out: cv2.VideoWriter):
		if self.color_frame_cp is None or out is None:
			return
		out.write(self.color_frame_cp)

	def print_bbox(self, cone):
		"""
		Mostra un rettangolo nel frame
		"""

		if self.color_frame_cp is not None:
			# Aggiunge riquadro al cono del colore individuato
			# sopra il riquadro scrive la distanza e sotto la confidenza
			cv2.rectangle(self.color_frame_cp, (cone.x1, cone.y1), (cone.x2, cone.y2), cone.color_bgr, 2)

			# se il cono non è valido è di colore GRAY
			if cone.color_bgr != Colors.GRAY:
				# cv2.putText(self.color_frame_cp, f"{cone.confidence}%", (cone.x2, cone.y2), 
				# 	cv2.FONT_HERSHEY_SIMPLEX, 0.35, Colors.GREEN, 1)				# scrive la confidenza sotto la bounding box
				if cone.distance is not None:
					# se è stata calcolata la distanza
					# sopra la bounding box scrive la distanza
					# cv2.putText(self.color_frame_cp, f"{cone.distance} m", (cone.x2, cone.y1 - 5 if cone.y1 - 5 > 0 else cone.y1),
					# 	cv2.FONT_HERSHEY_SIMPLEX, 0.4, Colors.GREEN, 1)			# scrive la distanza sopra la bounding box
					# posizione x, y del cono
					# cv2.putText(color_frame_cp, f"({x}, {y}, {z})", (x2, y1 - 20 if y1 - 20 > 0 else y1),
					# 	cv2.FONT_HERSHEY_SIMPLEX, 0.4, Colors.GREEN, 2)				# scrive la posizione sopra la bounding box
					# confidence del colore e della distanza
					cv2.putText(self.color_frame_cp, f"color: {round(cone.color_confidence * 100, 2)}%", (cone.x2, cone.y1), 
						cv2.FONT_HERSHEY_SIMPLEX, 0.4, Colors.GREEN, 1)
					cv2.putText(self.color_frame_cp, f"dist: {round(cone.distance_confidence * 100, 2)}%", (cone.x2, cone.y1 + 10), 
						cv2.FONT_HERSHEY_SIMPLEX, 0.4, Colors.GREEN, 1)
					# # dimensione della bb
					# cv2.putText(self.color_frame_cp, f"({cone.real_width:.2f} x {cone.real_height:.2f}) h/w={(cone.height/cone.width):.2f}",
					# 	(cone.x1, cone.y1 - 20 if cone.y1 - 20 > 0 else cone.y1),
					# 	cv2.FONT_HERSHEY_SIMPLEX, 0.4, Colors.GREEN, 2)
