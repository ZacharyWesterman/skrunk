"""application.types.theme"""

from typing import TypedDict


class Theme(TypedDict):
	name: str
	colors: list[str]
	text: list[str]
	special: list[str]
	border: str
