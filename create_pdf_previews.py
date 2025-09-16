"""This script generates previews for all PDF blobs."""

from pathlib import Path
from sys import argv

from application.integrations import images, pdf
from application.types.blob_storage import (BlobPreview, BlobStorage,
                                            BlobThumbnail)

if __name__ == '__main__':

	if len(argv) < 2:
		print("Usage: create_pdf_previews.py <blob_path>")
		exit(1)

	blob_path = Path(argv[1])
	if not blob_path.is_dir():
		print(f"Error: {blob_path} is not a valid directory.")
		exit(1)

	from application.db import blob, init_db
	init_db(blob_path=argv[1])

	for i in blob.db.find({'mimetype': 'application/pdf', 'preview': None}):
		storage = BlobStorage(i['_id'], i['ext'])
		if not storage.exists:
			continue

		preview = BlobPreview(i['_id'], '.png')
		thumbnail = BlobThumbnail(i['_id'], '.png')

		if pdf.create_preview(storage.path(), preview.path()):
			blob.db.update_one({'_id': i['_id']}, {'$set': {'preview': preview.basename()}})

			if images.downscale(preview.path(), 128, thumbnail.path()):
				blob.db.update_one({'_id': i['_id']}, {'$set': {'thumbnail': thumbnail.basename()}})
