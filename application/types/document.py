"""application.types.document"""

from typing import TypedDict
from bson.objectid import ObjectId
from datetime import datetime
from .usermindata import UserMinData


class Document(TypedDict):
	## The unique identifier of the document.
	_id: ObjectId
	id: str
	title: str
	body: str
	body_html: str
	created: datetime
	creator: UserMinData
	updated: datetime | None
	updater: UserMinData | None
	blob_id: str | None
	tags: list[str]
	shared_users: list[UserMinData]
	shared_groups: list[str]
