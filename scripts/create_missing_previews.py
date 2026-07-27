#!/usr/bin/env python3
"""This script searches for blobs with missing previews / thumbnails and creates them."""

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position

import sys  # nopep8
from pathlib import Path

if __name__ == '__main__' and __package__ is None:
	sys.path.append(str(Path(__file__).resolve().parent.parent))

import application  # nopep8

if __name__ == '__main__':
	args, app = application.new('Missing Preview Runner')

	if args.blob_path is None:
		print('ERROR: No blob path specified!')
		exit(1)

	from application.db.blob import (create_blob_previews,
	                                 find_blobs_without_previews)

	for i in find_blobs_without_previews():
		print(f'Creating missing preview for `{i["id"]}`...', flush=True)
		create_blob_previews([i])
