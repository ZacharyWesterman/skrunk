from typing import TypedDict
from .weathertemp import WeatherTemp


class WeatherUserInput(TypedDict):
	username: str
	lat: float
	lon: float
	max: WeatherTemp | None
	min: WeatherTemp | None
