"""application.types.userthemeoutput"""

from typing import TypedDict
from bson.objectid import ObjectId
from .themecoloroutput import ThemeColorOutput
from .themesizeoutput import ThemeSizeOutput


class UserThemeOutput(TypedDict):
	"""
	Theme settings for a user.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The colors defined in the user's theme.
	colors: list[ThemeColorOutput]
	## The sizes defined in the user's theme.
	sizes: list[ThemeSizeOutput]
