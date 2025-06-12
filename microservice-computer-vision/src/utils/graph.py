# import matplotlib.pyplot as plt

import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def plot_graph_error(erros, acc):
	# Plot dell'errore della profondità e dell'accelerometro nel tempo nello stesso grafico
	# l'errore è in percentuale e l'accelerometro è in m/s^2
	fig, ax1 = plt.subplots()
	ax1.set_xlabel('time (s)')
	ax1.set_ylabel('Depth Error (%)', color='tab:red')
	ax1.plot(erros, color='tab:red')
	ax1.tick_params(axis='y', labelcolor='tab:red')

	ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
	ax2.set_ylabel('Accel (m/s^2)', color='tab:blue')  # we already handled the x-label with ax1
	ax2.plot(acc, color='tab:blue')
	ax2.tick_params(axis='y', labelcolor='tab:blue')

	fig.tight_layout()  # otherwise the right y-label is slightly clipped
	plt.savefig("error-distance-acc.png")

def plot_graph_frame(time_to_get_frames, acc):
	# Plot del tempo per acquisire il frame e dell'accellerometro
	# su due assi diversi, il tempo è in secondi e l'accellerometro in m/s^2
	fig, ax1 = plt.subplots()
	ax1.set_xlabel('time (s)')
	ax1.set_ylabel('Time to get frame (s)', color='tab:red')
	ax1.plot(time_to_get_frames, color='tab:red')
	ax1.tick_params(axis='y', labelcolor='tab:red')

	ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
	ax2.set_ylabel('Accel (m/s^2)', color='tab:blue')  # we already handled the x-label with ax1
	ax2.plot(acc, color='tab:blue')
	ax2.tick_params(axis='y', labelcolor='tab:blue')

	fig.tight_layout()  # otherwise the right y-label is slightly clipped
	plt.savefig("time-frame-acc.png")

def plot_cones(cones_x, cones_y, cone_colors):
	# Plot dei coni riconosciuti
	fig, ax = plt.subplots()

	# cone_colors è composto da:
	# 1 -> blu
	# 2 -> giallo
	# 3 -> arancione

	cone_colors = ["blue" if color == 1 else "yellow" if color == 2 else "orange" for color in cone_colors]

	ax.scatter(cones_x, cones_y, c=cone_colors)
	plt.show()
