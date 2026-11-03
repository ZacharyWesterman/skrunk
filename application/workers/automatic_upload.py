"""Periodically sync specially-tagged blobs to their respective video/music server location."""

import subprocess

from application.db.blob import blobs_enabled, delete_blob, get_blobs_by_tags
from application.db.settings import get_config, global_module_enabled
from application.types.blob_storage import BlobStorage


def upload_videos(url: str) -> None:
	for blob in get_blobs_by_tags('video', '__autoupload'):
		storage = BlobStorage(blob['id'], blob['ext'])
		type_folder = 'Shows' if '__series' in blob['tags'] else 'Movies'

		try:
			# Transfer file up to host
			subprocess.run([
				'rsync',
				storage.path(),
				f'{url}/{type_folder}/autoupload/{blob["name"]}/',
			], check=True)
		except subprocess.CalledProcessError as e:
			print(f'ERROR: {e}', flush=True)
			break

		# Once transferred, delete the blob.
		delete_blob(blob['id'])


def upload_music(url: str) -> None:
	for blob in get_blobs_by_tags('audio', '__autoupload'):
		storage = BlobStorage(blob['id'], blob['ext'])

		try:
			# Transfer file up to host
			subprocess.run([
				'rsync',
				storage.path(),
				f'{url}/',
			], check=True)
		except subprocess.CalledProcessError as e:
			print(f'ERROR: {e}', flush=True)
			break

		# Once transferred, delete the blob.
		delete_blob(blob['id'])


def automatic_upload() -> None:
	"""
	Automatically sync specially-tagged blobs to their respective video/music server location.
	"""

	if not blobs_enabled() or not global_module_enabled('files'):
		return

	if video_url := get_config('autoupload:video'):
		upload_videos(video_url)

	if music_url := get_config('autoupload:music'):
		upload_music(music_url)
