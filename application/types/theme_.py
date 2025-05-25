"""application.types.theme_"""

from typing import TypedDict


class Theme_(TypedDict):
	"""
	Creation info for a new theme template.
	"""

	## The name of the theme.
	name: str
	## The colors defined in the theme.
	colors: list[str]
	## The text colors defined in the theme.
	text: list[str]
	## The special colors defined in the theme.
	special: list[str]
	## The border radius defined in the theme.
	border: str
