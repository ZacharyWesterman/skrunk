class ApiFailedError(Exception):
	pass

class UnsupportedFileFormat(Exception):
	def __init__(self, filename: str):
		super().__init__(f'Unsupported file format for {filename}')

class RepoFetchFailed(Exception):
	def __init__(self, url, text):
		super().__init__(f'Unable to fetch data due to error: {text}. Request URL: {url}')
