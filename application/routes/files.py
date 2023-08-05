from flask import Response
import mimetypes, os

# Remove absolute paths or paths that contain '../' to prevent access to files outside of site/
def sanitize_path(path: str) -> str:
	return os.path.relpath(os.path.normpath(os.path.join("/", path)), "/")

def read_file_data(path: str) -> Response:
	path = sanitize_path(path)
	try:
		with open(path, 'rb') as fp:
			mime = mimetypes.guess_type(path)
			if mime:
				return Response(fp.read(), 200, mimetype=mime[0])
			else:
				return Response(fp.read(), 200)
	except FileNotFoundError:
		return Response('File not found.', 404)