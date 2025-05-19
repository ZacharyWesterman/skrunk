from typing import TypedDict


class BlobCount(TypedDict):
	"""
	A type for getting the number of blobs that match a query.
	This type is used so that if the query fails, we can return an error message instead of zero.
	"""

	## The number of blobs that match the query
	count: int
