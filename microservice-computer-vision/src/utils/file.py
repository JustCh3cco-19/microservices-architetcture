import datetime

def gen_file_path(path: str, prefix: str="", ext: str="txt", timestamp: bool = True) -> str:
	"""
	Genera un percorso di file con timestamp
	"""

	if prefix and not prefix.endswith("_"):
		prefix += "_"
	path += f"/{prefix}"
	if timestamp:
		path += datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	if not ext.startswith("."):
		ext = f".{ext}"
	path += ext

	path = path.replace(" ", "_")
	path = path.replace("//", "/")

	return path