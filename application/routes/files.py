"""application.routes.files"""

import mimetypes
import os

from flask import Response


def sanitize_path(path: str) -> str:
	"""
	Sanitize the given path to prevent directory traversal attacks.

	Args:
		path (str): The path to sanitize.

	Returns:
		str: The sanitized path, relative to the root directory.
	"""
	return os.path.relpath(os.path.normpath(os.path.join("/", path)), "/")


def read_file_data(path: str) -> Response:
	"""
	Read the contents of a file and return it as a Flask Response object.

	Args:
		path (str): The path to the file to read.

	Returns:
		Response: A Flask Response object containing the file data, or an error message if the file is not found.
	"""

	try:
		with open(path, 'rb') as fp:
			mime = mimetypes.guess_type(path)
			return Response(fp.read(), 200, mimetype=mime[0] if mime else None)
	except FileNotFoundError:
		return Response('File not found.', 404)
