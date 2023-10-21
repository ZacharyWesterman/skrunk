from application.db import blob
import psutil
from pathlib import Path

def disk_usage() -> list[dict]:

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
			return [info('Application','.'), info('Blob Storage', blob.blob_path)]
	else:
		return [info('Application', '.')]
