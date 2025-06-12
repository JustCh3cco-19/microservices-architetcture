import cv2
import logging
import datetime
import numpy as np
from typing import Tuple, Optional

import config
from src.cone import Cone
from src.frames import Frames
from utils.colors import Colors
from utils.file import gen_file_path
from utils.decorators import log_time
from src.coneDetection import ConeDetector
from src.coneDiscrimination import validateCone


class ComputerVision:
	"""
	Interfaccia per computer vision

	permette di ottenere i coni con posizione colore e distanza
	viene utilizzata sia da cmd che da matlab

	- cuda: abilita l'esecuzione su GPU tramite CUDA
	- enable_display: abilita la visualizzazione dei frame
	- convert_bgr: converte il frame in formato BGR, per i video registrati in rgb quando non si usa il file di settings
	- record: abilita la registrazione del video
	- bag_name: nome del file bag, usato per la registrazione del video
	"""

	def __init__(self, cuda: Optional[bool]=False,
			  enable_display: Optional[bool]=False, convert_bgr: Optional[bool]=False,
			  record: Optional[bool]=False, bag_name: Optional[str]="") -> None:
		self.enable_display = enable_display
		self.convert_bgr = convert_bgr
		self.record = record
		self.frames_count = 0

		# inizializza la finestra per la visualizzazione
		if self.enable_display:
			cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)

		# inizializza la registrazione del video in mp4
		if self.record:
			filename = gen_file_path(config.CV_VIDEO_PATH, bag_name, "mp4")
			self.out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'),
							  30, (config.FRAME_WIDTH, config.FRAME_HEIGHT))
		else:
			self.out = None

		# impostazioni per l'esecuzione su GPU tramite CUDA o su CPU
		if cuda:
			self.cuda = '0'
		else:
			self.cuda = 'cpu'
		# inizializza il detector
		self.dnn = ConeDetector(self.cuda, config.WEIGHTS, 
						  conf_threshold=config.CONF_THRESHOLD, 
						  iou_threshold=config.IOU_THRESHOLD)

	@log_time
	def getCones(self, color_frame: np.ndarray, depth_frame: np.ndarray
			  ) -> Tuple[list, list, list, list, list, str]:
		"""
		Restituisce i coni con posizione colore e distanza nel frame corrente

		formato:
		((X), (Y), (colori), (confidenze colore), (confidenze distanza), (timestamp))
		scelto per essere comodo da manipolare in matlab
		"""

		timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

		if self.enable_display or self.record:
			self.frames_count += 1
		cones_x = list()
		cones_y = list()
		cones_color = list()
		color_confidences = list()
		pos_confidences = list()

		try:
			frames = Frames(color_frame, depth_frame, self.enable_display,
					default_resize=True, record=self.record, nbr=self.frames_count)

			# converte il frame in formato BGR
			if self.convert_bgr:
				frames.rgb2bgr()

			# riconosce i coni
			cones = self.dnn.forward(frames.color_frame)

			# creazione oggetti coni
			cones = [Cone(x1, y1, x2, y2, confidence, frames)
				for x1, y1, x2, y2, confidence in cones]

			# itera i coni riconosciuti
			for i, cone in enumerate(cones):
				try:
					# controlla se il cono è valido
					if validateCone(cone, cones[i+1:]):
						# arrotonda le coordinate
						x, y, z = cone.position

						# aggiunge le coordinate e il colore del cono alle liste
						cones_x.append(x)
						cones_y.append(y)
						cones_color.append(cone.color)
						color_confidences.append(cone.color_confidence)
						pos_confidences.append(cone.distance_confidence)
					else:
						# se il cono non è valido, lo colora di grigio
						cone.color_bgr = Colors.GRAY
					frames.print_bbox(cone)

				except Exception as e:
					logging.error(f"Errore durante la gestione del cono: {e}")

			logging.info(f"Coni validi: {len(cones_x)}/{len(cones)}")

			if self.enable_display:
				# visualizzazione frame con coni
				frames.show()

			# salva il frame nel video
			frames.save_frame(self.out)

		except Exception as e:
			logging.error(f"Errore durante il riconoscimento dei coni: {e}")

		return (cones_x, cones_y, cones_color,
				color_confidences, pos_confidences, timestamp)

	def close(self) -> None:
		"""
		Chiude le finestre aperte
		"""

		if self.enable_display:
			cv2.destroyAllWindows()
			cv2.waitKey(1)

		if self.out:
			self.out.release()
