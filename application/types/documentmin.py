"""application.types.documentmin"""

from typing import TypedDict
from bson.objectid import ObjectId
from .usermindata import UserMinData
from datetime import datetime


class DocumentMin(TypedDict):
	## The unique identifier of the document.
	_id: ObjectId
	id: str
	title: str
	creator: UserMinData
	created: datetime
