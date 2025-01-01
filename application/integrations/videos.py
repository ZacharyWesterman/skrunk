"""application.integrations.videos"""

from imageio.v3 import imread, imwrite


def extensions() -> list:
	"""
	Returns a list of common video file extensions.

	Returns:
		list: A list of strings representing video file extensions.
	"""
	return ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg', '.vob', '.ogv']


def create_preview_from_first_frame(video_path: str, output_image: str) -> None:
	"""
	Extracts the first frame from a video file and saves it as an image.

	Args:
		video_path (str): The path to the video file.
		output_image (str): The path where the output image will be saved.

	Returns:
		None
	"""
	first_frame = imread(video_path, index=0)
	imwrite(output_image, first_frame)
