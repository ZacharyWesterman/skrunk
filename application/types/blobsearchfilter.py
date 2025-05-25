from typing import TypedDict
from datetime import datetime


class BlobSearchFilter(TypedDict):
	"""
	An input type for filtering blob data.
	All fields are optional, and if a field is null, it will not be used in the query.
	"""

	## The username of the user who created the blob.
	creator: str | None
	## The earliest date the blob was created.
	begin_date: datetime | None
	## The latest date the blob was created.
	end_date: datetime | None
	## The original filename of the blob.
	name: str | None
	## The tag query to filter blobs by.
	tag_expr: str | None
	## Filter by whether the blob is ephemeral or not.
	ephemeral: bool | None
