from PIL import Image

def extensions() -> list:
	return ['.jpeg', '.jpg', '.png', '.bmp', '.webp']

def downscale(path: str, max_width: int, output_path: str) -> bool:
	image = Image.open(path)
	width = image.size[0]

	if width <= max_width:
		return False #No need to downscale

	image.thumbnail((max_width, max_width), Image.Resampling.LANCZOS)

	if path[-5::].lower() == '.jpeg':
		image.save(output_path, 'JPEG')
	else:
		image.save(output_path)

	return True
