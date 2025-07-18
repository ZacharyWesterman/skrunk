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
	updated: datetime | None
	creator: UserMinData
