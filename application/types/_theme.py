"""application.types._theme"""

from typing import TypedDict


class _Theme(TypedDict):
	name: str
	colors: list[str]
	text: list[str]
	special: list[str]
	border: str
