import requests
import urllib
import json
import flask

def process(dir: str) -> str:
	domain_name = urllib.parse.urlparse(flask.request.base_url).hostname
	my_url = urllib.parse.quote_plus(f'https://{domain_name}/{dir}')
	api_url = f'http://api.qrserver.com/v1/read-qr-code/?fileurl={my_url}'

	res = json.loads(requests.get(api_url).text)[0]

	if res['type'] != 'qrcode' or len(res['symbol']) == 0:
		return {
			'data': None,
			'error': 'No QR code detected.',
		}

	return {
		'data': res['symbol'][0]['data'],
		'error': res['symbol'][0]['error'],
	}