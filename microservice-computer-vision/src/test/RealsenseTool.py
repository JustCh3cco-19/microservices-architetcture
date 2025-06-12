import sys
import sys
# import pyrealsense2 as rs
from depthCamera import *
import positionRT as posizione
import coneDetection as cd

settingsFile = sys.argv[2]
recFile = sys.argv[1]

# Dichiarazione variabili globali a valori di default per evitare errori di lettura
# MatriceConi è la matrice che conterrà i coni da passare succcessivamente
# all funzione per il calcolo della traiettoria ottima
matriceConi = [[0 for x in range(3)] for y in range(10)]
# Contatore per evitare un overflow nella matrice
numeroConi = 0
# Valori RGB associati ai colori da identificare
giallo = [103, 76, 39]
blu = [2, 44, 59]
bianco = [255,255,255]
nero = [0,0,0]
arancione = [231,82,0]



# Funzione per individuare il colore
# compara i valori rgb dei singoli pixel mandati in input per
# trovare quello che più si avvicina al colore fra quelli standard
# inizializzati sopra. Il principio chiave applicato è quello per cui
# il vettore RGB è definibile del colore il cui scarto rispetto
# a quello di riferimento è più basso
def individuaColore(x,y):
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

# Interfaccia grafica a linea di comando
print("-----TrajectoryInference-----")

print(settingsFile, recFile)


# Inizializzazione "Oggetto" Camera
dc = DepthCamera(recFile, settingsFile)

print("1")

for i in range(100):
    ret, depth_frame, cdepth_frame, color_frame, accel, gyro = dc.get_frame()




res = cd.IdentificazioneConi(color_frame, '0','640x32.pt',False,0.25,0.45,640)

print("2")

numeroConi = 0
for c in res:
	
	print(numeroConi)
	
	xmid = round((c[0] + c[2])/2)
	ymid = round(c[3]-((c[3]-c[1])*0.3))
	distance = depth_frame[ymid,xmid]
	X, Y, Z = posizione.posizionee(xmid,ymid,distance/1000)
	
	colore = individuaColore(xmid,ymid)
	
	matriceConi[numeroConi] = [X, Y, colore]
	

	numeroConi+=1
	# limite imposto al numero di coni da passare alla funzione di triangolazione
	if numeroConi>=10:
		break



# debug    
print(matriceConi)
		
					   
			
			
				
		


ret, depth_frame, cdepth_frame, color_frame, accel, gyro = dc.get_frame()


ret, depth_frame, cdepth_frame, color_frame, accel, gyro = dc.get_frame()

res = cd.IdentificazioneConi(color_frame, '0','640x32.pt',True,0.25,0.45,640)

numeroConi = 0
for c in res:
	xmid = round((c[0] + c[2])/2)
	ymid = round(c[3]-((c[3]-c[1])*0.3))
	distance = depth_frame[ymid,xmid]
	X, Y, Z = posizione.posizionee(xmid,ymid,distance/1000)
	
	colore = input()
	if(colore=='b'):
		matriceConi[numeroConi] = [X, Y,'blu']
	else:
		matriceConi[numeroConi] = [X, Y,'giallo']

	numeroConi+=1
	# limite imposto al numero di coni da passare alla funzione di triangolazione
	if numeroConi>=10:
		break

# debug    
# print(matriceConi)

