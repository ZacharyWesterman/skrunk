"""application.types.weatheruser"""

from typing import TypedDict
from .weathertemp_ import WeatherTemp_
from datetime import datetime


class WeatherUser(TypedDict):
	"""
	Information about a user in the weather alerts system.
	"""

	## The username of the user.
	username: str
	## The latitude of the user's location.
	lat: float
	## The longitude of the user's location.
	lon: float
	## The maximum temperature the user wants to receive alerts for.
	max: WeatherTemp_
	## The minimum temperature the user wants to receive alerts for.
	min: WeatherTemp_
	## The date and time when the user was last sent an alert.
	last_sent: datetime | None
	## Whether the user is enabled to receive alerts.
	exclude: bool
