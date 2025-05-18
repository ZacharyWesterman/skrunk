from typing import TypedDict
from datetime import datetime


class FeedDocument(TypedDict):
	id: str
	feed: str
	author: str
	title: str
	posted: datetime
	body: str
	body_html: str
	created: datetime
	updated: datetime
	url: str
	read: bool
