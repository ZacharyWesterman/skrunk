"""application.types.badtagquery"""

from typing import TypedDict


class BadTagQuery(TypedDict):
	"""
	An error that occurs when a tag query has invalid syntax.
	"""

	## The error message
	message: str
