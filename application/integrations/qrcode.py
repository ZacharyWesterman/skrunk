from pyzxing import BarCodeReader

def process(file_path: str) -> str:
	reader = BarCodeReader()

	for result in reader.decode(file_path):
		if 'raw' in result:
			return {
				'data': result['raw'].decode('utf-8'),
				'error': None,
			}
		else:
			return {
				'data': None,
				'error': 'No QR / barcode detected.',
			}