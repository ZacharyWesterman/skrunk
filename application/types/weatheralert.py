"""application.types.weatheralert"""

from typing import TypedDict
from bson.objectid import ObjectId
from datetime import datetime


class WeatherAlert(TypedDict):
	"""
	A logging result of a weather alert.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The username of the user who received the alert.
	recipient: str
	## The contents of the alert message.
	message: str
	## The date and time when the alert was sent.
	sent: datetime
