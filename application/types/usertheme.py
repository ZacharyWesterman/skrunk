"""application.types.usertheme"""

from typing import TypedDict
from .themecolor import ThemeColor
from .themesize import ThemeSize


class UserTheme(TypedDict):
	"""
	Theme settings for a user.
	"""

	## The colors defined in the user's theme.
	colors: list[ThemeColor]
	## The sizes defined in the user's theme.
	sizes: list[ThemeSize]
