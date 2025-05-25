from typing import TypedDict
from .weathertemp_ import WeatherTemp_
from datetime import datetime


class WeatherUser(TypedDict):
	username: str
	lat: float
	lon: float
	max: WeatherTemp_
	min: WeatherTemp_
	last_sent: datetime | None
	exclude: bool
