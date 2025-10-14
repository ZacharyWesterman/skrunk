"""application.types.resetcode"""

from typing import TypedDict
from bson.objectid import ObjectId


class ResetCode(TypedDict):
	## The unique identifier of the document.
	_id: ObjectId
	## The reset code string.
	code: str
