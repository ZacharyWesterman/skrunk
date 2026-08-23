"""application.types.documentsearchfilter"""

from typing import TypedDict
from bson.objectid import ObjectId


class DocumentSearchFilter(TypedDict):
	"""
	An input type for filtering documents.
	All fields are optional, and if a field is null, it will not be used in the query.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The title of the document.
	title: str | None
	## The tag query to filter documents by.
	tag_expr: str | None
	## Whether documents are shared with the current user.
	shared: bool | None
