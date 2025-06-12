"""
Cone detection system for a Formula Student Driverless vehicle

(c) 2021 - Marco De Giovanni
"""

import torch
import logging
from threading import Thread

from models.experimental import attempt_load
from utils.general import non_max_suppression
from utils.torch_utils import select_device
from utils.decorators import log_time


class InferenceEngine:

	def __init__(self, device, weights, img_size, conf_threshold, iou_threshold, augmentation):
		self.device = select_device(device)
		self.half = self.device.type != 'cpu'
		
		logging.info('Using device \"{}\"'.format(self.device))
		
		self.model = attempt_load(weights, map_location=self.device)

		self.img_size = img_size + (img_size % int(self.model.stride.max()))
		logging.info('Image size: {}'.format(self.img_size))
		
		if self.half:
			self.model.half()
			logging.info('Using FP16')
		
		self.conf_threshold = conf_threshold
		self.iou_threshold = iou_threshold
		self.augmentation = augmentation

	def forward(self, image):
		height_ratio, width_ratio, _ = image.shape
		height_ratio /= self.img_size
		width_ratio /= self.img_size

		inf_image = image[:, :, [2,1,0]]
		
		blob = torch.from_numpy(inf_image.transpose(2, 0, 1)).to(self.device)
		blob = blob.half() if self.half else blob.float()
		
		blob /= 255.0
		if blob.ndimension() == 3:
			blob = blob.unsqueeze(0)
		
		pred = self.model(blob, augment=self.augmentation)
		pred = non_max_suppression(pred[0], self.conf_threshold, self.iou_threshold, classes=None, agnostic=False)[0]

		processed_preds = []
		for p in pred:
			processed_pred = [ int(width_ratio*p[0]), int(height_ratio*p[1]), int(width_ratio*p[2]), int(height_ratio*p[3]), int(p[4]*100) ]
			processed_preds.append(processed_pred)

		return processed_preds

class MultithreadingInferenceFacade(Thread):

	def __init__(self, inference_engine):
		Thread.__init__(self)
		self._ie = inference_engine
		self._preds = []

	def import_image(self, image):
		self._image = image

	def export_preds(self):
		return self._preds

	def run(self):
		self._preds = self._ie.forward(self._image)

class ConeDetector:
	def __init__(self, device, weights, img_size=640, conf_threshold=0.25, iou_threshold=0.45, augmentation=False):
		self._img_size = img_size

		self._ie_left = InferenceEngine(device, weights, img_size, conf_threshold, iou_threshold, augmentation)
		self._ie_right = InferenceEngine(device, weights, img_size, conf_threshold, iou_threshold, augmentation)
		self._ie_center = InferenceEngine(device, weights, img_size, conf_threshold, iou_threshold, augmentation)

	@log_time
	def forward(self, image):
		"""
		Identifica i coni nell'immagine passata come parametro
		
		restiuisce una lista di coni nel formato:
		[ [x1,y1,x2,y2,confidence], ... ]
		"""

		left_dnn = MultithreadingInferenceFacade(self._ie_left)
		right_dnn = MultithreadingInferenceFacade(self._ie_right)
		center_dnn = MultithreadingInferenceFacade(self._ie_center)

		left_dnn.import_image(image[0:self._img_size, 0:self._img_size])
		left_dnn.start()

		right_dnn.import_image(image[0:self._img_size, self._img_size:(2*self._img_size)])
		right_dnn.start()

		center_dnn.import_image(image[0:self._img_size, self._img_size//2:self._img_size*3//2])
		center_dnn.start()

		left_dnn.join()
		preds = left_dnn.export_preds()

		right_dnn.join()
		for p in right_dnn.export_preds():
			# trasla i coni rilevati nel frame destro
			cone = [p[0] + self._img_size, p[1], p[2] + self._img_size, p[3], p[4]]
			preds.append(cone)

		center_dnn.join()
		for p in center_dnn.export_preds():
			cone = [p[0] + self._img_size // 2, p[1], p[2] + self._img_size // 2, p[3], p[4]]
			if self.isBBcenter(cone):
				preds.append(cone)
				logging.debug("ADDED CENTER CONE at [{}-{}]".format(cone[0], cone[2]))

		return preds

	def isBBcenter(self, cone):
		return cone[0] <= self._img_size <= cone[2]

