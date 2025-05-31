"""application.types.feed"""

from typing import TypedDict
from datetime import datetime
from .sortingoutput import SortingOutput


class Feed(TypedDict):
	"""
	A type for storing information about a data feed.
	"""

	## The unique identifier for the feed.
	id: str
	## The name of the feed.
	name: str
	## The username of the user who created the feed.
	creator: str
	## The date and time when the feed was created.
	created: datetime
	## The type of feed, such as 'rss', 'atom', etc.
	kind: str
	## The URL from which the feed is fetched.
	url: str
	## Whether the feed is set to notify the user of new documents.
	notify: bool
	## Whether the feed is currently inactive. If true, the feed will not fetch new documents.
	inactive: bool
	## The current page of the feed for navigation purposes.
	currentPage: int | None
	## The current sorting method for the feed documents, for navigation purposes.
	currentSort: SortingOutput | None
