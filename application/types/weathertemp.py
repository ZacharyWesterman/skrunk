"""application.types.weathertemp"""

from typing import TypedDict


class WeatherTemp(TypedDict):
	default: bool
	disable: bool
	value: float
