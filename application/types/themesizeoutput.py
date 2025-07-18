"""application.types.themesizeoutput"""

from typing import TypedDict
from bson.objectid import ObjectId


class ThemeSizeOutput(TypedDict):
	"""
	Size settings for a user theme.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The name of the size setting.
	name: str
	## The value of the size setting.
	value: str
