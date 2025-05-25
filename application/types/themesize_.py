"""application.types.themesize_"""

from typing import TypedDict


class ThemeSize_(TypedDict):
	"""
	Size settings for a user theme.
	"""

	## The name of the size setting.
	name: str
	## The value of the size setting.
	value: str
