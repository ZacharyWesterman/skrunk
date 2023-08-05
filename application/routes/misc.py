from flask import Response
import requests
import random

application = None

def random_xkcd() -> Response:
    comic_num = random.randint(0, 200)
    response = requests.get(f'https://xkcd.com/{comic_num}/info.0.json')
    return Response(response.text, response.status_code)
