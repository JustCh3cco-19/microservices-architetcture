import json
import logging
import numpy as np
import pyrealsense2 as rs

from utils.file import gen_file_path
from utils.decorators import log_time


class DepthCamera():
	"""
	Classe che gestisce la camera di profondità Intel RealSense D455
	"""

	DS5_product_ids = ["0AD1", "0AD2", "0AD3", "0AD4", "0AD5", "0AF6", "0AFE", "0AFF", "0B00", "0B01", "0B03", "0B07", "0B3A", "0B5C"]

	def __init__(self, nomeFile, settings, record=False):
		"""
		Inizializza la camera di profondità

		- nomeFile: nome del file di registrazione
		- settings: nome del file di impostazioni
		- cmdline: se True, la registrazione viene avviata da linea di comando
		"""

		self.record = record

  		# Configure depth and color streams
		self.pipeline = rs.pipeline()
		config = rs.config()

		if settings!='default':
			jsonObj = json.load(open(settings))
			config.enable_stream(rs.stream.depth, int(jsonObj['viewer']['stream-width']), int(jsonObj['viewer']['stream-height']), rs.format.z16, int(jsonObj['viewer']['stream-fps']))
			config.enable_stream(rs.stream.color, int(jsonObj['viewer']['stream-width']), int(jsonObj['viewer']['stream-height']), rs.format.bgr8, int(jsonObj['viewer']['stream-fps']))
			config.enable_stream(rs.stream.accel)
			config.enable_stream(rs.stream.gyro)

			
			logging.info("Sprecifiche principali utilizzate:\nW: ", int(jsonObj['viewer']['stream-width']))
			logging.info("H: ", int(jsonObj['viewer']['stream-height']))
			logging.info("FPS: ", int(jsonObj['viewer']['stream-fps']))
		else:
			logging.warning("Utilizzate specifiche di default")
		
		if nomeFile != 'stream':
			logging.info("Caricamento registrazione da file...")
			rs.config.enable_device_from_file(config, nomeFile)
		
		# else:
		# 	print("Stream con la camera")
		# 	dev = self.find_device_that_supports_advanced_mode()
		# 	advnc_mode = rs.rs400_advanced_mode(dev)
		# 	# print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")

		# 	# Mostra i parametri di default del dispositivo
		# 	# serialized_string = advnc_mode.serialize_json()
		# 	# print("Controls as JSON: \n", serialized_string)
		# 	# as_json_object = json.loads(serialized_string)

		# 	json_string = str(jsonObj).replace("'", '\"')
		# 	advnc_mode.load_json(json_string)

		# 	# Mostra i parametri di default del dispositivo
		# 	# serialized_string = advnc_mode.serialize_json()
		# 	# print("Controls updated: \n", serialized_string)

		if self.record:
			filename = gen_file_path("outputs/bags", ext="bag")
			logging.info(f"Avvio registrazione su file: {filename}")
			rs.config.enable_record_to_file(config, filename)

		cfg = self.pipeline.start(config)

		logging.info("Camera di profondità avviata")

		# print("DEPTH SCALE:", cfg.get_device().first_depth_sensor().get_depth_scale())

	@log_time
	def get_frame(self):
		"""
		Ritorna un frame della registrazione come array numpy

		:return: frame della registrazione
		"""
		
		def gyro_data(gyro):
			return np.asarray([gyro.x, gyro.y, gyro.z])

		def accel_data(accel):
			return np.asarray([accel.x, accel.y, accel.z])
		
		# align_to = rs.stream.color
		# align = rs.align(align_to)

		frames = self.pipeline.wait_for_frames()

		# Align the depth frame to color frame
		# aligned_frames = align.process(frames)
		aligned_frames = frames

		depth_frame = aligned_frames.get_depth_frame()
		color_frame = aligned_frames.get_color_frame()

		# depth profile:
		# print(depth_frame.profile.as_video_stream_profile().intrinsics)

		if len(aligned_frames) < 4:
			accel = None
			gyro = None
			logging.warning("Dati di accelerazione e giroscopio non disponibili")
		else:
			accel = accel_data(aligned_frames[2].as_motion_frame().get_motion_data())
			gyro = gyro_data(aligned_frames[3].as_motion_frame().get_motion_data())

		# Tolto perchè non è necessario
		# colorizer = rs.colorizer()
		# colorizer.set_option(rs.option.color_scheme, 0)
		# cdepth_image = np.asanyarray(colorizer.colorize(depth_frame).get_data())
		
		depth_image = np.asanyarray(depth_frame.get_data())
		
		color_image = np.asanyarray(color_frame.get_data())

		# TODO: vedere se serve usare la funzione di realsense per allineare i frame
		# TODO: aggiungere un controllo per verificare che i frame siano stati acquisiti correttamente

		return depth_image, color_image, accel, gyro #, cdepth_image

	def release(self):
		"""
		Interrompe la pipeline della camera di profondità
		"""

		logging.info("Chiusura camera di profondità")
		self.pipeline.stop()

	@staticmethod
	def get_depth_error(depth_frame):
		"""
		Calcola la percentuale di pixel con errore (quanti pixel hanno valore 0)
		"""

		depth_error = np.count_nonzero(depth_frame == 0) / (depth_frame.shape[0] * depth_frame.shape[1])
		return round(depth_error * 100, 2)

	@staticmethod
	def find_device_that_supports_advanced_mode() :
		ctx = rs.context()
		devices = ctx.query_devices()
		for dev in devices:
			if dev.supports(rs.camera_info.product_id) and str(dev.get_info(rs.camera_info.product_id)) in DepthCamera.DS5_product_ids:
				if dev.supports(rs.camera_info.name):
					logging.info("Found device that supports advanced mode:", dev.get_info(rs.camera_info.name))
				return dev
		raise Exception("No device that supports advanced mode was found")
