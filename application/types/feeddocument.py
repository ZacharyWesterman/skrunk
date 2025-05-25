"""application.types.feeddocument"""

from typing import TypedDict
from datetime import datetime


class FeedDocument(TypedDict):
	id: str
	feed: str
	author: str | None
	title: str | None
	posted: datetime | None
	body: str
	body_html: str
	created: datetime
	updated: datetime | None
	url: str
	read: bool
