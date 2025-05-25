"""application.types.apikey"""

from typing import TypedDict
from datetime import datetime


class APIKey(TypedDict):
	"""
	A type describing an API key.
	"""

	## The unique identifier for the API key.
	key: str
	## A description of the API key, which can be used to identify its purpose.
	description: str
	## The date and time when the API key was created.
	created: datetime
	## The list of permissions granted to the API key.
	perms: list[str]
