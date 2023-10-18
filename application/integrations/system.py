from application.db import blob
import psutil

def disk_usage() -> list[dict]:

	def info(name: str, dir: str) -> dict:
		inf = psutil.disk_usage(dir)
		return {
			'name': name,
			'free': inf.free,
			'used': inf.used,
			'total': inf.total,
		}


	return [info('Application','.'), info('Blob Storage', blob.blob_path)] if blob.blob_path else [info('Application', '.')]
