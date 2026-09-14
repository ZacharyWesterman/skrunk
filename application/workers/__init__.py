"""Module for background worker process management."""

from os import environ

from apscheduler.schedulers.background import BackgroundScheduler

from .blob_cleanup import blob_cleanup
from .feeds import fetch_feeds
from .fetch_book_covers import fetch_book_covers
from .sync_google_books import sync_google_books

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

	_SCHEDULER.add_job(blob_cleanup, 'interval', hours=1)
	_SCHEDULER.add_job(fetch_feeds, 'interval', hours=1, kwargs={'hours': 1})
	_SCHEDULER.add_job(fetch_book_covers, 'interval', hours=1)
	_SCHEDULER.add_job(sync_google_books, 'interval', minutes=20)

	_SCHEDULER.start()
