"""application.types.themecolor"""

from typing import TypedDict
from bson.objectid import ObjectId


class ThemeColor(TypedDict):
	"""
	Color settings for a user theme.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The name of the color setting.
	name: str
	## The value of the color setting.
	value: str
