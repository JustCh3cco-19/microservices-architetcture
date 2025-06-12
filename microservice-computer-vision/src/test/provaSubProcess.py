# import subprocess

# # Crea un nuovo processo
# process = subprocess.Popen('python .\cone_detection.py --weights "640x32.pt" --source test.jpg --img-size 640 --conf-thres 0.25 --iou-thres 0.45 --device cpu --view-result --save-result --verbose', stdout=subprocess.PIPE, shell=True)

# # Invia un valore allo script
# #process.stdin.write(b'valore\n')
# #process.stdin.flush()

# # Leggi il valore restituito dallo script
# valore = process.stdout.readline().decode('utf-8').strip()

# # Stampa il valore
# print(valore)


import coneDetection as cd

#self, device, weights, img_size=640, conf_threshold=0.25, iou_threshold=0.45, verbose=False, augmentation=False
coneDet = cd('640x32.pt', 0, 640, 0.25, 0.45, 'cpu', True)

