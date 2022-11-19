import application.exceptions as exceptions
from application.db.weather import get_users

def resolve_get_weather_users(_, info) -> list:
	return get_users()
