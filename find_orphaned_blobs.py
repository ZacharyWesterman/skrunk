"""This script lists blobs files that do not have a corresponding entry in the database."""

from pathlib import Path
from sys import argv
from typing import Generator

from bson.objectid import ObjectId


def list_blobs(path: Path) -> Generator[Path, None, None]:
	"""
	Recursively list all files in the given directory.

	Args:
		path (Path): The directory to search for blob files.

	Returns:
		list[Path]: A list of file paths found in the directory.
	"""
	for item in path.iterdir():
		if item.is_dir():
			yield from list_blobs(item)
		elif item.is_file() and item.stem[-2:] not in ['_t', '_p']:
			yield item


if __name__ == '__main__':

	if len(argv) < 2:
		print("Usage: find_orphaned_blobs.py <blob_path>")
		exit(1)

	blob_path = Path(argv[1])
	if not blob_path.is_dir():
		print(f"Error: {blob_path} is not a valid directory.")
		exit(1)

	from application.db import blob, init_db
	init_db()

	for file in list_blobs(blob_path):
		if not blob.db.find_one({"_id": ObjectId(file.stem)}):
			print(file)
