"""application.types.weathertemp"""

from typing import TypedDict


class WeatherTemp(TypedDict):
	"""
	Temperature settings for weather alerts.
	"""

	## Whether this temperature setting is the default value.
	default: bool
	## Whether this temperature setting is disabled.
	disable: bool
	## The temperature value in degrees Fahrenheit.
	value: float
