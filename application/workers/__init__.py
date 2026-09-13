"""Module for background worker process management."""

from os import environ

from apscheduler.schedulers.background import BackgroundScheduler

from .blob_cleanup import blob_cleanup
from .fetch_book_covers import fetch_book_covers

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
	_SCHEDULER.add_job(fetch_book_covers, 'interval', seconds=3600)

	_SCHEDULER.start()
