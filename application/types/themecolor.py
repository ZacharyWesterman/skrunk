"""application.types.themecolor"""

from typing import TypedDict


class ThemeColor(TypedDict):
	"""
	Color settings for a user theme.
	"""

	## The name of the color setting.
	name: str
	## The value of the color setting.
	value: str
