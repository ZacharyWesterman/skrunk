"""application.types.weatherexecution"""

from typing import TypedDict
from bson.objectid import ObjectId
from datetime import datetime


class WeatherExecution(TypedDict):
	"""
	Information about the last weather execution.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The date and time when the last weather execution was performed.
	timestamp: datetime
	## A list of users who were alerted during the last weather execution.
	users: list[str]
	## Any error message from the last weather execution.
	error: str | None
