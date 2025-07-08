"""application.routes.misc"""

import random

import requests
from flask import Response


def random_xkcd() -> Response:
	"""
	Fetch a random XKCD comic.

	Returns:
		Response: A Flask Response object containing the JSON data of a random XKCD comic.
	"""

	comic_num = random.randint(1000, 2814)
	response = requests.get(f'https://xkcd.com/{comic_num}/info.0.json', timeout=10)
	return Response(response.text, response.status_code)
