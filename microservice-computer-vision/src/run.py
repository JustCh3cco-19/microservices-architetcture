import os
import cv2
import time
import logging
import argparse

import config
from computerVision import ComputerVision
from utils.file import gen_file_path
from utils.graph import plot_graph_error
from src.depthCamera import DepthCamera

import dummy_dvde_api as dvde
import sys
import json

def send_cones_matrix(cones_matrix, established_connection, established_channel) -> None:

	print("Sending the cones through RabbitMQ..")
	message = json.dumps(cones_matrix)

	connection = None
	channel = None

	while connection == None:
		
		connection = established_connection
		channel = established_channel

		try:
			connection, channel = dvde.produce("computer_vision", message, connection = connection, channel = channel)
		except (dvde.pika.exceptions.AMQPConnectionError, RuntimeError) as err:
			# Want to keep trying in case of errors
			print('Connection failed. Probably RabbitMQ is still starting up, sleeping for 4s..')

			established_connection = None
			established_channel = None
			# This is here just to ensure that the while loop repeats in case of error
			connection = None

			time.sleep(4)

	return connection, channel

def main(args) -> None:
	# Inizializzazione oggetti
	cv = ComputerVision(args.cuda, args.display, args.convert_bgr, args.record_cv, bag_name)
	depthCamera = DepthCamera(args.src_video, args.src_settings, args.record_bag)

	erros = []
	acc = []
	frames = 0

	connection = None
	channel = None

	if args.display:
		print("Premi 'p' per mettere in pausa")
		print("Premi 'esc' per uscire")

	# salvataggio coni su file (per testing in SLAM)
	if args.save_cones:
		prefix = "cones"
		if bag_name:
			prefix += "_" + bag_name
		file_cones_name = gen_file_path(config.CONES_PATH, prefix, "txt")
		file_cones = open(file_cones_name, "w")
		logging.info(f"Salvataggio coni attivato su {file_cones_name}")

	# visualizzazione frame di profondità
	if args.depth:
		cv2.namedWindow("Depth Frame", cv2.WINDOW_AUTOSIZE)

	try:
		while True:
			frames += 1
			logging.info(f"--------------- Frame {frames} ---------------")
			time_1 = time.perf_counter()

			# Ottengo i frame dalla camera
			depth_image, color_image, accel, gyro = depthCamera.get_frame()

			if args.depth:
				cdepth_image = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
				cv2.imshow("Depth Frame", cdepth_image)

			if args.log_error:
				erros.append(DepthCamera.get_depth_error(depth_image))
				acc.append(accel)

			# Ottengo i coni
			(cones_x, cones_y, cone_colors, color_confs, 
				dist_confs, timestamp) = cv.getCones(color_image, depth_image)

			cones_matrix = [ [cones_x[i], cones_y[i], cone_colors[i]] for i in range(len(cones_x)) ]	

			connection, channel = send_cones_matrix(cones_matrix, connection, channel)

			if args.save_cones:
				file_cones.write(f"{timestamp} {cones_x} {cones_y} {cone_colors} {color_confs} {dist_confs}\n")

			time_2 = time.perf_counter()
			logging.debug(f"Tempo totale: {time_2 - time_1:0.4f} secondi")

			# se è attivo sbs allora aspetta un tasto per mostrare il prossimo frame
			if args.display:
				key = cv2.waitKey(0 if args.sbs else 1)

				# se premuto 'p' metti in pausa
				if key == ord('p'):
					cv2.waitKey(0)

				# if pressed escape exit program
				if key == 27:
					break

	except KeyboardInterrupt:
		pass

	# chiusura finestre e rilascio risorse
	cv.close()
	depthCamera.release()
	
	if args.depth:
		cv2.destroyAllWindows()
		cv2.waitKey(1)
	
	if args.save_cones:
		file_cones.close()

	if args.log_error:
		plot_graph_error(erros, acc)
	
	logging.info("Programma terminato")

if __name__ == '__main__':

	# Inizializzazione parser
	parser = argparse.ArgumentParser(
		description='Modulo di Computer Vision per la vettura Driverless di Sapienza Fast Charge')
	# Parametro percorso video
	parser.add_argument('-i', '--src_video', type=str, nargs='?',
							help='Percorso del file video da analizzare, se non specificato usa lo stream',
							default='stream')
	# Parametro percorso settings
	parser.add_argument('-s', '--src_settings', type=str, nargs='?',
							help='Percorso del file di calibrazione/impostazioni della camera, se non specificato vengono usati automaticamente dei valori di default. Esempio formattazione: \'c:\\\\Users\\feder\\Desktop\\Settings\\customSettings2.json\'',
							default='default')

	# Parametro Display
	parser.add_argument('-d', '--display', action='store_true',
							help='Abilita la visualizzazione degli output dell\'inferenza a schermo')
	# Parametro Parallelizzazione
	parser.add_argument('-c', '--cuda', action='store_true',
							help='Abilita l\'esecuzione dell\'algoritmo su GPU tramite CUDA, NECESSARIA UNA SCHEDA VIDEO NVIDIA')

	parser.add_argument('--sbs' , action='store_true',
						help='Abilita il video in waitKey 0', default=False)
		
	parser.add_argument('-bgr', '--convert_bgr', action='store_true',
						help='Converte il frame in formato BGR, per i video registrati in rgb quando non si usa il file di settings', default=False)
	# registrazione video con opencv
	parser.add_argument('-rcv', '--record-cv', action='store_true',
						help='Abilita la registrazione del video', default=False)
	# registrazione video della camera (.bag) 
	parser.add_argument('-rbag', '--record-bag', action='store_true',
						help='Abilita la registrazione del video', default=False)
	# Mostra il frame di profondità
	parser.add_argument('--depth', action='store_true',
						help='Mostra il frame di profondità', default=False)
	# Salvataggio coni con timestamp su file
	parser.add_argument('--save-cones', action='store_true',
						help='Salva i coni con timestamp su file', default=False)
	# Salvataggio coni con timestamp su file
	parser.add_argument('--log-error', action='store_true',
						help='Salva l\'errore', default=False)

	# Assegnazione parametri passati da riga di comando
	args = parser.parse_args()

	# controllo che esistano le cartelle per i file di output se sono attive le flag
	if args.save_cones and not os.path.exists(config.CONES_PATH):
		os.makedirs(config.CONES_PATH)
	if args.record_cv and not os.path.exists(config.CV_VIDEO_PATH):
		os.makedirs(config.CV_VIDEO_PATH)
	if args.record_bag and not os.path.exists(config.BAG_VIDEO_PATH):
		os.makedirs(config.BAG_VIDEO_PATH)

	if args.src_video != "stream":
		bag_name = args.src_video.split("/")[-1].split(".")[0]
	else:
		bag_name = ""

	logpath = os.environ.get("LOGPATH", config.LOGPATH)
	if logpath and not os.path.exists(logpath):
		os.makedirs(logpath)
	logging.basicConfig(
		level=os.environ.get("LOGLEVEL", config.LOGLEVEL),
		format='%(asctime)s - %(levelname)s - %(message)s',
		handlers=[
			logging.StreamHandler()
		],
		datefmt='%M:%S'
	)
	if logpath:
		logging.getLogger().addHandler(logging.FileHandler(
			gen_file_path(logpath, f"log-{bag_name}", "log"), mode='w'))

	# Esecuzione del programma
	main(args)