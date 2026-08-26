"""application.integrations.images"""

from PIL import ExifTags, Image


def extensions() -> list:
	"""
	Returns a list of common image file extensions.

	Returns:
		list: A list containing image file extensions as strings.
	"""
	return ['.jpeg', '.jpg', '.png', '.bmp', '.webp', '.gif', '.tiff']


def downscale(path: str, max_width: int, output_path: str) -> bool:
	"""
	Downscale an image to a specified maximum width while maintaining aspect ratio.

	Parameters:
		path (str): The file path to the input image.
		max_width (int): The maximum width to downscale the image to.
		output_path (str): The file path to save the downscaled image.

	Returns:
		bool: True if the image was downscaled,
		False if the image width was already less than or equal to max_width.
	"""
	image = Image.open(path)
	width = image.size[0]

	if width <= max_width:
		return False  # No need to downscale

	# JPEGs can have metadata indicating their rotation. Account for that
	o = [i[0] for i in ExifTags.TAGS.items() if i[1] == 'Orientation']
	if len(o):
		exif = dict(image.getexif().items())
		orientation = {
			3: 180,
			6: 270,
			8: 90,
		}.get(exif[o[0]])
		if orientation is not None:
			image = image.rotate(orientation, expand=True)

	image.thumbnail((max_width, max_width), Image.Resampling.LANCZOS)

	if path[-5::].lower() == '.jpeg':
		image.save(output_path, 'JPEG')
	else:
		image.save(output_path)

	return True
