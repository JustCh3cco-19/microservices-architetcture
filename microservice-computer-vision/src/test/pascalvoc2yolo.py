#!/usr/bin/python3

import time
import argparse
import xml.etree.ElementTree as ET

def xml2yolo():
	tree = ET.parse(opt.xml)

	yaml_file = open('yolo_train.yml', 'w')
	yaml_file.write("train: {}\nval: {}\nnc: 1\nnames: ['cone']".format(opt.train, opt.val))
	yaml_file.close()

	filename = ''
	width = 0
	height = 0
	x_min = 0
	x_max = 0
	y_min = 0
	y_max = 0
	x = 0.0
	y = 0.0
	w = 0.0
	h = 0.0

	for root_element in tree.getroot():
		if root_element.tag == 'annotation':

			for element in root_element:
				if element.tag == 'image':

					for image_element in element:
						if image_element.tag == 'filename':
							filename = image_element.text
							print(filename)

						elif image_element.tag == 'size':
							for size_element in image_element:
								if size_element.tag == 'width':
									width = int(size_element.text)
									print('width:\t{}'.format(width))
								else:
									height = int(size_element.text)
									print('height:\t{}'.format(height))

						elif image_element.tag == 'object':
							for object_element in image_element:
								if object_element.tag == 'bndbox':
									for bndbox_element in object_element:
										if bndbox_element.tag == 'xmin':
											x_min = int(bndbox_element.text)
											if x_min < 0:
												x_min = x_min+width
											elif x_min > width:
												x_min = x_min-width
										elif bndbox_element.tag == 'xmax':
											x_max = int(bndbox_element.text)
											if x_max < 0:
												x_max = x_max+width
											elif x_max > width:
												x_max = x_max-width
										elif bndbox_element.tag == 'ymin':
											y_min = int(bndbox_element.text)
										elif bndbox_element.tag == 'ymax':
											y_max = int(bndbox_element.text)

							if x_min >= width or y_min >= height or x_max <= 0 or y_max <= 0:
								print('Aborted, cone is out of frame')
							else:
								if x_min < 0:
									x_min = 0

								if x_max > width:
									x_max = width

								if y_min < 0:
									y_min = 0

								if y_max > height:
									y_max = height

								print('[{},{}]\t[{},{}]'.format(x_min,y_min,x_max,y_max))

								x = ((x_min+x_max)/2)/width
								y = ((y_min+y_max)/2)/height
								w = (x_max-x_min)/width
								h = (y_max-y_min)/height
								if x > 0 and y > 0 and w > 0 and h > 0:
									file = open('labels/'+filename.replace('.png','.txt'), 'a')
									file.write('0\t{}\t{}\t{}\t{}\n'.format(x,y,w,h))
									file.close()
								else:
									print('Aborted, negative values')

					print('\n')

#------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Fast Charge Spotter - PascalVOC to YOLOv5 dataset converter')

	parser.addArgument('--xml', default='train.xml', help='XML file generated from Spotter')
	parser.addArgument('--train', default='images/', help='Location of train set images')
	parser.addArgument('--val', default='data/', help='Location of validation set images')

	opt = parser.parse_args()
	print(opt)

	t0 = time.time()
	print('{}\n\nStart processing {}'.format(opt, opt.xml), end='\n\n')

	xml2yolo()

	print('Done in {}s'.format(round(time.time()-t0, 2)))
