import numpy as np
from typing import Iterable, Tuple, Union

import config
from utils.colors import Colors


class ConeDepth:
	"""
	Classe per iterare i punti del cono e calcolare la distanza
	"""

	def __init__(self, cone) -> None:
		self.cone = cone
		# punto di inizio dell'iteratore
		self.start_point = ((cone.x1 + cone.x2) // 2, round(cone.y1 + cone.height * 0.7))
		self.x, self.y = self.start_point
		# range delle x
		self.max_x = round(cone.x1 + cone.width * config.DIST_MAX_X_PERCENT)
		self.min_x = round(cone.x1 + cone.width * config.DIST_MIN_X_PERCENT)
		# range delle y (il min è da dove parte)
		self.max_y = round(cone.y1 + cone.height * config.DIST_MAX_Y_PERCENT)
		# quanti punti aggiunge a desta e sinistra ogni iterazione
		self.points_per_direction = 1

	def __iter__(self) -> Iterable[Tuple[int, int]]:
		"""
		Iteratore per i punti del cono
		"""

		# itero i punti del cono
		for x, y in self.get_points():
			# controllo se il punto è valido per la distanza e il colore
			if self.validate_depth(x, y) and self.validate_color(x, y):
				# se il punto è valido, lo restituisco
				yield x, y

	def validate_color(self, x: int, y: int) -> bool:
		"""
		Funzione per validare un punto del cono
		controlla che il punto sia nel range di colore del cono
		"""

		x, y = x - self.cone.x1, y - self.cone.y1

		return self.cone.hsv_mask[y, x]

	def validate_depth(self, x: int, y: int) -> Union[float, None]:
		"""
		Funzione per validare un punto del cono
		controlla che il punto sia nel range di profondità valido

		ritorna la distanza se il punto è valido, altrimenti None
		"""

		# controllo se il punto è nel range di profondità
		distance = self.cone.frames.get_depth(x, y)

		# se la distanza è troppo grande o troppo piccola, il punto non è valido
		if distance >= config.MAX_DISTANCE or distance <= config.MIN_DISTANCE:
			return None

		return distance

	def get_points(self) -> Iterable[Tuple[int, int]]:
		"""
		Restituisce i punti del cono come generator

		parte dal punto medio
		poi scende alla riga sotto, ritorna il punto medio, il punto a sinistra e il punto a destra
		poi continua aumentando il numero di punti per riga di +1 in entrabe le direzioni

		non vengono validati i punti
		"""

		# controllo se sono arrivato alla fine dell'alt
		if self.y >= self.max_y:
			return
		# itero tutti i punti della riga partendo dal centro e andando a sinistra e a destra in modo alternato

		# punto centrale
		yield self.x, self.y

		# punti a sinistra e a destra
		for i in range(1, self.points_per_direction):
			# punto a destra
			x = self.x + i
			if x < self.max_x:
				yield x, self.y
			# punto a sinistra
			x = self.x - i
			if x > self.min_x:
				yield x, self.y
		# scendo di una riga
		self.y += 1
		# aumento il numero di punti per riga
		self.points_per_direction += 1

		# richiamo la funzione ricorsivamente
		yield from self.get_points()


def getConeDistance(cone) -> Tuple[Union[float, None], float]:
	"""
	Restituisce la distanza del cono usando la classe ConeDepth

	- cone: cono da cui calcolare la distanza

	:return: distanza del cono
	"""

	# init della classe ConeDepth
	cone_depth = ConeDepth(cone)

	i = 0
	depth_sum = 0
	# itero i punti del cono validi
	for x, y in cone_depth:
		# sommo le distanze
		depth_sum += cone.frames.get_depth(x, y)
		if cone.frames.color_frame_cp is not None:
			# colora i punti usati per il calcolo della distanza
			cone.frames.color_frame_cp[y, x] = Colors.GREEN
		if i >= config.MAX_POINTS:
			break
		i += 1

	if i == 0:
		# se non trova punti validi, prende il primo punto con la distanza valida
		point = cone_depth.start_point

		# se il punto non è valido, non è possibile calcolare la distanza
		if not cone_depth.validate_depth(*point):
			return None, 0

		# se il punto è valido, la distanza del cono è la distanza del punto
		distance = cone.frames.get_depth(*point)

		if cone.frames.color_frame_cp is not None:
			# colora il punto usato per il calcolo della distanza
			cone.frames.color_frame_cp[point[1], point[0]] = Colors.GREEN

	else:
		# altrimenti calcola la media delle distanze
		distance = round(depth_sum / i, 2)

	# la confidence dipende dal numero di punti usati per il calcolo
	# e dalla distanza, più siamo vicini e più la confidence è alta
	confidence = i / config.MAX_POINTS * (1 - (distance / config.MAX_DISTANCE))

	return distance, confidence
