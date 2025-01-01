"""application.integrations.system"""

from application.db import blob
import psutil
from pathlib import Path


def disk_usage() -> list[dict]:
	"""
	Retrieve disk usage information for the application and for blob storage (if it exists).
	If the application and blob storage are on the same disk, they are listed together.

	Returns:
		list[dict]: A list of dictionaries containing disk usage information. Each dictionary has the following keys:
			- 'name' (str): The name of the storage (e.g., 'Application', 'Blob Storage').
			- 'free' (int): The amount of free space in bytes.
			- 'used' (int): The amount of used space in bytes.
			- 'total' (int): The total amount of space in bytes.
	"""

	def info(name: str, dir: str) -> dict:
		inf = psutil.disk_usage(dir)
		return {
			'name': name,
			'free': inf.free,
			'used': inf.used,
			'total': inf.total,
		}

	def get_mount_point(dir: str) -> str:
		parent = Path(dir).resolve()
		while str(parent) != '/' and not parent.is_mount():
			parent = parent.parent

		return str(parent)

	if blob.blob_path:
		if get_mount_point('.') == get_mount_point(blob.blob_path):
			return [info('Application / Blob Storage', '.')]
		else:
			return [info('Application', '.'), info('Blob Storage', blob.blob_path)]
	else:
		return [info('Application', '.')]
