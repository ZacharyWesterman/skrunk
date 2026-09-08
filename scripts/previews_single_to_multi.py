#!/usr/bin/env python3
"""
This script converts all blobs from the single-preview format to multi-preview.
Not every blob will have multiple previews, this just adds future support for it.
"""

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position

import sys  # nopep8
from pathlib import Path

if __name__ == '__main__' and __package__ is None:
	sys.path.append(str(Path(__file__).resolve().parent.parent))

import application  # nopep8

if __name__ == '__main__':
	args, app = application.new('Multi Preview Data Patch')

	from application.db.blob import db

	for i in db.find({'preview': {'$exists': True}}):
		previews = [] if i.get('preview') is None else [i['preview']]
		db.update_one({'_id': i['_id']}, {'$set': {'previews': previews}, '$unset': {'preview': True}})
		print(i)
