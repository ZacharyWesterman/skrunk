"""application.types.theme_"""

from typing import TypedDict


class Theme_(TypedDict):
	name: str
	colors: list[str]
	text: list[str]
	special: list[str]
	border: str
