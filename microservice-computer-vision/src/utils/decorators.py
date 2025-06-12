import time
import logging
from functools import wraps

def log_time(f):
	"""
	Decorator che logga (DEBUG) il tempo di esecuzione di una funzione
	"""

	@wraps(f)
	def wrapper(*args, **kwargs):
		time_1 = time.perf_counter()
		result = f(*args, **kwargs)
		time_2 = time.perf_counter()

		logging.debug(f"{f.__name__} executed in {time_2 - time_1:0.4f} seconds")
		return result

	return wrapper