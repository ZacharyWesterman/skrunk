"""application.types.bugcomment"""

from typing import TypedDict
from bson.objectid import ObjectId
from datetime import datetime


class BugComment(TypedDict):
	"""
	A comment on a bug report.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The creation date and time of the comment.
	created: datetime
	## The username of the creator of the comment.
	creator: str
	## The raw text of the comment.
	body: str
	## The HTML-rendered version of the comment body.
	body_html: str
