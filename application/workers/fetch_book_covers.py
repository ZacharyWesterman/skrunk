"""Periodically scan for linked books with remote thumbnails and pull the thumbnails locally."""

import requests

from application.db.blob import (BlobStorage, add_reference, create_blob,
                                 create_blob_previews, delete_blob, file_info,
                                 mark_as_completed)
from application.db.book import get_remote_thumbs, set_thumbnail
from application.db.settings import global_module_enabled


def fetch_book_covers() -> None:
	"""
	If both books and blobs are enabled,
	scan for books with a remote thumbnail,
	and download it to blob storage.
	"""

	if not global_module_enabled('books') or not global_module_enabled('files'):
		return

	for book in get_remote_thumbs(50):
		thumb_url = book['thumbnail']

		response = requests.get(thumb_url, timeout=10)
		if response.status_code < 200 or response.status_code >= 300:
			print(f'WARN: Failed to download thumbnail for {book["_id"]}', flush=True)
			continue

		blob_id, ext = create_blob(
			'thumb.jpeg',
			['__book'],
			True,
			True,
			owner=book['creator']
		)
		storage_path = BlobStorage(blob_id, ext).path(create=True)

		try:
			with open(storage_path, 'wb') as fp:
				fp.write(response.content)
		except (FileNotFoundError, PermissionError, OSError):
			print(f'ERROR: Unable to create blob for book {book["_id"]}!', flush=True)
			delete_blob(blob_id)
			continue

		size, md5sum = file_info(storage_path)
		mark_as_completed(blob_id, size, md5sum)
		create_blob_previews([{'id': blob_id, 'ext': ext}])

		set_thumbnail(book['_id'], blob_id)
		add_reference(blob_id)
