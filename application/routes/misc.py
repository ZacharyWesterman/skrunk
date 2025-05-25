"""application.routes.misc"""

import random

import requests
from flask import Response


def random_xkcd() -> Response:
	comic_num = random.randint(1000, 2814)
	response = requests.get(f'https://xkcd.com/{comic_num}/info.0.json', timeout=10)
	return Response(response.text, response.status_code)
