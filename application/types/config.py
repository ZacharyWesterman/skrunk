"""application.types.config"""

from typing import TypedDict


class Config(TypedDict):
	"""
	A type for storing arbitrary configuration settings.
	"""

	## The name of the configuration setting.
	name: str
	## The value of the configuration setting.
	value: str | None
