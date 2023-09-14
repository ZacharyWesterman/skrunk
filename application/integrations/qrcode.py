import requests
import urllib
import json

def process(id: str, ext: str) -> str:
	my_url = urllib.parse.quote_plus(f'https://ftp.skrunky.com/blob/{id}{ext}')
	api_url = f'http://api.qrserver.com/v1/read-qr-code/?fileurl={my_url}'

	res = json.loads(requests.get(api_url).text)[0]

	if res['type'] != 'qrcode' or len(res['symbol']) == 0:
		return {
			'data': None,
			'error': 'No QR code detected.',
		}

	print(res, flush=True)

	return {
		'data': res['symbol'][0]['data'],
		'error': res['symbol'][0]['error'],
	}