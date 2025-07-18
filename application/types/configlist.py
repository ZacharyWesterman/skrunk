"""application.types.configlist"""

from typing import TypedDict
from bson.objectid import ObjectId
from .config import Config


class ConfigList(TypedDict):
	"""
	A list of configuration settings.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The list of configuration settings.
	configs: list[Config]
