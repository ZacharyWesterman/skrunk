"""application.routes.files"""

import mimetypes
import os

from flask import Response

# Remove absolute paths or paths that contain '../' to prevent access to files outside of site/


def sanitize_path(path: str) -> str:
	return os.path.relpath(os.path.normpath(os.path.join("/", path)), "/")


def read_file_data(path: str) -> Response:
	try:
		with open(path, 'rb') as fp:
			mime = mimetypes.guess_type(path)
			return Response(fp.read(), 200, mimetype=mime[0] if mime else None)
	except FileNotFoundError:
		return Response('File not found.', 404)
