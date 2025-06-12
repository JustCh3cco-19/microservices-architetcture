import re
from typing import Dict

FRAME_SEP = r'-+ Frame (\d+) -+'
FRAME_TIME = r'get_frame executed in (\d+\.\d+) seconds'
GET_CONES_TIME = r'getCones executed in (\d+\.\d+) seconds'
FORWARD_TIME = r'forward executed in (\d+\.\d+) seconds'
TOT_TIME = r'Tempo totale: (\d+\.\d+) secondi'

def str_to_ms(time: str):
	return round(float(time) * 1000, 2)

def parse_log(filename):
	frame = 0
	infos = dict()
	
	with open(filename) as f:

		for line in iter(f.readline, ''):
			if (not line):
				continue
			if (match := re.search(FRAME_SEP, line)):
				frame = int(match.group(1))
				infos[frame] = dict()
			elif (match := re.search(FRAME_TIME, line)):
				infos[frame]['frame_time'] = str_to_ms(match.group(1))
			elif (match := re.search(GET_CONES_TIME, line)):
				infos[frame]['get_cones_time'] = str_to_ms(match.group(1))
			elif (match := re.search(TOT_TIME, line)):
				infos[frame]['total_time'] = str_to_ms(match.group(1))
			elif (match := re.search(FORWARD_TIME, line)):
				infos[frame]['forward_time'] = str_to_ms(match.group(1))

	return infos

def get_stats(logs: Dict):
	tot_time_list, cv_time_list, forward_time_list, cones_time_list = [], [], [], []
	for frame in logs.keys():
		if 'total_time' not in logs[frame] or 'frame_time' not in logs[frame] or 'get_cones_time' not in logs[frame]:
			continue
		tot_time = logs[frame]['total_time'] - logs[frame]['frame_time']
		cv_time = logs[frame]['get_cones_time']
		forward_time = logs[frame]['forward_time']
		cones_time = cv_time - forward_time

		tot_time_list.append(tot_time)
		cv_time_list.append(cv_time)
		forward_time_list.append(forward_time)
		cones_time_list.append(cones_time)
	return tot_time_list, cv_time_list, forward_time_list, cones_time_list

def plot_stats(stats):
	import matplotlib.pyplot as plt
	import numpy as np

	
	tot_time, cv_time, forward_time, cones_time = stats
	x = np.arange(len(tot_time))

	fig, ax = plt.subplots()
	ax.plot(x, tot_time, label='Totale')
	ax.plot(x, forward_time, label='Forward')
	ax.plot(x, cones_time, label='Cones')
	ax.plot(x, cv_time, label='CV')
	ax.set_xlabel('Frame')
	ax.set_ylabel('Tempo (ms)')
	ax.legend()
	ax.set_title('Tempo di esecuzione')
	ax.grid()

	# scrive nel plot i valori massimi e medi in un riquadro in basso a destra
	max_tot = max(tot_time)
	max_cv = max(cv_time)
	max_forward = max(forward_time)
	max_cones = max(cones_time)
	avg_tot = np.mean(tot_time)
	avg_cv = np.mean(cv_time)
	avg_forward = np.mean(forward_time)
	avg_cones = np.mean(cones_time)

	textstr = '\n'.join((
		f'Massimo Totale: {max_tot:.2f} ms',
		f'Massimo CV: {max_cv:.2f} ms',
		f'Massimo Forward: {max_forward:.2f} ms',
		f'Massimo Cones: {max_cones:.2f} ms',
		f'Media Totale: {avg_tot:.2f} ms',
		f'Media CV: {avg_cv:.2f} ms',
		f'Media Forward: {avg_forward:.2f} ms',
		f'Media Cones: {avg_cones:.2f} ms'
	))
	props = dict(boxstyle='round', facecolor='white', alpha=0.8)
	ax.text(.80, .10
			, textstr
			, transform=ax.transAxes
			, fontsize=8
			, verticalalignment='bottom'
			, bbox=props)
	

	plt.show()



if __name__ == '__main__':
	import sys

	if len(sys.argv) != 2:
		print('Usage: python time_stats.py <logfile.log>')
		sys.exit(1)
	filename = sys.argv[1]
	logs = parse_log(filename)
	stats = get_stats(logs)
	plot_stats(stats)
