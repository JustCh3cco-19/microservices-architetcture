import triangle
import numpy as np
#import matplotlib.pyplot as plt
from scipy import interpolate

# ricezione parametri in input: xConi, yConi, coloreConi, maxConi (coni per colore massimi)
def pathPlanning(xConi, yConi, coloreConi, maxConi, xMacchina, yMacchina, intornoMacchina):
	try:
		
		# errore in caso di lista di coni individuati nulla
		if len(xConi) == 0:
			print("Nessun cono individuato")
			return [], []
		
		# errore in caso di zero coni individuati di un colore specifico (1 o 2)
		if np.count_nonzero(coloreConi==1) == 0 or np.count_nonzero(coloreConi==2) == 0:
			print("Non ci sono abbastanza coni di un colore specifico")
			return [], []
		
		# interpolazione semplificata in caso di una sola coppia di colori gialli e blu individuati
		if np.count_nonzero(coloreConi==1) == 1:
			
			# calcola midpoint fra due coni di colore diverso
			bluIndex = np.where(coloreConi == 1)[0]
			yellowIndex = np.where(coloreConi == 2)[0]
			xMid = [(xConi[bluIndex[0]] + xConi[yellowIndex[0]])/2]
			yMid = [(yConi[bluIndex[0]] + yConi[yellowIndex[0]])/2]
			xMid.append(xMacchina)
			yMid.append(yMacchina)
			xMid = np.asarray(xMid)
			yMid = np.asarray(yMid)
			
			# interpolazione
			wpx, wpy = interpolazione(xMid, yMid)

			# plot xMid, yMid
			# plt.plot(xMid, yMid, 'ro')
			# plt.show()
			return wpx, wpy

		# accorpo l'input in una matrice
		input_matrix = np.column_stack((xConi,yConi,coloreConi))
		# divisione input in matriceBlu e matriceGialla
		blueMatrix, yellowMatrix = getSortedMatrixOP(input_matrix, xMacchina, yMacchina, 100)
		# rimuovi a blueMatrix tutta la terza colonna
		#print(blueMatrix)
		blueMatrix = np.delete(blueMatrix, 2, axis=1)
		blueMatrix = blueMatrix.tolist()
		# rimuovi a yellowMatrix tutta la terza colonna
		yellowMatrix = np.delete(yellowMatrix, 2, axis=1)
		yellowMatrix = yellowMatrix.tolist()
		#plt.show()
		
		# mat = getSortedMatrix(input_matrix)
		# ordinamento dei coni
		# blueMatrix, yellowMatrix = divideMatrix(input_matrix)
		# blueMatrix = getSortedMatrix(blueMatrix)
		# yellowMatrix = getSortedMatrix(yellowMatrix)
	
		#print(blueMatrix, type(blueMatrix))
		
		# creazione di una matrice contenente i coni alternati e ordinati
		matrix = []
		if maxConi <= min(len(blueMatrix), len(yellowMatrix)):
			for i in range(maxConi):
				matrix.append(blueMatrix[i])
				matrix.append(yellowMatrix[i])
				
		elif len(blueMatrix) == len(yellowMatrix):
			for i in range(len(blueMatrix)):
				matrix.append(blueMatrix[i])
				matrix.append(yellowMatrix[i])
				
		elif len(blueMatrix) < len(yellowMatrix):
			for i in range(len(blueMatrix)):
				matrix.append(blueMatrix[i])
				matrix.append(yellowMatrix[i])
				
		elif len(blueMatrix) > len(yellowMatrix):
			for i in range(len(yellowMatrix)):
				matrix.append(blueMatrix[i])
				matrix.append(yellowMatrix[i])
			matrix.append(blueMatrix[len(yellowMatrix)])
		matrix = np.array(matrix)
		
		# definizione dei costraints della triangolazione
		segments = [(0,1)]
		# aggiunta dei costraints
		for i in range(len(matrix)-2):
			segments.append((i, i+2))
		segments.append((len(matrix)-2, len(matrix)-1))
		
		# definizione della geometria per la triangolazione
		geom = {
			'vertices': matrix,
			'segments': segments
		}
		
		# triangolazione di Delaunay con i costraints
		tri = triangle.triangulate(geom, 'p')
		
		# calcolo matrice di connettività della Triangolazione
		# {una matrice in cui ogni riga rappresenta una tripla contenente l'Id dei vertici che compongono ogni
		# triangolo della triangolazione}
		triangles = tri['triangles']

		# prendi i vertici dei triangoli
		tri_vertices = matrix[triangles]

		# riordinare le triple in base alla somma degli indici del triangolo nella matrice di connettività
		triangles = triangles[np.argsort(triangles.sum(axis=1))]
		
		# calcolo array (2) contenente tutte le x e tutte le y
		x = np.unique(tri_vertices[:,:,0])
		y = np.unique(tri_vertices[:,:,1])

		# calcolo una matrice contenente le tuple degli id dei vertici per ogni lato dei triangoli contenuti nella matrice dei triangoli
		edges = np.array([[(triangles[i,0], triangles[i,1]), (triangles[i,1], triangles[i,2]), (triangles[i,2], triangles[i,0])] for i in range(len(triangles))])
		
		# riordina gli indici in ciascuna tupla e rimuove i duplicati dalla matrice dei bordi
		edges = np.sort(edges, axis=2)
		edges = np.unique(edges.reshape(-1, edges.shape[-1]), axis=0)
		
		# prendo solo i segmenti che contengono ai vertici un cono blu e un cono giallo
		edges = edges[(edges[:,0] % 2) != (edges[:,1] % 2)]
		
		# di ognuno di questi calcolo il midpoint
		midpoints = (matrix[edges[:,0]] + matrix[edges[:,1]]) / 2

		# inserisce la posizione della macchina in modo ordinato fra i waypoints
		midpoints = np.insert(midpoints, 0, [xMacchina, yMacchina], axis=0)


		# riordino i waypoints in base alla distanza dalla macchina
		# distances = np.sqrt(midpoints[:,0].astype(np.float64)**2+midpoints[:,1].astype(np.float64)**2)
		# sorted_indices = np.argsort(distances)
		# midpoints = midpoints[sorted_indices]
		
		# find the index of tuple [xMacchina, yMacchina] in midpoints
		index = np.where((midpoints == [xMacchina, yMacchina]).all(axis=1))[0][0]
		
		# if exists, remove the next waypoint after the car
		if index < len(midpoints)-1:
			# if absolute distance between the car and the next waypoint is less than 1m, remove the next waypoint
			if np.sqrt((midpoints[index+1][0]-xMacchina)**2+(midpoints[index+1][1]-yMacchina)**2) < intornoMacchina:
				midpoints = np.delete(midpoints, index+1, axis=0)
		# if absolute distance between the car and the previous waypoint is less than 1m, remove the previous waypoint
		if index > 0:
			if np.sqrt((midpoints[index-1][0]-xMacchina)**2+(midpoints[index-1][1]-yMacchina)**2) < intornoMacchina:
				midpoints = np.delete(midpoints, index-1, axis=0)

		#print(midpoints)
		
		# interpolazione secondo le specifiche fornite da HLC
		wpx, wpy = interpolazione(midpoints[:,0], midpoints[:,1])

		# return waypoints
		return wpx, wpy
	except Exception as e:
		print("Errore in pathPlanning",e)
		return [], []

def getSortedMatrix(input_matrix):
	
	# eliminazione attributo colore
	input_matrix = np.delete(input_matrix, 2, axis=1)
	# calcolo distanza assoluta dal veicolo per ogni cono
	distances = np.sqrt(input_matrix[:,0].astype(np.float64)**2+input_matrix[:,1].astype(np.float64)**2)
	# ordinamento della matrice in base alla distanza
	sorted_indices = np.argsort(distances)
	sorted = input_matrix[sorted_indices]
	# cast a lista
	sorted = sorted.tolist()
	return sorted

def getSortedMatrixOP(input_matrix, xMacchina, yMacchina, limite):
	
	count = 0
	bluOrdinati = []
	gialliOrdinati = []
	# bluOrdinati = np.array(bluOrdinati)
	# gialliOrdinati = np.array(gialliOrdinati)
	
	# divido la matrice di input in lista di coni blu e gialli
	coniBlu = []
	coniGialli = []
	for i in range(len(input_matrix)):
		if(input_matrix[i][2] == 1):
			coniBlu.append(input_matrix[i])
		else:
			coniGialli.append(input_matrix[i])
   
	# calcolo delle distanze dei coni dal veicolo dividendoli per colore
	distancesBlu = []
	distancesGialli = []
	for i in range(len(coniBlu)):
		distancesBlu.append(np.sqrt((coniBlu[i][0]-xMacchina)**2+(coniBlu[i][1]-yMacchina)**2))
	for i in range(len(coniGialli)):
		distancesGialli.append(np.sqrt((coniGialli[i][0]-xMacchina)**2+(coniGialli[i][1]-yMacchina)**2))

	# ordino i coni in base alla distanza dal veicolo
	blueIndices = np.argsort(distancesBlu)
	yellowIndices = np.argsort(distancesGialli)
	coniBlu = np.array(coniBlu)
	coniGialli = np.array(coniGialli)
	coniBlu = coniBlu[blueIndices]
	coniGialli = coniGialli[yellowIndices]
 
	# prendo il cono giallo e il blu più vicini al veicolo
	blue = coniBlu[0]
	yellow = coniGialli[0]
	# calcolo il midpoint fra i due coni
	midpoint = [(blue[0]+yellow[0])/2, (blue[1]+yellow[1])/2]
	# rimuovo i coni dalla lista
	coniBlu = np.delete(coniBlu, 0, axis=0)
	coniGialli = np.delete(coniGialli, 0, axis=0)

	while((np.any(coniBlu) or np.any(coniGialli)) and count < limite):
		# riordino coniBlu e coniGialli in base alla distanza dal midpoint
		distances = []
		for i in range(len(coniBlu)):
			distances.append(np.sqrt((coniBlu[i][0]-midpoint[0])**2+(coniBlu[i][1]-midpoint[1])**2))
		blueIndices = np.argsort(distances)
		coniBlu = coniBlu[blueIndices]

		distances = []
		for i in range(len(coniGialli)):
			distances.append(np.sqrt((coniGialli[i][0]-midpoint[0])**2+(coniGialli[i][1]-midpoint[1])**2))
		yellowIndices = np.argsort(distances)
		coniGialli = coniGialli[yellowIndices]
  
		# caso in cui rimangono solo coni gialli
		if(not np.any(coniBlu)):
			gialliOrdinati.append(yellow.tolist())
			yellow = coniGialli[0]
			coniGialli = np.delete(coniGialli, 0, axis=0)
			midpoint = [(blue[0]+yellow[0])/2, (blue[1]+yellow[1])/2]
		# caso in cui rimangono solo coni blu
		elif(not np.any(coniGialli)):
			bluOrdinati.append(blue.tolist())
			blue = coniBlu[0]
			coniBlu = np.delete(coniBlu, 0, axis=0)
			midpoint = [(blue[0]+yellow[0])/2, (blue[1]+yellow[1])/2]
		# caso in cui rimangono coni di entrambi i colori
		
		else:
			# calcolo la lunghezza del segmento che ha per estremi il nuovo blu trovato e il vecchio giallo
			lunghezza1 = np.sqrt((coniBlu[0][0]-yellow[0])**2+(coniBlu[0][1]-yellow[1])**2)
			# calcolo la lunghezza del segmento che ha per estremi il nuovo giallo trovato e il vecchio blu
			lunghezza2 = np.sqrt((coniGialli[0][0]-blue[0])**2+(coniGialli[0][1]-blue[1])**2)
			# calcolo la lunghezza del segmento che ha per estremi il nuovo blu trovato e il nuovo giallo trovato
			lunghezza3 = np.sqrt((coniBlu[0][0]-coniGialli[0][0])**2+(coniBlu[0][1]-coniGialli[0][1])**2)
	
			# se lunghezza1 è minore delle altre
			if(lunghezza1 < lunghezza2 and lunghezza1 < lunghezza3):
				bluOrdinati.append(blue.tolist())
				blue = coniBlu[0]
				coniBlu = np.delete(coniBlu, 0, axis=0)
			# se lunghezza2 è minore delle altre
			elif(lunghezza2 < lunghezza1 and lunghezza2 < lunghezza3):
				gialliOrdinati.append(yellow.tolist())
				yellow = coniGialli[0]
				coniGialli = np.delete(coniGialli, 0, axis=0)
			# se lunghezza3 è minore delle altre
			else:
				bluOrdinati.append(blue.tolist())
				gialliOrdinati.append(yellow.tolist())
				blue = coniBlu[0]
				yellow = coniGialli[0]
				coniBlu = np.delete(coniBlu, 0, axis=0)
				coniGialli = np.delete(coniGialli, 0, axis=0)
				# plot del segmento che unisce blue a yellow
			#plt.plot([blue[0], yellow[0]], [blue[1], yellow[1]], 'go', linestyle="--")
			midpoint = [(blue[0]+yellow[0])/2, (blue[1]+yellow[1])/2]
			count += 1
	# plt.show()
	return bluOrdinati, gialliOrdinati

def divideMatrix(matrix):
	
	# inizializzazione delle matrici
	blueMatrix = []
	yellowMatrix = []
	
	# divisione della matrice
	for i in range(len(matrix)):
		if matrix[i][2] == 1:
			blueMatrix.append([matrix[i][0], matrix[i][1], matrix[i][2]])
		if matrix[i][2] == 2:
			yellowMatrix.append([matrix[i][0], matrix[i][1], matrix[i][2]])
			
	blueMatrix = np.array(blueMatrix)
	yellowMatrix = np.array(yellowMatrix)
	
	return blueMatrix, yellowMatrix

def calculateArea(matrix, segments):
	return 0

def isInterior(triangle, area):
	#  
	return area > 0

def interpolazione(x,y):

	# includo sempre l'origine nell'interpolazione
	# x = np.insert(x, 0, 0)
	# y = np.insert(y, 0, 0)
	
	# x da cui campioneremo i punti della curva interpolata
	# x_interp = np.linspace(np.min(x), np.max(x), round(np.max(x))*100)
	x_interp = np.linspace(np.min(x), np.max(x), round(np.max(x))*100)
	
	# conversione in liste
	# x = x.tolist()
	# y = y.tolist()
 
	t = np.linspace(0, 1, len(x))
	
	# se i punti sono solo 2, interpolo linearmente, altrimenti quadraticamente
	if len(x)==2:
		f = interpolate.interp1d(x, y, kind="linear")
	else:
		# fx = interpolate.interp1d(t, x, kind="quadratic")
		# fy = interpolate.interp1d(t, y, kind="quadratic")
		# Creazione della funzione interpolante
		
		# Generazione di dati di esempio
		# x = np.linspace(0, 1, len(x))  # Coordinate x
		# y = np.linspace(0, 1, len(x))  # Coordinate y
		# z = np.linspace(0, 4, 10)  # Coordinate z
		# data = np.random.rand(10, 10, 10)  # Dati casuali, sostituisci con i tuoi dati

		# Generazione di dati di esempio per la curva in 3D
		t = np.linspace(0, 1, len(x))  # Tempo
		z = t                       # Punti z
		
		# Creazione della funzione interpolante
		f = interpolate.RegularGridInterpolator((t,), np.column_stack((x, y, z)), "cubic")

		# Generazione di una griglia più fine per l'interpolazione
		t_new = np.linspace(0, 1, len(x)*10)
		grid_new = np.meshgrid(t_new, indexing='ij')
		points = np.vstack([grid_new[0].ravel()]).T

		# Interpolazione
		interpolated_values = f(points)

		# Estrazione dei valori interpolati di x e y
		x_interpolated = interpolated_values[:, 0]
		y_interpolated = interpolated_values[:, 1]


	
	# points = np.array([x_interp, x_interp]).T

	# Interpolazione
	# wp = f(points)

	# y_interp = f(x_interp,x_interp)
	
	
	# sortedInd = np.argsort(x)
	# x = x[sortedInd]
	# y = y[sortedInd]
 
	# f = CubicSpline(x, y)
	
	# y_interp = f(x_interp)
	# x_interp = fx(x_interp)
	# y_interp = fy(x_interp)
	
	#plot dei punti interpolati
	#plt.plot(x_interpolated, y_interpolated, 'ro')
	#plt.show()
 
	return x_interp.tolist(), x_interp.tolist()