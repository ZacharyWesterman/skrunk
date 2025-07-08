"""application.types.weatheruserinput"""

from typing import TypedDict
from .weathertemp import WeatherTemp


class WeatherUserInput(TypedDict):
	"""
	Update information for a user in the weather alerts system.
	"""

	## The username of the user.
	username: str
	## The latitude of the user's location.
	lat: float
	## The longitude of the user's location.
	lon: float
	## The maximum temperature the user wants to receive alerts for.
	max: WeatherTemp
	## The minimum temperature the user wants to receive alerts for.
	min: WeatherTemp
