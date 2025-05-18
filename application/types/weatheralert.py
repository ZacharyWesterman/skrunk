from typing import TypedDict
from datetime import datetime


class WeatherAlert(TypedDict):
	recipient: str
	message: str
	sent: datetime
