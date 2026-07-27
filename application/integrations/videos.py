"""application.integrations.videos"""

import subprocess

from imageio.v3 import imread, imwrite


def extensions() -> list:
	"""
	Returns a list of common video file extensions.

	Returns:
		list: A list of strings representing video file extensions.
	"""
	return [
		'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.webm',
		'.m4v', '.3gp', '.mpg', '.mpeg', '.vob', '.ogv'
	]


def create_thumbnail_from_first_frame(video_path: str, output_image: str) -> None:
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


def create_low_res(video_path: str, output_video: str) -> None:
	"""
	Creates a low-res version of the given video.

	Args:
		video_path (str): The path to the video file.
		output_video (str): The path where the output video will be saved.

	Returns:
		None
	"""
	subprocess.run([
		'ffmpeg', '-v', 'quiet', '-stats',
		'-i', video_path,
		'-vf', 'scale=480:-2,setsar=1:1', '-c:v', 'libx264',
		'-crf', '23', '-c:a', 'copy', output_video,
	])
