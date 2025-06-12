import cv2
import numpy as np
from typing import Tuple

import config
from utils.colors import Colors
from src.frames import Frames
from src.positionRT import position
from src.distance import getConeDistance
from src.colorDetection import colorDetector


class Cone:
	"""
	Classe per rappresentare un cono
	"""

	def __init__(self, x1: int, y1: int, x2:int, y2: int, confidence: int, frames: Frames) -> None:
		x1, y1, x2, y2 = max(0, x1), max(0, y1), min(config.FRAME_WIDTH, x2), min(config.FRAME_HEIGHT, y2)

		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.confidence = confidence
		self.frames = frames

		# colore
		self._color: int = None
		self.color_bgr = Colors.GRAY
		self.color_confidence = 0
		self._mask: np.ndarray = None
		# distanza e posizione
		self._distance: float = None
		self.distance_confidence: float = 0
		self._position: Tuple[int, int, int] = None
		# invece di essere rimosso se non valido, viene segnato come eliminato
		self.deleted = False

	@property
	def bb_color(self):
		"""Ritorna il sframe di colore solo della bounding box"""

		return self.frames.color_frame[self.y1:self.y2, self.x1:self.x2]

	@property
	def width(self) -> int:
		"""Calcola la larghezza della bounding box"""

		return self.x2 - self.x1

	@property
	def height(self) -> int:
		"""Calcola l'altezza della bounding box"""

		return self.y2 - self.y1
	
	@property
	def area(self) -> int:
		"""Calcola l'area della bounding box"""

		return self.width * self.height

	@property
	def center(self):
		"""Calcola il centro della bounding box rispetto al frame"""

		return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

	@property
	def color(self) -> int:
		"""Calcola il colore del cono"""

		if self._color is not None:
			return self._color

		(self._color, self.color_bgr,
			self._mask, self.color_confidence) = colorDetector(self)
		return self._color

	@property
	def hsv_mask(self) -> np.ndarray:
		"""Maschera HSV del colore del cono"""

		if self._mask is not None:
			return self._mask
		cone_info = [cone for cone in config.CONES if cone['id'] == self.color][0]
		hsv = cv2.cvtColor(self.bb_color, cv2.COLOR_BGR2HSV)
		lower_hsv, upper_hsv = cone_info['cone_hsv']
		self._mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
		return self._mask

	@property
	def distance(self) -> float:
		"""Calcola la distanza del cono"""

		if self._distance is not None:
			return self._distance
		self._distance, self.distance_confidence = getConeDistance(self)
		if self._distance is None:
			self.color_bgr = Colors.GRAY
		return self._distance

	@property
	def position(self) -> Tuple[int, int, int]:
		"""Calcola la posizione del cono"""

		if self._position is not None:
			return self._position
		x, y = self.frames.get_original_pos(*self.center)
		self._position = position(x, y, self.distance)
		self._position = map(lambda i: round(i, 2), self._position)
		return self._position

	def __str__(self) -> str:
		return f"Cone {self.width}x{self.height} at [{self.x1}, {self.y1}]"
