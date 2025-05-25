"""application.types.usertheme_"""

from typing import TypedDict
from .themecolor_ import ThemeColor_
from .themesize_ import ThemeSize_


class UserTheme_(TypedDict):
	colors: list[ThemeColor_]
	sizes: list[ThemeSize_]
