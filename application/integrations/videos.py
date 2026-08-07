"""application.integrations.videos"""

import subprocess
import uuid
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

	def run_local():
		subprocess.run(
			[
				'ffmpeg', '-v', 'quiet', '-stats',
				'-i', video_path,
				'-vf', 'scale=480:-2,setsar=1:1',
				output_video,
			],
			check=False
		)

	# If no hosts set in config, just run locally
	if len(hosts) == 0:
		run_local()
		return

	ideal_host = min(((i, get_normalized_load(i)) for i in hosts), key=lambda x: x[1])
	localhost_load = get_normalized_load()

	# If best host was a failure, just run locally
	if ideal_host[1] == 9999:
		run_local()
		return

	# If local load is 1/3rd or less, and the best host has VERY high percent load, just run locally.
	if localhost_load < 0.3 and ideal_host[1] > 0.8:
		run_local()
		return

	# All checks passed, run on best host
	host = ideal_host[0]
	jobid = uuid.uuid4()
	from_ext = video_path.split('.')[-1]
	to_ext = output_video.split('.')[-1]
	from_file = f'/var/tmp/skrunk-conv-input-{jobid}.{from_ext}'
	to_file = f'/var/tmp/skrunk-conv-output-{jobid}.{to_ext}'

	print(f'Sending blob to {host} for remote processing...', flush=True)

	# Transfer file up to host
	subprocess.run([
		'scp',
		video_path,
		f'{host}:{from_file}',
	], check=False)

	# Process the file
	proc = subprocess.Popen(
		['ssh', '-tt', host, f'ffmpeg -v quiet -stats -i {from_file} -vf scale=480:-2,setsar=1:1 {to_file}'],
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
	)
	proc.communicate()

	# Transfer file down from host
	subprocess.run([
		'scp',
		f'{host}:{to_file}',
		output_video,
	], check=False)

	# Clean up old files on host
	proc = subprocess.Popen(
		['ssh', '-tt', host, f'rm -f {from_file} {to_file}'],
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
	)
	proc.communicate()


def get_normalized_load(host: str = 'localhost') -> float:
	"""
	Get a number from 0.0 to 1.0 indicating the percent load on the given host.

	Args:
		host (str): The SSH name of the machine, or `localhost` to check locally.

	Returns:
		float: `9999` if unable to calculate the load,
			otherwise a number indicating the load if successfully calculated.
	"""

	try:
		if host in ['', 'localhost']:
			text = subprocess.check_output(['top', '-n', '1', '-b'])
			nproc = subprocess.check_output(['nproc'])
		else:
			proc = subprocess.Popen(
				['ssh', '-tt', host, '-oConnectTimeout=120', 'nproc; top -n 1 -b'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
			)
			stdout, _ = proc.communicate()

			if stdout is None:
				return 9999

			nproc, text = stdout.replace(b'\r', b'').split(b'\n', 1)
	except subprocess.CalledProcessError:
		return 9999

	text = text.split(b'\n', 1)[0]
	nproc = int(nproc)

	if text.find(b'load average: ') < 0:
		return 9999

	load = float(text.split(b'load average: ')[1].split(b',')[0])

	return load / nproc


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

	proc = subprocess.Popen(
		['ssh', '-tt', host, '-oConnectTimeout=120', 'which ffmpeg'],
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
	)
	proc.communicate()
	return proc.returncode == 0


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
