import application.exceptions as exceptions
from application.db.weather import get_users, get_last_exec, get_alert_history
from application.db import perms

@perms.module('weather')
def resolve_get_weather_users(_, info) -> list:
	return get_users()

@perms.module('weather')
def resolve_get_last_execution(_, info) -> dict:
	return get_last_exec() #May return None if weather alerts has never been run.

@perms.module('weather')
def resolve_get_alert_history(_, info, start: int, count: int) -> list:
	return get_alert_history(start, count)
