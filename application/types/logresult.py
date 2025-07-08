"""application.types.logresult"""

from typing import TypedDict


class LogResult(TypedDict):
	"""
	A type representing the result of a logging operation.
	"""

	## Whether the logging operation was successful.
	result: bool
