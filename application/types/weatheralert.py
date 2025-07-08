"""application.types.weatheralert"""

from typing import TypedDict
from datetime import datetime


class WeatherAlert(TypedDict):
	"""
	A logging result of a weather alert.
	"""

	## The username of the user who received the alert.
	recipient: str
	## The contents of the alert message.
	message: str
	## The date and time when the alert was sent.
	sent: datetime
