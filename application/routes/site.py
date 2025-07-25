"""application.routes.site"""

import re
from typing import Any

from flask import Response

from . import auth, files

application: Any = None

# Allow only specific files in site/ to be accessed without auth,
# as other files may have "sensitive" data.
try:
	with open('data/no_auth_files.txt', 'r', encoding='utf8') as fp:
		__NO_AUTH_FILES = [i.strip() for i in fp.readlines() if i.strip() != '']
except FileNotFoundError:
	__NO_AUTH_FILES = []


def main_page() -> Response:
	"""
	Return the main page of the application.

	Returns:
		Response: A Flask Response object containing the main page HTML.
	"""

	return files.read_file_data('site/html/index.html')


def get(path: str) -> Response:
	"""
	Get a file from the site directory.

	Args:
		path (str): The path to the file to retrieve.

	Returns:
		Response: A Flask Response object containing the file data or an error message.
	"""

	path = files.sanitize_path(path)

	jsfields = re.match(r'js/fields/[\w-]+\.js', path)
	styles = re.match(r'css/[\w-]+\.css', path)
	if not auth.authorized() and path not in __NO_AUTH_FILES and not jsfields and not styles:
		return Response('Access denied.', 403)

	if not application.is_initialized and path == 'html/login.html':
		with open(f'site/{path}', 'r', encoding='utf8') as f:
			return Response(f.read().replace(
				'Authentication Required',
				"""<b class="emphasis">
					This server has not been set up.<br><br>
					Login as user "admin" (any password) and create at least one user.
					<br><br>Then restart the server, and (optionally) delete the admin user.
				</b>"""
			), 200)

	i = path.rfind('.')
	if i > -1:
		ext = path[i + 1::]
	else:
		ext = ''

	if ext in ['js', 'css', 'html', 'dot', 'json', 'aff', 'dic']:
		return files.read_file_data(f'site/{path}')
	else:
		if auth.authorized():
			return Response('File not found.', 404)
		else:
			return Response('Access denied.', 403)


def get_icon(path: str) -> Response:
	"""
	Get an icon file from the site directory.

	Args:
		path (str): The path to the icon file to retrieve.

	Returns:
		Response: A Flask Response object containing the icon file data or an error message.
	"""
	path = files.sanitize_path(path)
	return files.read_file_data(f'data/{path}.png')


def get_svg(path: str) -> Response:
	"""
	Get an SVG file from the site directory.

	Args:
		path (str): The path to the SVG file to retrieve.

	Returns:
		Response: A Flask Response object containing the SVG file data or an error message.
	"""
	path = files.sanitize_path(path)
	return files.read_file_data(f'data/{path}.svg')
