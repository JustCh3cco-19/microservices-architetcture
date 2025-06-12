import math
import numpy as np

import config


def position(pixelAsc: int, pixelOrd: int, distance: float) -> np.ndarray:
	"""
	Questa funzione calcola la posizione di un punto rispetto al baricentro della macchina

	ritorna un vettore V=(X;Y;Z) = posizione del punto rispetto al baricentro della macchina

	Il sistema di riferimento è composto dall'asse x che punto verso il cono (= distanza)
	l'asse y orizzontale con verso positivo verso sinistra (distanza dal centro)
	l'asse z verticale con verso positivo verso l'alto
	"""

	#%t=[500;160;1140];
	#t=[0;0;0]; %posizione della camera rispetto a baricentro macchina
	# tilt della camera rispetto alla terna iniziale
	phi=-math.pi/2 #%phi=102*pi/180;
	theta=0 #%theta=0;
	psi=-math.pi/2
		#%psi=pi/2;
		#phi=-pi/2; % rollio della camera
		#theta=0; % beccheggio " "
		#psi=-pi/2; % imbardata  " "
	# cx centro della camera asse orizzontale in pixel
	# cy centro della camera asse verticale in pixel
	cx, cy = config.CAMERA_CENTER

	# fx, fy distanza focale in pixel
	fx, fy = config.CAMERA_FOCAL

	ux=pixelAsc #ux = point(1); 
	vx=pixelOrd #vx = point(2);
	z=distance #z  = point(3);
	R=[[math.cos(psi)*math.cos(theta),math.cos(psi)*math.sin(theta)*math.sin(phi)-math.cos(phi)*math.sin(psi),math.sin(psi)*math.sin(phi)+math.cos(psi)*math.cos(phi)*math.sin(theta)],[math.cos(theta)*math.sin(psi), math.cos(psi)*math.cos(phi)+math.sin(psi)*math.sin(theta)*math.sin(phi), math.cos(phi)*math.sin(psi)*math.sin(theta)-math.cos(psi)*math.sin(phi)],[-math.sin(theta), math.cos(theta)*math.sin(phi), math.cos(theta)*math.cos(phi)]] #R=[cos(psi)*cos(theta) cos(psi)*sin(theta)*sin(phi)-cos(phi)*sin(psi) sin(psi)*sin(phi)+cos(psi)*cos(phi)*sin(theta); cos(theta)*sin(psi) cos(psi)*cos(phi)+sin(psi)*sin(theta)*sin(phi) cos(phi)*sin(psi)*sin(theta)-cos(psi)*sin(phi); -sin(theta) cos(theta)*sin(phi) cos(theta)*cos(phi)];
	R=np.array(R)
	x=z*(ux-cx) / fx   #x=z*(ux-cx)/fx;
	y=z*(vx-cy) / fy   #y=z*(vx-cy)/fy;
	v=np.array([x,y,z])#v=[x;y;z];
	V=np.dot(R,v)#V = (R*v+t); %la funzione restituisce in output un vettore V=(X;Y;Z) = posizione del punto rispetto al baricentro della macchina
	V=np.add(V, config.CAMERA_POS)
	return V
