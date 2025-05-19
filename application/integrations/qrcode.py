"""application.integrations.qrcode"""

from pyzxing import BarCodeReader
import qrcode
import uuid
from PIL import Image
from typing import Any


def process(file_path: str) -> dict:
	"""
	Processes a file to decode QR or barcodes.

	Args:
		file_path (str): The path to the file containing the QR or barcode.

	Returns:
		str: A dictionary containing the decoded data or an error message.
			- 'data' (str or None): The decoded data if a QR or barcode is detected, otherwise None.
			- 'error' (str or None): An error message if no QR or barcode is detected, otherwise None.
	"""
	reader = BarCodeReader()

	for result in reader.decode(file_path):
		if result and result.get('raw') is not None:
			return {
				'data': result['raw'].decode('utf-8'),
				'error': None,
			}
		else:
			break

	return {
		'data': None,
		'error': 'No QR / barcode detected.',
	}


def generate(file_path: str, text: str | None, amount: int) -> None:
	"""
	Generates a specified amount of QR codes and saves them to a file.

	Args:
		file_path (str): The path where the generated image will be saved.
		text (str | None): The text to encode in the QR codes. If None, a random UUID will be used.
		amount (int): The number of QR codes to generate.

	Returns:
		None
	"""
	canvas = Image.new('RGB', (2590, 3700), color=(255, 255, 255))

	print(f'Generating {amount} QR codes...', flush=True)
	for i in range(amount):
		qr_text = str(uuid.uuid4()).replace('-', '') if text is None else text
		image: Any = qrcode.make(qr_text)

		canvas.paste(image, ((i % 7) * 370, (i // 7) * 370))

	canvas.save(file_path)
	print(f'Successfully generated {amount} QR codes.', flush=True)
