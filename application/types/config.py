"""application.types.config"""

from typing import TypedDict
from bson.objectid import ObjectId


class Config(TypedDict):
	"""
	A type for storing arbitrary configuration settings.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The name of the configuration setting.
	name: str
	## The value of the configuration setting.
	value: str | None
