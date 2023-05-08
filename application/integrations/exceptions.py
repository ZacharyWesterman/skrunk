class ApiFailedError(Exception):
	pass

class UnsupportedFileFormat(Exception):
	def __init__(self, filename: str):
		super().__init__(f'Unsupported file format for {filename}')