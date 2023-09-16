import requests
import urllib
import json
import flask

def process(basename: str, real_filename: str) -> str:
	files = {'file': (
		basename,
		open(real_filename, 'rb'),
		'application-type',
	)}
	payload = {
		'file-name': 'Filename',
		'category': '19',
	}
	api_url = f'http://api.qrserver.com/v1/read-qr-code/'

	session = requests.Session()
	res = json.loads(session.post(api_url, data=payload, files=files).text)[0]

	print(res, flush=True)

	if res['type'] != 'qrcode' or len(res['symbol']) == 0:
		return {
			'data': None,
			'error': 'No QR code detected.',
		}

	return {
		'data': res['symbol'][0]['data'],
		'error': res['symbol'][0]['error'],
	}