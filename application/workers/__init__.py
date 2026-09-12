"""Module for background worker process management."""

import time
from threading import Thread

from application.db.blob import delete_blob, get_old_ephemeral_blobs

_THREAD: Thread | None = None


def begin() -> None:
	"""
	Launch background worker processes.
	"""
	global _THREAD
	if _THREAD is not None:
		return

	_THREAD = Thread(target=blob_cleanup)
	_THREAD.start()


def blob_cleanup() -> None:
	"""
	Periodically scan for orphan blobs and clean them up.
	"""

	while True:
		deleted_ct = 0
		for blob_id in get_old_ephemeral_blobs():
			delete_blob(str(blob_id))

		if deleted_ct:
			print(f'Deleted {deleted_ct} orphan (ephemeral) blob entries.', flush=True)

		# Only check for orphan blobs once per hour
		time.sleep(3600)
