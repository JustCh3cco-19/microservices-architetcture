from depthCamera import *
import coneDetection as cd
import positionRT as posizione
import test.Triangolazione as triangolazione

# Funzione per individuare il colore
# compara i valori rgb dei singoli pixel mandati in input per
# trovare quello che più si avvicina al colore fra quelli standard
# inizializzati sopra. Il principio chiave applicato è quello per cui
# il vettore RGB è definibile del colore il cui scarto rispetto
# a quello di riferimento è più basso
def individuaColore(color_frame, x, y):
	giallo = [103, 76, 39]
	blu = [2, 44, 59]
	# il color frame passato ha la struttura bgr
	bgr = color_frame[y,x]
	rgb = [int(bgr[2]), int(bgr[1]), int(bgr[0])]
	print(rgb)
	subGiallo = [rgb[i] - giallo[i] for i in range(len(rgb))]
	subBlu = [rgb[i] - blu[i] for i in range(len(rgb))]
	difGiallo = 0
	difBlu = 0
	#difBianco = 0
	for e in subGiallo:
		difGiallo += abs(e)
	for e in subBlu:
		difBlu += abs(e)
  
	print(difBlu, difGiallo)
	match = min(difBlu, difGiallo)
	if match == difGiallo:
		res = 'giallo'
	elif match == difBlu:
		res = 'blu'
	else: 
		res = 'blu'
	return res

def camera_init(fname, confname):
	return DepthCamera(fname, confname)

def camera_close(depthcamera):
	return depthcamera.pipeline.stop()

def get_frame_from_camera(depthcamera):
	# Acquisizione dati del frame attuale della camera: ret, depth_frame, cdepth_frame, color_frame, accel, gyro
	return depthcamera.get_frame()

def triangolate(infoConi):
    
    matriceConi = list(infoConi)
    
    return triangolazione.triangolazione(matriceConi, len(matriceConi), 10)

def get_cones_from_frame(frame):
    
	color_frame = frame[3]
	depth_frame = frame[1]
	distance = 1
	matriceConi = [[0 for x in range(3)] for y in range(10)]
	numeroConi = 0

	cones = cd.IdentificazioneConi(color_frame,'0','640x32.pt',True,0.25,0.45,640)

	# per ogni coni individuato si identifica il pixel da utilizzare
	# per il calcolo del colore cono, si calcola la posizione nello spazio 2D
	# e lo si aggiunge alla matrice dei coni che verrà passata alla funzione
	# per la triangolazione
	for cone in cones:
		# Calcolo punto all'interno della BB che verrà utilizzato per il calcolo della distanza
		# e del colore
		#     /\
		#    /__\
		#   /____\
		#  /  xx  \
		# /________\
		# ----------  
		# Il punto per ora è scelto prendendo orizzontalmente
		# la metà della bounding box e verticalmente prendendo
		# un punto al 30% dell'altezza della BB partendo dal basso
		# le due x indicano circa la posizione del cono
		xmid = round((cone[0] + cone[2]) / 2)
		ymid = round(cone[3] - ((cone[3] - cone[1]) * 0.3))
		distance = depth_frame[ymid, xmid]

		X, Y, Z = posizione.posizionee(xmid, ymid, distance/1000)

		# Codice per utilizzare l'algoritmo di individuazione del colore dei coni
		matriceConi[numeroConi] = [X, Y, individuaColore(color_frame, xmid, ymid)]

		numeroConi += 1
		# limite imposto al numero di coni da passare alla funzione di triangolazione
		if numeroConi >= 10:
			break

	return matriceConi, numeroConi