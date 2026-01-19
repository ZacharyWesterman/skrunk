"""application.types.feeddocument"""

from typing import TypedDict
from bson.objectid import ObjectId
from datetime import datetime


class FeedDocument(TypedDict):
	"""
	An individual feed document, representing an item in a feed.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The unique identifier for the feed document.
	id: str
	## The ID of the feed this document belongs to.
	feed: str
	## The original author of the document, if available.
	author: str | None
	## The title of the document.
	title: str | None
	## The date and time when the document was posted.
	posted: datetime | None
	## The raw text content of the document.
	body: str
	## The HTML-rendered version of the document body.
	body_html: str
	## The date and time when the document was first fetched.
	created: datetime
	## The date and time when the document was last updated.
	updated: datetime | None
	## The URL from which the document was fetched.
	url: str
	## Whether the document is marked as read.
	read: bool
	## The length of the HTML-rendered version of the document body.
	html_len: int
