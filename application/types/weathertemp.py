"""application.types.weathertemp"""

from typing import TypedDict
from bson.objectid import ObjectId


class WeatherTemp(TypedDict):
	"""
	Temperature settings for weather alerts.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## Whether this temperature setting is the default value.
	default: bool
	## Whether this temperature setting is disabled.
	disable: bool
	## The temperature value in degrees Fahrenheit.
	value: float
