"""Sync google books so the data stays up-to-date."""

from datetime import UTC, datetime, timedelta

from application.db.book import list_books_not_synced, sync_book_data


def sync_google_books() -> None:
	"""
	Sync data for a handful of books, if they haven't been synced in a while.
	"""
	since = datetime.now(UTC) - timedelta(weeks=1)

	for book_id in list_books_not_synced(since, 0, 10):
		sync_book_data(book_id)
