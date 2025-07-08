"""application.types.weatherexecution"""

from typing import TypedDict
from datetime import datetime


class WeatherExecution(TypedDict):
	"""
	Information about the last weather execution.
	"""

	## The date and time when the last weather execution was performed.
	timestamp: datetime
	## A list of users who were alerted during the last weather execution.
	users: list[str]
	## Any error message from the last weather execution.
	error: str | None
