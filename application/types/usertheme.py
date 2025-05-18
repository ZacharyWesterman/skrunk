from typing import TypedDict
from .themecolor import ThemeColor
from .themesize import ThemeSize


class UserTheme(TypedDict):
	colors: list[ThemeColor | None]
	sizes: list[ThemeSize | None]
