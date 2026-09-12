"""Module for background worker process management."""

from os import environ

from apscheduler.schedulers.background import BackgroundScheduler

from application.db.blob import delete_blob, get_old_ephemeral_blobs

_SCHEDULER = None


def begin() -> None:
	"""
	Launch background worker processes.
	"""

	# In dev mode, this prevents workers from getting spawned twice.
	if environ.get("WERKZEUG_RUN_MAIN") == "true":
		return

	global _SCHEDULER
	_SCHEDULER = BackgroundScheduler(daemon=True)
	_SCHEDULER.add_job(blob_cleanup, 'interval', seconds=3600)
	_SCHEDULER.start()


def blob_cleanup() -> None:
	"""
	Periodically scan for orphan blobs and clean them up.
	"""

	deleted_ct = 0
	for blob_id in get_old_ephemeral_blobs():
		delete_blob(str(blob_id))

	if deleted_ct:
		print(f'Deleted {deleted_ct} orphan (ephemeral) blob entries.', flush=True)
