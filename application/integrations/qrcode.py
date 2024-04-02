from pyzxing import BarCodeReader
import qrcode, uuid
from PIL import Image

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

def generate(file_path: str, text: str|None, amount: int) -> None:
	canvas = Image.new('RGB', (2590, 3700), color = (255, 255, 255))

	print(f'Generating {amount} QR codes...', flush = True)
	for i in range(amount):
		qr_text = str(uuid.uuid4()).replace('-', '') if text is None else text
		image = qrcode.make(qr_text)

		canvas.paste(image, ((i % 7) * 370, (i // 7) * 370))

	canvas.save(file_path)
	print(f'Successfully generated {amount} QR codes.', flush = True)

