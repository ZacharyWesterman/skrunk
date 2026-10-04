"""application.types.motd"""

from typing import TypedDict
from bson.objectid import ObjectId


class Motd(TypedDict):
	## The unique identifier of the document.
	_id: ObjectId
	id: str
	text: str
