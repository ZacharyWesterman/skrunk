"""application.integrations.videos"""

import subprocess
from functools import cache
from shutil import which

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


def create_low_res(video_path: str, output_video: str, hosts: list[str]) -> None:
	"""
	Creates a low-res version of the given video.

	Args:
		video_path (str): The path to the video file.
		output_video (str): The path where the output video will be saved.
		hosts (list[str]): The list of remote hosts to process on rather than locally.

	Returns:
		None
	"""
	subprocess.run(
		[
			'ffmpeg', '-v', 'quiet', '-stats',
			'-i', video_path,
			'-vf', 'scale=480:-2,setsar=1:1',
			output_video,
		],
		check=False
	)


@cache
def has_ffmpeg(host: str = 'localhost') -> bool:
	"""
	Check if the local machine or a given remote host is accessible and has ffmpeg.

	Args:
		host (str): The SSH name of the machine, or `localhost` to check locally.

	Returns:
		bool: True if the given machine has ffmpeg, False otherwise.
	"""

	if host in ['', 'localhost']:
		return which('ffmpeg') is not None

	try:
		subprocess.check_call([
			'ssh', host,
			'-oConnectTimeout=10',
			'which ffmpeg'
		])
	except subprocess.CalledProcessError:
		return False

	return True


def can_create_previews(hosts: list[str]) -> bool:
	"""
	Check if either the local machine or any remote hosts can create video previews with ffmpeg.

	Args:
		hosts (list[str]): The list of remote hosts to process on rather than locally.

	Returns:
		bool: True if any hosts have ffmpeg, False otherwise.
	"""
	if has_ffmpeg():
		return True

	for i in hosts:
		if has_ffmpeg(i):
			return True

	return False
