"""application.types.usertheme_"""

from typing import TypedDict
from .themecolor_ import ThemeColor_
from .themesize_ import ThemeSize_


class UserTheme_(TypedDict):
	"""
	Theme settings for a user.
	"""

	## The colors defined in the user's theme.
	colors: list[ThemeColor_]
	## The sizes defined in the user's theme.
	sizes: list[ThemeSize_]
