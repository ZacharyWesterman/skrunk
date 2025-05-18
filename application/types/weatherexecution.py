from typing import TypedDict
from datetime import datetime

class WeatherExecution(TypedDict):
	timestamp: datetime
	users: list[str]
	error: str

