"""application.types.zipprogress"""

from typing import TypedDict


class ZipProgress(TypedDict):
	"""
	A type for keeping track of the progress of a zip archive creation.
	"""

	## The progress of the zip archive creation. 0-100%
	progress: float
	## The filename of the item being zipped
	item: str
