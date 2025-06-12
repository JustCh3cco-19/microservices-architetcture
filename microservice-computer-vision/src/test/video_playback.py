#####################################################
##               Read bag from file                ##
#####################################################


# First import library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
# Import argparse for command-line options
import argparse
# Import os.path for file path manipulation
import os.path


# Colori in BGR (da colorDetection.py)
YELLOW = [39, 76, 103]
BLUE = [59, 44, 2]

# Da utils.py
def get_limits(color):
	"""
	Get the lower and upper HSV limits for a color
	- color: BGR value
	:return: lowerLimit, upperLimit
	"""

	c = np.uint8([[color]])  # BGR values
	hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)

	hue = hsvC[0][0][0]  # Get the hue value

	# Handle red hue wrap-around
	if hue >= 165:  # Upper limit for divided red hue
		lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
		upperLimit = np.array([180, 255, 255], dtype=np.uint8)
	elif hue <= 15:  # Lower limit for divided red hue
		lowerLimit = np.array([0, 100, 100], dtype=np.uint8)
		upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)
	else:
		lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
		upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)

	return lowerLimit, upperLimit


# Create object for parsing command-line options
parser = argparse.ArgumentParser(description="Read recorded bag file and display depth stream in jet colormap.\
								Remember to change the stream fps and format to match the recorded.")
# Add argument which takes path to a bag file as an input
parser.add_argument("-i", "--input", type=str, help="Path to the bag file")
# Parse the command line arguments to an object
args = parser.parse_args()
# Safety if no parameter have been given
if not args.input:
	print("No input paramater have been given.")
	print("For help type --help")
	exit()
# Check if the given file have bag extension
if os.path.splitext(args.input)[1] != ".bag":
	print("The given file is not of correct file format.")
	print("Only .bag files are accepted")
	exit()
try:
	# Create pipeline
	pipeline = rs.pipeline()

	# Create a config object
	config = rs.config()

	# Tell config that we will use a recorded device from file to be used by the pipeline through playback.
	rs.config.enable_device_from_file(config, args.input)

	# Configure the pipeline to stream the depth stream
	# Change this parameters according to the recorded bag file resolution
	
	# Start streaming from file
	pipeline.start(config)

	# Create opencv window to render image in
	cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)
	
	# Create colorizer object
	colorizer = rs.colorizer()

	# Streaming loop
	while True:
		# Get frameset of depth
		frames = pipeline.wait_for_frames()

		# Get depth frame
		depth_frame = frames.get_depth_frame()

		# Colorize depth frame to jet colormap
		depth_color_frame = colorizer.colorize(depth_frame)

		# Convert depth_frame to numpy array to render image in opencv
		depth_color_image = np.asanyarray(depth_color_frame.get_data())

		# Render image in opencv window
		# cv2.imshow("Depth Stream", depth_color_image)

		# Color frame
		color_frame = frames.get_color_frame()

		color_image = np.asanyarray(color_frame.get_data())
		color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

		color_image_cp = np.copy(color_image)

		# rimpicciolisco l'immagine
		# depth_frame = cv2.resize(depth_frame, (1280, 720), interpolation = cv2.INTER_AREA)
		color_frame = cv2.resize(color_image, (1280, 720), interpolation = cv2.INTER_AREA)
		cv2.imshow("Color Stream", color_image)

		cv2.imshow("Copia", color_image_cp)


		# visualizzazione delle maschere

		hsvImage = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)

		# Per il giallo
		y_lowerLimit, y_upperLimit = (np.array([10, 80, 50]), np.array([75, 255, 255]))

		# Per il bianco
		# lowerLimit, upperLimit = (np.array([0, 0, 70]), np.array([180, 50, 255]))
		# sensitivity = 140
		# lowerLimit = np.array([50,0,255-sensitivity])
		# upperLimit = np.array([255,sensitivity,255])

		# Per il nero
		# lowerLimit, upperLimit = (np.array([0, 0, 0]), np.array([180, 255, 25]))

		# Per il blu
		b_lowerLimit = np.array([90, 60, 30])
		b_upperLimit = np.array([130, 255, 255])

		y_mask = cv2.inRange(hsvImage, y_lowerLimit, y_upperLimit)
		b_mask = cv2.inRange(hsvImage, b_lowerLimit, b_upperLimit)


		cv2.imshow("Mask", y_mask)
		cv2.imshow("Mask2", b_mask)


		key = cv2.waitKey(1)
		# if pressed escape exit program
		if key == ord("q"):
			cv2.destroyAllWindows()
			break

finally:
	pass