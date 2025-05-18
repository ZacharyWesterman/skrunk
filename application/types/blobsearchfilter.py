from typing import TypedDict
from datetime import datetime


class BlobSearchFilter(TypedDict):
	"""
	An input type for filtering blob data.
	All fields are optional, and if a field is null, it will not be used in the query.
	"""

	## The username of the user who created the blob.
	creator: str
	## The earliest date the blob was created.
	begin_date: datetime
	## The latest date the blob was created.
	end_date: datetime
	## The original filename of the blob.
	name: str
	## The tag query to filter blobs by.
	tag_expr: str
	## Filter by whether the blob is ephemeral or not.
	ephemeral: bool
